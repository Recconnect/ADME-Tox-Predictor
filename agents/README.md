# ADMETox.AI — Outreach Agents

Репозиторий: https://github.com/Recconnect/ADME-Tox-Predictor

Автоматизированная система для продвижения продукта и привлечения инвесторов.

## Архитектура

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
│   ├── metrics_collector.py # Сбор метрик, еженедельные отчёты
│   ├── feedback_collector.py # Сбор обратной связи из GitHub/email
│   ├── conference_tracker.py # Отслеживание конференций
│   └── social_publisher.py  # Публикация в соцсети (LinkedIn, Twitter)
│
├── coordinator/             # Оркестратор всех агентов
│   └── coordinator.py      # Расписание и запуск задач
│
├── data/                    # Базы данных
│   ├── investors.csv       # 66 инвесторов (biotech/healthtech)
│   ├── metrics.db          # SQLite для метрик
│   ├── email_log.db        # Лог отправленных писем
│   ├── feedback.db         # Обратная связь
│   ├── conferences.db      # 10 конференций
│   ├── social_posts.db     # Посты для соцсетей
│   └── articles/           # Сгенерированные статьи
│
├── config.yml              # Конфигурация
├── .env                    # Секреты (не коммитится)
└── requirements.txt        # Зависимости
```

## Агенты

### 1. GitHub Agent
- **Автогенерация changelog** при коммитах в master
- **Автоответы на issues** через LLM
- **Создание releases** с автоматическим версионированием

### 2. Content Agent
- **Генерация статей** через LLM (GPT-4o-mini)
- **6 тем** для статей (biotech, AI, drug discovery)
- **Публикация** на Medium, Habr, VC.ru

### 3. Investor Agent
- **66 инвесторов** в базе (biotech/healthtech VCs и angels)
- **Персонализированные письма** через LLM
- **Follow-up** через 7/14/30 дней
- **Лимит**: 5 писем/день (анти-спам)

### 4. Feedback Agent
- **Сбор обратной связи** из GitHub issues
- **Классификация**: bug, feature request, question, investor interest
- **Приоритизация**: high/medium/low
- **Статистика** по типам и статусам

### 5. Conference Agent
- **10 конференций** в базе (Bio-IT World, MLDD, ACS и др.)
- **Отслеживание дедлайнов** для CFP
- **Напоминания** о предстоящих конференциях
- **Релевантность**: drug discovery, AI, biotech

### 6. Social Media Agent
- **Генерация постов** для LinkedIn, Twitter, Medium
- **Персонализация** под каждую платформу
- **Хэштеги** и call-to-action
- **Статистика** публикаций

### 7. Metrics Agent
- **Сбор метрик** GitHub (stars, forks, issues)
- **Email статистика** (отправленные/открытые)
- **Еженедельные отчёты** на email
- **SQLite** для хранения метрик

## Установка

```bash
cd agents

# Установить зависимости
pip install -r requirements.txt

# Создать .env из шаблона
cp .env.example .env

# Отредактировать .env:
# - OPENAI_API_KEY: получить на https://platform.openai.com/api-keys
# - GITHUB_TOKEN: уже заполнен (your_github_token_here)
# - EMAIL_PASSWORD: пароль от your_email@example.com (или app-specific password)
```

## Использование

### Координатор (оркестратор всех агентов)

```bash
# Показать статус всех агентов
python -m coordinator.coordinator status

# Запустить ежедневные задачи (GitHub, feedback, conferences)
python -m coordinator.coordinator daily

# Запустить еженедельные задачи (articles, outreach, social)
python -m coordinator.coordinator weekly

# Запустить все задачи
python -m coordinator.coordinator all

# Запустить планировщик (постоянная работа)
python -m coordinator.coordinator schedule
```

### Ручной запуск отдельных агентов

```bash
# GitHub release (при коммите в master)
python -m tasks.github_release

# Автоответы на issues
python -m tasks.github_respond

# Генерация статьи
python -m tasks.content_writer

# Outreach инвесторам (макс 5 писем)
python -m tasks.investor_outreach

