@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\project_scope_status.ps1"
pause
