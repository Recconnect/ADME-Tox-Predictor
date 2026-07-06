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
│   └── metrics_collector.py # Сбор метрик, еженедельные отчёты
│
├── data/                    # Базы данных
│   ├── investors.csv       # Список инвесторов
│   ├── metrics.db          # SQLite для метрик
│   ├── email_log.db        # Лог отправленных писем
│   └── articles/           # Сгенерированные статьи
│
├── coordinator.py          # Оркестратор (расписание)
├── config.yml              # Конфигурация
├── .env                    # Секреты (не коммитится)
└── requirements.txt        # Зависимости
```

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

### Ручной запуск задач

```bash
# GitHub release (при коммите в master)
python coordinator.py release

# Автоответы на issues
python coordinator.py respond

# Генерация статьи
python coordinator.py article

# Outreach инвесторам (макс 5 писем)
python coordinator.py outreach

# Follow-up инвесторам (>7 дней без ответа)
python coordinator.py followup

# Сбор метрик и отчёт
python coordinator.py metrics

# Запуск всех задач
python coordinator.py all
```

### Автоматический запуск (расписание)

```bash
# Запуск в режиме планировщика (бесконечный цикл)
python coordinator.py schedule
```

**Расписание:**
- GitHub release: ежедневно в 10:00
- Автоответы на issues: ежедневно в 10:05
- Генерация статьи: понедельник в 09:00
- Outreach инвесторам: пн-пт в 11:00 (макс 5 писем/день)
- Follow-up инвесторам: пятница в 14:00
- Еженедельный отчёт: воскресенье в 20:00

### Запуск через cron (Linux/Mac)

```bash
# Редактировать crontab
crontab -e

# Добавить задачи:
# GitHub release: каждый день в 10:00
0 10 * * * cd /path/to/agents && python coordinator.py release

# Outreach: пн-пт в 11:00
0 11 * * 1-5 cd /path/to/agents && python coordinator.py outreach

# Еженедельный отчёт: воскресенье в 20:00
0 20 * * 0 cd /path/to/agents && python coordinator.py metrics
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
