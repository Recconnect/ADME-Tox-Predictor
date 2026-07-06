# ADME/Tox Predictor — Session Resume

Дата: 2026-07-06  
Репозиторий: `D:\AI\biotech\adme_proto`  
Git: 15+ коммитов, ветка `master`

---

## Быстрый старт (с нуля)

```powershell
cd D:\AI\biotech\adme_proto
.\venv\Scripts\activate

streamlit run app.py                   # Streamlit UI → http://localhost:8501
python run_train.py                    # переобучить модели
python -m pytest tests -v              # 69 тестов
start.bat                              # Windows launcher
```

---

## Git история (последние коммиты)

```
8ab3a3d fix: resolve Streamlit session_state error for drug selection buttons
ed56b3a refactor: move agents/ to separate client_engagement/ project
6cdb5ca docs: update AGENTS.md with all 7 agents and new coordinator commands
498c2a9 feat: add 3 new outreach agents (feedback, conference, social media)
99c63af feat: add outreach agents module for automated product promotion
f93e500 docker: production-ready compose with nginx + certbot + embedded models
eaee7f4 security: fix 14 issues from pre-deployment audit
74b476b QA fix: _prop_to_pct crash on class string values, use_container_width deprecation
2b3a7c3 UI/UX: investor-friendly terminology, health score, grouped cards, brand theme
1e1f55e Optimize: 504->1 warning, lazy loading, single Mol parse, DRY predict cycle
cf9ee42 Phase C: PDF export (professional reports in RU/EN)
76e4aca Phase C: radar chart (spider plot) for ADME profile visualization
66dfafe Phase C: usage logging & analytics (SQLite + /admin/usage)
74c0c97 Phase C: JWT multi-user auth (+register/login endpoints)
edc1ff6 Обновление: метрики 10 моделей в sidebar + JSON/Python экспорт новых 5 моделей
```

---

## Структура проекта

```
adme_proto/
├── app.py                       # Streamlit UI (3 tabs)
├── run_train.py                 # Обучение всех моделей
├── requirements.txt
├── SESSION_RESUME.md            # Этот файл
├── AGENTS.md                    # История сессии и коммиты
├── start.bat                    # Windows launcher
│
├── src/                         # Ядро (v2.0)
│   ├── config.py                # Пути, MODEL_PARAMS, VALIDATION_DRUGS
│   ├── features.py              # RDKit дескрипторы (30) + Morgan (2048), canonicalization
│   ├── data_loader.py           # Harvard Dataverse, scaffold split, sanitization
│   ├── models.py                # LightGBM train/eval, save/load с metadata
│   ├── train.py                 # Пайплайн обучения
│   ├── predict.py               # ADMETPredictor (single/batch/validate)
│   ├── i18n.py                  # Интернационализация (RU/EN)
│   ├── pdf_report.py            # PDF отчёты
│   ├── radar.py                 # Radar charts
│   └── auth.py                  # JWT аутентификация
│
├── api/                         # FastAPI REST API
│   ├── main.py                  # API endpoints
│   ├── schemas.py               # Pydantic schemas
│   └── auth.py                  # Auth middleware
│
├── tests/                       # 69 тестов
│   ├── test_features.py         # 17 тестов
│   ├── test_models.py           # 5 тестов
│   ├── test_predict.py          # 9 тестов
│   ├── test_api.py              # API тесты
│   ├── test_auth.py             # Auth тесты
│   └── ...
│
├── data/                        # .tab датасеты (авто-скачивание)
├── models/                      # 11 .pkl моделей + training_results.json
├── logs/                        # app.log
│
├── landing/                     # Лендинг на русском (GitHub Pages)
│   └── index.html               # admetox.ai — продукт, метрики, цены
├── Dockerfile                   # Контейнеризация (multi-stage)
├── docker-compose.yml           # docker compose up (nginx + api + ui + certbot)
│
├── deploy/                      # Deployment configs
│   ├── nginx/                   # Docker nginx config
│   ├── nginx.conf               # Production nginx (bare-metal)
│   ├── systemd/                 # systemd unit files
│   └── Makefile                 # deploy/update/restart
│
├── team/                        ##=== КОМАНДА АГЕНТОВ ===##
│   ├── base.py                  # BaseAgent: чтение артефактов, генерация отчётов
│   ├── config.py                # 8 CRO, 16 pharma, 7 грантов, 6 конкурентов РФ
│   ├── runner.py                # Оркестратор (audit / strategy / single)
│   └── ...                      # 6 агентов команды
│
├── team_output/
│   ├── audit/                   # 6 аудитов (129 находок, 47 рекомендаций)
│   ├── strategy/
│   │   └── gtm_plan_russia.md   # GTM план (11 разделов, KPI, roadmap)
│   └── week1/                   # Week 1 документы
│
├── promo/                       # Маркетинговые материалы
└── investor_kit/                # Инвесторская аналитика
```

---

## Текущее состояние

### Модели (11 штук)

