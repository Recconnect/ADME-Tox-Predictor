"""Conference tracker agent - отслеживает релевантные конференции"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import json
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class ConferenceTracker:
    """Отслеживание конференций по drug discovery, AI, biotech"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "conferences.db"
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных для конференций"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT,
                location TEXT,
                start_date TEXT,
                end_date TEXT,
                deadline TEXT,
                topic TEXT,
                relevance_score REAL DEFAULT 0,
                status TEXT DEFAULT 'discovered',
                notes TEXT,
                discovered_at REAL NOT NULL,
                registered_at REAL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conferences_status ON conferences(status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conferences_start_date ON conferences(start_date)
        """)
        conn.commit()
        conn.close()
    
    def add_conference(self, name, url=None, location=None, start_date=None, 
                      end_date=None, deadline=None, topic=None, relevance_score=0):
        """Добавить конференцию"""
        conn = sqlite3.connect(str(self.db_path))
        
        # Проверяем, есть ли уже такая конференция
        existing = conn.execute(
            "SELECT id FROM conferences WHERE name=?", (name,)
        ).fetchone()
        
        if existing:
            conn.close()
            return False
        
        conn.execute(
            """INSERT INTO conferences 
               (name, url, location, start_date, end_date, deadline, topic, relevance_score, discovered_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, url, location, start_date, end_date, deadline, topic, relevance_score, 
             datetime.now().timestamp())
        )
        conn.commit()
        conn.close()
        return True
    
    def get_upcoming_conferences(self, days=90):
        """Получить предстоящие конференции"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        cutoff = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        rows = conn.execute(
            """SELECT * FROM conferences 
               WHERE start_date >= ? AND start_date <= ?
               ORDER BY start_date ASC""",
            (today, cutoff)
        ).fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def get_deadlines(self, days=30):
        """Получить ближайшие дедлайны"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        cutoff = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        rows = conn.execute(
            """SELECT * FROM conferences 
               WHERE deadline >= ? AND deadline <= ?
               ORDER BY deadline ASC""",
            (today, cutoff)
        ).fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def mark_registered(self, conference_id):
        """Отметить конференцию как зарегистрированную"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "UPDATE conferences SET status='registered', registered_at=? WHERE id=?",
            (datetime.now().timestamp(), conference_id)
        )
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Статистика по конференциям"""
        conn = sqlite3.connect(str(self.db_path))
        
        stats = {
            'total': conn.execute("SELECT COUNT(*) FROM conferences").fetchone()[0],
            'by_status': {},
            'upcoming_90d': len(self.get_upcoming_conferences(90)),
            'deadlines_30d': len(self.get_deadlines(30))
        }
        
        for row in conn.execute(
            "SELECT status, COUNT(*) as cnt FROM conferences GROUP BY status"
        ).fetchall():
            stats['by_status'][row[0]] = row[1]
        
        conn.close()
        return stats


def load_initial_conferences():
    """Загрузка начального списка релевантных конференций"""
    tracker = ConferenceTracker()
    
    # Список релевантных конференций для drug discovery + AI
    conferences = [
        {
            "name": "Bio-IT World Conference & Expo",
            "url": "https://www.bio-itworldexpo.com/",
            "location": "Boston, MA, USA",
            "topic": "bioinformatics, drug discovery",
            "relevance_score": 0.95
        },
        {
            "name": "ELISp Drug Discovery Conference",
            "url": "https://www.elisp.org/",
            "location": "Europe",
            "topic": "drug discovery, AI",
            "relevance_score": 0.90
        },
        {
            "name": "Machine Learning in Drug Discovery (MLDD)",
            "url": "https://mldd.org/",
            "location": "Various",
            "topic": "machine learning, drug discovery",
            "relevance_score": 0.95
        },
        {
            "name": "AI in Drug Discovery Summit",
            "url": "https://www.aidrugdiscovery.com/",
            "location": "USA",
            "topic": "AI, drug discovery",
            "relevance_score": 0.95
        },
        {
            "name": "RECOMB Conference",
            "url": "https://recomb.org/",
            "location": "Various",
            "topic": "computational biology, bioinformatics",
            "relevance_score": 0.85
        },
        {
            "name": "ISMB/ECCB Conference",
            "url": "https://www.iscb.org/ismbeccb2024",
            "location": "Various",
            "topic": "bioinformatics, computational biology",
            "relevance_score": 0.85
        },
        {
            "name": "PSB Pacific Symposium on Biocomputing",
            "url": "https://psb.stanford.edu/",
            "location": "Hawaii, USA",
            "topic": "biocomputing, drug discovery",
            "relevance_score": 0.80
        },
        {
            "name": "American Chemical Society (ACS) Spring",
            "url": "https://www.acs.org/meetings.html",
            "location": "USA",
            "topic": "chemistry, drug discovery",
            "relevance_score": 0.75
        },
        {
            "name": "Drug Discovery Technology Exchange",
            "url": "https://www.ddtex.com/",
            "location": "San Diego, CA, USA",
            "topic": "drug discovery, technology",
            "relevance_score": 0.90
        },
        {
            "name": "Pharmaceutical Science and Technology",
            "url": "https://www.aaps.org/",
            "location": "Various",
            "topic": "pharmaceutical science",
            "relevance_score": 0.70
        }
    ]
    
    added = 0
    for conf in conferences:
        if tracker.add_conference(**conf):
            added += 1
    
    print(f"[conference_tracker] Loaded {added} initial conferences")
    return added


def track_conferences():
    """Основная функция отслеживания конференций"""
    print("[conference_tracker] Starting conference tracking...")
    
    tracker = ConferenceTracker()
    
    # Загружаем начальный список если база пустая
    stats = tracker.get_stats()
    if stats['total'] == 0:
        load_initial_conferences()
    
    # Получаем статистику
    stats = tracker.get_stats()
    print(f"[conference_tracker] Total conferences: {stats['total']}")
    print(f"[conference_tracker] Upcoming (90 days): {stats['upcoming_90d']}")
    print(f"[conference_tracker] Deadlines (30 days): {stats['deadlines_30d']}")
    
    # Показываем ближайшие дедлайны
    deadlines = tracker.get_deadlines(30)
    if deadlines:
        print("\n[conference_tracker] Upcoming deadlines:")
        for conf in deadlines[:5]:
            print(f"  - {conf['name']}: {conf['deadline']}")
    
    return stats


if __name__ == "__main__":
    track_conferences()
