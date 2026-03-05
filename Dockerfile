FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

# Если не нужен dos2unix после этого, можно удалить его:
RUN apt-get remove -y dos2unix && apt-get autoremove -y

ENTRYPOINT ["/app/entrypoint.sh"]