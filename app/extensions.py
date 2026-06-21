from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Entre para acessar sua missão.'
# Nenhum job está registrado ainda. Ao adicionar jobs reais (lembretes), use um
# jobstore compartilhado (ex.: Redis) se o app rodar com mais de um worker/processo,
# senão cada worker executará o mesmo job duplicado.
scheduler = BackgroundScheduler(timezone='America/Sao_Paulo')
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