# Follow-up инвесторам (>7 дней без ответа)
python -m tasks.investor_followup

# Сбор обратной связи
python -m tasks.feedback_collector

# Отслеживание конференций
python -m tasks.conference_tracker

# Публикация в соцсети
python -m tasks.social_publisher

# Сбор метрик и отчёт
python -m tasks.metrics_collector
```

### Автоматический запуск (расписание)

```bash
# Запуск в режиме планировщика (бесконечный цикл)
python -m coordinator.coordinator schedule
```

**Расписание:**
- **Ежедневно в 10:00**: GitHub release, автоответы на issues, сбор feedback, отслеживание конференций
- **Еженедельно (понедельник в 09:00)**: генерация статьи, outreach инвесторам, follow-up, публикация в соцсети, отчёт по метрикам

### Запуск через cron (Linux/Mac)

```bash
# Редактировать crontab
crontab -e

# Добавить задачи:
# Ежедневные задачи: каждый день в 10:00
0 10 * * * cd /path/to/agents && python -m coordinator.coordinator daily

# Еженедельные задачи: каждый понедельник в 09:00
0 9 * * 1 cd /path/to/agents && python -m coordinator.coordinator weekly
```

## Конфигурация

### `.env` (секреты)

```env
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
EMAIL_USER=your_email@example.com
EMAIL_PASSWORD=your_password
```

### `config.yml` (опционально)

Можно настроить через `config.yml`, но по умолчанию используются значения из `.env`.

## Бюджет

| Сервис | Стоимость | Примечания |
|--------|-----------|------------|
| OpenAI API (GPT-4o-mini) | ~$5/мес | ~16M токенов при умеренном использовании |
| GitHub API | Бесплатно | Лимит 5000 запросов/час |
| Email (Яндекс.Почта) | Бесплатно | Лимит 500 писем/день |
| **Итого** | **~$5/мес** | |

## Безопасность

- Все API ключи хранятся в `.env` (не коммитится)
- GitHub токен с минимальными правами (`repo`)
- Email пароль через app-specific password (рекомендуется)
- Максимум 5 писем/день (анти-спам)
- Все исходящие письма содержат `[Unsubscribe]` ссылку

## Мониторинг

### Логи

Все задачи логируют в stdout. Для сохранения в файл:

```bash
python coordinator.py schedule >> agents/logs/coordinator.log 2>&1
```

### Метрики

- `data/metrics.db` — SQLite с метриками (звёзды, форки, письма)
- `data/email_log.db` — лог отправленных писем
- Еженедельный отчёт отправляется на `your_email@example.com`

### Проверка статуса

```bash
# Статус по инвесторам
python -m tasks.investor_outreach status

# Список сгенерированных статей
python -m tasks.content_writer list
```

## Разработка

### Добавление новой задачи

1. Создать файл в `tasks/` (например, `tasks/new_task.py`)
2. Реализовать функцию задачи
3. Добавить в `tasks/__init__.py`
4. Добавить в `coordinator.py` (расписание + команда)

### Переключение LLM провайдера

В `core/llm.py` можно переключиться на другой провайдер:

```python
# Ollama (локально, бесплатно)
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# DashScope (Qwen)
import dashscope
dashscope.api_key = "your_key"
```

## Troubleshooting

### Ошибка: "OPENAI_API_KEY not set"

Убедитесь, что `.env` файл создан и содержит `OPENAI_API_KEY`.

### Ошибка: "EMAIL_PASSWORD not set"

Для Яндекс.Почты нужен app-specific password:
1. Зайти на https://id.yandex.ru/security
2. Создать "Пароль для приложений"
3. Использовать его в `.env`

### Ошибка: "GITHUB_TOKEN not set"

Токен уже в `.env.example`. Убедитесь, что `.env` создан из шаблона.

### Письма попадают в спам

- Использовать app-specific password (не основной пароль)
- Настроить SPF/DKIM для домена cdo.ru
- Не превышать лимит 5 писем/день

## Лицензия

Internal use only. Не распространять.
