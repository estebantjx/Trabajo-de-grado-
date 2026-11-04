@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist venv\Scripts\activate.bat (
  echo Primero ejecuta instalar.bat
  pause
  exit /b 1
)
call venv\Scripts\activate.bat
echo Iniciando la aplicacion en http://localhost:5000  (Ctrl + C para detener)
start "" http://localhost:5000
python run.py
pause