# ADME/Tox Predictor

AI-прототип для предсказания ADME-свойств и токсичности молекул (drug discovery).

## Быстрый старт

```powershell
cd D:\AI\biotech\adme_proto

# Активировать окружение
.\venv\Scripts\activate

# Запустить веб-интерфейс
streamlit run app.py
```

Откройте в браузере: http://localhost:8501

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
├── src/
│   ├── config.py        # Настройки, пути, названия датасетов
│   ├── data_loader.py   # Загрузка AqSolDB, Caco-2, hERG с Harvard Dataverse
│   ├── features.py      # 30 RDKit дескрипторов + Morgan fingerprint (2048 бит)
│   ├── models.py        # LightGBM (регрессия + классификация)
│   ├── train.py         # Пайплайн обучения всех моделей
│   └── predict.py       # Класс ADMETPredictor для инференса
├── app.py               # Streamlit UI (3 вкладки: Single/Batch/Validation)
├── models/              # Сохранённые .pkl модели
│   ├── solubility_model.pkl
│   ├── caco2_model.pkl
│   └── herg_model.pkl
└── data/                # Сырые .tab файлы датасетов
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
