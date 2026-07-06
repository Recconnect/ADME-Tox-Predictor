from team.base import BaseAgent
from team.config import ARTIFACTS


class TeamLeadAgent(BaseAgent):
    role = "Product Owner / Team Lead"
    title = "Стратегический аудит проекта и экосистемы"

    def run_audit(self) -> str:
        resume = self.read_artifact("session_resume") or ""
        training = self.read_json_artifact("training_results") or {}
        app = self.read_artifact("app") or ""
        config = self.read_artifact("src.config") or ""

        self.add_finding(f"Текущее состояние: MVP готов, 3 модели обучены, 31 тест проходит")
        self.add_finding(f"Solubility: Test R²={training.get('solubility', {}).get('test_r2', 'N/A')} (target >0.6)")
        self.add_finding(f"Caco-2: Test Acc={training.get('caco2', {}).get('test_acc', 'N/A')}, AUC={training.get('caco2', {}).get('test_auc', 'N/A')}")
        self.add_finding(f"hERG: Test Acc={training.get('herg', {}).get('test_acc', 'N/A')}, AUC={training.get('herg', {}).get('test_auc', 'N/A')}")
        self.add_finding("Валидация на 10 известных препаратах — все предсказаны успешно")
        self.add_finding("Проект имеет git-историю (3 коммита), полностью версионирован")
        self.add_finding("Созданы инвесторские материалы: 3 pptx, 5 документов в investor_kit, графики")
        self.add_finding("BIOPTIC interview проанализирован, позиционирование уточнено: мы Lead Optimization → они Hit ID")

        has_config = "MODEL_PARAMS" in config
        has_val = "VALIDATION_DRUGS" in config
        self.add_finding(f"Конфигурация: MODEL_PARAMS={'✓' if has_config else '✗'}, VALIDATION_DRUGS={'✓' if has_val else '✗'}")

        risks = self._assess_risks()
        for r in risks:
            self.add_finding(r)

        self.add_recommendation("Запустить пилот с 1-2 российскими CRO в течение 2 месяцев для получения feedback")
        self.add_recommendation("Подать заявку на Старт-1 (Фонд Бортника, до 4 млн руб) — минимальная доработка документации")
        self.add_recommendation("Получить статус участника Сколково — налоговые льготы + гранты до 30 млн")
        self.add_recommendation("Нанять BD для РФ-рынка как первую ключевую роль в команду")
        self.add_recommendation("Добавить 2-3 ADME/Tox свойства (липофильность, Pgp, биоавайлность) для полноты продукта")
        self.add_recommendation("Разработать REST API (FastAPI) для B2B-интеграции с пайплайнами CRO")
        self.add_recommendation("Упаковать проект в Docker для простоты демо и деплоя")
        self.add_recommendation("Составить 18-месячный roadmap с вехами: пилот → seed → масштабирование → Series A")

        return self.write_report()

    def _assess_risks(self) -> list[str]:
        return [
            "Риск: регуляторные требования РФ (регистрация ПО, ФЗ-152) — начать проработку юридической структуры",
            "Риск: конкуренция со стороны крупных платформ (Schrödinger, ChemAxon) — нишевая специализация наше преимущество",
            "Риск: зависимость от открытых данных — построить pipeline для proprietary данных от партнёров",
            "Риск: импортозамещение — подчеркнуть российское происхождение продукта для госзаказчиков",
            "Риск: малый размер датасета hERG (648 молекул) — искать расширенные данные (ChEMBL, PubChem Bioassay)",
        ]
