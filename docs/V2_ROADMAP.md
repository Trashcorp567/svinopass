# Svinopass v2 — roadmap для Cursor AI

> Подключай в чате: `@docs/V2_ROADMAP.md` (+ `@docs/CONTEXT.md` для базовой архитектуры)
>
> **Цель:** расширять продукт локально, **не трогая прод** (`svinopass.ru`, `/opt/svinopass`, боевые ключи ЮKassa).
> Деплой v2 — только после явного запроса пользователя.

---

## Как работать с этим документом

1. Пользователь говорит: «Сделай фичу X из V2» или «Возьми следующий блок из roadmap».
2. AI читает `@docs/CONTEXT.md` + этот файл.
3. Реализация **только в dev-ветке / локально**. `YOOKASSA_MOCK=true` для новых фич, пока не сказано иное.
4. Каждый блок — **1 сессия (1–4 часа)**. Не смешивать блоки в одном PR без запроса.
5. После блока: `pytest`, `npm run build`, краткий чеклист из раздела «Готово когда».

### Жёсткие ограничения (не ломать)

| Правило | Почему |
|---------|--------|
| Пароль **не пишем в Postgres** | Ядро безопасности v4 |
| Платный flow: checkout → webhook → fulfill → Redis one-time | Уже в проде |
| Не менять URL webhook и prod `.env` без запроса | `https://svinopass.ru/api/webhooks/yookassa` |
| Новые бесплатные фичи — **без хранения** введённого пароля на сервере | Trust + compliance |
| Мем только в UI-копирайте; security-логика — серьёзная | Бренд |
| Минимальный diff, без over-engineering | См. user rules |

### Тон бренда (копирайт)

- Заголовки: игра слов («Хрюк-чек», «Свинорепорт», «Паспорт кабана»).
- Подзаголовки и метрики: сухие факты (биты энтропии, NIST, утечки, политика).
- Никаких обещаний «невзламываемости». Формулировка: «криптографически стойкий», «CSPRNG», «не храним».

---

## Приоритет (что делать первым)

