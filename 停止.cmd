@echo off
start "" powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0RAG\scripts\desktop.ps1" -Action Stop
exit /b
