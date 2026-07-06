"""
Outreach Coordinator
Оркестратор всех агентов. Запуск по расписанию или вручную.

Стратегия:
- GitHub release: при каждом коммите в master (или раз в день)
- Статьи: раз в неделю (понедельник)
- Outreach инвесторам: раз в день (макс 5 писем)
- Follow-up: раз в неделю (пятница)
- Метрики + отчёт: раз в неделю (воскресенье)
"""
import sys
import time
import schedule
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Загрузка .env
from dotenv import load_dotenv
load_dotenv()

# Загрузка GitHub токена из файла (если не в .env)
import os
if not os.getenv("GITHUB_TOKEN"):
    token_file = Path(r"D:\AI\biotech\git_tkn.txt")
    if token_file.exists():
        os.environ["GITHUB_TOKEN"] = token_file.read_text().strip()

from tasks import (
    auto_release,
    auto_respond_to_issues,
    write_article,
    outreach_batch,
    followup_batch,
    collect_metrics,
    send_weekly_report,
)


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


def run_github_release():
    """Запуск: GitHub release"""
    log("Running: GitHub auto-release")
    try:
        auto_release()
    except Exception as e:
        log(f"GitHub release failed: {e}")


def run_respond_issues():
    """Запуск: Автоответы на issues"""
    log("Running: Auto-respond to issues")
    try:
        auto_respond_to_issues()
    except Exception as e:
        log(f"Issue response failed: {e}")


def run_write_article():
    """Запуск: Генерация статьи"""
    log("Running: Write article")
    try:
        result = write_article()
        if result:
            log(f"Article generated: {result['topic']}")
        else:
            log("No new topics to write")
    except Exception as e:
        log(f"Article generation failed: {e}")


def run_outreach():
    """Запуск: Outreach инвесторам"""
    log("Running: Investor outreach (max 5)")
    try:
        sent = outreach_batch(max_emails=5)
        log(f"Outreach complete: {sent} emails sent")
    except Exception as e:
        log(f"Outreach failed: {e}")


def run_followup():
    """Запуск: Follow-up инвесторам"""
    log("Running: Investor follow-up")
    try:
        sent = followup_batch(days_since=7, max_emails=5)
        log(f"Follow-up complete: {sent} emails sent")
    except Exception as e:
        log(f"Follow-up failed: {e}")


def run_metrics():
    """Запуск: Сбор метрик и отчёт"""
    log("Running: Weekly metrics report")
    try:
        send_weekly_report()
    except Exception as e:
        log(f"Metrics report failed: {e}")


def run_all():
    """Запуск всех задач (для ручного запуска)"""
    log("=" * 50)
    log("Running ALL tasks")
    log("=" * 50)
    run_github_release()
    run_respond_issues()
    run_write_article()
    run_outreach()
    run_followup()
    run_metrics()
    log("=" * 50)
    log("All tasks complete")
    log("=" * 50)


def setup_schedule():
    """Настройка расписания"""
    log("Setting up schedule...")

    # GitHub: каждый день в 10:00
    schedule.every().day.at("10:00").do(run_github_release)
    schedule.every().day.at("10:05").do(run_respond_issues)

    # Статьи: понедельник в 09:00
    schedule.every().monday.at("09:00").do(run_write_article)

    # Outreach: каждый день в 11:00 (кроме выходных)
    schedule.every().monday.at("11:00").do(run_outreach)
    schedule.every().tuesday.at("11:00").do(run_outreach)
    schedule.every().wednesday.at("11:00").do(run_outreach)
    schedule.every().thursday.at("11:00").do(run_outreach)
    schedule.every().friday.at("11:00").do(run_outreach)

    # Follow-up: пятница в 14:00
    schedule.every().friday.at("14:00").do(run_followup)

    # Метрики: воскресенье в 20:00
    schedule.every().sunday.at("20:00").do(run_metrics)

    log("Schedule configured:")
    log("  - GitHub release: daily 10:00")
    log("  - Issue responses: daily 10:05")
    log("  - Article writing: Monday 09:00")
    log("  - Investor outreach: Mon-Fri 11:00")
    log("  - Investor follow-up: Friday 14:00")
    log("  - Weekly metrics: Sunday 20:00")


def run_scheduled():
    """Запуск в режиме планировщика (бесконечный цикл)"""
    setup_schedule()
    log("Coordinator started. Press Ctrl+C to stop.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log("Coordinator stopped by user")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Outreach Coordinator")
    parser.add_argument(
        "command",
        choices=["run", "schedule", "release", "respond", "article", "outreach", "followup", "metrics", "all"],
        help="Command to run",
    )
    args = parser.parse_args()

    commands = {
        "release": run_github_release,
        "respond": run_respond_issues,
        "article": run_write_article,
        "outreach": run_outreach,
        "followup": run_followup,
        "metrics": run_metrics,
        "all": run_all,
        "run": run_all,
        "schedule": run_scheduled,
    }

    commands[args.command]()
