@echo off

REM --- Configuración ---
REM Establece la ruta a tu ejecutable de Python.
REM Opción 1: Si Python está en tu PATH, puedes usar solo "python".
SET PYTHON_EXE="python"


REM Nombre de tu script de Python
SET PYTHON_SCRIPT="automatizacion_nba.py"

REM --- Ejecución ---
ECHO Iniciando el script de Python: %PYTHON_SCRIPT%

REM Cambia al directorio donde se encuentra este archivo .bat (y tu script .py)
cd /d "%~dp0"

REM Ejecuta el script de Python
%PYTHON_EXE% %PYTHON_SCRIPT%

ECHO.

pause