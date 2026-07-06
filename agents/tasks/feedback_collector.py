"""Feedback collector agent - собирает обратную связь из разных каналов"""
import sys
from pathlib import Path
from datetime import datetime
import sqlite3
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.github_client import GitHubClient


class FeedbackCollector:
    """Сбор обратной связи из GitHub, email и других каналов"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "feedback.db"
        self._init_db()
        self.github = GitHubClient()
    
    def _init_db(self):
        """Инициализация базы данных для feedback"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                author TEXT,
                url TEXT,
                collected_at REAL NOT NULL,
                status TEXT DEFAULT 'new',
                priority TEXT DEFAULT 'medium',
                response TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_collected_at ON feedback(collected_at)
        """)
        conn.commit()
        conn.close()
    
    def collect_from_github(self):
        """Сбор feedback из GitHub issues"""
        print("[feedback_collector] Collecting from GitHub...")
        
        issues = self.github.get_issues(state="all", limit=100)
        new_count = 0
        
        conn = sqlite3.connect(str(self.db_path))
        
        for issue in issues:
            # Проверяем, есть ли уже этот issue
            existing = conn.execute(
                "SELECT id FROM feedback WHERE source='github' AND url=?",
                (issue['url'],)
            ).fetchone()
            
            if not existing:
                # Определяем тип feedback
                feedback_type = self._classify_issue(issue)
                
                conn.execute(
                    """INSERT INTO feedback 
                       (source, type, title, content, author, url, collected_at, status, priority)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        "github",
                        feedback_type,
                        issue['title'],
                        issue['body'],
                        issue['author'],
                        issue['url'],
                        datetime.now().timestamp(),
                        "new",
                        self._determine_priority(issue)
                    )
                )
                new_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"[feedback_collector] Collected {new_count} new items from GitHub")
        return new_count
    
    def collect_from_email(self, email_log_db=None):
        """Сбор feedback из email логов (ответы на письма)"""
        # TODO: Implement email reply checking via IMAP
        # For now, just check email_log.db for any responses
        print("[feedback_collector] Email feedback collection not yet implemented")
        return 0
    
    def _classify_issue(self, issue):
        """Классификация issue по типу"""
        title = issue['title'].lower()
        body = (issue['body'] or '').lower()
        
        if any(word in title or word in body for word in ['bug', 'error', 'crash', 'fail']):
            return 'bug'
        elif any(word in title or word in body for word in ['feature', 'request', 'add', 'support']):
            return 'feature_request'
        elif any(word in title or word in body for word in ['question', 'how to', 'help']):
            return 'question'
        elif any(word in title or word in body for word in ['investor', 'investment', 'partnership']):
            return 'investor_interest'
        elif any(word in title or word in body for word in ['conference', 'talk', 'presentation']):
            return 'conference_invitation'
        else:
            return 'general'
    
    def _determine_priority(self, issue):
        """Определение приоритета issue"""
        labels = issue.get('labels', [])
        
        if 'critical' in labels or 'bug' in labels:
            return 'high'
        elif 'enhancement' in labels or 'feature' in labels:
            return 'medium'
        else:
            return 'low'
    
    def get_new_feedback(self, limit=50):
        """Получить новый feedback"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        rows = conn.execute(
            "SELECT * FROM feedback WHERE status='new' ORDER BY collected_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def mark_as_processed(self, feedback_id, response=None):
        """Отметить feedback как обработанный"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "UPDATE feedback SET status='processed', response=?, processed_at=? WHERE id=?",
            (response, datetime.now().timestamp(), feedback_id)
        )
        conn.commit()
        conn.close()
    
    def get_stats(self, days=7):
        """Статистика по feedback"""
        conn = sqlite3.connect(str(self.db_path))
        cutoff = datetime.now().timestamp() - days * 86400
        
        stats = {
            'total': conn.execute(
                "SELECT COUNT(*) FROM feedback WHERE collected_at >= ?", (cutoff,)
            ).fetchone()[0],
            'by_type': {},
            'by_status': {},
            'by_priority': {}
        }
        
        # By type
        for row in conn.execute(
            "SELECT type, COUNT(*) as cnt FROM feedback WHERE collected_at >= ? GROUP BY type",
            (cutoff,)
        ).fetchall():
            stats['by_type'][row[0]] = row[1]
        
        # By status
        for row in conn.execute(
            "SELECT status, COUNT(*) as cnt FROM feedback WHERE collected_at >= ? GROUP BY status",
            (cutoff,)
        ).fetchall():
            stats['by_status'][row[0]] = row[1]
        
        # By priority
        for row in conn.execute(
            "SELECT priority, COUNT(*) as cnt FROM feedback WHERE collected_at >= ? GROUP BY priority",
            (cutoff,)
        ).fetchall():
            stats['by_priority'][row[0]] = row[1]
        
        conn.close()
        return stats


def collect_all_feedback():
    """Сбор feedback из всех источников"""
    print("[feedback_collector] Starting feedback collection...")
    
    collector = FeedbackCollector()
    
    github_count = collector.collect_from_github()
    email_count = collector.collect_from_email()
    
    total = github_count + email_count
    print(f"[feedback_collector] Collection complete: {total} new items")
    
    return total


if __name__ == "__main__":
    collect_all_feedback()
