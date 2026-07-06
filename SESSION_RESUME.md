# ADME/Tox Predictor — Session Resume

Дата: 2026-07-06  
Репозиторий: `D:\AI\biotech\adme_proto`  
Git: 6 коммитов, ветка `master`

---

## Быстрый старт (с нуля)

```powershell
cd D:\AI\biotech\adme_proto
.\venv\Scripts\activate

streamlit run app.py                   # Streamlit UI → http://localhost:8501
python run_train.py                    # переобучить модели
python -m pytest tests -v              # 31 тест
python -m team.runner --strategy       # аудит + GTM план
```

---

## Git история

```
0ca3b69 Add Week 1 deliverables: ChemRar cold pitch + Start-1 grant application
21dc7ab Add Strategist agent: consolidated GTM plan for Russia
c3f3aa1 Add local team agents: 6-role audit pipeline
314995a Add SESSION_RESUME.md — full project summary
d44132c Add investor_kit: strategy analysis, competitive positioning, metrics dashboard
495b665 v2.0: major refactor - tests, SMILES canonicalization, logging, security
```

---

## Структура проекта

```
adme_proto/
├── app.py                       # Streamlit UI (3 tabs)
├── run_train.py                 # Обучение всех моделей
├── requirements.txt
├── SESSION_RESUME.md            # Этот файл
│
├── src/                         # Ядро (v2.0)
│   ├── config.py                # Пути, MODEL_PARAMS, VALIDATION_DRUGS
│   ├── features.py              # RDKit дескрипторы (30) + Morgan (2048), canonicalization
│   ├── data_loader.py           # Harvard Dataverse, scaffold split, sanitization
│   ├── models.py                # LightGBM train/eval, save/load с metadata
│   ├── train.py                 # Пайплайн обучения
│   └── predict.py               # ADMETPredictor (single/batch/validate)
│
├── tests/                       # 31 тестов
│   ├── test_features.py         # 17 тестов
│   ├── test_models.py           # 5 тестов
│   └── test_predict.py          # 9 тестов
│
├── data/                        # .tab датасеты (авто-скачивание)
├── models/                      # .pkl + training_results.json
├── logs/                        # app.log
│
├── team/                        ##=== КОМАНДА АГЕНТОВ ===##
│   ├── base.py                  # BaseAgent: чтение артефактов, генерация отчётов
│   ├── config.py                # 8 CRO, 16 pharma, 7 грантов, 6 конкурентов РФ
│   ├── runner.py                # Оркестратор (audit / strategy / single)
│   │
│   ├── agent_team_lead.py       # Product Owner — стратегический аудит
│   ├── agent_bioengineer.py     # Хемоинформатик — модели, данные, регуляторика
│   ├── agent_ml_engineer.py     # ML Engineer — архитектура, production
│   ├── agent_business_dev.py    # BD — рынок РФ, CRO, GTM
│   ├── agent_designer.py        # UI/UX — интерфейс, брендинг
│   ├── agent_financial_expert.py # Финансы — гранты, юнит-экономика
│   ├── agent_strategist.py      # Strategist — GTM план (18 мес)
│   └── agent_week1.py           # Week 1 deliverables
│
├── team_output/
│   ├── audit/                   # 6 аудитов (129 находок, 47 рекомендаций)
│   ├── strategy/
│   │   └── gtm_plan_russia.md   # GTM план (11 разделов, KPI, roadmap)
│   └── week1/                   # Week 1 документы
│       ├── chemrar_pitch.md     # Письмо ChemRar + value prop + outreach
│       └── start1_application.md # Заявка Старт-1 (структура + бюджет)
│
├── promo/                       # Маркетинговые материалы
│   ├── ADMET_Predictor_Investors_RU.pptx
│   ├── ADMET_Predictor_Investor_Pitch.pptx
│   ├── ADMET_Predictor_Executive_Summary.pptx
│   ├── investor_presentation.md
│   ├── metrics_summary.json
│   └── charts/
│
└── investor_kit/                # Инвесторская аналитика
    ├── strategy_from_bioptic.md
    ├── investor_brief.md
    ├── competitive_positioning.md
    ├── investor_memo.md
    └── metrics_dashboard.json
```

---

## Текущее состояние

### Модели

| Модель | Задача | Датасет | Размер | Ключевая метрика | Значение |
|--------|--------|---------|--------|-------------------|----------|
| Solubility | Регрессия | AqSolDB | 9 980 | Test R² | 0.806 |
| Caco-2 | Классификация | Wang et al. | 906 | Test Acc / AUC | 85.6% / 0.932 |
| hERG | Классификация | TDC | 648 | Test Acc / AUC | 82.2% / 0.846 |

### Тесты: 31/31 passed

### GTM план для РФ (18 месяцев)

**Ключевые вехи:**
- **v2.1** (Jul–Sep 2026): Брендинг, лендинг, free tier, hERG расширение
- **v2.2** (Sep–Jan 2027): LogD7.4, Pgp, FastAPI, Docker, radar chart
- **v3.0** (Jan–Jul 2027): GNN, ONNX, enterprise features, 5-15 клиентов
- **Funding**: Старт-1 (₽4M) → Сколково (₽30M) → Pre-seed ($100K) → Seed ($200-500K)
- **Team**: BD (мес 1) → ML + Bio (мес 3) → Designer (мес 6)

**Week 1 действия:**
1. Зарегистрировать юрлицо (ОКВЭД 72.19)
2. Начать заявку Старт-1 (https://fasie.ru/programs/programma-start/)
3. Собрать 50 контактов CRO (LinkedIn + Pharmaprojects)
4. Отправить письмо ChemRar (см. `team_output/week1/chemrar_pitch.md`)
5. Создать лендинг на русском

---

## Команда: команды

```powershell
python -m team.runner                    # аудит 6 агентов
python -m team.runner --strategy         # аудит + GTM план
python -m team.runner --agent=bioengineer   # один агент
python -m team.agent_week1               # Week 1 документы
python -m team.agent_week1 --chemrar     # только письмо ChemRar
python -m team.agent_week1 --grant       # только заявка Старт-1
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
- [ ] Подавить warnings в коде

### Medium-term (недели)
- [ ] Docker + FastAPI (пункты GTM v2.2)
- [ ] LogD7.4 + Pgp модели
- [ ] Лендинг на русском
- [ ] Статус участника Сколково

### Long-term (месяцы)
- [ ] GNN (PyTorch Geometric)
- [ ] Enterprise-версия
- [ ] Seed-раунд $200-500K

---

## Исходные данные

- План: `D:\AI\biotech\План 1.0.docx`
- Интервью BIOPTIC: `D:\AI\biotech\business_model.txt`
- Код: `D:\AI\biotech\adme_proto`
- GTM план: `team_output/strategy/gtm_plan_russia.md`
- Аудиты: `team_output/audit/`
- Week 1: `team_output/week1/`

```
Последний коммит: 0ca3b69 — Add Week 1 deliverables
Всего коммитов: 6
Ветка: master
```
