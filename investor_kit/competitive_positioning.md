# ADME/Tox Predictor — Competitive Analysis v2.0

## Позиционирование на рынке

```
                        Сложность технологии
                              ↑
                    Isomorphic | Schrodinger
                    (DeepMind)  | (FEP+)
                    $2B funded  | Public co.
                              |
            BIOptIC          |  ▲
            (Hit ID gen)     |  │
            $11M raised      |  │ ADME/Tox Predictor ← МЫ
                              |  │ (Lead Optimization)
                              |  │
                    ChemAxon  |  │
                    (десктоп)  |  │
                    $5K/год   |  │
                              └──┴──────────────────→ Цена/доступность
                                Низкая    Высокая
```

## Сравнение

| Параметр | Schrodinger | BIOptIC | Isomorphic | ChemAxon | **ADME/Tox Pred.** |
|----------|------------|---------|------------|----------|-------------------|
| **Цена** | $100K+/год | Enterprise | N/A | $5K/год | **$10-50K/год** |
| **Фокус** | FEP+ docking | Hit ID gen | Hit ID gen | Descriptors | **ADME/Tox** |
| **AI** | Да | Да | Да (DeepMind) | Нет | **LightGBM** |
| **Target** | Любая мишень | Любая мишень | Любая | Любая | **ADME/Tox** |
| **MVP** | Да | Да | Partial | Да | **Да** |
| **Data** | Proprietary | Public + own | Proprietary | Public | **TDC / Public** |
| **Time to try** | Недели | Месяцы | N/A | Дни | **5 минут** |
| **Установка** | Cloud | Cloud | N/A | Desktop | **Streamlit / API** |

## Наши преимущества

### 1. Speed to value
- Streamlit UI: попробовать за 5 минут
- Не нужно ставить софт, не нужно обучение
- Ввод SMILES → результат за 1 секунду

### 2. Специализация
- Schrodinger: универсальная платформа → дорого, сложно
- Мы: только ADME/Tox → дешево, просто, точно
- CRO не нужен FEP+ за $100K, им нужен быстрый скрининг за $10K

### 3. Комплемент к BIOPTIC
- BIOPTIC находит активные молекулы (Hit ID)
- Мы проверяем их на ADME/Tox (Lead Optimization)
- Вместе: полный пайплайн hit-to-lead за недели вместо лет

### 4. Data moát через партнёрства
- Публичные данные дают baseline
- Proprietary данные от CRO — барьер для конкурентов
- Чем больше клиентов, тем лучше модель

## Позиционирование для разных аудиторий

### Для CRO
> "Сократите время Lead Optimization на 60%. Не синтезируйте молекулы,
> которые отсеются на ADME/Tox. Платите $10K/год за API."

### Для Biotech стартапов
> "Проверьте 10,000 молекул за $50. Не тратьте $100K на синтез
> нерастворимых соединений."

### Для инвесторов
> "MVP с metrics выше target. Ниша без конкурентов. Рынок $7.6B к 2028.
> SaaS с ARR $10-50K на клиента. Exit через M&A."

## Go-to-Market

### Фаза 1: Direct Sales (месяцы 1-6)
- Цель: 3-5 CRO клиентов на пилот
- Канал: LinkedIn, Pharma conferences, партнёрства
- Цена: Бесплатный trial на 30 дней, $10K/год после

### Фаза 2: Product-Led Growth (месяцы 6-12)
- Web-based UI, self-serve
- Credit-based pricing: $50 за 1,000 predictions
- Referral program для CRO

### Фаза 3: Enterprise (год 2+)
- Dedicated instance
- Fine-tuning на данных клиента
- $100-500K/год за enterprise лицензию
