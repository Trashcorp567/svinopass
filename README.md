# Svinopass

Paid secure password generator with YooKassa payments.

## Stack

- **Backend:** FastAPI, PostgreSQL, Redis, YooKassa SDK
- **Frontend:** React + Vite + TypeScript
- **Infra:** Docker Compose (postgres, redis, backend, frontend/nginx)

## Flow

1. User selects tier and enters email
2. `POST /api/checkout` creates order and YooKassa payment (receipt 54-FZ)
3. User pays on YooKassa page
4. Webhook `payment.succeeded` triggers password generation + email
5. User returns to `/payment/success?order_id=...` and sees password once (also in email)
6. Password is **not stored** in Postgres (one-time Redis cache for screen display)

## Quick start (local)

```powershell
copy .env.example .env
docker compose up postgres redis -d

cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000

cd ..\frontend
npm install
npm run dev
```

Open http://localhost:5173/

## Yandex SMTP (recommended)

Without `SMTP_HOST`, emails are **not sent** in development — only logged in the backend terminal:

```
DEV email (SMTP not configured): to=... password_len=20
```

Add to root `.env` (loaded from `backend/` automatically):

```env
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=you@yandex.ru
SMTP_PASSWORD=your-mailbox-password
SMTP_FROM=you@yandex.ru
```

**Yandex mailbox setup:**

1. Yandex Mail -> Settings -> Mail clients
2. Enable **Allow access via mail clients**
3. Use your mailbox password in `SMTP_PASSWORD` (or app password if 2FA is on)
4. `SMTP_FROM` must match `SMTP_USER`

Restart backend after changing `.env`.

## Gmail SMTP (alternative)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your@gmail.com
SMTP_PASSWORD=<16-char App Password>
SMTP_FROM=your@gmail.com
```

Requires Google 2FA + App Password.

## YooKassa setup

### Test vs production

| Scenario | Domain required? | Notes |
|----------|------------------|-------|
| `YOOKASSA_MOCK=true` (default dev) | No | Instant mock payment |
| Test shop (`test_` keys) | No for `return_url` | `http://localhost:5173/payment/success` |
| Webhook `payment.succeeded` | **Yes — public HTTPS** | Use ngrok locally |
| Live payments | Yes | `https://svinopass.ru` |

**Production deploy is not required to start.** Use a test shop + ngrok for webhooks.

### Test shop

```env
YOOKASSA_MOCK=false
YOOKASSA_SHOP_ID=<test shop id>
YOOKASSA_SECRET_KEY=<test secret>
YOOKASSA_RETURN_URL=http://localhost:5173/payment/success
```

Webhook in YooKassa cabinet: `https://<ngrok-host>/api/webhooks/yookassa`

See [YooKassa webhook docs](https://yookassa.ru/developers/using-api/webhooks).

### Production

- `YOOKASSA_MOCK=false` with live credentials
- `YOOKASSA_RETURN_URL=https://svinopass.ru/payment/success`
- Webhook: `https://svinopass.ru/api/webhooks/yookassa`
- SMTP + Redis configured
- `docker compose up --build`

## Environment variables

See `.env.example`: `DATABASE_URL`, `REDIS_URL`, `YOOKASSA_*`, `SMTP_*`, `CORS_ORIGINS`, `ENV`.

## Tests

```powershell
cd backend
.\.venv\Scripts\pytest -v

cd frontend
npm run test:e2e
```

## Docker production

```powershell
# Local full stack (frontend :3000, API proxied at /api/)
docker compose up --build

# Server: only ports 80/443 (Caddy + auto HTTPS), ENV=production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Frontend: http://localhost:3000 — API proxied at `/api/`.  
In Docker, `YOOKASSA_RETURN_URL` is overridden to `:3000` (local) or `https://svinopass.ru` (prod override).

### Deploy on svinopass.ru (reg.ru)

1. **VPS** (not shared hosting): Ubuntu 22.04+, 2 GB RAM, public IPv4. Domain can stay on reg.ru; VPS — reg.ru or any provider.
2. **DNS** in reg.ru → domain `svinopass.ru` → DNS records:
   - `A` `@` → VPS IP
   - `A` `www` → VPS IP (or `CNAME` `www` → `svinopass.ru`)
3. **Server**: install Docker, clone repo, copy `.env` with prod secrets (`YOOKASSA_MOCK=false`, SMTP, keys).
4. **Start**: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d`
5. **YooKassa** webhook: `https://svinopass.ru/api/webhooks/yookassa`
6. Open firewall: `22`, `80`, `443` only.

Caddy in prod compose issues Let's Encrypt certificates automatically once DNS points to the server.