#!/usr/bin/env bash
set -e

host="$POSTGRES_HOST"
port="${POSTGRES_PORT:-5432}"

echo "Aguardando Postgres em $host:$port..."

until nc -z "$host" "$port"; do
  echo "Postgres não disponível ainda - aguardando..."
  sleep 1
done

echo "Postgres está disponível"
