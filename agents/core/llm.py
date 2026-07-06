"""
LLM Client - обёртка над OpenAI API (GPT-4o-mini)
Можно переключиться на Ollama (локально) или DashScope (Qwen)
"""
import os
from openai import OpenAI


class LLMClient:
    def __init__(self, api_key=None, model="gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set. Set it in .env file.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate(self, prompt, system_prompt=None, max_tokens=2000, temperature=0.7):
        """Генерация текста через LLM"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def generate_article(self, topic, audience="investors", language="en"):
        """Генерация статьи"""
        system_prompt = f"""You are a professional technical writer specializing in biotech and AI.
Write for {audience} audience in {language} language.
Focus on practical value, real-world applications, and business impact.
Use clear, engaging language. Include concrete examples and metrics."""

        prompt = f"""Write a comprehensive article about: {topic}

Context: ADMETox.AI is an AI-powered platform for ADME/Tox prediction in drug discovery.
It predicts solubility, Caco-2 permeability, hERG toxicity, lipophilicity, and P-gp from SMILES strings.
The platform uses LightGBM models trained on public datasets (AqSolDB, Wang et al., TDC).

Structure:
1. Compelling headline
2. Introduction (hook the reader)
3. Problem statement (why this matters)
4. Solution overview (how ADMETox.AI solves it)
5. Technical details (brief, accessible)
6. Real-world impact (metrics, use cases)
7. Call to action

Length: 800-1200 words"""

        return self.generate(prompt, system_prompt, max_tokens=3000)

    def generate_investor_email(self, investor_name, fund_name, product_info):
        """Генерация персонализированного письма инвестору"""
        system_prompt = """You are a startup founder reaching out to potential investors.
Write a concise, professional email (200-300 words).
Focus on: problem, solution, traction, ask.
Be respectful of their time. Include a clear call to action."""

        prompt = f"""Write an email to {investor_name} from {fund_name}.

Product: {product_info}

Context: ADMETox.AI reduces ADME/Tox screening time from weeks to seconds,
cutting costs by 90% compared to traditional methods.
Current metrics: 10 models, 69 tests passing, Docker-ready for production.

Include:
- Brief introduction
- Problem (expensive, slow ADME screening)
- Solution (AI-powered prediction in seconds)
- Traction (models trained, tests passing, production-ready)
- Ask (15-minute call to discuss partnership/investment)

Keep it under 300 words."""

        return self.generate(prompt, system_prompt, max_tokens=1000)

    def generate_changelog(self, commits):
        """Генерация changelog из коммитов"""
        system_prompt = """You are a technical writer creating release notes.
Group changes by category: Features, Fixes, Improvements, Security.
Use clear, concise language. Include commit hashes for reference."""

        commits_text = "\n".join([f"- {c}" for c in commits])
        prompt = f"""Generate a changelog from these commits:

{commits_text}

Format:
## [Version] - [Date]

### Features
- ...

### Fixes
- ...

### Improvements
- ...

### Security
- ..."""

        return self.generate(prompt, system_prompt, max_tokens=1500)

    def generate_release_summary(self, changelog):
        """Генерация краткого summary для GitHub release"""
        system_prompt = "Summarize release notes in 2-3 sentences. Focus on key improvements."
        prompt = f"Summarize this changelog:\n\n{changelog}"
        return self.generate(prompt, system_prompt, max_tokens=300)
