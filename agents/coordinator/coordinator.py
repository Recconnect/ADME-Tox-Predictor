"""Coordinator agent - оркестратор всех агентов"""
import sys
from pathlib import Path
from datetime import datetime
import schedule
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tasks import (
    auto_release, auto_respond_to_issues,
    write_article, list_articles,
    outreach_batch, followup_batch, investor_status,
    collect_metrics, generate_weekly_report, send_weekly_report,
    collect_all_feedback,
    track_conferences,
    publish_social_posts
)


def run_daily_tasks():
    """Ежедневные задачи"""
    print(f"\n{'='*60}")
    print(f"[coordinator] Running daily tasks - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    # 1. GitHub release (при коммитах)
    print("\n[coordinator] 1. Checking GitHub for new commits...")
    auto_release()
    
    # 2. GitHub issue responses
    print("\n[coordinator] 2. Responding to GitHub issues...")
    auto_respond_to_issues()
    
    # 3. Feedback collection
    print("\n[coordinator] 3. Collecting feedback...")
    collect_all_feedback()
    
    # 4. Conference tracking
    print("\n[coordinator] 4. Tracking conferences...")
    track_conferences()


def run_weekly_tasks():
    """Еженедельные задачи"""
    print(f"\n{'='*60}")
    print(f"[coordinator] Running weekly tasks - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    # 1. Write article
    print("\n[coordinator] 1. Writing article...")
    write_article()
    
    # 2. Investor outreach
    print("\n[coordinator] 2. Investor outreach...")
    outreach_batch()
    
    # 3. Investor follow-up
    print("\n[coordinator] 3. Investor follow-up...")
    followup_batch()
    
    # 4. Social media publishing
    print("\n[coordinator] 4. Publishing social media posts...")
    publish_social_posts()
    
    # 5. Metrics report
    print("\n[coordinator] 5. Generating metrics report...")
    generate_weekly_report()


def run_all_tasks():
    """Запуск всех задач"""
    print("\n[coordinator] Running ALL tasks...")
    run_daily_tasks()
    run_weekly_tasks()


def setup_schedule():
    """Настройка расписания"""
    print("[coordinator] Setting up schedule...")
    
    # Ежедневные задачи - каждый день в 10:00
    schedule.every().day.at("10:00").do(run_daily_tasks)
    
    # Еженедельные задачи - каждый понедельник в 09:00
    schedule.every().monday.at("09:00").do(run_weekly_tasks)
    
    print("[coordinator] Schedule configured:")
    print("  - Daily tasks: every day at 10:00")
    print("  - Weekly tasks: every Monday at 09:00")
    print("\n[coordinator] Scheduler is running. Press Ctrl+C to stop.")


def run_scheduler():
    """Запуск планировщика"""
    setup_schedule()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[coordinator] Scheduler stopped by user")


def show_status():
    """Показать статус всех агентов"""
    print("\n[coordinator] Agent Status Report")
    print("="*60)
    
    # GitHub status
    print("\n[GitHub Agent]")
    print("  - Auto-release: enabled")
    print("  - Issue responses: enabled")
    
    # Content agent
    print("\n[Content Agent]")
    articles = list_articles()
    print(f"  - Articles generated: {len(articles)}")
    
    # Investor agent
    print("\n[Investor Agent]")
    investor_status()
    
    # Feedback agent
    print("\n[Feedback Agent]")
    from tasks.feedback_collector import FeedbackCollector
    fc = FeedbackCollector()
    stats = fc.get_stats(7)
    print(f"  - Feedback collected (7 days): {stats['total']}")
    print(f"  - By type: {stats['by_type']}")
    print(f"  - By status: {stats['by_status']}")
    
    # Conference agent
    print("\n[Conference Agent]")
    from tasks.conference_tracker import ConferenceTracker
    ct = ConferenceTracker()
    stats = ct.get_stats()
    print(f"  - Total conferences: {stats['total']}")
    print(f"  - Upcoming (90 days): {stats['upcoming_90d']}")
    print(f"  - Deadlines (30 days): {stats['deadlines_30d']}")
    
    # Social media agent
    print("\n[Social Media Agent]")
    from tasks.social_publisher import SocialMediaPublisher
    sp = SocialMediaPublisher()
    stats = sp.get_stats(30)
    print(f"  - Posts (30 days): {stats['total']}")
    print(f"  - By platform: {stats['by_platform']}")
    print(f"  - By status: {stats['by_status']}")
    
    # Metrics agent
    print("\n[Metrics Agent]")
    print("  - Weekly reports: enabled")
    print("  - Email notifications: configured")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Outreach Coordinator")
    parser.add_argument('command', choices=['daily', 'weekly', 'all', 'schedule', 'status'],
                       help='Command to run')
    
    args = parser.parse_args()
    
    if args.command == 'daily':
        run_daily_tasks()
    elif args.command == 'weekly':
        run_weekly_tasks()
    elif args.command == 'all':
        run_all_tasks()
    elif args.command == 'schedule':
        run_scheduler()
    elif args.command == 'status':
        show_status()
