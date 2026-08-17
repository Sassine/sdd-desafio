@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
  set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
)

if not exist "%PYTHON_EXE%" (
  echo Python not found. Install Python 3.12 and try again.
  echo.
  pause
  exit /b 1
)

if "%~1"=="" (
  echo Uso: reembolso.cmd --input exemplos/despesas-exemplo.json --output resultado.json
  echo Exemplo: reembolso.cmd --input exemplos/despesas-exemplo.json --output resultado.json
  echo.
  pause
  exit /b 0
)

"%PYTHON_EXE%" "%SCRIPT_DIR%src\reembolso.py" %*
if errorlevel 1 (
  echo.
  echo Falha ao executar o motor de reembolso.
  pause
)
exit /b %ERRORLEVEL%
