"""
GitHub Client - обёртка над PyGithub
Поддержка releases, issues, commits, metrics
"""
import os
from datetime import datetime, timedelta
from github import Github
from github.GithubException import GithubException


class GitHubClient:
    def __init__(self, token=None, owner="Recconnect", repo="ADME-Tox-Predictor"):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set. Set it in .env file.")
        self.github = Github(self.token)
        self.repo = self.github.get_repo(f"{owner}/{repo}")
        self.owner = owner
        self.repo_name = repo

    def get_recent_commits(self, since=None, limit=50):
        """Получить коммиты с указанной даты"""
        if since is None:
            since = datetime.now() - timedelta(days=7)
        commits = self.repo.get_commits(since=since)
        result = []
        for i, commit in enumerate(commits):
            if i >= limit:
                break
            result.append({
                "sha": commit.sha[:7],
                "message": commit.commit.message.split("\n")[0],
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat(),
            })
        return result

    def get_latest_release(self):
        """Получить последний release"""
        try:
            return self.repo.get_latest_release()
        except GithubException:
            return None

    def create_release(self, tag, title, body, draft=False, prerelease=False):
        """Создать новый release"""
        release = self.repo.create_git_release(
            tag=tag,
            name=title,
            message=body,
            draft=draft,
            prerelease=prerelease,
        )
        return release

    def get_issues(self, state="open", labels=None, limit=50):
        """Получить issues"""
        issues = self.repo.get_issues(state=state)
        result = []
        for i, issue in enumerate(issues):
            if i >= limit:
                break
            if issue.pull_request:
                continue
            result.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "labels": [l.name for l in issue.labels],
                "created_at": issue.created_at.isoformat(),
                "body": (issue.body or "")[:500],
            })
        return result

    def comment_on_issue(self, issue_number, comment):
        """Добавить комментарий к issue"""
        issue = self.repo.get_issue(issue_number)
        return issue.create_comment(comment)

    def get_stars_count(self):
        """Количество звёзд"""
        return self.repo.stargazers_count

    def get_forks_count(self):
        """Количество форков"""
        return self.repo.forks_count

    def get_watchers_count(self):
        """Количество наблюдателей"""
        return self.repo.subscribers_count

    def get_open_issues_count(self):
        """Количество открытых issues"""
        return self.repo.open_issues_count

    def get_contributors_count(self):
        """Количество контрибьюторов"""
        return self.repo.get_contributors().totalCount

    def get_all_metrics(self):
        """Собрать все метрики репозитория"""
        return {
            "stars": self.get_stars_count(),
            "forks": self.get_forks_count(),
            "watchers": self.get_watchers_count(),
            "open_issues": self.get_open_issues_count(),
            "contributors": self.get_contributors_count(),
            "size_kb": self.repo.size,
            "language": self.repo.language,
            "created_at": self.repo.created_at.isoformat(),
            "updated_at": self.repo.updated_at.isoformat(),
        }

    def increment_version(self, current_tag):
        """Инкремент версии (semver)"""
        if not current_tag:
            return "v0.1.0"
        version = current_tag.lstrip("v")
        parts = version.split(".")
        if len(parts) != 3:
            return "v0.1.0"
        try:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            return f"v{major}.{minor}.{patch + 1}"
        except ValueError:
            return "v0.1.0"
