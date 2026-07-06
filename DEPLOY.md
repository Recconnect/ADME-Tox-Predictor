# Deploy ADMETox.AI

## Option A: Docker Compose (быстрый старт)

```bash
git clone https://github.com/bradist/ADME-Tox-Predictor.git
cd ADME-Tox-Predictor

# Обучить модели (нужно ~1-2 ГБ ОЗУ)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_train.py

# Запустить оба сервиса
docker compose up -d

# Streamlit UI: http://localhost:8501
# FastAPI docs:  http://localhost:8000/docs
```

## Option B: Native Ubuntu (продакшн)

### 1. Requirements

- Ubuntu 22.04+
- Python 3.14
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
python run_train.py
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
sudo cp deploy/nginx.conf /etc/nginx/sites-available/admetox
sudo ln -s /etc/nginx/sites-available/admetox /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload

# SSL (Let's Encrypt)
sudo certbot --nginx -d admetox.ai -d www.admetox.ai
```

### 5. Landing страница

```bash
# GitHub Pages автоматически деплоит landing/ при пуше в master
# https://bradist.github.io/ADME-Tox-Predictor/
```

### 6. Обновление

```bash
cd /opt/admetox
make deploy
# или пошагово:
# git pull
# pip install -r requirements.txt
# sudo systemctl restart admetox-api admetox-ui
```

## Структура портов

| Сервис | Порт | URL |
|--------|------|-----|
| Streamlit UI | 8501 | `/ui/` (через nginx) |
| FastAPI API | 8000 | `/api/` (через nginx) |
| Landing page | 80/443 | `/` (статический nginx) |

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `API_PORT` | 8000 | Порт FastAPI |
| `UI_PORT` | 8501 | Порт Streamlit |
| `DEBUG` | false | Режим отладки |
