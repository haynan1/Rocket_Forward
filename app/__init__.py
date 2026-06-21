import secrets
from flask import Flask, request
from flask_login import current_user
from flask_migrate import upgrade as migrate_upgrade
from sqlalchemy import text
from config import Config
from .extensions import db, migrate, login_manager, scheduler, csrf, limiter

# Lock id arbitrário usado só para serializar a migration entre workers no Postgres.
_MIGRATION_LOCK_ID = 727271

def _run_migrations(app):
    with app.app_context():
        if db.engine.dialect.name != 'postgresql':
            # SQLite é o caminho documentado de processo único (python run.py); sem
            # múltiplos workers concorrendo pela migration, o lock não é necessário.
            migrate_upgrade()
            return
        # Em deploy multi-worker (ex.: gunicorn -w N), todo worker sobe e tentaria correr
        # `flask db upgrade` ao mesmo tempo; o advisory lock serializa isso e evita corrida
        # na tabela alembic_version.
        with db.engine.connect() as conn:
            conn.execute(text('SELECT pg_advisory_lock(:id)'), {'id': _MIGRATION_LOCK_ID})
            try:
                migrate_upgrade()
            finally:
                conn.execute(text('SELECT pg_advisory_unlock(:id)'), {'id': _MIGRATION_LOCK_ID})

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    # Muda a versão dos arquivos visuais a cada inicialização, evitando que o
    # navegador reutilize CSS/JS antigos depois de `python run.py`.
    app.config['ASSET_VERSION'] = secrets.token_urlsafe(8)
    db.init_app(app); migrate.init_app(app, db); login_manager.init_app(app)
    csrf.init_app(app); limiter.init_app(app)
    from .models import User
    from .i18n import EN_US, current_locale, translate
    @app.context_processor
    def inject_translations():
        return {'_': translate, 'current_locale': current_locale(), 'translations': EN_US}
    @login_manager.user_loader
    def load_user(user_id): return db.session.get(User, int(user_id))
    from .blueprints import auth, main, goals, api
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(goals)
    app.register_blueprint(api)
    # API JSON usa a mesma sessão de cookie do site, mas é consumida via fetch/XHR
    # (nunca por <form> HTML) e DELETE não é um método de form HTML — SESSION_COOKIE_SAMESITE
    # ='Lax' já impede o envio do cookie em requisições cross-site para esses métodos,
    # então o token CSRF (pensado para <form> renderizados pelo servidor) não se aplica aqui.
    csrf.exempt(api)

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com 'unsafe-inline'; "
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
            "img-src 'self' data:"
        )
        if app.config.get('SESSION_COOKIE_SECURE'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'no-store, max-age=0, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    @app.after_request
    def sync_locale_cookie(response):
        # Espelha o idioma do usuário logado num cookie para que as telas
        # de login/cadastro/recuperação (sem usuário autenticado) continuem
        # respeitando a preferência depois do logout.
        if request.endpoint != 'static' and current_user.is_authenticated:
            response.set_cookie(
                'locale', current_user.locale, max_age=31536000,
                httponly=True, samesite='Lax', secure=app.config.get('SESSION_COOKIE_SECURE', False),
            )
        return response

    _run_migrations(app)
    if not scheduler.running:
        scheduler.start()
    @app.cli.command('demo-user')
    def demo_user():
        from .services import create_demo_user
        create_demo_user(); print('Usuário demo criado: demo@rocket.forward / foguete123')
    return app
