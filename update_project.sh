#!/bin/bash
set -e

# ===============================
# Настройки проекта (дефолтные значения)
# ===============================
PROJECT_DIR="/root/Projects/makrei_online"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="makrei_online.service"
GIT_BRANCH="main"  # Дефолтная ветка, если аргумент не передан

# Обработка аргументов
if [ $# -gt 0 ]; then
    GIT_BRANCH="$1"
    echo "Используется ветка из аргумента: $GIT_BRANCH"
else
    echo "Используется дефолтная ветка: $GIT_BRANCH"
fi

echo "--- НАЧАЛО ОБНОВЛЕНИЯ ---"

# Переходим в директорию проекта
cd "$PROJECT_DIR"

# ===============================
# Получение последних изменений
# ===============================
echo "1. Получаем последние изменения из репозитория (ветка $GIT_BRANCH)..."
git fetch origin

# Проверяем существование удалённой ветки
if ! git show-ref --verify --quiet "refs/remotes/origin/$GIT_BRANCH"; then
    echo "Ошибка: ветка $GIT_BRANCH не найдена в удалённом репозитории"
    exit 1
fi

# Переключаемся на нужную ветку (создаём при необходимости)
if git rev-parse --verify "$GIT_BRANCH" >/dev/null 2>&1; then
    # Локальная ветка существует — переключаемся
    echo "Переключаемся на локальную ветку $GIT_BRANCH..."
    git checkout "$GIT_BRANCH"
else
    # Локальной ветки нет — создаём и привязываем к удалённой
    echo "Создаём локальную ветку $GIT_BRANCH, привязанную к origin/$GIT_BRANCH..."
    git checkout -b "$GIT_BRANCH" "origin/$GIT_BRANCH"
fi

# Синхронизируем с удалённой веткой
echo "Синхронизируем ветку с origin/$GIT_BRANCH..."
git reset --hard "origin/$GIT_BRANCH"
git clean -fd

# ===============================
# Виртуальное окружение
# ===============================
echo "2. Проверяем виртуальное окружение..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Создаём виртуальное окружение..."
    python3 -m venv "$VENV_DIR"
fi

echo "3. Активируем виртуальное окружение..."
source "$VENV_DIR/bin/activate"

# ===============================
# Установка зависимостей
# ===============================
echo "4. Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# ===============================
# Миграции базы данных
# ===============================
echo "5. Применяем миграции базы данных..."
python manage.py migrate --noinput

# ===============================
# Установка DEBUG = False
# ===============================
echo "6. Устанавливаем DEBUG = False..."
# Заменяем любую строку с DEBUG на DEBUG = False (сохраняем комментарий если есть)
sed -i 's/^DEBUG = .*/DEBUG = False/' "$PROJECT_DIR/core/settings.py"
sed -i 's/^DEBUG=.*/DEBUG = False/' "$PROJECT_DIR/core/settings.py"
echo "DEBUG установлен в False"

# ===============================
# Сборка статики
# ===============================
echo "7. Собираем статику..."
python manage.py collectstatic --noinput

# ===============================
# Перезапуск Gunicorn
# ===============================
echo "8. Перезапускаем Gunicorn..."
sudo systemctl restart "$SERVICE_NAME"
echo "Статус службы: $(sudo systemctl is-active "$SERVICE_NAME")"

# Дополнительная проверка текущей ветки
echo "Текущая ветка после обновления: $(git rev-parse --abbrev-ref HEAD)"

echo "--- ОБНОВЛЕНИЕ ЗАВЕРШЕНО ---"
