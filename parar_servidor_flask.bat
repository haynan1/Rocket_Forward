@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0parar_servidor_flask.ps1" -Port 5000
pause
