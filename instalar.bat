@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Creando entorno virtual...
python -m venv venv || (echo Error: verifica que Python este instalado con el comando python --version & pause & exit /b 1)
call venv\Scripts\activate.bat
echo Instalando dependencias...
python -m pip install -r requirements.txt || (echo Error al instalar las dependencias. Revisa el README. & pause & exit /b 1)
echo.
echo Instalacion terminada. Ahora ejecuta iniciar.bat
pause