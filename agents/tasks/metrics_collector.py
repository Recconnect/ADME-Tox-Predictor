"""
Metrics Collector Task
Сбор метрик GitHub, email, и генерация еженедельных отчётов
"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import GitHubClient, EmailSender


def collect_metrics():
    """Сбор всех метрик и сохранение в SQLite"""
    print("[metrics_collector] Collecting metrics...")

    github = GitHubClient()
    db_path = Path(__file__).resolve().parents[1] / "data" / "metrics.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Инициализация БД
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collected_at REAL NOT NULL,
            stars INTEGER,
            forks INTEGER,
            watchers INTEGER,
            open_issues INTEGER,
            contributors INTEGER,
            emails_sent_7d INTEGER,
            emails_sent_30d INTEGER
        )
    """)
    conn.commit()

    # Сбор GitHub метрик
    gh_metrics = github.get_all_metrics()
    print(f"[metrics_collector] GitHub: {gh_metrics['stars']} stars, {gh_metrics['forks']} forks")

    # Сбор email метрик
    try:
        email_sender = EmailSender()
        emails_7d = email_sender.get_sent_count(days=7)
        emails_30d = email_sender.get_sent_count(days=30)
    except Exception:
        emails_7d = 0
        emails_30d = 0

    # Сохранение
    conn.execute(
        """INSERT INTO metrics 
           (collected_at, stars, forks, watchers, open_issues, contributors, emails_sent_7d, emails_sent_30d)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now().timestamp(),
            gh_metrics["stars"],
            gh_metrics["forks"],
            gh_metrics["watchers"],
            gh_metrics["open_issues"],
            gh_metrics["contributors"],
            emails_7d,
            emails_30d,
        ),
    )
    conn.commit()
    conn.close()

    print(f"[metrics_collector] Metrics saved. Emails sent: {emails_7d} (7d), {emails_30d} (30d)")

    return {
        "github": gh_metrics,
        "emails_7d": emails_7d,
        "emails_30d": emails_30d,
    }


def generate_weekly_report():
    """Генерация еженедельного отчёта"""
    print("[metrics_collector] Generating weekly report...")

    db_path = Path(__file__).resolve().parents[1] / "data" / "metrics.db"
    if not db_path.exists():
        print("[metrics_collector] No metrics data yet")
        return None

    conn = sqlite3.connect(str(db_path))

    # Получаем последнюю запись
    latest = conn.execute(
        "SELECT * FROM metrics ORDER BY collected_at DESC LIMIT 1"
    ).fetchone()

    # Получаем запись за неделю до
    week_ago = (datetime.now() - timedelta(days=7)).timestamp()
    prev = conn.execute(
        "SELECT * FROM metrics WHERE collected_at <= ? ORDER BY collected_at DESC LIMIT 1",
        (week_ago,),
    ).fetchone()

    conn.close()

    if not latest:
        print("[metrics_collector] No metrics data")
        return None

    # Вычисляем изменения
    if prev:
        stars_delta = latest[2] - prev[2]
        forks_delta = latest[3] - prev[3]
    else:
        stars_delta = 0
        forks_delta = 0

    report = f"""ADMETox.AI — Weekly Outreach Report
{'=' * 40}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

GitHub:
  Stars: {latest[2]} ({'+' if stars_delta >= 0 else ''}{stars_delta} this week)
  Forks: {latest[3]} ({'+' if forks_delta >= 0 else ''}{forks_delta} this week)
  Watchers: {latest[4]}
  Open Issues: {latest[5]}
  Contributors: {latest[6]}

Email Outreach:
  Sent (7 days): {latest[7]}
  Sent (30 days): {latest[8]}

{'=' * 40}
Next report: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
"""

    print(report)
    return report


def send_weekly_report():
    """Сбор метрик и отправка отчёта на email"""
    print("[metrics_collector] Collecting metrics and sending report...")

    collect_metrics()
    report = generate_weekly_report()

    if not report:
        print("[metrics_collector] No report to send")
        return

    try:
        email_sender = EmailSender()
        email_sender.send(
            to_email="your_email@example.com",
            subject=f"ADMETox.AI — Weekly Report ({datetime.now().strftime('%Y-%m-%d')})",
            body=report,
        )
        print("[metrics_collector] Report sent to your_email@example.com")
    except Exception as e:
        print(f"[metrics_collector] Failed to send report: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Metrics collection tasks")
    parser.add_argument("task", choices=["collect", "report", "send"], help="Task to run")
    args = parser.parse_args()

    if args.task == "collect":
        collect_metrics()
    elif args.task == "report":
        generate_weekly_report()
    elif args.task == "send":
        send_weekly_report()
