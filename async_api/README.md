# Async Items API

FastAPI Backend-проект для управління items і обробки паралельних запитів з використанням Async + Redis

**Стек:** Python 3.12 · FastAPI · Sqlite+Aiosqlite · SQLAlchemy (async) · Docker

## Швидкий старт

```bash
git clone <repo>
cd async_api

docker run -d -p 6379:6379 redis:alpine

uvicorn main:app --reload
```


## Endpoints

| Назва | Метод | Навіщо |
|------|-----|--------|
| `/items` | POST | Створити item|
| `/items` | GET | Список всіх items |
| `/items/{id}` | GET | Отримати item по ID |
| `/items/{id}` | DELETE | Видалити item|
| `/health` | GET | Статус сервісу та Redis|


## Особливості
- Async SQLAlchemy + aiosqlite для неблокуючих запитів до БД
- Redis кешування з автоматичною інвалідацією
- Rate limiting (5 req/хв per IP)