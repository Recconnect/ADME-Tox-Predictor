from team.base import BaseAgent
from team.config import RUSSIAN_GRANTS, VCS_RUSSIAN, ARTIFACTS


class FinancialExpertAgent(BaseAgent):
    role = "Финансовый эксперт"
    title = "Аудит финансовой модели, гранты РФ, стратегия привлечения инвестиций"

    def run_audit(self) -> str:
        training = self.read_json_artifact("training_results") or {}
        session = self.read_artifact("session_resume") or ""

        self.assess_grants()
        self.assess_unit_economics()
        self.assess_funding_strategy()
        self.assess_financial_risks()

        self.add_recommendation("Подать заявку на Старт-1 (₽4 млн) в ближайший цикл — минимальные доработки")
        self.add_recommendation("Одновременно подать на Сколково — статус участника даёт ₽30 млн грантов и налоговые льготы")
        self.add_recommendation("Составить 3-летнюю финмодель с Revenue, CAC, LTV, Burn Rate до Series A")
        self.add_recommendation("Подготовить data room для pre-seed: metrics, roadmap, competitive analysis, team")
        self.add_recommendation("Целевые фонды РФ: Kama Flow (seed), RBF Ventures (pre-seed), Phystech Ventures")
        self.add_recommendation("Рассмотреть бизнес-ангелов из фармы (ex-BIOCAD, ex-R-Pharm) для advisory board")
        self.add_recommendation("После грантов (3-6 мес) выходить на seed-раунд $200-500K с metrics от пилотов")
        self.add_recommendation("Подготовить отчётность по ФЗ-152 (обработка персональных данных) для выхода на enterprise")

        return self.write_report()

    def assess_grants(self):
        self.add_finding(f"Доступно грантовых программ: {len(RUSSIAN_GRANTS)}")

        total_min = 0
        for g in RUSSIAN_GRANTS:
            amt = g["amount"]
            parts = amt.split("до ")
            if len(parts) > 1:
                try:
                    val = int(parts[1].split(" ")[0].replace(",", ""))
                    total_min += val
                except (ValueError, IndexError):
                    pass
            self.add_finding(f"  {g['org']} — {g['program']}: {amt} ({g['stage']})")

        self.add_finding(f"Суммарный грантовый потенциал (первые 12 мес): до ₽{total_min}M+")

    def assess_unit_economics(self):
        CAC = 30000
        monthly_revenue = 10000 / 12
        LTV = 3 * 10000
        gross_margin = 0.85
        months_to_payback = CAC / (monthly_revenue * gross_margin)

        self.add_finding(f"Целевой CAC: ~$3K (поиск + demo + сделка)")
        self.add_finding(f"Целевой LTV: $30K (при retention 3 года)")
        self.add_finding(f"Gross margin: 85% (инфраструктура ~15%)")
        self.add_finding(f"Payback period: ~{months_to_payback:.1f} месяцев")
        self.add_finding(f"LTV/CAC ratio: {LTV / CAC:.1f}x (приемлемо >3x, у нас {LTV / CAC:.1f}x)")

    def assess_funding_strategy(self):
        self.add_finding(f"Фаза 1 (0-6 мес): гранты ₽{4 + 30}M (Старт-1 + Сколково) — non-dilutive")
        self.add_finding(f"Фаза 2 (6-12 мес): pre-seed $100K от бизнес-ангелов / RBF Ventures")
        self.add_finding(f"Фаза 3 (12-18 мес): seed $200-500K от Kama Flow / Phystech Ventures")
        self.add_finding(f"Фаза 4 (18+ мес): Series A $2-5M при 20+ клиентах и $500K+ ARR")

    def assess_financial_risks(self):
        self.add_finding("Риск: задержка грантов (Фонд Бортника рассматривает заявки 3-6 мес)")
        self.add_finding("Риск: уход иностранных венчурных фондов из РФ — фокус на российские фонды")
        self.add_finding("Риск: валютные колебания (фиксировать цены в ₽ для РФ)")
        self.add_finding("Риск: длинный sales cycle в enterprise — предусмотреть 6-12 мес на первые продажи")
        self.add_finding("Риск: конкуренция за гранты (высокая — 5-10%成功率)")
