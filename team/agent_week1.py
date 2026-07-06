"""
Week 1 Agent — генерирует "Действия прямо сейчас" из GTM-плана.

Запуск:
    python -m team.agent_week1            # все документы
    python -m team.agent_week1 --chemrar  # только письмо ChemRar
    python -m team.agent_week1 --grant    # только заявка Старт-1
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from team.config import OUTPUT_DIR

WEEK1_DIR = OUTPUT_DIR / "week1"
WEEK1_DIR.mkdir(parents=True, exist_ok=True)


def generate_chemrar_pitch() -> str:
    content = r"""# ChemRar — Commercial Proposal

**От:** ADMETox.AI (AI-предсказание ADME/Tox свойств)
**Дата:** 2026-07-06
**Тип:** Холодный контакт -> Пилотный проект

---

## Сопроводительное письмо

**Тема:** AI-скрининг ADME/Tox для вашего пайплайна lead optimization

Уважаемый [Имя],

Мы разработали AI-модель, предсказывающую растворимость, Caco-2 проницаемость
и hERG токсичность по SMILES-формуле за <1 секунды, без синтеза.

**Почему это важно для ChemRar:**
- Вы проводите hit-to-lead и lead optimization — самый затратный этап R&D
- 90% кандидатов отсеиваются на ADME/Tox
- Наша модель сокращает количество синтезируемых молекул в 5-10 раз
- Метрики: R² 0.806 (solubility), AUC 0.932 (Caco-2), AUC 0.845 (hERG)

**Что предлагаем:**
Бесплатный пилот на 30 дней: 100 ваших молекул — мы предсказываем ADME/Tox
и сравниваем с вашими экспериментальными данными.

Готовы обсудить на 15-минутном звонке?

С наилучшими пожеланиями,
[Ваше имя]
ADMETox.AI

---

## Value Proposition

| Параметр | Значение |
|----------|----------|
| Компания | ChemRar (Москва), 500+ сотрудников |
| Фокус | Drug discovery, hit ID, lead optimization |
| Потребность | Быстрый ADME/Tox скрининг на ранних стадиях |
| Бюджет на in silico | $50-200K/год |

**Экономический эффект:**

| Показатель | Без нас | С нами |
|------------|---------|--------|
| Молекул синтезировать | 1000 | 100-200 |
| Стоимость синтеза | $2-5M | $200-500K |
| Время lead optimization | 4-5 лет | 1.5-2 года |
| Стоимость подписки | — | $10-50K/год |

## План outreach

| День | Действие |
|------|----------|
| 1 | Найти контакт R&D директора (LinkedIn + Pharmaprojects) |
| 2 | Отправить письмо |
| 5 | Follow-up LinkedIn |
| 7 | Звонок в приёмную |
| 10 | Demo-call (15 мин, показать UI) |
| 14 | Отправить proposal |
| 21 | Согласование NDA |
| 30 | Старт пилота |
"""
    path = WEEK1_DIR / "chemrar_pitch.md"
    path.write_text(content, encoding="utf-8")
    print(f"  OK -> {path}")
    return str(path)


def generate_start1_application() -> str:
    content = r"""# Заявка Старт-1 (Фонд содействия инновациям)

**Программа:** Старт-1 (НИОКР)
**Сумма:** до 4 млн руб (безвозвратное финансирование)
**Тема:** AI-платформа предсказания ADME/Tox свойств для drug discovery

---

## О программе

| Параметр | Значение |
|----------|----------|
| Организация | Фонд содействия инновациям (Фонд Бортника) |
| Макс. сумма | 4 000 000 руб |
| Тип | Безвозвратный грант (70% на НИОКР) |
| Срок | 12 месяцев |
| Сайт | https://fasie.ru/programs/programma-start/ |

## Аннотация

AI-модель (LightGBM + RDKit) предсказывает ADME/Tox свойства по SMILES.
MVP готов: 3 модели обучены (R² 0.806, AUC 0.932, AUC 0.845).
Валидирована на 10 известных препаратах. Целевые клиенты — российские CRO.

## Календарный план

| Мес | Работы | Результат | Бюджет |
|-----|--------|-----------|--------|
| 1 | Расширение hERG (ChEMBL до 3000+) | Улучшенный датасет | 200K |
| 2-3 | LogD7.4 + Pgp модели | 2 новые модели | 600K |
| 4-5 | FastAPI + Docker | REST API, контейнеризация | 700K |
| 6-7 | Расширение до 5-6 свойств | CYP450, Bioavail | 800K |
| 8-9 | Внешняя валидация на CRO | 2 отчёта | 800K |
| 10-11 | Enterprise-функции, GNN | Enterprise версия | 600K |
| 12 | Пилот с 2 CRO | Коммерческие пилоты | 300K |
| **Итого** | | | **4,000K** |

## Бюджет

| Статья | Сумма (руб) |
|--------|-------------|
| ML Engineer (12 мес) | 1,200,000 |
| Bioengineer (6 мес) | 360,000 |
| Product Manager | 600,000 |
| Облачные вычисления | 240,000 |
| Закупка данных | 100,000 |
| Оборудование (2 ПК) | 500,000 |
| Внешняя экспертиза | 400,000 |
| Регистрация ПО | 200,000 |
| Конференции | 200,000 |
| Накладные (10%) | 200,000 |
| **Итого** | **4,000,000** |

## Чек-лист подачи

- [ ] Зарегистрировать ИП/ООО (ОКВЭД 72.19)
- [ ] Получить ЭЦП
- [ ] Зарегистрироваться на fasie.ru
- [ ] Заполнить форму проекта
- [ ] Приложить презентацию (5-7 слайдов)
- [ ] Приложить резюме команды
- [ ] Приложить календарный план
- [ ] Приложить смету
- [ ] Отправить до дедлайна

**Deadline:** уточнить на https://fasie.ru/programs/programma-start/
"""
    path = WEEK1_DIR / "start1_application.md"
    path.write_text(content, encoding="utf-8")
    print(f"  OK -> {path}")
    return str(path)


def generate_both():
    print("=" * 65)
    print("  Week 1 Actions — генерация документов")
    print("=" * 65)
    generate_chemrar_pitch()
    generate_start1_application()
    print(f"\n  Все документы: {WEEK1_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    if "--chemrar" in sys.argv:
        generate_chemrar_pitch()
    elif "--grant" in sys.argv:
        generate_start1_application()
    else:
        generate_both()
