"""Social media publisher agent - публикация контента в социальные сети"""
import sys
from pathlib import Path
from datetime import datetime
import sqlite3
import json
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.llm import LLMClient


class SocialMediaPublisher:
    """Публикация контента в социальные сети"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "social_posts.db"
        self._init_db()
        self.llm = LLMClient()
    
    def _init_db(self):
        """Инициализация базы данных для постов"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS social_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                article_id INTEGER,
                scheduled_at REAL,
                published_at REAL,
                status TEXT DEFAULT 'draft',
                url TEXT,
                metrics TEXT,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_posts(platform)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status)
        """)
        conn.commit()
        conn.close()
    
    def generate_linkedin_post(self, article_title, article_summary):
        """Генерация поста для LinkedIn"""
        prompt = f"""Create a professional LinkedIn post about: {article_title}

Summary: {article_summary}

Context: ADMETox.AI is an AI-powered platform for ADME/Tox prediction in drug discovery.
It predicts solubility, Caco-2 permeability, hERG toxicity, lipophilicity, and P-gp from SMILES strings.

Requirements:
- Professional tone for biotech/pharma audience
- Include relevant hashtags (#DrugDiscovery #AI #ADME #Toxicity #PharmaTech)
- 150-300 words
- Include a call to action
- Mention key benefits (speed, cost reduction, accuracy)
- Tag relevant communities if possible

Format as plain text ready for LinkedIn."""
        
        return self.llm.generate(prompt, max_tokens=1000)
    
    def generate_twitter_post(self, article_title, article_summary):
        """Генерация поста для Twitter/X"""
        prompt = f"""Create a Twitter/X post about: {article_title}

Summary: {article_summary}

Context: ADMETox.AI - AI-powered ADME/Tox prediction for drug discovery.

Requirements:
- Max 280 characters
- Include 2-3 relevant hashtags
- Engaging and concise
- Include a link placeholder [LINK]
- Focus on key value proposition

Format as plain text ready for Twitter."""
        
        return self.llm.generate(prompt, max_tokens=300)
    
    def generate_medium_intro(self, article_title, article_summary):
        """Генерация вступительного текста для Medium"""
        prompt = f"""Create an engaging introduction for a Medium article: {article_title}

Summary: {article_summary}

Context: ADMETox.AI - AI-powered ADME/Tox prediction platform for drug discovery.

Requirements:
- Hook the reader in first 2 sentences
- Professional but accessible tone
- 100-200 words
- Set up the problem and solution
- Include relevant tags suggestions (3-5 tags)

Format as plain text."""
        
        return self.llm.generate(prompt, max_tokens=800)
    
    def create_post(self, platform, content, article_id=None, scheduled_at=None):
        """Создать пост"""
        conn = sqlite3.connect(str(self.db_path))
        
        conn.execute(
            """INSERT INTO social_posts 
               (platform, content, article_id, scheduled_at, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (platform, content, article_id, scheduled_at, 'draft', datetime.now().timestamp())
        )
        conn.commit()
        conn.close()
    
    def get_drafts(self, platform=None):
        """Получить черновики постов"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        if platform:
            rows = conn.execute(
                "SELECT * FROM social_posts WHERE platform=? AND status='draft' ORDER BY created_at DESC",
                (platform,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM social_posts WHERE status='draft' ORDER BY created_at DESC"
            ).fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def mark_published(self, post_id, url=None):
        """Отметить пост как опубликованный"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "UPDATE social_posts SET status='published', published_at=?, url=? WHERE id=?",
            (datetime.now().timestamp(), url, post_id)
        )
        conn.commit()
        conn.close()
    
    def get_stats(self, days=30):
        """Статистика по постам"""
        conn = sqlite3.connect(str(self.db_path))
        cutoff = datetime.now().timestamp() - days * 86400
        
        stats = {
            'total': conn.execute(
                "SELECT COUNT(*) FROM social_posts WHERE created_at >= ?", (cutoff,)
            ).fetchone()[0],
            'by_platform': {},
            'by_status': {}
        }
        
        for row in conn.execute(
            "SELECT platform, COUNT(*) as cnt FROM social_posts WHERE created_at >= ? GROUP BY platform",
            (cutoff,)
        ).fetchall():
            stats['by_platform'][row[0]] = row[1]
        
        for row in conn.execute(
            "SELECT status, COUNT(*) as cnt FROM social_posts WHERE created_at >= ? GROUP BY status",
            (cutoff,)
        ).fetchall():
            stats['by_status'][row[0]] = row[1]
        
        conn.close()
        return stats


def create_social_posts_for_article(article_title, article_summary, article_id=None):
    """Создание постов для всех платформ для одной статьи"""
    print(f"[social_publisher] Creating social posts for: {article_title}")
    
    publisher = SocialMediaPublisher()
    
    # LinkedIn
    linkedin_post = publisher.generate_linkedin_post(article_title, article_summary)
    publisher.create_post('linkedin', linkedin_post, article_id)
    print("[social_publisher] LinkedIn post created")
    
    # Twitter
    twitter_post = publisher.generate_twitter_post(article_title, article_summary)
    publisher.create_post('twitter', twitter_post, article_id)
    print("[social_publisher] Twitter post created")
    
    # Medium intro
    medium_intro = publisher.generate_medium_intro(article_title, article_summary)
    publisher.create_post('medium', medium_intro, article_id)
    print("[social_publisher] Medium intro created")
    
    return 3


def publish_social_posts():
    """Основная функция публикации"""
    print("[social_publisher] Starting social media publishing...")
    
    publisher = SocialMediaPublisher()
    
    # Получаем черновики
    drafts = publisher.get_drafts()
    
    if not drafts:
        print("[social_publisher] No drafts to publish")
        return 0
    
    print(f"[social_publisher] Found {len(drafts)} drafts")
    
    # Группируем по платформе
    by_platform = {}
    for draft in drafts:
        platform = draft['platform']
        if platform not in by_platform:
            by_platform[platform] = []
        by_platform[platform].append(draft)
    
    # Показываем статистику
    for platform, posts in by_platform.items():
        print(f"[social_publisher] {platform}: {len(posts)} posts ready")
    
    # TODO: Implement actual publishing via APIs
    # For now, just show what would be published
    print("\n[social_publisher] Posts ready for manual publishing:")
    for platform, posts in by_platform.items():
        print(f"\n--- {platform.upper()} ---")
        for post in posts[:3]:  # Show first 3
            print(f"\n{post['content'][:200]}...")
    
    # Статистика
    stats = publisher.get_stats()
    print(f"\n[social_publisher] Stats (30 days):")
    print(f"  Total posts: {stats['total']}")
    print(f"  By platform: {stats['by_platform']}")
    print(f"  By status: {stats['by_status']}")
    
    return len(drafts)


if __name__ == "__main__":
    publish_social_posts()
