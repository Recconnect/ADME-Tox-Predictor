from team.base import BaseAgent
from team.config import ARTIFACTS


class MlEngineerAgent(BaseAgent):
    role = "ML Engineer"
    title = "Технический аудит: ML-архитектура, инфраструктура, performance"

    def run_audit(self) -> str:
        models_src = self.read_artifact("src.models") or ""
        predict_src = self.read_artifact("src.predict") or ""
        train_src = self.read_artifact("src.train") or ""
        features_src = self.read_artifact("src.features") or ""
        training = self.read_json_artifact("training_results") or {}
        app_src = self.read_artifact("app") or ""

        self.assess_model_architecture(models_src)
        self.assess_performance(predict_src, features_src)
        self.assess_inference_pipeline(models_src, predict_src)
        self.assess_infrastructure(app_src)
        self.assess_export_format(models_src)

        self.add_recommendation("Обновить LightGBM до последней версии и зафиксировать версии пакетов в requirements.txt")
        self.add_recommendation("Добавить автоматический GridSearchCV или Optuna для подбора гиперпараметров")
        self.add_recommendation("Внедрить мониторинг дрейфа данных (Data drift detection via Evidently AI или аналог)")
        self.add_recommendation("Создать REST API на FastAPI с асинхронной обработкой для production B2B")
        self.add_recommendation("Добавить тестирование на производительность (latency, throughput) в CI")
        self.add_recommendation("Разработать Dockerfile + docker-compose для одношагового деплоя")
        self.add_recommendation("Добавить feature store (feast или простой SQLite) для отслеживания фичей между версиями моделей")
        self.add_recommendation("Исследовать GNN (PyTorch Geometric) для улучшения метрик на 5-10% в следующей итерации")

        return self.write_report()

    def assess_model_architecture(self, src: str):
        has_regression = "LGBMRegressor" in src
        has_classification = "LGBMClassifier" in src
        has_early_stopping = "early_stopping" in src
        has_feature_importance = "feature_importance" in src
        has_kfold = "KFold" in src or "cross_val" in src

        self.add_finding(f"Регрессия (Solubility): LGBMRegressor {'✓' if has_regression else '✗'}")
        self.add_finding(f"Классификация (Caco-2, hERG): LGBMClassifier {'✓' if has_classification else '✗'}")
        self.add_finding(f"Early stopping: {'✓' if has_early_stopping else '✗ — переобучение не контролируется'}")
        self.add_finding(f"Feature importance: {'✓' if has_feature_importance else '✗ — добавить анализ важности'}")
        self.add_finding(f"Cross-validation: {'✓' if has_kfold else '✗ — только scaffold split'}")
        self.add_finding("Ансамбль из 3 моделей — адекватная архитектура для MVP")

    def assess_performance(self, predict_src: str, features_src: str):
        has_cache = "lru_cache" in features_src
        has_batch = "predict_batch" in predict_src
        has_chunk = "chunk_size" in features_src or "BATCH_CHUNK_SIZE" in predict_src
        has_validation = "predict_validated" in predict_src

        self.add_finding(f"LRU caching: {'✓' if has_cache else '✗'}")
        self.add_finding(f"Batch processing: {'✓' if has_batch else '✗'}")
        self.add_finding(f"Chunking: {'✓' if has_chunk else '✗'}")
        self.add_finding(f"Validation mode: {'✓' if has_validation else '✗'}")

    def assess_inference_pipeline(self, models_src: str, predict_src: str):
        has_save = "save_model" in models_src
        has_load = "load_model" in models_src
        has_metadata = "metadata" in models_src
        has_dim_check = "_validate_feature" in predict_src
        has_error_handling = "error" in predict_src

        self.add_finding(f"Model persistence (joblib): {'✓' if has_save and has_load else '✗'}")
        self.add_finding(f"Metadata in saved models: {'✓' if has_metadata else '✗'}")
        self.add_finding(f"Feature dimension validation: {'✓' if has_dim_check else '✗'}")
        self.add_finding(f"Graceful error handling: {'✓' if has_error_handling else '✗'}")

    def assess_infrastructure(self, app_src: str):
        has_streamlit = "streamlit" in app_src
        has_st_tabs = "st.tabs" in app_src
        has_st_cache = "cache_resource" in app_src
        has_multipage = "tabs" in app_src
        has_download = "download_button" in app_src

        self.add_finding(f"Streamlit: {'✓' if has_streamlit else '✗'}")
        self.add_finding(f"Resource caching: {'✓' if has_st_cache else '✗'}")
        self.add_finding(f"Tabbed UI: {'✓' if has_multipage else '✗'}")
        self.add_finding(f"CSV export: {'✓' if has_download else '✗'}")

    def assess_export_format(self, src: str):
        has_joblib = "joblib" in src
        has_pickle = "pickle" in src or ".pkl" in src
        has_onnx = "onnx" in src
        has_mlflow = "mlflow" in src

        self.add_finding(f"Export format: {'joblib' if has_joblib else 'pickle' if has_pickle else 'не определен'}")
        self.add_finding(f"ONNX export: {'✓' if has_onnx else '✗ — добавить для production'}")
        self.add_finding(f"MLflow tracking: {'✓' if has_mlflow else '✗ — добавить для экспериментов'}")
