#!/bin/bash
set -e

SERVICE="web"

echo "🔄 Criando migrations..."
docker compose exec $SERVICE python manage.py makemigrations

echo "🚀 Aplicando migrations..."
docker compose exec $SERVICE python manage.py migrate

echo "✅ Migrations concluídas!"
