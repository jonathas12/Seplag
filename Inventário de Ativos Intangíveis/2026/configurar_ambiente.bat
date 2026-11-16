@echo off
REM Cria o ambiente Python do projeto e instala as bibliotecas (clique duas vezes).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0configurar_ambiente.ps1"
pause
