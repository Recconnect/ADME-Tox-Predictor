# ADME/Tox Predictor

AI-прототип для предсказания ADME-свойств и токсичности молекул (drug discovery).

## Быстрый старт (Docker — рекомендовано)

```bash
# 1. Клонировать
git clone https://github.com/bradist/ADME-Tox-Predictor.git
cd ADME-Tox-Predictor

# 2. Создать .env с секретами
cp .env.example .env
# Отредактировать .env: сгенерировать ADMETOX_JWT_SECRET
#   openssl rand -hex 32

# 3. Собрать и запустить
docker compose up -d --build

# 4. Открыть в браузере
#   Landing:  http://localhost
#   UI:       http://localhost/ui/
#   API docs: http://localhost/docs
```

## Быстрый старт (локально)

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# .\venv\Scripts\activate  # Windows

pip install -r requirements.txt
streamlit run app.py --server.port=8501
```

Откройте: http://localhost:8501

## Обучение моделей заново

```powershell
cd D:\AI\biotech\adme_proto
.\venv\Scripts\activate
python run_train.py
```

Обучение скачает данные с Harvard Dataverse (~10-30 сек), вычислит фичи и обучит 3 модели.

## Архитектура

```
adme_proto/
├── src/                  # Ядро: фичи, модели, предикт
├── api/                  # FastAPI REST API
├── app.py                # Streamlit UI
├── deploy/
│   ├── nginx/
│   │   ├── Dockerfile    # nginx + certbot
│   │   └── default.conf  # маршрутизация: / → landing, /api/ → FastAPI, /ui/ → Streamlit
│   ├── nginx.conf        # production nginx (bare-metal)
│   ├── systemd/          # systemd unit-файлы (bare-metal)
│   └── Makefile          # команды deploy/update/restart
├── landing/              # Статическая landing page
├── models/               # Обученные .pkl модели (вшиты в Docker-образ)
├── data/                 # Сырые датасеты .tab
├── Dockerfile            # Многостадийный: base → ui / api
├── docker-compose.yml    # 3 сервиса: nginx + api + ui (+ certbot для SSL)
└── .env.example          # Шаблон переменных окружения
```

## Docker Compose (рекомендованный способ)

### Сервисы

| Сервис | Роль | Порт | Доступ через nginx |
|--------|------|------|--------------------|
| **nginx** | TLS termination, роутинг, landing page | 80/443 | `/` — landing, `/ui/` — Streamlit, `/api/` — FastAPI, `/docs` — Swagger |
| **api** | FastAPI REST API (predict, batch, health) | 8000 | `/api/`, `/docs` |
| **ui** | Streamlit Web UI | 8501 | `/ui/` |
| **certbot** | Автоматическое получение SSL-сертификатов | — | Разовый запуск: `docker compose --profile setup run certbot` |

### Переменные окружения (.env)

| Переменная | Обязательная | Описание |
|------------|-------------|----------|
| `ADMETOX_JWT_SECRET` | ✅ | Секрет для JWT-токенов (64 символа hex) |
| `ADMETOX_API_KEYS` | ❌ | API-ключи через запятую (если пусто — только JWT) |
| `ADMETOX_CORS_ORIGINS` | ❌ | Разрешённые CORS-источники через запятую |
| `DOMAIN` | для SSL | Домен для Let's Encrypt |
| `SSL_EMAIL` | для SSL | Email для уведомлений Let's Encrypt |

### SSL-сертификаты

```bash
# Получить сертификаты (однократно)
docker compose --profile setup run certbot

# nginx автоматически подхватит сертификаты после перезапуска
docker compose restart nginx

# Обновление сертификатов (каждые 60 дней)
docker compose run --rm certbot renew
```

### Обновление

```bash
git pull
docker compose up -d --build
```

## Модели

| Модель | Тип | Размер данных | Val R²/Acc/AUC | Test R²/Acc/AUC |
|--------|-----|---------------|----------------|-----------------|
| **Solubility** (AqSolDB) | регрессия (logS) | 9 982 молекул | R²=0.801 | R²=0.826 |
| **Caco-2** (Wang et al.) | бинарная классификация | 910 молекул | Acc=0.890, AUC=0.964 | Acc=0.830, AUC=0.884 |
| **hERG** (TDC) | бинарная классификация | 655 молекул | Acc=0.846, AUC=0.914 | Acc=0.803, AUC=0.873 |

Все метрики превышают целевые показатели из плана (R²>0.6, Acc>75%, AUC>0.7).

## Как использовать

### Веб-интерфейс (Streamlit)

1. **Single Prediction** — введите SMILES (например `CCO`), нажмите Predict
2. **Batch Prediction** — введите несколько SMILES (по одному на строку) или загрузите CSV
3. **Validation** — проверка на 10 известных препаратах (аспирин, ибупрофен и т.д.)

### Из Python

```python
import sys
sys.path.insert(0, r'D:\AI\biotech\adme_proto')
from src.predict import ADMETPredictor

predictor = ADMETPredictor()
result = predictor.predict_single("CCO")
print(result["Solubility (logS)"])      # -0.123
print(result["Caco-2 Class"])           # High permeability
print(result["hERG Class"])             # Safe (low risk)
```

### Батч-предсказание

```python
smiles_list = ["CCO", "CC(=O)Oc1ccccc1C(=O)O", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"]
df = predictor.predict_dataframe(smiles_list, drug_names=["Ethanol", "Aspirin", "Caffeine"])
print(df)
```

## Источники данных

- **AqSolDB** — растворимость в воде (9 982 записи) — Harvard Dataverse ID: 4259610
- **Caco-2** — проницаемость через Caco-2 (910 записей) — Harvard Dataverse ID: 4259569
- **hERG** — hERG токсичность (655 записей) — Harvard Dataverse ID: 4259588

Данные получены из [Therapeutics Data Commons (TDC)](https://tdcommons.ai/).

## Зависимости

- rdkit — химическая информатика (валидация SMILES, дескрипторы, fingerprints)
- lightgbm — градиентный бустинг
- streamlit — веб-интерфейс
- pandas, numpy, scikit-learn, matplotlib, seaborn
- requests — загрузка датасетов с Harvard Dataverse

## Примечания

- Caco-2 датасет бинаризован по порогу logPapp > -5.5 (высокая проницаемость)
- Для production-использования требуется fine-tuning на корпоративных данных и валидация по ICH M7/FDA Guidance
- Модель на open-source данных НЕ заменяет экспериментальную валидацию
