#!/usr/bin/env bash
# Запуск веб-просмотрщика базы знаний и вопросов по Java.
# Работает и из терминала, и по двойному клику из файлового менеджера:
# при запуске из GUI сам открывает терминал и запускает в нём сервер.

SELF="$(readlink -f "$0")"
APP_DIR="$(dirname "$SELF")/webapp"

run_server() {
  cd "$APP_DIR" || { echo "Не найден каталог: $APP_DIR"; read -rp "Нажмите Enter для выхода..."; exit 1; }
  if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
  echo "Запуск приложения… Откроется браузер: http://127.0.0.1:8000/"
  echo "Для остановки нажмите Ctrl+C."
  exec "$PY" app.py
}

# Уже в терминале (есть TTY) или повторный запуск с флагом — просто запускаем сервер.
if [ -t 1 ] || [ "$1" = "--in-terminal" ]; then
  run_server
fi

# Запуск из GUI (нет TTY): открыть терминал и выполнить этот же скрипт внутри него.
for term in xfce4-terminal x-terminal-emulator gnome-terminal konsole mate-terminal xterm; do
  command -v "$term" >/dev/null 2>&1 || continue
  if [ "${KBAPP_DRYRUN:-0}" = "1" ]; then echo "выбран терминал: $term"; exit 0; fi
  case "$term" in
    xfce4-terminal|x-terminal-emulator)
      exec "$term" --title="База знаний Java" -x bash "$SELF" --in-terminal ;;
    gnome-terminal|mate-terminal)
      exec "$term" -- bash "$SELF" --in-terminal ;;
    konsole|xterm)
      exec "$term" -e bash "$SELF" --in-terminal ;;
  esac
done

# Терминал не найден — запускаем в фоне (браузер откроется сам из app.py).
run_server
