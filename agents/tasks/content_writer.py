"""
Content Writer Task
Генерация статей для Medium, Habr, VC.ru через LLM
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import LLMClient


# Темы статей с приоритетами
ARTICLE_TOPICS = [
    {
        "topic": "How AI is Transforming ADME/Tox Prediction in Drug Discovery",
        "audience": "investors",
        "platform": "medium",
        "priority": 1,
    },
    {
        "topic": "Why Traditional ADME Screening Costs Millions — and How ML Changes That",
        "audience": "investors",
        "platform": "medium",
        "priority": 2,
    },
    {
        "topic": "Case Study: Screening 100 Drug Candidates in 3 Seconds with ADMETox.AI",
        "audience": "technical",
        "platform": "medium",
        "priority": 3,
    },
    {
        "topic": "Open Source Drug Discovery: ADMETox.AI Technical Deep Dive",
        "audience": "developers",
        "platform": "habr",
        "priority": 4,
    },
    {
        "topic": "AI в drug discovery: как мы сократили скрининг ADME/Tox с недель до секунд",
        "audience": "ru_investors",
        "platform": "vc_ru",
        "priority": 5,
    },
    {
        "topic": "LightGBM vs Neural Networks для предсказания ADME-свойств",
        "audience": "ru_developers",
        "platform": "habr",
        "priority": 6,
    },
]


def write_article(topic_info=None, custom_topic=None):
    """Генерация статьи"""
    print("[content_writer] Starting article generation...")

    llm = LLMClient()

    if custom_topic:
        topic_info = {
            "topic": custom_topic,
            "audience": "investors",
            "platform": "medium",
        }
    elif topic_info is None:
        # Берём следующую не написанную статью
        topic_info = _get_next_topic()
        if not topic_info:
            print("[content_writer] No more topics to write")
            return None

    print(f"[content_writer] Writing: {topic_info['topic']}")
    print(f"[content_writer] Audience: {topic_info['audience']}, Platform: {topic_info['platform']}")

    # Генерируем статью
    article = llm.generate_article(
        topic=topic_info["topic"],
        audience=topic_info["audience"],
        language="ru" if "ru" in topic_info["platform"] else "en",
    )

    # Сохраняем статью
    output_dir = Path(__file__).resolve().parents[1] / "data" / "articles"
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    safe_topic = topic_info["topic"][:50].replace(" ", "_").replace("/", "_")
    filename = f"{date_str}_{safe_topic}.md"
    filepath = output_dir / filename

    # Добавляем метаданные
    header = f"""---
title: "{topic_info['topic']}"
audience: {topic_info['audience']}
platform: {topic_info['platform']}
generated: {datetime.now().isoformat()}
status: draft
---

"""
    full_content = header + article

    filepath.write_text(full_content, encoding="utf-8")
    print(f"[content_writer] Article saved: {filepath}")

    return {
        "filepath": str(filepath),
        "topic": topic_info["topic"],
        "platform": topic_info["platform"],
        "content": article,
    }


def _get_next_topic():
    """Получить следующую не написанную тему"""
    articles_dir = Path(__file__).resolve().parents[1] / "data" / "articles"
    if not articles_dir.exists():
        return ARTICLE_TOPICS[0] if ARTICLE_TOPICS else None

    written_topics = set()
    for f in articles_dir.glob("*.md"):
        content = f.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.startswith("title:"):
                title = line.split('"')[1] if '"' in line else line.split(":", 1)[1].strip()
                written_topics.add(title)
                break

    for topic in ARTICLE_TOPICS:
        if topic["topic"] not in written_topics:
            return topic

    return None


def list_articles():
    """Список всех сгенерированных статей"""
    articles_dir = Path(__file__).resolve().parents[1] / "data" / "articles"
    if not articles_dir.exists():
        print("[content_writer] No articles yet")
        return []

    articles = []
    for f in sorted(articles_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        title = ""
        platform = ""
        status = ""
        for line in content.split("\n"):
            if line.startswith("title:"):
                title = line.split('"')[1] if '"' in line else line.split(":", 1)[1].strip()
            elif line.startswith("platform:"):
                platform = line.split(":", 1)[1].strip()
            elif line.startswith("status:"):
                status = line.split(":", 1)[1].strip()
        articles.append({
            "file": f.name,
            "title": title,
            "platform": platform,
            "status": status,
        })

    return articles


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Content generation tasks")
    parser.add_argument("task", choices=["write", "list"], help="Task to run")
    parser.add_argument("--topic", help="Custom topic for article")
    args = parser.parse_args()

    if args.task == "write":
        write_article(custom_topic=args.topic)
    elif args.task == "list":
        articles = list_articles()
        for a in articles:
            print(f"  [{a['status']}] {a['title']} ({a['platform']})")
