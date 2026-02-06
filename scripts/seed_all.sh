#!/bin/bash
set -e

SERVICE="web"

echo "🌱 Limpando e gerando dados fake..."

docker compose exec $SERVICE python manage.py clinics_seed --reset
docker compose exec $SERVICE python manage.py seed_parameters --reset
docker compose exec $SERVICE python manage.py seed_analyses --reset

echo "📄 Gerando relatório..."
docker compose exec $SERVICE python manage.py shell -c \
"from core.utils.report import generate_report; generate_report()"

echo "📊 Gerando gráfico..."
docker compose exec $SERVICE python manage.py shell -c \
"from core.utils.monthly_chart import generate_monthly_chart; generate_monthly_chart()"

echo "✅ Seed completo finalizado!"
echo "📁 Veja core/utils/reports/"
