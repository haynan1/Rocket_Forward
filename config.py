import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Variável de ambiente {name} é obrigatória. Defina-a em seu .env "
            f"(veja .env.example)."
        )
    return value


IS_PRODUCTION = os.getenv('FLASK_ENV', 'development') == 'production'


class Config:
    SECRET_KEY = _require_env('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///rocket_forward.db').replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TIMEZONE = 'America/Sao_Paulo'
    DEBUG = not IS_PRODUCTION and os.getenv('FLASK_DEBUG', '0') == '1'
    DEMO_MODE = os.getenv('DEMO_MODE', '1') == '1'

    # Cookies de sessão: HttpOnly sempre, Secure obrigatório em produção (exige HTTPS).
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = IS_PRODUCTION

    WTF_CSRF_ENABLED = True

    # Limite global de corpo de requisição: evita uploads (ex.: foto de perfil) usados
    # como vetor de esgotamento de memória/disco.
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024

    # Backend do rate limiter. Em memória funciona para um único processo (uso atual);
    # em deploy com múltiplos workers, configure RATELIMIT_STORAGE_URI=redis://... no .env.
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
