#!/bin/bash
set -e

SERVICE="web"

echo "🧠 Rodando scheduler MILP..."

docker compose exec $SERVICE python manage.py shell -c \
"from core.utils.scheduler import run_scheduler; print(run_scheduler())"

echo "✅ Scheduling concluído!"
