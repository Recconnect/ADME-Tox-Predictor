# GTM Plan: ADME/Tox Predictor → Российский рынок

**Дата:** 2026-07-06
**Версия:** 1.0 (синтез 6 аудитов команды)
**Горизонт:** 18 месяцев

---

## 1. Executive Summary

| Параметр | Значение |
|----------|----------|
| Продукт | AI-платформа предсказания ADME/Tox свойств молекул до синтеза |
| Целевой рынок | Российские CRO и R&D отделы фармкомпаний |
| TAM (РФ) | $50-100 млн/год |
| Цель Jul 2027 | 5-15 платящих клиентов, $50-150K ARR |
| Цель Dec 2027 | 20+ клиентов, $500K+ ARR, подготовка к Series A |
| Финансирование | Гранты ₽34M (0-6 мес) → Pre-seed $100K (6-12) → Seed $200-500K (12-18) |
| Команда | 1 (основатель) → 3-5 чел к Jul 2027 |

### Ключевые метрики (сейчас)

| Модель | Метрика | Значение | Статус |
|--------|---------|----------|--------|
| Solubility (logS) | Test R² | 0.806 | ✓ выше target (0.6) |
| Caco-2 проницаемость | Test Acc / AUC | 85.6% / 0.932 | ✓ выше target (75%) |
| hERG токсичность | Test Acc / AUC | 82.2% / 0.846 | ✓ выше target (AUC 0.7) |
| Тесты | пройдено | 31/31 | ✓ |
| Валидация | известные препараты | 10/10 | ✓ |

---

## 2. Продукт: Roadmap

### Фаза v2.1 — Quick Win (Jul 2026–Sep 2026)

| Что | Зачем | Кто |
|-----|-------|-----|
| **Брендинг**: нейминг (ADMETox.AI), логотип, favicon, цветовая схема | Без бренда нельзя в рынок | Дизайнер |
| **Лендинг** на русском: 5 секций (проблема → решение → метрики → цена → контакты) | Первая точка входа для CRO | Дизайнер |
| **Free tier**: 100 предсказаний/мес без регистрации | Академия, building brand | ML Engineer |
| **Color-coding** результатов (красный/жёлтый/зелёный) | Быстрая оценка для клиентов | Дизайнер |
| **hERG датасет**: расширить до 3,000+ через ChEMBL | Критично для РФ-регуляторов (ICH S7B) | Bioengineer |
| **Lipinski Rule-of-Five** фильтр | Быстрый скрининг, востребован CRO | Bioengineer |
| **Feature importance** анализ | Доверие к модели, explainability | ML Engineer |

### Фаза v2.2 — Product-Market Fit (Sep 2026–Jan 2027)

| Что | Зачем | Кто |
|-----|-------|-----|
| LogD7.4, Pgp ингибирование | Востребовано российскими CRO | Bioengineer + ML |
| Confidence intervals для solubility | Доверие клиентов к цифрам | ML Engineer |
| REST API (FastAPI) + документация | B2B-интеграция с пайплайнами CRO | ML Engineer |
| Dockerfile + docker-compose | Простота деплоя у клиента | ML Engineer |
| Radar chart + scaffold viewer | Визуализация для презентаций | Дизайнер |
| Локализация интерфейса (русский язык) | B2B продажи в РФ | Дизайнер |
| Dark theme | Профессиональный вид | Дизайнер |

### Фаза v3.0 — Scale (Jan 2027–Jul 2027)

| Что | Зачем | Кто |
|-----|-------|-----|
| GNN на PyTorch Geometric (+5-10% к метрикам) | Конкурентное преимущество | ML Engineer |
| ONNX export моделей | Production deployment | ML Engineer |
| MLflow для экспериментов | MLOps, воспроизводимость | ML Engineer |
| Data drift monitoring (Evidently AI) | Enterprise SLA | ML Engineer |
| Доп. свойства: Bioavailability, CYP450 | Полнота ADME-пайплайна | Bioengineer |
| Enterprise: dedicated instance, fine-tuning | Ключевой продукт для крупных клиентов | Вся команда |

---

## 3. Рынок: Целевые компании и sales pipeline

### Приоритет 1: CRO (первые пилоты, Jul 2026–Nov 2026)

