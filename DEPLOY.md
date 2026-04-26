# Server Deploy

Bot hozir 2 ta alohida process bilan ishlaydi:

- `bot.py` — Telegram polling bot
- `web_app_api.py` — FastAPI mini app backend

## 1. Tayyorlash

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

```bash
cd /opt
sudo mkdir -p smmbot
sudo chown $USER:$USER smmbot
cd smmbot
```

Loyiha fayllarini shu papkaga joylang, keyin:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 2. `.env` tayyorlash

`.env.example` ni `.env` qilib nusxalang:

```bash
cp .env.example .env
```

Majburiy qiymatlar:

- `BOT_TOKEN`
- `ADMINS`
- `SMM_API_KEY`
- `SMS_API_KEY`
- `CARD_NUMBER`
- `CARD_HOLDER`
- `WEB_APP_ALLOWED_ORIGINS`

## 3. Lokal smoke test

```bash
source .venv/bin/activate
python -m compileall .
python -c "import bot; import web_app_api; print('imports ok')"
python deploy_check.py
```

## 4. Qo'lda ishga tushirish

Bot:

```bash
source .venv/bin/activate
python bot.py
```

Web API:

```bash
source .venv/bin/activate
uvicorn web_app_api:app --host 0.0.0.0 --port 8000
```

Healthcheck:

```bash
curl http://127.0.0.1:8000/healthz
```

## 5. systemd service

### `/etc/systemd/system/smmbot-bot.service`

```ini
[Unit]
Description=SMM Telegram Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/smmbot
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/smmbot/.venv/bin/python /opt/smmbot/bot.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/smmbot-web.service`

```ini
[Unit]
Description=SMM Bot FastAPI
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/smmbot
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/smmbot/.venv/bin/uvicorn web_app_api:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Yoqish:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now smmbot-bot
sudo systemctl enable --now smmbot-web
```

Loglar:

```bash
sudo journalctl -u smmbot-bot -f
sudo journalctl -u smmbot-web -f
```

## 6. Nginx reverse proxy

Mini App ishlatsa, `web_app_api` ni domen orqali oching. Masalan:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Keyin SSL qo'ying:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 7. Muhim eslatmalar

- SQLite fayl endi loyiha ichida absolute path bilan ishlaydi, shuning uchun systemd `cwd` tufayli boshqa joyga baza ochilib ketmaydi.
- SQLite connection `WAL` rejimida ishlaydi, bu `bot.py` va `web_app_api.py` bir paytning o'zida yozganda lock muammolarini kamaytiradi.
- FastAPI startup paytida baza avtomatik init qilinadi.
- `WEB_APP_ALLOWED_ORIGINS` ni albatta o'zingizning domeningizga qo'ying.
- Polling va FastAPI alohida service bo'lgani uchun ikkalasini ham yoqish kerak.
- FSM hozir `MemoryStorage` bilan ishlaydi. Shu sabab serverda faqat bitta bot process ishlating; bir nechta polling instance tavsiya etilmaydi.
- To'lovlar hozir webhook bilan to'liq avtomatik tasdiqlanmaydi. Foydalanuvchi so'rov yuboradi, admin esa haqiqiy tushumni ko'rib tasdiqlaydi.

## 8. Railway sozlamalari

Railway'da bu loyihani **2 ta alohida service** qilib qo'ying:

- `smmbot-bot` — Telegram polling uchun
- `smmbot-web` — FastAPI mini app uchun

### `smmbot-bot` service

- `Root Directory`: bo'sh qoldiring yoki repo root
- `Branch`: `main`
- `Builder`: `Railpack / Nixpacks`
- `Build Command`: bo'sh qoldiring
- `Start Command`: `python bot.py`
- `Healthcheck Path`: bo'sh qoldiring
- `Public Networking`: o'chirilgan bo'lsin
- `Restart Policy`: `ON FAILURE`
- `Serverless`: o'chirilgan bo'lsin
- `Replicas`: `1`

### `smmbot-web` service

- `Root Directory`: bo'sh qoldiring yoki repo root
- `Branch`: `main`
- `Builder`: `Railpack / Nixpacks`
- `Build Command`: bo'sh qoldiring
- `Start Command`: `uvicorn web_app_api:app --host 0.0.0.0 --port $PORT`
- `Healthcheck Path`: `/healthz`
- `Public Networking`: yoqilgan bo'lsin
- `Domain`: yarating
- `Restart Policy`: `ON FAILURE`
- `Serverless`: o'chirilgan bo'lsin
- `Replicas`: `1`

### Railway Variables

Har ikkala service'ga ham quyidagilarni kiriting:

- `BOT_TOKEN`
- `ADMINS`
- `SMM_API_KEY`
- `SMM_API_URL`
- `SMS_API_KEY`
- `SMS_API_URL`
- `CARD_NUMBER`
- `CARD_HOLDER`
- `DEFAULT_SMM_MARKUP_PERCENT`
- `DAILY_BONUS_DEFAULT`

Faqat `smmbot-web` service'da qo'shimcha:

- `WEB_APP_ALLOWED_ORIGINS=https://sizning-domainingiz.railway.app`

Mini App uchun custom domain ishlatsangiz, `WEB_APP_ALLOWED_ORIGINS` ga aynan o'sha domenni yozing.
