#!/usr/bin/env python3
"""
Setup script for ADMETox.AI Outreach Agents
Установка зависимостей и проверка конфигурации
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10+ required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def install_dependencies():
    """Установка зависимостей"""
    print("\nInstalling dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("✓ Dependencies installed")


def check_env_file():
    """Проверка .env файла"""
    env_path = Path(".env")
    if not env_path.exists():
        print("\n⚠ .env file not found")
        print("Creating from .env.example...")
        os.system("cp .env.example .env")
        print("\nIMPORTANT: Edit .env and add your API keys:")
        print("  - OPENAI_API_KEY: https://platform.openai.com/api-keys")
        print("  - GITHUB_TOKEN: already set")
        print("  - EMAIL_PASSWORD: your email password")
        return False

    print("✓ .env file exists")

    # Проверяем наличие ключей
    with open(env_path) as f:
        content = f.read()

    missing = []
    if "OPENAI_API_KEY=your_openai_api_key_here" in content:
        missing.append("OPENAI_API_KEY")
    if "EMAIL_PASSWORD=your_email_password_here" in content:
        missing.append("EMAIL_PASSWORD")

    if missing:
        print(f"\n⚠ Missing API keys in .env: {', '.join(missing)}")
        print("Please edit .env and add your keys")
        return False

    print("✓ API keys configured")
    return True


def test_imports():
    """Проверка импортов"""
    print("\nTesting imports...")
    try:
        from core import LLMClient, EmailSender, GitHubClient
        print("✓ Core modules imported")
    except ImportError as e:
        print(f"✗ Failed to import core modules: {e}")
        return False

    try:
        from tasks import auto_release, write_article, outreach_batch
        print("✓ Task modules imported")
    except ImportError as e:
        print(f"✗ Failed to import task modules: {e}")
        return False

    return True


def test_github_token():
    """Проверка GitHub токена"""
    print("\nTesting GitHub token...")
    try:
        from core import GitHubClient
        github = GitHubClient()
        metrics = github.get_all_metrics()
        print(f"✓ GitHub API working: {metrics['stars']} stars, {metrics['forks']} forks")
        return True
    except Exception as e:
        print(f"✗ GitHub API failed: {e}")
        return False


def test_llm():
    """Проверка LLM API"""
    print("\nTesting LLM API...")
    try:
        from core import LLMClient
        llm = LLMClient()
        response = llm.generate("Say 'Hello' in one word", max_tokens=10)
        print(f"✓ LLM API working: {response}")
        return True
    except Exception as e:
        print(f"✗ LLM API failed: {e}")
        return False


def main():
    print("=" * 50)
    print("ADMETox.AI Outreach Agents - Setup")
    print("=" * 50)

    # Проверки
    if not check_python_version():
        return

    install_dependencies()

    if not check_env_file():
        print("\nSetup incomplete. Please configure .env and run again.")
        return

    if not test_imports():
        print("\nSetup failed. Check dependencies.")
        return

    # Опциональные тесты
    if test_github_token():
        print("✓ GitHub integration ready")

    if test_llm():
        print("✓ LLM integration ready")

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Test a task: python coordinator.py release")
    print("2. Run all tasks: python coordinator.py all")
    print("3. Start scheduler: python coordinator.py schedule")
    print("\nSee README.md for detailed documentation.")


if __name__ == "__main__":
    main()
