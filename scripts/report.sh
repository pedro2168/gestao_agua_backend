#!/bin/bash

# ---------------------------------------
# Extrai relatório de análises de água
# ---------------------------------------

echo "🔎 Gerando relatório..."

docker compose exec web \
python manage.py shell -c \
"from core.utils.report import generate_report; generate_report()"

echo "✅ Relatório finalizado!"
echo "📁 Veja em: core/utils/reports/"
