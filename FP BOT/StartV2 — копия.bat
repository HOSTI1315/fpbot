@echo off
REM Переменная для указания пути к Python (если Python не добавлен в системные переменные PATH)
set PYTHON_PATH=python

REM Проверяем наличие Python
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден. Убедитесь, что Python установлен и доступен в системном PATH.
    pause
    exit /b
)

REM Запускаем основной скрипт
echo Запуск скрипта...
cd /d %~dp0
%PYTHON_PATH% main.py

REM Если скрипт завершился, показываем сообщение
echo Скрипт завершил работу.
pause