Целевые компании (по убыванию приоритета):

  - ChemRar (Moscow) — hit ID, lead optimization, medicinal chemistry
  - Khimrar (Moscow) — custom synthesis, library design
  - PharmChem (Moscow) — ADME assays, in vitro screening
  - Novoteh (Moscow region) — preclinical studies, toxicology
  - CRO Renovation (SPb) — clinical trials, regulatory
  - RML-CRO (Moscow) — preclinical, analytical
  - BioPharmExpert (Moscow) — regulatory, CMC, preclinical
  - NPO Farmanaliz (Moscow) — analytical chemistry, quality control

**План действий:**
1. **Неделя 1-2**: Собрать 50 контактов (LinkedIn + Pharmaprojects + конференции)
2. **Неделя 3-4**: Холодные письма/звонки в ChemRar, Khimrar, PharmChem
3. **Месяц 2-3**: Бесплатный пилот для ChemRar (их молекулы, валидация их данными)
4. **Месяц 3-4**: Презентация результатов → conversion в платный тариф
5. **Месяц 4-6**: Повторить с BIOCAD и R-Pharm

### Приоритет 2: Фармпроизводители (Nov 2026–Apr 2027)

  - BIOCAD (SPb) — oncology, immunology, revenue ~$1B
  - R-Pharm (Moscow) — hospital, oncology, revenue ~$1.5B
  - Geropharm (SPb) — diabetes, CNS, revenue N/A
  - Pharmasyntez (Irkutsk) — oncology, HIV, revenue ~$200M
  - Valenta Pharm (Moscow) — OTC, generics, revenue ~$300M
  - Otisifarm (Moscow) — generics, pediatrics, revenue N/A
  - Akrikhin (Moscow region) — generics, branded generics, revenue ~$400M
  - Vertex (SPb) — generics, OTC, revenue ~$200M
  - Nizhpharm (Stada) (Nizhny Novgorod) — generics, OTC, revenue N/A
  - Sotex (Moscow region) — infusions, cardiovascular, revenue N/A
  - Novo Nordisk Russia (Moscow) — diabetes, obesity, revenue N/A
  - Pfizer Russia (Moscow) — oncology, vaccines, revenue N/A
  - Sanofi Russia (Moscow) — diabetes, rare diseases, revenue N/A

**Подход:** Через R&D директоров, участие в PharmaRussia конференциях

### Приоритет 3: Госзакупки (Apr 2027+)

- Статус участника Сколково → право на ФЗ-44 и ФЗ-223
- Внесение в реестр российского ПО (Минцифры) — обязательно для госзаказчиков
- Пилот с Минздравом или подведомственным институтом

### Ценовая модель

| Тариф | Цена | Включено |
|-------|------|----------|
| Free | Бесплатно | 100 предсказаний/мес, базовые свойства |
| Starter | $10K/год (₽800K) | 10K предсказаний, email support |
| Enterprise | $50K/год (₽4M) | Dedicated instance, API, fine-tuning, SLA |
| Credits | $50/1K предсказаний | Разовые проекты без подписки |

---

## 4. Финансирование: Гранты → Pre-seed → Seed

### Грантовые программы (0–6 месяцев)

  - **Фонд содействия инновациям (Фонд Бортника)** — Старт-1: до 4 млн руб (НИОКР, прототип, проведение испытаний)
  - **Фонд содействия инновациям** — Старт-2: до 15 млн руб (коммерциализация, выпуск опытной партии)
  - **Фонд Сколково** — Сколково (участник): льготы + гранты до 30 млн руб (получение статуса участника стартапа, компенсация R&D)
  - **Российский научный фонд** — РНФ (молодежные): до 7 млн руб/год (фундаментальные и поисковые исследования)
  - **Российский фонд развития информационных технологий** — РФРИТ: до 300 млн руб (AI и ПО, импортозамещение)
  - **Фонд содействия инновациям** — Коммерциализация: до 30 млн руб (расширение производства, масштабирование)
  - **Минэкономразвития + Сбер** — ИИ-стартапы: до 50 млн руб (AI-first продукты, внедрение AI в промышленности)

**Приоритетная последовательность:**
1. **Старт-1** (₽4 млн, безвозвратно) — подать в ближайший цикл (3-4 недели на подготовку)
2. **Сколково** (статус + гранты до ₽30 млн) — подать параллельно
3. **РНФ** (₽7 млн/год) — если есть академический соавтор

