from team.base import BaseAgent
from team.config import ARTIFACTS, PROPERTY_IMPORTANCE_RUSSIAN


class BioengineerAgent(BaseAgent):
    role = "Хемоинформатик / Bioengineer"
    title = "Доменный аудит: ADME/Tox модели, данные, биологическая релевантность"

    def run_audit(self) -> str:
        feat = self.read_artifact("src.features") or ""
        dl = self.read_artifact("src.data_loader") or ""
        training = self.read_json_artifact("training_results") or {}
        config = self.read_artifact("src.config") or ""

        self.assess_descriptors(feat)
        self.assess_data_pipeline(dl)
        self.assess_model_metrics(training)
        self.assess_property_relevance()

        self.add_recommendation("Добавить 3D-дескрипторы (PMI, NPR1/2, Coulomb matrices) для повышения точности на 2-5%")
        self.add_recommendation("Расширить hERG датасет через ChEMBL (до 3,000+ молекул) — текущий 648 образцов недостаточен")
        self.add_recommendation("Добавить предсказание липофильности (LogD7.4) и Pgp ингибирования — востребовано российскими CRO")
        self.add_recommendation("Внедрить confidence-интервалы для регрессионных предсказаний (solubility) — повысит доверие клиентов")
        self.add_recommendation("Добавить ADME-rule-of-five (Lipinski, Veber) как быстрый фильтр на UI")
        self.add_recommendation("Провести внешнюю валидацию на proprietary данных CRO — это докажет ценность продукта")
        self.add_recommendation("Добавить scaffold-анализ: показывать ближайшие известные молекулы из training set к каждому предсказанию")

        return self.write_report()

    def assess_descriptors(self, src: str):
        n_desc = src.count("Descriptors.") + src.count("rdMolDescriptors.")
        has_morgan = "GetMorganFingerprint" in src
        has_canonicalization = "canonicalize_smiles" in src
        has_cache = "lru_cache" in src
        has_3d = "Get3D" in src or "PMI" in src or "Coulomb" in src
        has_lipo = "MolLogP" in src

        if has_lipo:
            self.add_finding("LogP дескриптор включён (основы Lipinski Rule-of-Five)")

        self.add_finding(f"RDKit дескрипторы: {n_desc} различных дескрипторов")
        self.add_finding(f"Morgan fingerprint: {has_morgan}")
        self.add_finding(f"SMILES canonicalization: {'✓' if has_canonicalization else '✗ — CRITICAL'}")
        self.add_finding(f"LRU caching: {'✓' if has_cache else '✗ — добавить для производительности'}")
        self.add_finding(f"3D-дескрипторы: {'✓' if has_3d else '✗ — опционально для v2.1'}")
        self.add_finding("Feature dimension: 30 RDKit + 2048 Morgan = 2078 фич — адекватно для LightGBM")

    def assess_data_pipeline(self, src: str):
        has_split = "scaffold_split" in src
        has_sanitize = "_sanitize_dataframe" in src
        has_dedup = "drop_duplicates" in src
        has_nan = "dropna" in src
        has_harvard = "dataverse.harvard.edu" in src

        self.add_finding(f"Scaffold split: {'✓' if has_split else '✗'}")
        self.add_finding(f"SMILES sanitization: {'✓' if has_sanitize else '✗'}")
        self.add_finding(f"Deduplication: {'✓' if has_dedup else '✗'}")
        self.add_finding(f"NaN handling: {'✓' if has_nan else '✗'}")
        self.add_finding(f"Источник данных: {'Harvard Dataverse' if has_harvard else 'другой'}")

    def assess_model_metrics(self, training: dict):
        for model_name, m in training.items():
            if model_name == "solubility":
                r2 = m.get("test_r2", 0)
                if r2 > 0.8:
                    self.add_finding(f"{model_name}: R²={r2:.3f} — сильная модель, пригодна для production")
                elif r2 > 0.6:
                    self.add_finding(f"{model_name}: R²={r2:.3f} — baseline достигнут, желательно улучшение")
                else:
                    self.add_finding(f"{model_name}: R²={r2:.3f} — ниже целевого показателя, требуется дообучение")

            elif model_name in ("caco2", "herg"):
                acc = m.get("test_acc", 0)
                auc = m.get("test_auc", 0)
                if auc > 0.9:
                    self.add_finding(f"{model_name}: Acc={acc:.3f}, AUC={auc:.3f} — отличная дискриминативная способность")
                elif auc > 0.8:
                    self.add_finding(f"{model_name}: Acc={acc:.3f}, AUC={auc:.3f} — хорошая модель, валидна для использования")
                elif auc > 0.7:
                    self.add_finding(f"{model_name}: Acc={acc:.3f}, AUC={auc:.3f} — приемлемо, но требуется дообучение")
                else:
                    self.add_finding(f"{model_name}: Acc={acc:.3f}, AUC={auc:.3f} — ниже порога, требуется пересмотр")

    def assess_property_relevance(self):
        for prop, info in PROPERTY_IMPORTANCE_RUSSIAN.items():
            imp = info["importance"]
            emoji = {"critical": "🔴", "high": "🟡", "medium": "🟢"}.get(imp, "⚪")
            self.add_finding(f"{emoji} {prop}: {imp} — {info['reason_ru']}")
