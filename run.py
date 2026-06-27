"""Inicializador da Rocket Forward.

Execute apenas: ``python run.py``. Na primeira execucao, o script cria a
venv local, instala requirements.txt, prepara o .env e reinicia dentro dela
automaticamente.
"""
from __future__ import annotations

import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
ENV_PATH = ROOT / '.env'


def _default_env(secret_key: str) -> str:
    return f"""SECRET_KEY={secret_key}
DATABASE_URL=sqlite:///rocket_forward.db

# development habilita o debugger do Flask (FLASK_DEBUG=1) e cookies de sessao sem flag Secure.
# Em producao use FLASK_ENV=production: forca debug desligado e cookies de sessao so por HTTPS.
FLASK_ENV=development
FLASK_DEBUG=1

# Liga o botao de "ativar Premium" sem cobranca real. Desligue (DEMO_MODE=0) antes de cobrar de verdade.
DEMO_MODE=1

# Recuperacao de senha por e-mail (opcional no computador local).
# Sem SMTP configurado, o link temporario e registrado somente no terminal do programa.
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_SENDER=
SMTP_USE_TLS=1
"""


def _has_secret_key(content: str) -> bool:
    for line in content.splitlines():
        if line.strip().startswith('SECRET_KEY='):
            return bool(line.split('=', 1)[1].strip())
    return False


def ensure_env_file() -> None:
    """Cria ou completa o .env local antes de carregar a configuracao Flask."""
    if not ENV_PATH.exists():
        print('Criando arquivo .env com configuracao local...')
        ENV_PATH.write_text(_default_env(secrets.token_hex(32)), encoding='utf-8')
        return

    content = ENV_PATH.read_text(encoding='utf-8')
    if _has_secret_key(content):
        return

    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith('SECRET_KEY='):
            lines[index] = f'SECRET_KEY={secrets.token_hex(32)}'
            break
    else:
        lines.insert(0, f'SECRET_KEY={secrets.token_hex(32)}')

    print('Preenchendo SECRET_KEY no .env...')
    ENV_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def ensure_virtualenv() -> None:
    """Cria e prepara a venv antes de carregar qualquer dependencia web."""
    if Path(sys.executable).resolve() == VENV_PYTHON.resolve():
        return

    if not VENV_PYTHON.exists():
        print('Criando ambiente virtual...')
        subprocess.check_call([sys.executable, '-m', 'venv', str(ROOT / 'venv')])

    print('Verificando dependências...')
    subprocess.check_call([str(VENV_PYTHON), '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')])
    print('Ambiente pronto. Iniciando Rocket Forward...')
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])


ensure_env_file()
ensure_virtualenv()

from app import create_app  # noqa: E402  (carregado somente dentro da venv)

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
