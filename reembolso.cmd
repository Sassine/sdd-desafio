@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 "%SCRIPT_DIR%src\reembolso.py" %*
  exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  python "%SCRIPT_DIR%src\reembolso.py" %*
  exit /b %ERRORLEVEL%
)

echo Python not found. Install Python 3.12 and try again. 1>&2
exit /b 1
