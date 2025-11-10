#!/bin/bash
# Скрипт обновления проекта Makrei на VPS

set -e  # Выход при ошибке

PROJECT_DIR="/root/Projects/makrei_online"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="makrei_online.service"

echo "1. Переходим в папку проекта..."
cd "$PROJECT_DIR"

echo "2. Получаем последние изменения из GitHub..."
git fetch origin
git reset --hard origin/main

echo "3. Проверяем виртуальное окружение..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Создаём новое виртуальное окружение..."
    python3 -m venv "$VENV_DIR"
fi

echo "4. Активируем виртуальное окружение..."
source "$VENV_DIR/bin/activate"

echo "5. Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

echo "6. Перезапускаем Gunicorn..."
sudo systemctl daemon-reload
sudo systemctl restart $SERVICE_NAME
sudo systemctl status $SERVICE_NAME --no-pager

echo "Обновление проекта завершено!"
