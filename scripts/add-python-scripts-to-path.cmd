@echo off
REM Add current default "python" Scripts folder to PATH (session or user).
REM
REM Session mode runs in a separate PowerShell process: it does NOT change
REM the PATH of an already-open PowerShell window. For that, run the .ps1
REM in the same PowerShell:  .\scripts\add-python-scripts-to-path.ps1
REM
REM Usage:
REM   scripts\add-python-scripts-to-path.cmd
REM   scripts\add-python-scripts-to-path.cmd user
setlocal
set SCOPE=Session
if /i "%~1"=="user" set SCOPE=User

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0add-python-scripts-to-path.ps1" -Scope %SCOPE%

endlocal
