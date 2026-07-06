"""
GitHub Release Task
Автоматическая генерация changelog и создание release при коммите в master
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import LLMClient, GitHubClient


def auto_release():
    """Автоматическое создание release"""
    print("[github_release] Starting auto-release...")

    github = GitHubClient()
    llm = LLMClient()

    # 1. Получить последний release
    latest = github.get_latest_release()
    if latest:
        since_date = latest.created_at
        current_tag = latest.tag_name
        print(f"[github_release] Latest release: {current_tag} at {since_date}")
    else:
        since_date = datetime.now() - __import__("datetime").timedelta(days=30)
        current_tag = None
        print(f"[github_release] No previous release, using last 30 days")

    # 2. Получить коммиты с последнего release
    commits = github.get_recent_commits(since=since_date)
    if not commits:
        print("[github_release] No new commits since last release")
        return

    print(f"[github_release] Found {len(commits)} new commits")

    # 3. Сгенерировать changelog через LLM
    commit_messages = [f"{c['sha']}: {c['message']}" for c in commits]
    changelog = llm.generate_changelog(commit_messages)

    # 4. Сгенерировать краткое summary
    summary = llm.generate_release_summary(changelog)

    # 5. Создать новый release
    new_tag = github.increment_version(current_tag)
    title = f"Release {new_tag}"
    body = f"{summary}\n\n{changelog}"

    print(f"[github_release] Creating release {new_tag}...")
    release = github.create_release(new_tag, title, body)
    print(f"[github_release] Release created: {release.html_url}")

    return release


def auto_respond_to_issues():
    """Автоматические ответы на новые issues"""
    print("[github_release] Checking for new issues...")

    github = GitHubClient()
    llm = LLMClient()

    issues = github.get_issues(state="open")
    new_issues = [i for i in issues if not i.get("labels")]

    for issue in new_issues:
        # Пропускаем issues с ответами
        if "auto-responded" in issue.get("labels", []):
            continue

        # Генерируем ответ
        prompt = f"""Respond to this GitHub issue for ADMETox.AI project:

Title: {issue['title']}
Body: {issue['body']}

Context: ADMETox.AI is an AI-powered ADME/Tox prediction platform.
Be helpful, concise, and professional.
If it's a bug, ask for reproduction steps.
If it's a feature request, acknowledge and add to roadmap.
If it's a question, provide a clear answer."""

        response = llm.generate(prompt, max_tokens=500)

        # Добавляем комментарий
        github.comment_on_issue(issue["number"], response)
        print(f"[github_release] Responded to issue #{issue['number']}: {issue['title']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub automation tasks")
    parser.add_argument("task", choices=["release", "respond"], help="Task to run")
    args = parser.parse_args()

    if args.task == "release":
        auto_release()
    elif args.task == "respond":
        auto_respond_to_issues()
