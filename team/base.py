import json
from pathlib import Path
from datetime import datetime
import importlib.util

from team.config import AUDIT_DIR, ARTIFACTS


class BaseAgent:
    role: str = ""
    title: str = ""

    def __init__(self):
        self.findings: list[str] = []
        self.recommendations: list[str] = []
        self.sources_used: list[str] = []
        self._artifact_cache: dict[str, str | None] = {}

    def read_artifact(self, key: str) -> str | None:
        if key in self._artifact_cache:
            val = self._artifact_cache[key]
            return val
        path = ARTIFACTS.get(key)
        if path is None:
            for sk, sv in ARTIFACTS.items():
                if isinstance(sv, dict):
                    for sk2, sv2 in sv.items():
                        if sk2 == key or f"{sk}.{sk2}" == key:
                            path = sv2
                            break
            if path is None:
                self._artifact_cache[key] = None
                return None
        if isinstance(path, dict):
            self._artifact_cache[key] = None
            return None
        p = Path(path) if isinstance(path, str) else path
        if not p.exists():
            self._artifact_cache[key] = None
            return None
        val = p.read_text(encoding="utf-8")
        self._artifact_cache[key] = val
        self.sources_used.append(str(p))
        return val

    def read_json_artifact(self, key: str) -> dict | None:
        text = self.read_artifact(key)
        if text is None:
            return None
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return None

    def add_finding(self, finding: str):
        self.findings.append(finding)

    def add_recommendation(self, rec: str):
        self.recommendations.append(rec)

    def write_report(self, filename: str | None = None) -> str:
        if filename is None:
            role_key = self.__class__.__name__.replace("Agent", "").lower()
            filename = f"audit_{role_key}.md"
        path = AUDIT_DIR / filename

        header = f"""# Аудит: {self.title}

**Роль:** {self.role}
**Дата:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Источники:** {len(self.sources_used)} файлов проанализировано

---

"""
        sections = []

        if self.findings:
            sections.append("## Ключевые находки\n")
            for i, f in enumerate(self.findings, 1):
                sections.append(f"{i}. {f}")
            sections.append("")

        if self.recommendations:
            sections.append("## Рекомендации\n")
            for i, r in enumerate(self.recommendations, 1):
                sections.append(f"{i}. **{r}**")
            sections.append("")

        content = header + "\n".join(sections)

        path.write_text(content, encoding="utf-8")
        return str(path)

    @property
    def module_name(self) -> str:
        return f"team.agent_{self.role.lower().replace(' ', '_').replace('/', '_')}"
