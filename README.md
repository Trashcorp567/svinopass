# Svinopass

**svinopass.ru** — витрина микро-услуг: ввёл данные → оплатил → получил результат на экран и email. Без регистрации и личного кабинета.

Прод: https://svinopass.ru  
Репозиторий: https://github.com/Trashcorp567/svinopass

---

## Продукты

| Раздел | Что продаём | Тарифы |
|--------|-------------|--------|
| **/** | Криптостойкие пароли (CSPRNG) | Свиномат 99₽ · Бекон Pro 499₽ · Легенда 1999₽ |
| **/check** | Бесплатная проверка пароля (клиентская) | — |
| **/watch** | Мониторинг email в утечках | Свиной сторож 199₽/мес |
| **/names** | Ники, псевдонимы, био для соцсетей | Клички 99₽ · Псевдонимы 149₽ · Соцпак 249₽ |
| **/sell** | Описание товара по фото для маркетплейсов | Ozon / WB / Avito 149₽ · Полный пакет 349₽ |
| **/qr** | QR со ссылкой на **картинку** (30 дней) | QR-картинка 99₽ |

Дополнительно: **Запасной хлев** 149₽ — 10 backup-кодов 2FA.

### Общий платёжный flow

```
Выбор тарифа + email (+ опции)
    → POST /api/checkout → ЮKassa
    → webhook payment.succeeded → fulfill
    → Redis (one-time) + письмо
    → страница success: результат один раз
```

Секреты (пароли, ники, коды) **не пишем в Postgres** — только метаданные заказа.

После оплаты пароля на экране success показывается **QR-код** с тем же паролем: можно отсканировать камерой и сохранить в менеджер паролей или заметки (рядом с кнопкой «Скопировать»).

---

## Roadmap

### `/sell` — карточка маркетплейса по фото (реализовано)

```
Фото товара + опционально: название, категория, подсказки
        ↓
Vision (Yandex GPT multimodal) — что на фото
        ↓
Текстовая модель — 5 заголовков + SEO-описание под лимиты площадки
        ↓
Экран + email (checkout → fulfill)
```

Фото хранится в Redis до 30 минут только для оплаты и генерации, затем удаляется.

### Не в планах

- Управление Telegram-ботами и автопостинг по ссылке на паблик (отдельный SaaS, см. ContentPilot — не интегрируем).
- QR с **видео и аудио** — не делаем (только картинки на `/qr`).

Детальный бэклог v2: `docs/V2_ROADMAP.md`.

---

## Стек

| Слой | Технологии |
|------|------------|
| Backend | FastAPI, PostgreSQL, Redis, YooKassa |
| Frontend | React, Vite, TypeScript |
| AI | Yandex GPT (ники, скоро — vision для /sell) |
| Email | Yandex Postbox (HTTPS) на проде |
| Infra | Docker Compose, Caddy + Let's Encrypt |

---

## Локальный запуск

```powershell
copy .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000  
- API: http://localhost:3000/api/ (прокси nginx)  
- `YOOKASSA_MOCK=true` — мгновенная «оплата» без ЮKassa

### Без Docker (разработка)

```powershell
docker compose up postgres redis -d

cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000

cd ..\frontend
npm install
npm run dev
```

Vite: http://localhost:5173

### Миграции БД (при обновлении)

```powershell
docker compose exec -T postgres psql -U svinopass -d svinopass -f - < scripts/migrate-v4-creative.sql
```

Скрипты: `scripts/migrate-v*.sql` — идемпотентные (`IF NOT EXISTS`).

---

## Переменные окружения

См. `.env.example`:

| Группа | Ключи |
|--------|-------|
| Core | `DATABASE_URL`, `REDIS_URL`, `ENV`, `CORS_ORIGINS` |
| ЮKassa | `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, `YOOKASSA_RETURN_URL`, `YOOKASSA_MOCK` |
| Почта | `EMAIL_PROVIDER`, `SMTP_*` или `YANDEX_POSTBOX_*` |
| Утечки | `BREACH_PROVIDER`, `LEAKCHECK_API_KEY` |
| AI | `YANDEX_GPT_API_KEY`, `YANDEX_GPT_FOLDER_ID`, `CREATIVE_AI_ENABLED` |

`.env` в git не коммитится.

---

## ЮKassa

| Режим | Webhook |
|-------|---------|
| Локально + mock | не нужен |
| Тестовый магазин | ngrok → `/api/webhooks/yookassa` |
| **Прод** | `https://svinopass.ru/api/webhooks/yookassa` |

Return URL на проде: `https://svinopass.ru/payment/success` (и отдельные success для `/watch`, `/names`).

---

## Продакшен (svinopass.ru)

Сервер: VPS `168.222.143.232`, код в `/opt/svinopass`.

```bash
cd /opt/svinopass
git pull
# при необходимости: cat scripts/migrate-v4-creative.sql | docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T postgres psql -U svinopass -d svinopass
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

DNS reg.ru: `A` `@` и `www` → IP VPS. Caddy сам выпускает SSL.

---

## Тесты

```powershell
cd backend
.\.venv\Scripts\pytest -v

cd frontend
npm run build
npm run test:e2e
```

---

## SEO

`robots.txt`, `sitemap.xml`, meta/OG на страницах, JSON-LD. Верификация: Google Search Console, Яндекс Вебмастер.

---

## Связанные проекты

**ContentPilot** (`Work_Projects/contentpilot`) — подписочный контент-план + автопостинг в Telegram. С Svinopass **не сливаем**: другая модель (SaaS vs разовые покупки). Идеи маркетплейс-контента идут в Svinopass `/sell`.
