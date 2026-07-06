from team.base import BaseAgent
from team.config import (
    RUSSIAN_PHARMA_COMPANIES, RUSSIAN_CRO_COMPANIES,
    AI_RUSSIAN_COMPETITORS,
)


class BusinessDevAgent(BaseAgent):
    role = "Business Development (Российский рынок)"
    title = "Аудит рынка РФ: целевые компании, конкуренты, GTM-стратегия"

    def run_audit(self) -> str:
        self.assess_market_size()
        self.assess_target_segments()
        self.assess_competitors()
        self.assess_pricing()
        self.assess_sales_channels()

        self.add_recommendation("Сфокусироваться на CRO как первом сегменте — у них есть recurring need в ADME-скрининге")
        self.add_recommendation("ChemRar — первый пилотный клиент:他们有 свой R&D пайплайн и понимают ценность in silico")
        self.add_recommendation("Предложить BIOCAD пилот на их собственных молекулах (top-10 кандидатов) — бесплатно, с публикацией результатов")
        self.add_recommendation("Участвовать в Pharmaprojects-конференциях и PharmaRussia для нетворкинга с CRO")
        self.add_recommendation("Создать лендинг на русском: 'AI-скрининг ADME/Tox для российских CRO и R&D отделов'")
        self.add_recommendation("Разработать free tier: 100 предсказаний/месяц для привлечения академических пользователей")
        self.add_recommendation("Собрать базу из 50 контактов (LinkedIn + Pharmaprojects) и начать outreach")
        self.add_recommendation("Подготовить use case для госзакупок (ФЗ-44, ФЗ-223) в рамках импортозамещения ПО")

        return self.write_report()

    def assess_market_size(self):
        self.add_finding("Рынок AI в drug discovery: global $3.5B (2025) → $7.6B (2028), CAGR 30%")
        self.add_finding("Российский фармрынок: ~$30 млрд (2025), из них R&D — ~$1.5 млрд")
        self.add_finding("Российские CRO тратят $50-200K/год на in silico инструменты (оценка)")
        self.add_finding("TAM (РФ): $50-100 млн/год — AI ADME/Tox для CRO и фармы")
        self.add_finding("Целевая доля: 2-5% рынка РФ = 5-15 клиентов при ARPU $10K/год = $50-150K ARR")

    def assess_target_segments(self):
        self.add_finding(f"Сегмент 1: CRO (ChemRar, Khimrar, PharmChem) — прямая потребность в скрининге молекул")
        self.add_finding(f"Сегмент 2: Фармпроизводители (BIOCAD, R-Pharm, Geropharm) — R&D отделы")
        self.add_finding(f"Сегмент 3: Биотех-стартапы РФ — мало, но быстрорастущий сегмент")
        self.add_finding(f"Сегмент 4: Академические лаборатории — для free-tier и building brand")
        self.add_finding(f"Всего целевых компаний в РФ: ~20 CRO + ~30 pharma R&D = 50 клиентов")

    def assess_competitors(self):
        self.add_finding("Прямые конкуренты в РФ: отсутствуют — AI ADME/Tox ниша не занята")
        self.add_finding(f"Непрямые: Schrodinger ($100K/год), ChemAxon ($5K/год) — не AI-native, дороги для РФ")
        self.add_finding(f"Потенциальные: Insilico (глобально, нет dedicated ADME-продукта)")
        self.add_finding(f"Академические: Way2Drug (PASS) — веб-инструмент, не SaaS, некоммерческий")
        self.add_finding("Конкурентное преимущество: AI-native, российское происхождение, цена $10K/год")
        self.add_finding("Риск: снижение цены на Schrödinger для РФ — но они фокусируются на крупных клиентах")

    def assess_pricing(self):
        self.add_finding("Базовый тариф: $10K/год (₽800K/год) — 10,000 предсказаний, email support")
        self.add_finding("Enterprise: $50K/год (₽4M/год) — dedicated instance, fine-tuning, API SLA")
        self.add_finding("Free tier: 100 предсказаний/месяц — для академии и первичного знакомства")
        self.add_finding("Credit-based: $50/1000 предсказаний — для разовых проектов")
        self.add_finding("Цена в ₽ фиксированная: ₽60K/мес за enterprise — учтён курс и платежи РФ")

    def assess_sales_channels(self):
        self.add_finding("Канал 1: Direct sales (LinkedIn, email, конференции) — основной для РФ")
        self.add_finding("Канал 2: Партнёрства с вендорами (например, Cloud4Y для хостинга в РФ)")
        self.add_finding("Канал 3: Госзакупки (ФЗ-44, 223) через статус участника Сколково")
        self.add_finding("Канал 4: Реферальная программа для CRO-партнёров")
        self.add_finding("Канал 5: Pharmaprojects каталог — внесение в реестр CRO-услуг")
