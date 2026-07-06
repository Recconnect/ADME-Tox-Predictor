# ADMETox.AI — Правила оптимизированной разработки

## 1. Feature Pipeline (главный bottleneck)

### 1.1. Один парсинг Mol — два результата
**Правило:** Никогда не парсить SMILES в `rdkit.Chem.Mol` дважды.  
`compute_rdkit_descriptors()` + `get_morgan_fingerprint()` должны работать от одного `Mol`.

```python
# ❌ ПЛОХО — парсит SMILES 2 раза:
desc = compute_rdkit_descriptors(smiles)
fp = get_morgan_fingerprint(smiles)

# ✅ ХОРОШО — один парсинг:
mol = Chem.MolFromSmiles(smiles)
desc = _descriptors_from_mol(mol)
fp = _fingerprint_from_mol(mol)
```

### 1.2. LRU-кеш для дескрипторов и fingerprint
**Правило:** Все тяжёлые вычисления (`MolFromSmiles`, `Descriptors`, Morgan) кешировать через `@functools.lru_cache(maxsize=32768)`.  
Размер кеша достаточен для ~30K уникальных молекул.

### 1.3. Feature names — lru_cache вместо global
**Правило:** `get_feature_names()` использовать `@functools.lru_cache` вместо модульной глобальной переменной.

## 2. Model Serving

### 2.1. Lazy loading моделей
**Правило:** Загружать модель через `joblib.load()` только при первом запросе к ней.  
`ADMETPredictor.__init__` только сканирует `.pkl` файлы, не загружает их.

```python
# ❌ ПЛОХО — загружает все 10 моделей при старте (1.86s, 213 MB)
self.models[key] = load_model(path)

# ✅ ХОРОШО — ленивая загрузка
if path.exists():
    self._model_paths[key] = path

def _get_model(self, key):
    if key not in self._models:
        self._models[key] = load_model(self._model_paths[key])
    return self._models[key]
```

### 2.2. Предсказания через цикл
**Правило:** Не дублировать 10 блоков `if key in self.models`.  
Использовать конфигурационный список (label, key, is_classification, threshold_fn).

## 3. Streamlit

### 3.1. Кеш для predictor
**Правило:** Использовать `@st.cache_resource` для всех тяжёлых объектов.

```python
@st.cache_resource
def get_predictor():
    return ADMETPredictor()
```

### 3.2. Импорты наверх
**Правило:** Все `import` на уровне модуля, не внутри функций.  
`from rdkit.Chem import Draw` один раз сверху файла.

## 4. Warnings

### 4.1. Подавление известных предупреждений
**Правило:** В `pyproject.toml` или `conftest.py` настроить `filterwarnings` для известных безвредных предупреждений:
- `X does not have valid feature names` → `ignore`
- `MorganGenerator` deprecation → `ignore`
- `numpy array shape deprecation` → `ignore`

Цель: **<50 warnings** при прогоне тестов (сейчас 504).

## 5. Docker

### 5.1. .dockerignore
**Правило:** Исключать из контекста сборки:
```
venv/
.git/
__pycache__/
*.pyc
data/*.tab
data/*.csv
data/*.zip
team_output/
logs/
*.db
users.json
promo/
```

### 5.2. Разделение установки и копирования
**Правило:** Сначала `COPY requirements.txt` + `pip install`, потом `COPY . .`.  
Это кеширует слой зависимостей при изменении кода.

## 6. Инфраструктура

### 6.1. .gitignore
**Правило:** Добавить:
- `usage.db` — SQLite БД использования
- `users.json` — хранилище пользователей
- `*.pkl`, `*.json` в `models/` — бинарники моделей уже в gitignore

### 6.2. pyproject.toml
**Правило:** Единый конфигурационный файл для:
- Метаданных проекта (name, version)
- Ruff (линтер + форматтер)
- Pytest (filterwarnings, testpaths)

```toml
[tool.ruff]
target-version = "py314"
line-length = 120

[tool.pytest.ini_options]
filterwarnings = ["ignore:.*X does not have valid feature names.*"]
```

### 6.3. requirements.txt
**Правило:** Все зависимости с минимальными версиями.  
Периодически запускать `pip list --outdated` для обновления.

## 7. Code Style

### 7.1. DRY (Don't Repeat Yourself)
**Правило:** Любой повторяющийся код длиннее 3 строк → функция/цикл.  
Особенно: блоки `if key in self.models` в `predict.py`, списки `prop_keys` в нескольких файлах.

### 7.2. Type hints
**Правило:** Все функции должны иметь аннотации типов для параметров и возврата.

### 7.3. Без комментариев в продакшн-коде
**Правило:** Код самодокументируемый. Комментарии — только для WHY, не для WHAT/HOW.

## 8. Производительность (целевые метрики)

| Метрика | Было | Сейчас | Цель | Статус |
|---------|------|--------|------|--------|
| Startup time (API) | 1.86s | ~1.7s | <0.3s | ⚠️ В процессе |
| Single predict (новый SMILES) | 176ms | ~26ms | <50ms | ✅ Достигнуто |
| Batch predict (среднее) | 38ms | ~32ms | <15ms | ⚠️ В процессе |
| RAM | 213 MB | ~200 MB | <150 MB | ⚠️ В процессе |
| Warnings в тестах | 504 | 1 | <50 | ✅ Достигнуто |

**Примечание:** Lazy loading моделей (коммит `1e1f55e`) значительно улучшил single predict время. Warnings снижены с 504 до 1 через filterwarnings в pyproject.toml.

## 9. Безопасность

### 9.1. Хранение секретов
**Правило:** Никогда не хранить секреты (токены, пароли, API ключи) в коде или конфигурационных файлах.

**Правильно:**
```python
# ✅ Использовать переменные окружения
import os
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("GITHUB_TOKEN not set in .env")
```

**Неправильно:**
```python
# ❌ Хардкод секретов
token = "ghp_abc123..."
```

### 9.2. Структура секретов
**Правило:** Секреты хранятся в `D:\AI\biotech\secrets\` (не коммитится в git).

```
D:\AI\biotech\secrets\
├── git_tkn.txt          # GitHub Personal Access Token
├── openai_key.txt       # OpenAI API Key
└── email_creds.txt      # Email credentials (user:password)
```

### 9.3. .env файлы
**Правило:** `.env` файлы добавлены в `.gitignore` и никогда не коммитятся.

**Шаблон:** `.env.example` содержит placeholder'ы, но не реальные секреты.

```env
# .env.example
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 9.4. Проверка перед коммитом
**Правило:** Перед каждым коммитом проверять:
- Нет ли секретов в staged файлах: `git diff --cached | grep -i "token\|password\|secret"`
- Нет ли `.env` файлов: `git status | grep "\.env"`
- Нет ли файлов из `secrets/`: `git status | grep "secrets/"`

### 9.5. Ротация секретов
**Правило:** Регулярно ротировать секреты (каждые 90 дней):
1. Отозвать старый токен через GitHub/провайдер
2. Сгенерировать новый
3. Обновить `.env` и `secrets/`
4. Удалить старые секреты

### 9.6. Чувствительная информация в git history
**Правило:** Если секрет попал в git history — немедленно:
1. Отозвать токен/пароль
2. Переписать git history через `git filter-repo`
3. Force push (если репозиторий публичный)
4. Уведомить команду

### 9.7. Минимальные права
**Правило:** Создавать токены с минимально необходимыми правами:
- GitHub: только `repo` scope (не `admin`, не `delete`)
- Email: app-specific password (не основной пароль)
- API ключи: только необходимые endpoints
