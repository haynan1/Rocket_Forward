"""Inicializador da Rocket Forward.

Execute apenas: ``python run.py``. Na primeira execução, o script cria a
venv local, instala requirements.txt e reinicia dentro dela automaticamente.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def ensure_virtualenv() -> None:
    """Cria e prepara a venv antes de carregar qualquer dependência web."""
    if Path(sys.executable).resolve() == VENV_PYTHON.resolve():
        return

    if not VENV_PYTHON.exists():
        print('Criando ambiente virtual...')
        subprocess.check_call([sys.executable, '-m', 'venv', str(ROOT / 'venv')])

    print('Verificando dependências...')
    subprocess.check_call([str(VENV_PYTHON), '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt')])
    print('Ambiente pronto. Iniciando Rocket Forward...')
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])


ensure_virtualenv()

from app import create_app  # noqa: E402  (carregado somente dentro da venv)

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
