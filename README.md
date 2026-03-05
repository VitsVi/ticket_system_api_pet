# Ticket System Management API (PET)

### Ссылка на скриншоты работы программы
https://disk.yandex.ru/d/176zCRHEtTsasg

## Описание
Проект реализует систему управления тикетами с операторами, клиентами и сообщениями.  
Поддерживает полный **CRUD** для всех сущностей и бизнес-логику по распределению тикетов между операторами.

Основные сущности:
- **Tickets** - тикеты с различными статусами
- **Operators** - операторы, которые обрабатывают тикеты
- **Clients** - клиенты, создающие тикеты
- **Messages** - сообщения внутри тикетов  

---

## Функциональные возможности

### CRUD для всех сущностей
- Создание, чтение, обновление, удаление
- Получение списка (для тикетов, клиентов и операторов)
- Получение одного объекта по `id`

### Бизнес-логика тикетов
- При создании тикет автоматически назначается свободному оператору:
  - Статус оператора - `online`
  - Наименьшее количество активных тикетов
- Если свободных операторов нет - тикет остаётся без оператора и получает статус `new`
- Переход тикета между статусами валидируется:
  - Допустимые переходы (пример):
    - `new` → `in_progress` / `waiting`
    - `in_progress` → `waiting` / `closed`
    - `waiting` → `in_progress` / `closed`
    - `closed` → запрещено возвращаться в любой активный статус
- При закрытии тикета оператору автоматически назначается следующий тикет из очереди (если есть)

### Фоновая задача
- Тикеты в статусе `waiting` дольше 24 часов автоматически переводятся в `closed`

### Кэширование (Redis)
- Кэшируется количество тикетов по статусам
- Кэш инвалидируется при изменении статуса тикета

---

## Эндпоинты API

### Tickets
- `GET /tickets` - список всех тикетов
- `GET /tickets/{ticket_id}` - получение тикета по ID
- `POST /tickets` - создание тикета
- `PATCH /tickets/{ticket_id}` - обновление тикета
- `DELETE /tickets/{ticket_id}` - удаление тикета

### Clients
- `GET /clients` - список клиентов
- `GET /clients/{client_id}` - получение клиента по ID
- `POST /clients` - создание клиента
- `PATCH /clients/{client_id}` - обновление клиента
- `DELETE /clients/{client_id}` - удаление клиента

### Operators
- `GET /operators` - список операторов
- `GET /operators/{operator_id}` - получение оператора по ID
- `POST /operators` - создание оператора
- `PATCH /operators/{operator_id}` - обновление оператора
- `DELETE /operators/{operator_id}` - удаление оператора

### Messages
- `POST /messages` - создание сообщения
- `PATCH /messages/{message_id}` - обновление сообщения
- `DELETE /messages/{message_id}` - удаление сообщения

---

## Технологии и зависимости

Проект реализован на Python с асинхронным веб-фреймворком и полной поддержкой CRUD для тикетов, клиентов, операторов и сообщений.  

### Основные технологии
- Python 3.11+
- aiohttp 3.8.4 - веб-фреймворк
- aiohttp-middlewares 2.3.0 - middleware для aiohttp
- aiohttp-swagger3 0.7.4 - документация API Swagger
- SQLAlchemy 2.0.29 - ORM
- asyncpg 0.29.0 - асинхронный драйвер PostgreSQL
- greenlet 3.0.3 - поддержка SQLAlchemy
- alembic 1.13.1 - миграции базы данных
- psycopg2-binary 2.9.9 - драйвер PostgreSQL
- redis 5.0.4 - кэширование
- Pydantic 2.6.4 + pydantic-settings 2.2.1 + pydantic[email] - валидация данных и схемы
- python-dotenv 1.0.1 - работа с `.env` файлами
- aiosignal 1.3.1 - сигналы для async библиотек
- structlog 24.1.0 - структурированное логирование
- isort - автоматическая сортировка импортов

### Асинхронные возможности
- AsyncIO - асинхронная обработка
- Background tasks - фоновая обработка тикетов (например, перевод `waiting` → `closed` через 24 часа)

---

### Новые ревизии и применение миграций алембика
Происходят в entrypoint.sh (настроено в docker compose). Создается файл ревизии, если на текущий момент нет.


## Запуск проекта в Docker

1. Создать файл `.env` с параметрами базы данных и Redis:
(Текущий файл .env в репозитории уже настроен под запуск проекта локально. .env Удален из .gitignore)
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ticket_db
REDIS_URL=redis://localhost:6379/0

DB_USER=postgres
DB_PASSWORD=password
DB_NAME=ticket_db
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

APP_HOST=0.0.0.0
APP_PORT=8000
```
---

2. В корневой папке проекта запустить docker-compose.yml:
```bash
docker compose up --build -d
```
