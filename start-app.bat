@echo off
REM Запуск веб-просмотрщика базы знаний и вопросов по Java (Windows).
REM Работает из командной строки и по двойному клику в проводнике.
chcp 65001 >nul
cd /d "%~dp0webapp" || (echo Не найден каталог webapp & pause & exit /b 1)

echo Запуск приложения... Откроется браузер: http://127.0.0.1:8000/
echo Для остановки нажмите Ctrl+C.

REM Сначала пробуем launcher "py", затем "python".
where py >nul 2>nul && (py app.py) || (python app.py)

REM Окно не закрывается сразу, чтобы было видно сообщения об ошибке.
pause