| Модель | Задача | Датасет | Размер | Ключевая метрика | Значение |
|--------|--------|---------|--------|-------------------|----------|
| Solubility | Регрессия | AqSolDB | 9,980 | Test R² | 0.826 |
| Caco-2 | Классификация | Wang et al. | 910 | Test Acc / AUC | 83.0% / 0.884 |
| hERG | Классификация | TDC | 655 | Test Acc / AUC | 80.3% / 0.873 |
| Lipophilicity | Регрессия | AqSolDB | 9,982 | Test R² | 0.815 |
| P-gp | Классификация | TDC | 1,117 | Test Acc / AUC | 85.2% / 0.912 |
| CYP3A4 | Классификация | TDC | 12,286 | Test Acc / AUC | 87.4% / 0.934 |
| CYP2D6 | Классификация | TDC | 13,130 | Test Acc / AUC | 89.1% / 0.945 |
| Ames | Классификация | TDC | 7,831 | Test Acc / AUC | 86.3% / 0.921 |
| Bioavailability | Классификация | TDC | 763 | Test Acc / AUC | 78.5% / 0.856 |
| PPB | Регрессия | TDC | 1,614 | Test R² | 0.742 |
| hERG (expanded) | Классификация | TDC | 9,505 | Test Acc / AUC | 84.7% / 0.918 |

### Тесты: 69/69 passed

### Security Audit: 14 фиксов
- C-1: JWT secret generation (no hardcoded fallback)
- C-2: CORS whitelist (ADMETOX_CORS_ORIGINS)
- C-3: Admin endpoint authentication
- H-1: Model file integrity verification (SHA-256)
- H-2: XSS protection (HTML escaping)
- H-3: Password policy (min 8 chars)
- H-4: File permissions (0o600 on sensitive files)
- H-5: Metrics endpoint authentication
- M-1: Reload mode controlled by environment variable
- M-3: Login rate limiting (5/min)
- M-5: SMILES truncation in error messages
- M-6: Input validation (max_length=10000)
- M-7: CSV upload validation

### Docker Deployment
- Multi-stage Dockerfile (base → api / ui)
- docker-compose.yml: nginx + api + ui + certbot
- Production-ready with TLS/SSL support
- Domain: admetox.ai (available)

### Client Engagement (Separate Project)
**Location:** `D:\AI\biotech\client_engagement\`

7 automated agents for product promotion:
1. GitHub Agent — auto-release, changelog, issue responses
2. Content Agent — article generation via LLM
3. Investor Agent — email outreach to 66 biotech investors
4. Feedback Agent — GitHub feedback collection
5. Conference Agent — conference tracking
6. Social Media Agent — LinkedIn, Twitter, Medium posts
7. Metrics Agent — weekly reports

---

## Команды

```powershell
# Development
streamlit run app.py                   # Streamlit UI
python -m uvicorn api.main:app --reload --port 8000  # FastAPI API
python -m pytest tests -v              # Run tests
python run_train.py                    # Retrain models
start.bat                              # Windows launcher

# Docker
docker compose up -d --build           # Build and run
docker compose down                    # Stop
docker compose logs -f                 # View logs

# Client Engagement
cd D:\AI\biotech\client_engagement
start.bat                              # Launcher with menu
```

---

## Важные нюансы

| Пункт | Детали |
|-------|--------|
| **Платформа** | Windows native — без WSL2, без Conda |
| **Python** | 3.14.4 с `rdkit` (не `rdkit-pypi`) |
| **Streamlit first run** | Запрашивает email — просто Enter |
| **MorganGenerator** | Deprecation warning — косметический |
| **Feature names warning** | LightGBM — косметический |
| **Данные** | Harvard Dataverse (ID: 4259610, 4259569, 4259588) |
| **Caco-2** | Бинаризован при logPapp > -5.5 |
| **BIOPTIC analogy** | Мы = Lead Optimization (они = Hit ID) |
| **Exit strategy** | M&A в CRO/Big Pharma, $5-15M |
| **Конкуренты в РФ** | Прямых нет — ниша свободна |
| **Гранты РФ** | Старт-1 (₽4M), Сколково (₽30M), РФРИТ (до ₽300M) |

---

## Что можно сделать дальше

### Short-term (дни)
- [ ] Подать заявку Старт-1 — `team_output/week1/start1_application.md`
- [ ] Отправить письмо ChemRar — `team_output/week1/chemrar_pitch.md`
- [ ] Зарегистрировать юрлицо
- [ ] Настроить Client Engagement агенты
- [ ] Запустить outreach кампанию

### Medium-term (недели)
- [ ] Развернуть на сервере (admetox.ai)
- [ ] Настроить HTTPS/SSL
- [ ] Запустить автоматические публикации
- [ ] Собрать первые отзывы от инвесторов

### Long-term (месяцы)
- [ ] GNN (PyTorch Geometric)
- [ ] Enterprise-версия
- [ ] Seed-раунд $200-500K

---

## Исходные данные

- План: `D:\AI\biotech\План 1.0.docx`
- Интервью BIOPTIC: `D:\AI\biotech\business_model.txt`
- Код: `D:\AI\biotech\adme_proto`
- Client Engagement: `D:\AI\biotech\client_engagement`
- GTM план: `team_output/strategy/gtm_plan_russia.md`
- Аудиты: `team_output/audit/`
- Week 1: `team_output/week1/`

```
Последний коммит: 8ab3a3d — fix: resolve Streamlit session_state error
Всего коммитов: 15+
Ветка: master
```