### Инвестиции (6–18 месяцев)

  - **Kama Flow** — deep tech, biotech, seed-series A, чек $0.5-5M
  - **RBF Ventures** — bio/med tech, pre-seed, seed, чек $0.1-1M
  - **PharmMed Ventures** — pharma, med devices, seed-growth, чек $0.5-3M
  - **VEB Ventures** — deep tech, AI, pharma, series A+, чек $1-10M
  - **Sber Investments** — AI, healthcare, growth, чек $5M+
  - **Internet Initiatives Development Fund (IIDF)** — IT, AI, seed, чек до ₽25M

**План фандрайзинга:**

| Фаза | Срок | Сумма | Канал | Milestone |
|------|------|-------|-------|-----------|
| Гранты | 0-6 мес | ₽34M non-dilutive | Старт-1 + Сколково | Пилот с CRO |
| Pre-seed | 6-12 мес | $100K | RBF Ventures, бизнес-ангелы | 3-5 платящих клиентов |
| Seed | 12-18 мес | $200-500K | Kama Flow, Phystech Ventures | $150K+ ARR |
| Series A | 18+ мес | $2-5M | VEB, Sber, strategic | $500K+ ARR, 20+ клиентов |

---

## 5. Команда: Найм и роли

| Роль | Когда | З/п (мес) | Источник |
|------|-------|-----------|----------|
| **BD для РФ** (ключевая) | Месяц 1 | $2-3K | LinkedIn, Pharmaprojects, нетворк |
| **ML Engineer** (part-time → full) | Месяц 3 | $3-4K | Хабр Карьера, hh.ru, телеграм-каналы |
| **Chemoinformatician** (совмещение) | Месяц 3 | $2-3K | Академгородки, MSU, Skoltech |
| **Дизайнер** (freelance → full) | Месяц 6 | $1-2K | Behance, fl.ru |

**Бюджет на команду до seed:** ~$120K/год (с учётом грантов)

---

## 6. Legal & Compliance

| Задача | Срок | Статус | Комментарий |
|--------|------|--------|-------------|
| Регистрация юрлица (ИП/ООО) | 0-2 мес | ❌ | ООО для enterprise, ИП для грантов Старт |
| Статус Сколково | 1-4 мес | ❌ | Налоговые льготы + гранты |
| ФЗ-152 (персональные данные) | 3-6 мес | ❌ | Обязательно для работы с CRO |
| Реестр отечественного ПО | 6-12 мес | ❌ | Для госзакупок |
| Договорная база (NDA, SaaS) | 1-3 мес | ❌ | Юрист на аутсорсе |
| Патент (способ предсказания) | 6-12 мес | ❌ | Опционально, для exit-стратегии |

---

## 7. Подробный план по неделям

### Месяц 1 (Jul 2026) — Foundation

| Неделя | Product | Market | Finance | Legal |
|--------|---------|--------|---------|-------|
| 1 | Брендинг, нейминг | 50 контактов CRO | Заявка Старт-1 (начало) | Регистрация юрлица |
| 2 | Лендинг (структура) | Outreach ChemRar | Финансовая модель (3 года) | Счёт в банке |
| 3 | Color-coding + free tier | Переговоры с ChemRar | Бюджет на 12 мес | Налоговый режим |
| 4 | hERG dataset расширение | Договорённость о пилоте | Подача Старт-1 | — |

### Месяц 2 (Sep 2026) — Pilot Start

| Неделя | Product | Market | Finance | Legal |
|--------|---------|--------|---------|-------|
| 1 | Lipinski filter + radar chart | Пилот ChemRar (start) | Подготовка Сколково | Договор NDA |
| 2 | Feature importance | Анализ первых результатов | Заявка Сколково | SaaS договор (шаблон) |
| 3 | Dockerfile | Outreach BIOCAD | Финансовый план CRO | — |
| 4 | FastAPI (MVP) | Презентация на конференции | — | — |

### Месяц 3–4 (Sep 2026–Nov 2026) — Product-Market Fit

- LogD7.4 + Pgp модели (обучение)
- CI/CD pipeline
- Лицензионный договор с ChemRar (первый $)
- Найм ML Engineer
- Запуск paid tier

### Месяц 5–6 (Dec 2026–Jan 2027) — Scale Begins

- GNN исследование
- Внешняя валидация на данных CRO
- 3-5 платящих клиентов
- Заявка на Старт-2 / РФРИТ
- Найм дизайнера

### Месяц 7–12 (Feb 2027–Jul 2027) — Growth

- Enterprise: dedicated instance + fine-tuning
- Внесение в реестр ПО
- 5-15 клиентов, $50-150K ARR
- Pre-seed раунд $100K
- Series A preparation

