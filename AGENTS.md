# Session: ADMETox.AI — Pre-deployment audit, security fixes, Docker packaging, Outreach agents

## Источники данных
- Путь: `D:\AI\biotech\adme_proto`
- Ветка: `master`
- GitHub: https://github.com/Recconnect/ADME-Tox-Predictor
- Последние коммиты:
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
├── agents/           # Outreach agents (НЕ в Docker)
│   ├── core/         # LLM, Email, GitHub клиенты
│   ├── tasks/        # GitHub release, content, outreach, metrics
│   ├── data/         # investors.csv, metrics.db, articles/
│   ├── coordinator.py # Оркестратор
│   └── start.bat     # Ярлык запуска
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

## 5. Outreach Agents (модуль продвижения)

**Расположение:** `agents/` (НЕ входит в Docker-образ)

**Назначение:** Автоматизация продвижения продукта и привлечения инвесторов.

### Архитектура

```
agents/
├── core/                    # Базовые клиенты
│   ├── llm.py              # OpenAI API (GPT-4o-mini)
│   ├── email_sender.py     # SMTP (Яндекс.Почта)
│   └── github_client.py    # GitHub API (PyGithub)
│
├── tasks/                   # Бизнес-логика агентов
│   ├── github_release.py   # Автогенерация changelog + release
│   ├── content_writer.py   # Генерация статей через LLM
│   ├── investor_outreach.py # Email outreach инвесторам
│   └── metrics_collector.py # Сбор метрик, еженедельные отчёты
│
├── data/                    # Базы данных
│   ├── investors.csv       # 70+ биотех/healthtech инвесторов
│   ├── metrics.db          # SQLite для метрик
│   ├── email_log.db        # Лог отправленных писем
│   └── articles/           # Сгенерированные статьи
│
├── coordinator.py          # Оркестратор (расписание)
├── config.yml              # Конфигурация
├── .env                    # Секреты (не коммитится)
└── start.bat               # Ярлык запуска (Windows)
```

### Расписание задач

| Задача | Частота | Описание |
|--------|---------|----------|
| GitHub release | ежедневно 10:00 | Changelog + release при коммитах |
| Автоответы на issues | ежедневно 10:05 | Шаблонные ответы через LLM |
| Генерация статьи | понедельник 09:00 | Статья для Medium/Habr/VC.ru |
| Outreach инвесторам | пн-пт 11:00 | Макс 5 писем/день |
| Follow-up инвесторам | пятница 14:00 | Напоминания через 7 дней |
| Еженедельный отчёт | воскресенье 20:00 | Метрики + email на your_email@example.com |

### Команды запуска

```bash
# Ярлык запуска (Windows)
agents\start.bat

# Или вручную:
cd agents
python coordinator.py release      # GitHub release
python coordinator.py article      # Генерация статьи
python coordinator.py outreach     # Outreach инвесторам
python coordinator.py followup     # Follow-up
python coordinator.py metrics      # Сбор метрик
python coordinator.py all          # Все задачи
python coordinator.py schedule     # Режим планировщика
```

### Настройка

1. Установить зависимости: `pip install -r requirements.txt`
2. Создать `.env` из `.env.example`
3. Добавить `OPENAI_API_KEY` (https://platform.openai.com/api-keys)
4. Добавить `EMAIL_PASSWORD` (app-specific password для Яндекс.Почты)
5. GitHub токен уже настроен

### Бюджет

| Сервис | Стоимость |
|--------|-----------|
| OpenAI API (GPT-4o-mini) | ~$5/мес |
| GitHub API | Бесплатно |
| Email (Яндекс.Почта) | Бесплатно |
| **Итого** | **~$5/мес** |

### Инвесторы

База `data/investors.csv` содержит 70+ биотех/healthtech инвесторов:
- Deep Knowledge Ventures, Insilico Medicine, J&J Innovation
- Third Rock Ventures, Flagship Pioneering, a16z
- Sequoia Capital, Khosla Ventures, Founders Fund
- И другие (полный список в CSV)
