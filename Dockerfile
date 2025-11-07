FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Dependências do sistema para psycopg2 e build
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do projeto
COPY . .

# Coleta arquivos estáticos (agora o manage.py existe!)
RUN python manage.py collectstatic --noinput

# Expõe a porta padrão do Django
EXPOSE 8000

# Comando de inicialização
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
