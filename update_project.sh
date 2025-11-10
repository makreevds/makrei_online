#!/bin/bash
set -e  # Остановить выполнение при любой ошибке

PROJECT_DIR="/root/Projects/makrei_online"   # Папка проекта на сервере
VENV_DIR="$PROJECT_DIR/venv"                 # Путь к виртуальному окружению
SERVICE_NAME="makrei_online.service"         # Название службы Gunicorn

echo "--- НАЧАЛО ОБНОВЛЕНИЯ ---"

cd "$PROJECT_DIR"  # Переходим в папку проекта

echo "1. Получаем последние изменения из репозитория..."
git fetch origin              # Получаем обновления
git pull --rebase origin main # Подтягиваем и накладываем изменения

echo "2. Проверяем виртуальное окружение..."
if [ ! -d "$VENV_DIR" ]; then
    # Создаём окружение, если не существует
    python3 -m venv "$VENV_DIR"
fi

echo "3. Активируем виртуальное окружение..."
source "$VENV_DIR/bin/activate"  # Включаем venv

echo "4. Устанавливаем зависимости..."
pip install --upgrade pip         # Обновляем pip
pip install -r requirements.txt   # Ставим необходимые пакеты

echo "5. Применяем миграции базы данных..."
python manage.py migrate --noinput  # Обновляем структуру БД

echo "6. Собираем статику..."
python manage.py collectstatic --noinput  # Копируем статические файлы в STATIC_ROOT

echo "7. Перезапускаем Gunicorn..."
sudo systemctl restart $SERVICE_NAME      # Перезапускаем службу

echo "Статус службы: $(sudo systemctl is-active $SERVICE_NAME)"  # Проверяем статус

echo "--- ОБНОВЛЕНИЕ ЗАВЕРШЕНО ---"
