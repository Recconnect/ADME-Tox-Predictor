# Session: ADMETox.AI — Pre-deployment audit, security fixes, Docker packaging, Outreach agents

## Источники данных
- Путь: `D:\AI\biotech\adme_proto`
- Ветка: `master`
- GitHub: https://github.com/Recconnect/ADME-Tox-Predictor
- Последние коммиты:
  - `8ab3a3d` — fix: resolve Streamlit session_state error for drug selection buttons
  - `ed56b3a` — refactor: move agents/ to separate client_engagement/ project
  - `6cdb5ca` — docs: update AGENTS.md with all 7 agents and new coordinator commands
  - `498c2a9` — feat: add 3 new outreach agents (feedback, conference, social media)
  - `99c63af` — feat: add outreach agents module for automated product promotion
  - `f93e500` — docker: production-ready compose with nginx + certbot + embedded models
  - `eaee7f4` — security: fix 14 issues from pre-deployment audit

## Что сделано

### 1. Замена терминологии (investor-ready)
- Исходные: Solubility → Water Solubility, Caco-2 → Gut Absorption, hERG → Cardiotoxicity, Ames → Mutagenicity, P-gp → Drug Resistance
- `src/i18n.py` — PROP_NAMES, translate_prop_name(), translate_class()
- `app.py` — group labels: "Absorption & Solubility", "Safety & Toxicity", "Metabolism & Transport", "Pharmacokinetics"
- PDF-отчёт — переведён на русский

### 2. Тестирование
- 69/69 тестов проходят (`pytest tests/ -v`)
- CSV upload edge cases: missing SMILES column, empty file, mixed valid/invalid, 100-molecule batch (3.1s)
- API: predict, batch, health, metrics, validate — все возвращают корректную структуру
- Performance: predict ~26ms (после прогрева), batch ~32ms/mol

### 3. Security audit — 14 фиксов

| # | Суть | Файл |
|---|---|---|
| C-1 | JWT secret — генерация случайного ключа через `secrets.token_hex(32)` | `src/auth.py` |
| C-2 | CORS — белый список из `ADMETOX_CORS_ORIGINS` | `api/main.py` |
| C-3 | `/admin/usage` — добавлена аутентификация | `api/main.py` |
| H-1 | Model integrity — SHA-256 верификация через `checksums.txt` | `src/models.py` |
| H-2 | XSS — `html.escape()` для SMILES перед `to_html(escape=False)` | `app.py` |
| H-3 | Password policy — min 6 → 8 символов | `src/auth.py` |
| H-4 | File permissions — `os.chmod(0o600)` на `usage.db` и `users.json` | `src/usage.py`, `src/auth.py` |
| H-5 | `/metrics` — добавлена аутентификация | `api/main.py` |
| M-1 | `reload=True` → управляется через `ADMETOX_DEV_RELOAD` | `api/main.py` |
| M-3 | Login rate limit: 20 → 5/min | `api/main.py` |
| M-5 | SMILES в ошибках truncated до 200 символов | `api/main.py` |
| M-6 | `max_length=10000` на SMILES поля | `api/schemas.py` |
| M-7 | CSV validation: UTF-8, null bytes, dimensions, size | `app.py` |
| — | Validation summary: `st.json()` → `st.metric()` cards | `app.py` |
| — | Batch placeholder: raw SMILES → drug names (i18n) | `src/i18n.py` |

### 4. Docker packaging

**Архитектура (3 контейнера + certbot):**

```
nginx (:80/:443) — TLS, landing, /api/ → FastAPI, /ui/ → Streamlit
  ├── api (:8000) — FastAPI REST API
  └── ui  (:8501) — Streamlit UI
certbot (profile: setup) — Let's Encrypt SSL
```

**Файлы:**
- `Dockerfile` — 3 стадии: `base` (python:3.12-slim + rdkit), `api`, `ui`
- `docker-compose.yml` — 3 сервиса + certbot profile
- `deploy/nginx/Dockerfile` — nginx:1.27-alpine + certbot
- `deploy/nginx/default.conf` — роутинг: `/` → landing, `/api/` → FastAPI, `/ui/` → Streamlit
- `.env.example` — шаблон переменных окружения

**Домен:** рекомендован `admetox.ai` (доступен, проверено через whois).

## Команды для разработки

```bash
# Запустить тесты
python -m pytest tests/ -v

# Запустить локально (Streamlit)
streamlit run app.py --server.port=8501

# Запустить локально (FastAPI)
python -m uvicorn api.main:app --reload --port 8000

# Docker
docker compose up -d --build
```

## Структура проекта

```
adme_proto/
├── src/              # Ядро: features, models, predict, config, i18n, pdf, radar
├── api/              # FastAPI: main.py, schemas.py
├── app.py            # Streamlit UI
├── models/           # 10 .pkl моделей (вшиты в Docker-образ)
├── data/             # .tab датасеты
├── landing/          # Landing page (static)
├── deploy/
│   ├── nginx/        # Dockerfile + конфиг для nginx контейнера
│   ├── nginx.conf    # Production nginx (bare-metal)
│   ├── systemd/      # systemd unit-файлы
│   └── Makefile      # deploy/update/restart
├── Dockerfile        # Многостадийный: base → api / ui
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── README.md
└── DEPLOY.md
```

## URL для доступа

| Сервис | Локально | Через nginx |
|--------|----------|-------------|
| Streamlit UI | http://localhost:8501 | http://localhost/ui/ |
| FastAPI API | http://localhost:8000 | http://localhost/api/ |
| Swagger docs | http://localhost:8000/docs | http://localhost/docs |
| Landing page | — | http://localhost/ |

## Переменные окружения (.env)

| Переменная | Обязательная | Дефолт |
|------------|-------------|--------|
| `ADMETOX_JWT_SECRET` | ✅ | генерируется случайно |
| `ADMETOX_API_KEYS` | ❌ | — |
| `ADMETOX_CORS_ORIGINS` | ❌ | `https://admetox.ai` |
| `DOMAIN` | для SSL | — |
| `SSL_EMAIL` | для SSL | — |

## 5. Client Engagement (отдельный проект)

**Расположение:** `D:\AI\biotech\client_engagement\` (отдельный проект, НЕ входит в основной репозиторий)

**Назначение:** Автоматизация продвижения продукта и привлечения инвесторов.

### Документация

Полная документация находится в `D:\AI\biotech\client_engagement\README.md`

### Быстрый запуск

```bash
cd D:\AI\biotech\client_engagement
start.bat
```

### Агенты (7 штук)

1. **GitHub Agent** — автогенерация changelog, release, автоответы на issues
2. **Content Agent** — генерация статей через LLM (6 тем)
3. **Investor Agent** — email outreach 66 инвесторам, follow-up
4. **Feedback Agent** — сбор обратной связи из GitHub, классификация
5. **Conference Agent** — отслеживание 10 конференций, дедлайны CFP
6. **Social Media Agent** — генерация постов для LinkedIn, Twitter, Medium
7. **Metrics Agent** — сбор метрик, еженедельные отчёты

### Связь с основным проектом

- **GitHub**: https://github.com/Recconnect/ADME-Tox-Predictor
- **Основной код**: `D:\AI\biotech\adme_proto\`
- **Модели**: `D:\AI\biotech\adme_proto\models\`
- **API**: `D:\AI\biotech\adme_proto\api\`
