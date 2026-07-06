"""
Audit Runner — запускает всех агентов команды последовательно.

Usage:
    python -m team.runner                     # полный аудит
    python -m team.runner --strategy          # аудит + GTM стратегия
    python -m team.runner --quick             # только вывод сводки (без генерации отчётов)
    python -m team.runner --agent=team_lead   # запустить одного агента
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from team.config import AUDIT_DIR, TEAM_DIR


def get_all_agents():
    from team.agent_team_lead import TeamLeadAgent
    from team.agent_bioengineer import BioengineerAgent
    from team.agent_ml_engineer import MlEngineerAgent
    from team.agent_business_dev import BusinessDevAgent
    from team.agent_designer import DesignerAgent
    from team.agent_financial_expert import FinancialExpertAgent

    return [
        TeamLeadAgent(),
        BioengineerAgent(),
        MlEngineerAgent(),
        BusinessDevAgent(),
        DesignerAgent(),
        FinancialExpertAgent(),
    ]


def run_agent(agent_class):
    agent = agent_class()
    title = agent.title
    role = agent.role
    print(f"  [{role}] {title}...")
    t0 = time.time()
    report_path = agent.run_audit()
    elapsed = time.time() - t0
    print(f"    OK {elapsed:.1f}s -> {report_path}")
    return agent


def run_all():
    print("=" * 65)
    print("  ADME/Tox Predictor — Team Audit Pipeline")
    print("=" * 65)
    print()
    print(f"Состав команды: 6 агентов")
    print(f"Выходные отчёты: {AUDIT_DIR}")
    print()

    results = {}
    agents = get_all_agents()
    for agent_class in agents:
        cls = agent_class.__class__
        results[agent_class.role] = run_agent(cls)

    print()
    print("=" * 65)
    print("  АУДИТ ЗАВЕРШЁН")
    print("=" * 65)
    print()
    print(f"  Отчёты сгенерированы в: {AUDIT_DIR}")
    print()

    summary = {
        "total_agents": len(results),
        "total_findings": sum(len(a.findings) for a in results.values()),
        "total_recommendations": sum(len(a.recommendations) for a in results.values()),
        "total_sources": sum(len(a.sources_used) for a in results.values()),
    }
    print(f"  Находок: {summary['total_findings']}")
    print(f"  Рекомендаций: {summary['total_recommendations']}")
    print(f"  Файлов проанализировано: {summary['total_sources']}")
    print()

    print("  Файлы:")
    for role_cls, agent in zip([a.__class__ for a in agents], results.values()):
        role_key = role_cls.__name__.replace("Agent", "").lower()
        print(f"    audit_{role_key}.md  <- {agent.role}")

    return results


def quick_summary():
    agents = get_all_agents()
    print("=" * 65)
    print("  TEAM AUDIT — QUICK SUMMARY")
    print("=" * 65)
    for agent in agents:
        print(f"\n  [{agent.role}]")
        print(f"  {agent.title}")
    print(f"\n  {'─' * 65}")
    print(f"  6 агентов, {len(AUDIT_DIR.parents[0])} источников данных")
    print(f"  Запустите `python -m team.runner` для полного аудита")


if __name__ == "__main__":
    if "--quick" in sys.argv:
        quick_summary()
    elif "--agent" in sys.argv:
        idx = sys.argv.index("--agent") + 1
        agent_name = sys.argv[idx] if idx < len(sys.argv) else ""
        mapping = {
            "team_lead": "agent_team_lead",
            "bioengineer": "agent_bioengineer",
            "ml_engineer": "agent_ml_engineer",
            "business_dev": "agent_business_dev",
            "designer": "agent_designer",
            "financial_expert": "agent_financial_expert",
        }
        mod_name = mapping.get(agent_name, agent_name)
        import importlib
        mod = importlib.import_module(f"team.{mod_name}")
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type) and "Agent" in name and name != "BaseAgent":
                run_agent(obj)
                break
    elif "--strategy" in sys.argv:
        run_all()
        print()
        print("─" * 65)
        print("  Generating GTM Strategy...")
        from team.agent_strategist import StrategistAgent
        strat = StrategistAgent()
        path = strat.run()
        print(f"  → {path}")
    else:
        run_all()
