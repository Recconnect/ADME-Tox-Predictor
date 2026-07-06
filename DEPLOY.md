# Deploy ADMETox.AI

## Option A: Docker Compose (recommended)

### Requirements

- Docker Engine 24+
- Docker Compose v2
- 2+ GB RAM
- Domain (for HTTPS)

### Quick Start

```bash
git clone https://github.com/Recconnect/ADME-Tox-Predictor.git
cd ADME-Tox-Predictor

# 1. Setup .env
cp .env.example .env
#   - Generate ADMETOX_JWT_SECRET: openssl rand -hex 32
#   - Set DOMAIN and SSL_EMAIL for HTTPS

# 2. Build and run
docker compose up -d --build

# 3. Verify
curl http://localhost/api/health
curl -X POST http://localhost/api/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CCO"}'
```

### HTTPS (Let's Encrypt)

```bash
# Get certificates (one-time)
docker compose --profile setup run certbot

# Restart nginx to apply certificates
docker compose restart nginx

# Setup auto-renewal (crontab -e):
#   0 3 1 */2 * cd /opt/admetox && docker compose run --rm certbot renew && docker compose restart nginx
```

### Update

```bash
git pull
docker compose up -d --build
```

### Logs

```bash
docker compose logs -f api
docker compose logs -f ui
docker compose logs -f nginx
```

---

## Option B: Native Ubuntu (without Docker)

### 1. Requirements

- Ubuntu 22.04+
- Python 3.12
- nginx
- Let's Encrypt / certbot
- 2+ GB RAM

### 2. Installation

```bash
adduser admetox
usermod -aG sudo admetox
su - admetox

git clone https://github.com/Recconnect/ADME-Tox-Predictor.git /opt/admetox
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
# Adapt server_name in deploy/nginx.conf to your domain
sudo cp deploy/nginx.conf /etc/nginx/sites-available/admetox
sudo ln -s /etc/nginx/sites-available/admetox /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload

# SSL (Let's Encrypt)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 5. Update

```bash
cd /opt/admetox
make deploy
```

---

## Port Structure (Docker)

| Service | Internal Port | External Port | URL |
|---------|---------------|---------------|-----|
| nginx | 80/443 | 80/443 | `http://localhost/` |
| FastAPI API | 8000 | — | `/api/` via nginx |
| Streamlit UI | 8501 | — | `/ui/` via nginx |

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `ADMETOX_JWT_SECRET` | — | ✅ | JWT secret (generate with `openssl rand -hex 32`) |
| `ADMETOX_API_KEYS` | — | ❌ | Comma-separated API keys |
| `ADMETOX_CORS_ORIGINS` | `https://admetox.ai` | ❌ | Allowed CORS origins |
| `DOMAIN` | — | for SSL | Domain for Let's Encrypt |
| `SSL_EMAIL` | — | for SSL | Email for Let's Encrypt |
