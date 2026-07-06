# Deploy ADMETox.AI

## Option A: Docker Compose (рекомендовано)

### Требования

- Docker Engine 24+
- Docker Compose v2
- 2+ GB RAM
- Домен (для HTTPS)

### Быстрый старт

```bash
git clone https://github.com/bradist/ADME-Tox-Predictor.git
cd ADME-Tox-Predictor

# 1. Настроить .env
cp .env.example .env
#   - Сгенерировать ADMETOX_JWT_SECRET: openssl rand -hex 32
#   - Указать DOMAIN и SSL_EMAIL для HTTPS

# 2. Запустить
docker compose up -d --build

# 3. Проверить
curl http://localhost/api/health
curl -X POST http://localhost/api/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CCO"}'
```

### HTTPS (Let's Encrypt)

```bash
# Получить сертификаты
docker compose --profile setup run certbot

# Перезапустить nginx
docker compose restart nginx

# Настроить автообновление (crontab -e):
#   0 3 1 */2 * cd /opt/admetox && docker compose run --rm certbot renew && docker compose restart nginx
```

### Обновление

```bash
git pull
docker compose up -d --build
```

### Логи

```bash
docker compose logs -f api
docker compose logs -f ui
docker compose logs -f nginx
```

---

## Option B: Native Ubuntu (без Docker)

### 1. Requirements

- Ubuntu 22.04+
- Python 3.12
- nginx
- Let's Encrypt / certbot
- 2+ GB RAM

### 2. Установка

```bash
adduser admetox
usermod -aG sudo admetox
su - admetox

git clone https://github.com/bradist/ADME-Tox-Predictor.git /opt/admetox
cd /opt/admetox

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export ADMETOX_JWT_SECRET=$(openssl rand -hex 32)
```

### 3. Systemd

```bash
sudo cp deploy/systemd/admetox-api.service /etc/systemd/system/
sudo cp deploy/systemd/admetox-ui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable admetox-api admetox-ui
sudo systemctl start admetox-api admetox-ui
```

### 4. Nginx + SSL

```bash
# Адаптировать server_name в deploy/nginx.conf под свой домен
sudo cp deploy/nginx.conf /etc/nginx/sites-available/admetox
sudo ln -s /etc/nginx/sites-available/admetox /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload

# SSL (Let's Encrypt)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 5. Обновление

```bash
cd /opt/admetox
make deploy
```

---

## Структура портов (Docker)

| Сервис | Внутренний порт | Внешний порт | URL |
|--------|----------------|--------------|-----|
| nginx | 80/443 | 80/443 | `http://localhost/` |
| FastAPI API | 8000 | — | `/api/` через nginx |
| Streamlit UI | 8501 | — | `/ui/` через nginx |

## Переменные окружения

| Переменная | По умолчанию | Обязательная | Описание |
|------------|-------------|-------------|----------|
| `ADMETOX_JWT_SECRET` | — | ✅ | Секрет для JWT (сгенерировать `openssl rand -hex 32`) |
| `ADMETOX_API_KEYS` | — | ❌ | API-ключи через запятую |
| `ADMETOX_CORS_ORIGINS` | `https://admetox.ai` | ❌ | Разрешённые CORS-источники |
| `DOMAIN` | — | для SSL | Домен для Let's Encrypt |
| `SSL_EMAIL` | — | для SSL | Email для Let's Encrypt |
