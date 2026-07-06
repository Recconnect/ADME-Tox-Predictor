"""
Investor Outreach Task
Email outreach потенциальным инвесторам через LLM + SMTP
"""
import sys
import csv
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import LLMClient, EmailSender


PRODUCT_INFO = """ADMETox.AI — AI-powered ADME/Tox screening platform for drug discovery.

Key features:
- Predicts solubility, Caco-2 permeability, hERG toxicity, lipophilicity, P-gp inhibition
- 10 LightGBM models trained on public datasets
- Results in seconds vs weeks for traditional methods
- 90% cost reduction compared to experimental screening
- Production-ready: Docker, CI/CD, 69 automated tests
- Open source core with commercial API

Target market: $45B drug discovery market, ADME/Tox segment ~$8B
Traction: Models trained, API operational, landing page live
Team: Solo founder with ML + pharma domain expertise"""


def load_investors(csv_path=None):
    """Загрузка списка инвесторов из CSV"""
    if csv_path is None:
        csv_path = Path(__file__).resolve().parents[1] / "data" / "investors.csv"

    if not csv_path.exists():
        print(f"[investor_outreach] Investors CSV not found: {csv_path}")
        return []

    investors = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            investors.append(row)
    return investors


def save_investors(investors, csv_path=None):
    """Сохранение обновлённого списка инвесторов"""
    if csv_path is None:
        csv_path = Path(__file__).resolve().parents[1] / "data" / "investors.csv"

    if not investors:
        return

    fieldnames = investors[0].keys()
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(investors)


def outreach_batch(max_emails=5, dry_run=False):
    """Отправка batch писем инвесторам"""
    print(f"[investor_outreach] Starting outreach batch (max {max_emails} emails)...")

    investors = load_investors()
    if not investors:
        print("[investor_outreach] No investors found")
        return

    llm = LLMClient()
    email_sender = EmailSender()

    # Фильтруем инвесторов для контакта
    eligible = [
        inv for inv in investors
        if inv.get("status", "") in ("", "new", "pending")
        and inv.get("email", "")
    ]

    if not eligible:
        print("[investor_outreach] No eligible investors to contact")
        return

    # Ограничиваем количество
    batch = eligible[:max_emails]
    sent = 0

    for investor in batch:
        name = investor.get("name", "Investor")
        fund = investor.get("fund", "")
        email = investor["email"]

        print(f"[investor_outreach] Generating email for {name} ({fund})...")

        # Генерируем персонализированное письмо
        email_body = llm.generate_investor_email(
            investor_name=name,
            fund_name=fund,
            product_info=PRODUCT_INFO,
        )

        subject = f"AI-Powered ADME/Tox Screening — {fund} Partnership Opportunity"

        if dry_run:
            print(f"[investor_outreach] DRY RUN - Would send to {email}:")
            print(f"  Subject: {subject}")
            print(f"  Body preview: {email_body[:200]}...")
        else:
            try:
                email_sender.send(email, subject, email_body)
                print(f"[investor_outreach] Sent to {email}")
                sent += 1

                # Обновляем статус
                investor["status"] = "contacted"
                investor["last_contact"] = datetime.now().isoformat()
                investor["email_subject"] = subject

            except Exception as e:
                print(f"[investor_outreach] Failed to send to {email}: {e}")
                investor["status"] = f"failed: {e}"

    # Сохраняем обновлённый список
    if not dry_run:
        save_investors(investors)
        print(f"[investor_outreach] Batch complete: {sent}/{len(batch)} sent")

    return sent


def followup_batch(days_since=7, max_emails=5, dry_run=False):
    """Follow-up письма для тех, кто не ответил"""
    print(f"[investor_outreach] Starting follow-up batch (>{days_since} days)...")

    investors = load_investors()
    llm = LLMClient()
    email_sender = EmailSender()

    cutoff = (datetime.now() - timedelta(days=days_since)).isoformat()

    eligible = [
        inv for inv in investors
        if inv.get("status") == "contacted"
        and inv.get("last_contact", "") < cutoff
        and inv.get("followup_count", "0") == "0"
    ]

    if not eligible:
        print("[investor_outreach] No investors need follow-up")
        return

    batch = eligible[:max_emails]
    sent = 0

    for investor in batch:
        name = investor.get("name", "Investor")
        email = investor["email"]

        subject = f"Re: AI-Powered ADME/Tox Screening — Follow-up"
        body = f"""Hi {name},

I wanted to follow up on my previous email about ADMETox.AI.

Quick reminder: we've built an AI platform that predicts ADME/Tox properties
(solubility, permeability, toxicity) in seconds, reducing screening costs by 90%.

Would you have 15 minutes this week for a quick call?

Best regards,
ADMETox.AI Team"""

        if dry_run:
            print(f"[investor_outreach] DRY RUN - Follow-up to {email}")
        else:
            try:
                email_sender.send(email, subject, body)
                investor["followup_count"] = str(int(investor.get("followup_count", "0")) + 1)
                investor["last_contact"] = datetime.now().isoformat()
                sent += 1
                print(f"[investor_outreach] Follow-up sent to {email}")
            except Exception as e:
                print(f"[investor_outreach] Follow-up failed for {email}: {e}")

    if not dry_run:
        save_investors(investors)
        print(f"[investor_outreach] Follow-up complete: {sent}/{len(batch)} sent")

    return sent


def investor_status():
    """Статус по инвесторам"""
    investors = load_investors()
    if not investors:
        print("[investor_outreach] No investors in database")
        return

    statuses = {}
    for inv in investors:
        s = inv.get("status", "new")
        statuses[s] = statuses.get(s, 0) + 1

    print(f"[investor_outreach] Total investors: {len(investors)}")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Investor outreach tasks")
    parser.add_argument("task", choices=["outreach", "followup", "status"], help="Task to run")
    parser.add_argument("--max", type=int, default=5, help="Max emails per batch")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send emails")
    parser.add_argument("--days", type=int, default=7, help="Days since last contact for follow-up")
    args = parser.parse_args()

    if args.task == "outreach":
        outreach_batch(max_emails=args.max, dry_run=args.dry_run)
    elif args.task == "followup":
        followup_batch(days_since=args.days, max_emails=args.max, dry_run=args.dry_run)
    elif args.task == "status":
        investor_status()
