@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
  set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
)

if not exist "%PYTHON_EXE%" (
  echo Python 3.12 not found. Install Python and try again.
  echo.
  pause
  exit /b 1
)

if "%~1"=="" (
  echo Uso: reembolso.bat --input exemplos/despesas-exemplo.json --output resultado.json
  echo Exemplo: reembolso.bat --input exemplos/despesas-exemplo.json --output resultado.json
  echo.
  pause
  exit /b 0
)

"%PYTHON_EXE%" "src\reembolso.py" %*
if errorlevel 1 (
  echo.
  echo Falha ao executar o motor de reembolso.
  pause
)
exit /b %ERRORLEVEL%