### Месяц 13–18 (Jul 2027–Dec 2027) — Market Leadership

- 20+ клиентов, $500K+ ARR
- Seed раунд $200-500K
- Патентная заявка
- Выход на рынки СНГ

---

## 8. KPI Dashboard

### Product KPIs

| KPI | Jul 2026 | Oct 2026 | Jan 2027 | Jul 2027 | Dec 2027 |
|-----|------|------|------|-------|-------|
| ADME/Tox свойств | 3 | 5 | 7 | 10 | 12+ |
| Test R² (solubility) | 0.806 | 0.83 | 0.85 | 0.87 | 0.90 |
| Test AUC (caco2) | 0.932 | 0.94 | 0.95 | 0.96 | 0.97 |
| Test AUC (herg) | 0.845 | 0.86 | 0.88 | 0.90 | 0.92 |
| API Ready | ✗ | ✓ | ✓ | ✓ | ✓ |
| Docker | ✗ | ✓ | ✓ | ✓ | ✓ |
| ONNX | ✗ | ✗ | ✓ | ✓ | ✓ |

### Market KPIs

| KPI | Jul 2026 | Oct 2026 | Jan 2027 | Jul 2027 | Dec 2027 |
|-----|------|------|------|-------|-------|
| Контактов в CRM | 0 | 50 | 100 | 200 | 500 |
| Активных пилотов | 0 | 2 | 4 | 6 | 8 |
| Платящих клиентов | 0 | 0 | 3 | 10 | 20 |
| ARR | $0 | $0 | $30K | $100K | $500K |
| Churn rate | — | — | — | <15% | <10% |
| NPS | — | — | — | >40 | >50 |

### Funding KPIs

| KPI | Jul 2026 | Oct 2026 | Jan 2027 | Jul 2027 | Dec 2027 |
|-----|------|------|------|-------|-------|
| Гранты (₽) | 0 | 4M | 34M | 34M | 34M+ |
| Pre-seed ($) | 0 | 0 | 0 | 100K | 100K |
| Seed ($) | 0 | 0 | 0 | 0 | 200-500K |
| Runway (мес) | 12 | 18+ | 24+ | 24+ | 24+ |

---

## 9. Риски и митигация

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Гранты не получены | Medium | High | Подать на 3 программы одновременно, не ждать деньги от грантов |
| Sales cycle > 6 мес | High | Medium | Параллельно вести 10+ переговоров, free tier для low-friction entry |
| Конкуренты снижают цены | Low | Medium | Нишевая специализация, российское ПО, госзакупки |
| Регуляторные изменения | Medium | High | Юрист на аутсорсе, членство в ассоциациях фармы |
| Ключевой сотрудник уходит | Medium | High | Документация процессов, equity для ключевых ролей |
| Валютные риски | High | Medium | Цены в ₽ для РФ, хеджирование через валютный счёт |
| Данных для обучения не хватает | Medium | Medium | ChEMBL, PubChem, партнёрства с CRO для данных |
| Импортозамещение (нельзя использовать) | Low | High | Полный реестр ПО РФ, open-source компоненты с лицензиями |

---

## 10. Действия прямо сейчас (Week 1)

1. **Зарегистрировать юрлицо** (ООО или ИП) — 1-3 дня
2. **Начать заявку Старт-1** — 3-4 недели до дедлайна
3. **Собрать 50 контактов** CRO (LinkedIn + Pharmaprojects)
4. **Создать лендинг** (Tilda / Readymag / GitHub Pages)
5. **Написать первое письмо** ChemRar
6. **Обновить README** с контактами для РФ
7. **Залить сайт на русский хостинг** (Timeweb / Beget / Cloud4Y)

---

## 11. Приложение: Полезные ссылки

| Ресурс | URL |
|--------|-----|
| Фонд Бортника (Старт) | https://fasie.ru/programs/programma-start/ |
| Сколково | https://sk.ru/ |
| РФРИТ | https://rfrit.ru/ |
| РНФ | https://rscf.ru/ |
| Реестр ПО РФ | https://reestr.digital.gov.ru/ |
| Pharmaprojects | https://pharmaprojects.ru/ |
| ФЗ-152 | https://pd.rkn.gov.ru/ |

---

*Сгенерировано StrategistAgent на основе 6 аудитов команды: Team Lead, Bioengineer, ML Engineer, Business Dev, Designer, Financial Expert.*
*Дата: 2026-07-06 00:00*
