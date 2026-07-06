# Svinopass — контекст для Cursor

> Подключай в чате: `@docs/CONTEXT.md`

## Проект

**Путь:** `C:\Users\Trash\Work_Projects\svinopass`  
**Продукт:** платный генератор криптографически стойких паролей (мем-оболочка Svinopass).

## Архитектура (v4)

```
Тариф + email
  -> POST /api/checkout
  -> ЮKassa (или YOOKASSA_MOCK=true)
  -> webhook payment.succeeded
  -> fulfill: generate + email + Redis (одноразовый показ)
  -> return /payment/success?order_id=
  -> GET /api/orders/{id}/result (один раз, потом 410)
```

**Безопасность:** пароль **не хранится в Postgres**. В БД — заказ и статус. Одноразовый показ на экран — **Redis** (TTL 15 мин, удаление после первого GET). Дублирование — **SMTP email**.

## Стек

| Слой | Технологии |
|------|------------|
| Backend | FastAPI, PostgreSQL, Redis, YooKassa SDK, slowapi |
| Frontend | React, Vite, TypeScript |
| Infra | Docker Compose: postgres, redis, backend, frontend (nginx :3000) |

## Ключевые файлы

| Файл | Назначение |
|------|------------|
| `backend/app/api/routes.py` | checkout, result, webhook |
| `backend/app/services/yookassa_client.py` | платежи + чек 54-ФЗ |
| `backend/app/services/fulfillment.py` | generate -> email -> Redis |
| `backend/app/services/ephemeral.py` | Redis one-time password |
| `backend/app/services/email.py` | SMTP (Yandex/Gmail) |
| `backend/app/config.py` | env, читает `../.env` и `.env` |
| `frontend/src/App.tsx` | логотип-ссылка, confirm при загрузке пароля |
| `frontend/src/pages/PaymentSuccess.tsx` | polling, русские ошибки, «На главную» |
| `.env` | секреты (gitignored) |
| `.env.example` | шаблон без паролей |

## Удалён legacy

Auth, Socket.IO, Generator, StatusFeed, useSocket, auth routes, session_repo.

## Env-переменные

```env
DATABASE_URL=postgresql://svinopass:svinopass@localhost:5432/svinopass
REDIS_URL=redis://localhost:6379/0
ENV=development
YOOKASSA_MOCK=true
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_RETURN_URL=http://localhost:5173/payment/success

# Yandex SMTP (рабочий ящик: supersvinopass@yandex.ru)
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_TLS=false
SMTP_USER=supersvinopass@yandex.ru
SMTP_PASSWORD=<пароль приложения из .env, не коммитить>
SMTP_FROM=supersvinopass@yandex.ru
```

Пароль приложения хранится только в локальном `.env`. В чат не писать.

## Запуск локально

```powershell
docker compose up postgres redis -d

cd backend
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000

cd ..\frontend
npm run dev
```

- Frontend: http://localhost:5173/
- API: http://127.0.0.1:8000/api/health

## ЮKassa

| Режим | Нужен домен? |
|-------|--------------|
| `YOOKASSA_MOCK=true` | Нет — мгновенная mock-оплата |
| Тестовый магазин | Нет для return_url (localhost OK) |
| Webhook | **Да — публичный HTTPS** (ngrok локально) |
| Боевые платежи | `https://svinopass.ru` |

Webhook prod: `https://svinopass.ru/api/webhooks/yookassa`  
События: `payment.succeeded`, `payment.canceled`

## Frontend UX

- Checkout -> редирект на ЮKassa (или mock return_url)
- `/payment/success?order_id=` — polling результата
- Логотип **Svinopass** и **Главная** — ссылки на `/`
- Пока пароль грузится — confirm перед уходом
- StrictMode fix: in-flight promise dedup + sessionStorage в PaymentSuccess

## Тесты (последний прогон)

- `pytest tests/test_api.py` — 9/9 passed
- `npx playwright test` — 5/5 passed
- `npm run build` — OK

## Известные проблемы (Windows)

**UTF-16 при правках через Cursor Write/StrReplace** — файлы ломаются (`null bytes`).  
Писать кириллицу через PowerShell:

```powershell
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("path", $content, $utf8)
```

Или: `python -c` decode utf-16 -> write utf-8.

## Тарифы

| ID | Название | Цена | Длина пароля |
|----|----------|------|--------------|
| svinomat | Свиномат | 99 RUB | 20 |
| bacon | Бекон | 499 RUB | 24 |
| legend | Легенда | 1999 RUB | 32 |

## Что сделано в сессиях

1. Поэтапный план ЮKassa (этапы 1–7) — реализован
2. Навигация: кликабельный логотип, confirm, «На главную» на ошибках
3. README + .env.example: Yandex SMTP, ЮKassa test vs prod
4. Yandex SMTP настроен и протестирован (письма уходят)
5. Playwright: clipboard permissions, reuseExistingServer: false

## Следующие шаги (prod)

- [ ] `YOOKASSA_MOCK=false` + тестовый/боевой магазин
- [ ] Webhook в ЛК ЮKassa
- [ ] Деплой на svinopass.ru + HTTPS
- [ ] `docker compose up --build` на сервере

## Полезные команды

```powershell
# Тесты
cd backend; .\.venv\Scripts\pytest tests/test_api.py -q
cd frontend; npm run test:e2e

# Остановить зависшие dev-процессы
netstat -ano | findstr ":8000 :5173"
```

## Документация

- `README.md` — полная инструкция
- `scripts/migrate-v3.sql` — миграция orders для существующей БД