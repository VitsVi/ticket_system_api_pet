FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh
# # CMD запускается через docker-compose
# RUN chmod +x /app/entrypoint.sh

# # Запуск по умолчанию через entrypoint
# ENTRYPOINT ["entrypoint.sh"]