| # | Блок | Ценность | Сложность | Часы |
|---|------|----------|-----------|------|
| 1 | [B1 — Password Health Check](#b1--password-health-check-бесплатно) | Виральность, SEO, доверие | Низкая | 2–3 |
| 2 | [B2 — Пресеты «под задачу»](#b2--пресеты-под-задачу) | Конверсия в оплату | Низкая | 2–3 |
| 3 | [B3 — Passphrase-режим](#b3--passphrase-режим) | Новый use-case | Средняя | 3–4 |
| 4 | [B4 — Локальная генерация в браузере](#b4--локальная-генерация-в-браузере) | Trust, PR | Средняя | 3–4 |
| 5 | [B5 — Backup codes](#b5--backup-codes-новый-тариф) | Монетизация | Средняя | 3–4 |
| 6 | [B6 — Свинорепорт PDF](#b6--свинорепорт-pdf) | Upsell | Высокая | 4–6 |

---

## B1 — Password Health Check (бесплатно)

**Идея:** `/check` — пользователь вводит пароль, получает оценку. Пароль **не уходит на сервер** (только client-side) ИЛИ уходит как SHA-1 prefix для HIBP k-anonymity (стандарт Have I Been Pwned).

**Рекомендация:** гибрид — анализ силы локально, утечки через k-anonymity API с клиента (`api.pwnedpasswords.com`).

### UI

- Страница: `frontend/src/pages/CheckPage.tsx`
- Роут в `App.tsx`: `case "/check":`
- Ссылка в `SiteHeader` / `SiteFooter`: «Проверить пароль»
- Поле ввода `type="password"`, кнопка «Проверить хрюк-чеком»
- Результат:
  - Оценка: Слабый / Норм / Крепкий / Легенда хлева
  - Entropy (биты) — та же формула, что в `password.py` (портировать в TS)
  - Длина, классы символов, типичные паттерны (123, qwerty, password, год)
  - Утечки: «Найден в N утечках» / «В публичных утечках не встречался»
  - CTA: «Сгенерировать нормальный →» скролл на `/#pricing`

### Логика (frontend)

Новый файл: `frontend/src/lib/passwordAnalysis.ts`

```ts
export type HealthResult = {
  score: "weak" | "fair" | "strong" | "legend";
  entropyBits: number;
  length: number;
  hasLower: boolean;
  hasUpper: boolean;
  hasDigit: boolean;
  hasSymbol: boolean;
  warnings: string[];  // человекочитаемые, RU
  breachCount: number | null;  // null = проверка не выполнена
};
```

**HIBP k-anonymity (клиент):**
1. SHA-1 пароля (Web Crypto `subtle.digest`)
2. Отправить первые 5 hex символов на `https://api.pwnedpasswords.com/range/{prefix}`
3. Найти полный суффикс в ответе
4. Пароль и полный хеш **нигде не логировать**

### Backend

**Не обязателен** для B1. Если нужен прокси (CORS): `GET /api/tools/hibp-range/{prefix}` — только prefix, rate limit 30/min.

### Готово когда

- [x] `/check` открывается, пароль не появляется в Network tab на наш API
- [x] Оценка и warnings на русском
- [x] HIBP работает или graceful fallback «проверка утечек недоступна»
- [x] CTA ведёт на покупку
- [x] `npm run build` OK

---

## B2 — Пресеты «под задачу»

**Идея:** перед выбором тарифа — карточки сценариев. Пресет **не меняет цену**, только подсвечивает рекомендуемый тариф и показывает policy.

### Пресеты

| ID | Название (мем) | Рекомендуемый tier | Policy hint |
|----|----------------|-------------------|-------------|
| `bank` | Для банка | bacon | 24+, спецсимволы, без ambiguous |
| `social` | Для соцсетей | svinomat | 20, буквы+цифры |
| `wifi` | Для Wi‑Fi гостей | svinomat | 16–20, легко продиктовать → passphrase в B3 |
| `corp` | Для корпоративки | legend | 32, макс. энтропия |

### UI

- `frontend/src/components/UseCasePicker.tsx` — над `Pricing`
- При клике: `setSelectedTier(preset.recommendedTier)`, скролл к checkout
- Бейдж на карточке тарифа: «Рекомендуем для банка»

### Backend

Опционально: расширить `GET /api/tiers` полем `recommended_for: string[]` в `payment.py` / `TierInfo` schema. Или держать пресеты только на фронте (быстрее).

### Готово когда

- [x] 4 пресета на главной
- [x] Клик выбирает тариф
- [x] Существующий checkout не сломан
- [ ] Тесты API зелёные (не запускались — API offline)

---

## B3 — Passphrase-режим

**Идея:** альтернатива random string — 4–6 слов из wordlist + цифра + спецсимвол. Удобно диктовать, высокая энтропия.

### Wordlist

- Файл: `backend/app/data/wordlist_ru.txt` (~2048 коротких слов, 4–8 букв, без омонимов-матов по возможности)
- Или английский EFF wordlist (проще, 7776 слов) — **решение за продуктом**, по умолчанию EFF short list

### Генерация

`backend/app/services/passphrase.py`:

```python
def generate_passphrase(word_count: int = 4, separator: str = "-") -> str:
    # secrets.choice из wordlist
    # + обязательная цифра и спецсимвол в хвосте
```

### Интеграция в тарифы

В `fulfillment.py` — если в metadata заказа `mode=passphrase` (опционально) или отдельный tier `bacon-pass` (позже).

**MVP:** toggle на checkout «Слова вместо абракадабры» → передавать в `POST /api/checkout` поле `mode: "passphrase" | "random"` (default random).

Схема `CheckoutRequest`: добавить `mode: Literal["random", "passphrase"] = "random"`.

`fulfillment.py`: ветка по mode.

### UI

- Чекбокс в `Checkout.tsx`
- Подсказка: «4 слова + цифра + символ ≈ N бит энтропии»

### Готово когда

- [x] Passphrase генерируется CSPRNG
- [x] Email и Redis flow тот же
- [x] Unit-тест `test_passphrase.py`
- [x] Random mode по умолчанию — поведение как сейчас
- [ ] `test_api.py` — нужен перезапуск backend с `YOOKASSA_MOCK=true`

---

## B4 — Локальная генерация в браузере

**Идея:** `/local` — демо-генератор без оплаты. Web Crypto API. «Свинка не видит ваш пароль».

### UI

- `frontend/src/pages/LocalGeneratorPage.tsx`
- Слайдеры: длина 12–32, вкл/выкл спецсимволы, ambiguous
- Кнопка «Сгенерировать» → показ + copy
- Дисклеймер: «Бесплатно и локально. Для гарантии доставки на email и чека — платный тариф»

### Логика

`frontend/src/lib/generatePassword.ts` — порт логики из `password.py` (те же alphabet rules по tier-like presets).

**Никакого API.** Полностью offline-capable.

### Готово когда

- [x] Генерация без сетевых запросов
- [x] Copy to clipboard
- [x] CTA на платные тарифы
- [x] `npm run build` OK (wordlist не подключался)

---

## B5 — Backup codes (новый тариф)

**Идея:** платный набор одноразовых recovery codes (8–10 штук, 10 hex chars), как у 2FA backup.

### Тариф

В `payment.py` → `TIERS`:

```python
"backup": {
    "id": "backup",
    "name": "Запасной хлев",
    "price": 149,
    "price_label": "149₽",
    "description": "10 одноразовых кодов восстановления",
    "length": 10,  # не используется для пароля
    "features": [...],
    "product_type": "backup_codes",  # NEW
}
```

### Генерация

`backend/app/services/backup_codes.py`:

```python
def generate_backup_codes(count: int = 10, length: int = 10) -> list[str]:
    # secrets.token_hex(length // 2) или custom alphabet
```

`fulfillment.py`: если `tier.get("product_type") == "backup_codes"` → генерировать список, email как нумерованный список, Redis payload `codes: string[]`.

### Frontend

- `PasswordResult.tsx` — ветка для backup codes (таблица, не один пароль)
- Pricing card для нового tier

### Email

Шаблон в `email.py`: «Ваши коды восстановления» + предупреждение хранить офлайн.

### Готово когда

- [x] Новый tier в `/api/tiers`
- [x] Оплата mock → 10 кодов на экране и в письме
- [x] One-time show через Redis
- [x] Unit-тест `test_backup_codes.py` + fulfill test (нужен boto3 в venv)

---

## B6 — Свинорепорт PDF

**Идея:** после покупки legend — опциональная кнопка «Скачать свинорепорт» (PDF с метриками, без повторного показа пароля).

### Содержимое PDF

- Дата, order_id (короткий), tier
- Entropy bits, длина, policy
- Чеклист: сменить на других сервисах, не reuse, менеджер паролей
- **Пароль в PDF не включать** (уже показан / в email)

### Backend

- `weasyprint` или `reportlab` в requirements-dev / optional
- `GET /api/orders/{id}/report` — только если `paid` + `fulfilled`, отдаёт `application/pdf`, rate limit

### Готово когда

- [x] PDF генерируется для legend tier
- [x] Без пароля внутри
- [x] 404 для неоплаченных / не-legend

---

## Общие технические заметки

### Новые роуты (сводка)

| Метод | Путь | Блок |
|-------|------|------|
| — | `/check` | B1 (frontend only) |
| — | `/local` | B4 (frontend only) |
| POST | `/api/checkout` + `mode` | B3 |
| GET | `/api/tools/hibp-range/{prefix}` | B1 optional |
| GET | `/api/orders/{id}/report` | B6 |

### Файлы, которые чаще всего трогаем

```
backend/app/api/routes.py
backend/app/api/schemas.py
backend/app/services/payment.py
backend/app/services/fulfillment.py
backend/app/services/password.py
frontend/src/App.tsx
frontend/src/api/client.ts
frontend/src/components/Pricing.tsx
frontend/src/components/Checkout.tsx
frontend/src/pages/PaymentSuccess.tsx
frontend/src/components/PasswordResult.tsx
```

### Тесты (добавлять по блокам)

```
backend/tests/test_password_analysis.py   # B1 если backend
backend/tests/test_passphrase.py          # B3
backend/tests/test_backup_codes.py        # B5
frontend/e2e/check.spec.ts                # B1
```

### Dev-запуск перед тестами

```powershell
docker compose up postgres redis -d
cd backend && .\.venv\Scripts\uvicorn app.main:app --port 8000
cd frontend && npm run dev
# .env: YOOKASSA_MOCK=true
```

---

## SEO-страницы (быстрые победы, 30 мин каждая)

| URL | Title | Зачем |
|-----|-------|-------|
| `/check` | Проверка надёжности пароля | Трафик |
| `/local` | Генератор паролей онлайн | Трафик |
| `/passphrase` | Генератор passphrase | Long-tail |

Добавить в `frontend/src/config/seo.ts` и `public/sitemap.xml`.

---

## Что НЕ делать в v2 (пока)

- Полноценный личный кабинет с auth
- Хранение истории паролей
- Подписки / recurring billing
- Мобильное приложение
- Прямой деплой на прод без ревью

---

## Шаблон промпта для пользователя

```
@docs/CONTEXT.md @docs/V2_ROADMAP.md
Сделай блок B1 (Password Health Check).
Не трогай прод. YOOKASSA_MOCK=true.
После — pytest и npm run build.
```

---

## Changelog (заполняет AI после блока)

| Дата | Блок | Статус | Примечание |
|------|------|--------|------------|
| 2026-07-08 | B1 | done | `/check`, `passwordAnalysis.ts`, HIBP k-anonymity |
| 2026-07-08 | B2 | done | UseCasePicker, бейдж на тарифе |
| 2026-07-08 | B3 | done | `mode=passphrase`, EFF wordlist, миграция SQL |
| 2026-07-08 | B4 | done | `/local`, `generatePassword.ts`, Web Crypto |
| 2026-07-08 | B5 | done | тариф «Запасной хлев», backup codes |
| 2026-07-08 | B6 | done | Свинорепорт PDF, GET /api/orders/{id}/report |
