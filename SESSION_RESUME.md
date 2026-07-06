# ADME/Tox Predictor — Session Resume

Дата: 2026-07-06  
Репозиторий: `D:\AI\biotech\adme_proto`  
Git: 2 коммита, ветка `master`

---

## Быстрый старт (с нуля)

```powershell
# 1. Активировать окружение
cd D:\AI\biotech\adme_proto
.\venv\Scripts\activate

# 2. Запустить Streamlit UI
streamlit run app.py
# Открыть http://localhost:8501

# 3. Переобучить модели (если нужно)
python run_train.py
```

---

## Git история

```
d44132c Add investor_kit: strategy analysis, competitive positioning, metrics dashboard
495b665 v2.0: major refactor - tests, SMILES canonicalization, logging, security
```

---

## Структура проекта

```
adme_proto/
├── app.py                     # Streamlit UI (3 вкладки: Single/Batch/Validation)
├── run_train.py               # Точка входа для обучения
├── requirements.txt           # Зависимости
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── config.py              # Настройки, пути, MODEL_PARAMS, VALIDATION_DRUGS
│   ├── features.py            # RDKit дескрипторы + Morgan fp, canonicalize
│   ├── data_loader.py         # Загрузка с Harvard Dataverse, scaffold split
│   ├── models.py              # LightGBM train/eval, save/load с метаданными
│   ├── train.py               # Пайплайн: data → features → train → test
│   └── predict.py             # ADMETPredictor класс (single/batch/validate)
│
├── tests/
│   ├── __init__.py
│   ├── test_features.py       # 17 тестов — SMILES, дескрипторы, fingerprint, batch
│   ├── test_models.py         # 5 тестов — регрессия, классификация, save/load
│   └── test_predict.py        # 9 тестов — загрузка, predict, валидация
│
├── data/                      # .tab файлы датасетов (скачиваются автоматически)
│   ├── solubility.tab
│   ├── caco2.tab
│   ├── herg.tab
│   └── datasets_info.json     # Метаданные по сплитам (auto-generated)
│
├── models/                    # .pkl файлы (auto-generated)
│   ├── solubility_model.pkl
│   ├── caco2_model.pkl
│   ├── herg_model.pkl
│   └── training_results.json
│
├── logs/                      # Логи (app.log)
│
├── promo/                     # Маркетинговые материалы
│   ├── ADMET_Predictor_Investors_RU.pptx     # Презентация рус (10 сл.)
│   ├── ADMET_Predictor_Investor_Pitch.pptx   # Презентация eng (10 сл.)
│   ├── ADMET_Predictor_Executive_Summary.pptx  # Executive summary (6 сл.)
│   ├── investor_presentation.md              # Текстовая версия
│   ├── metrics_summary.json                  # Ключевые метрики
│   ├── charts/                               # Сгенерированные графики
│   └── generate_*.py                         # Генераторы pptx/charts
│
└── investor_kit/              # Аналитика для инвесторов (из интервью BIOPTIC)
    ├── strategy_from_bioptic.md              # Разбор бизнес-модели
    ├── investor_brief.md                     # Investor brief
    ├── competitive_positioning.md            # Позиционирование на рынке
    ├── investor_memo.md                      # One-page memo
    └── metrics_dashboard.json               # Машиночитаемые метрики
```

---

## Текущее состояние

### Модели — все метрики превышают целевые

| Модель | Задача | Датасет | Размер | Ключевая метрика | Значение |
|--------|--------|---------|--------|-------------------|----------|
| Solubility | Регрессия | AqSolDB | 9 980 | Test R² | 0.806 |
| Caco-2 | Классификация | Wang et al. | 906 | Test Acc / AUC | 85.6% / 0.932 |
| hERG | Классификация | TDC | 648 | Test Acc / AUC | 82.2% / 0.846 |

### Тесты: 31/31 passed

- `test_features.py` — 17 тестов (SMILES валидация, дескрипторы, fingerprint)
- `test_models.py` — 5 тестов (train, predict, save/load)
- `test_predict.py` — 9 тестов (inference на реальных молекулах)

### Команды

```powershell
# Запустить UI
streamlit run app.py

# Запустить тесты
python -m pytest tests -v

# Обучение
python run_train.py

# Сгенерировать графики для презентаций
python promo/generate_charts.py

# Сгенерировать pptx
python promo/generate_pptx.py
python promo/generate_pptx_ru.py
python promo/generate_executive_summary.py
```

---

## Что было сделано (Session 1)

### Phase 1: MVP

1. Проанализирован план из `D:\AI\biotech\План 1.0.docx`
2. Создана структура проекта, `requirements.txt`
3. Установлены: rdkit, pandas, scikit-learn, lightgbm, streamlit
4. Реализован загрузчик данных с Harvard Dataverse (AqSolDB, Caco-2, hERG)
5. Реализован scaffold split через Morgan fingerprints + MiniBatchKMeans
6. 30 RDKit дескрипторов + 2048 Morgan fingerprints
7. 3 модели LightGBM обучены, сохранены как .pkl
8. Streamlit UI с 3 табами (Single, Batch, Validation)
9. Валидация на 10 известных препаратах

### Phase 2: v2.0 Refactor

1. **SMILES canonicalization** — все входы нормализуются
2. **LRU caching** — дескрипторы и fingerprint кэшируются
3. **Logging** — вместо print() через модуль logging
4. **Data integrity** — dedup, NaN check, sanitization
5. **Error handling** — пустые/невалидные SMILES
6. **Security** — MAX_UPLOAD_MB, MAX_BATCH_SIZE
7. **Models metadata** — save_model сохраняет feature_names
8. **Tests** — 31 тест
9. **requirements.txt** — убраны неработающие пакеты (tdc, rdkit-pypi)

### Phase 3: Инвесторские материалы

1. Анализ интервью Андрея Дороничева (BIOPTIC) — `business_model.txt`
2. Разбор бизнес-модели, позиционирование, конкурентный анализ
3. Презентации pptx (3 шт: RU, EN, Executive Summary)
4. Графики для презентаций (5 шт)
5. `investor_kit/` — 5 документов для инвесторов

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
| **BIOPTIC analogy** | Наш проект = Lead Optimization (их = Hit ID) |
| **Exit strategy** | M&A в CRO/Big Pharma, оценка $5-15M |

---

## Что можно сделать дальше

### Short-term (дни)
- [ ] Подавить warnings (MorganGenerator → use_container_width)
- [ ] Добавить Dockerfile
- [ ] Развернуть на Streamlit Cloud / Hugging Face Spaces

### Medium-term (недели)
- [ ] GNN модель (PyTorch Geometric) +5-10% к метрикам
- [ ] REST API (FastAPI) для программного доступа
- [ ] Добавить Pgp, Lipophilicity, Bioavailability

### Long-term (месяцы)
- [ ] CI/CD (GitHub Actions)
- [ ] Proprietary data pipeline (партнёрства с CRO)
- [ ] Fine-tuning на данных клиентов
- [ ] Series A raise при 50+ клиентах

---

## Исходные данные

- План: `D:\AI\biotech\План 1.0.docx`
- Интервью BIOPTIC: `D:\AI\biotech\business_model.txt`
- Код: `D:\AI\biotech\adme_proto`
- Логи: `D:\AI\biotech\adme_proto\logs\app.log`
