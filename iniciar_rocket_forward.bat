@echo off
setlocal

rem Inicia o Rocket Forward em segundo plano a partir desta pasta.
set "ROOT=%~dp0"

if exist "%ROOT%venv\Scripts\python.exe" (
    start "Rocket Forward" /min "%ROOT%venv\Scripts\python.exe" "%ROOT%run.py"
) else (
    rem Na primeira execução, run.py cria a venv e instala as dependências.
    start "Rocket Forward" /min python "%ROOT%run.py"
)

endlocal
