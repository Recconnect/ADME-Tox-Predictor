from team.base import BaseAgent
from team.config import ARTIFACTS


class DesignerAgent(BaseAgent):
    role = "UI/UX Designer"
    title = "Аудит интерфейса, пользовательского опыта и брендинга"

    def run_audit(self) -> str:
        app = self.read_artifact("app") or ""
        predict = self.read_artifact("src.predict") or ""
        config = self.read_artifact("src.config") or ""

        self.assess_ui_structure(app)
        self.assess_user_flow(app)
        self.assess_visualization(app)
        self.assess_branding()
        self.assess_mobile_responsiveness(app)

        self.add_recommendation("Добавить визуализацию результатов: radar chart для сравнения молекул по 3+ свойствам")
        self.add_recommendation("Добавить scaffold viewer (молекулярную структуру) через RDKit + Streamlit или st.image")
        self.add_recommendation("Внедрить color-coding результатов (зелёный/жёлтый/красный) для быстрой оценки")
        self.add_recommendation("Добавить onboarding для новых пользователей: tooltips, примеры SMILES, quick guide")
        self.add_recommendation("Разработать брендинг: логотип, цветовая схема, favicon")
        self.add_recommendation("Создать лендинг на русском с CJM: от входа до оплаты enterprise-лицензии")
        self.add_recommendation("Добавить dark theme для Streamlit (через config или сторонний компонент)")
        self.add_recommendation("Провести usability testing с 3-5 CRO-специалистами перед запуском в РФ")

        return self.write_report()

    def assess_ui_structure(self, src: str):
        has_tabs = "st.tabs" in src
        has_nav = "sidebar" in src
        has_input = "text_input" in src or "text_area" in src
        has_upload = "file_uploader" in src
        has_download = "download_button" in src
        has_metrics = "st.metric" in src
        has_expander = "st.expander" in src
        has_dataframe = "st.dataframe" in src
        has_spinner = "st.spinner" in src

        tabs = src.count("with tab") + src.count("with st")
        self.add_finding(f"Tabbed layout: {tabs} tabs {'✓' if has_tabs else '✗'}")
        self.add_finding(f"Sidebar: {'✓' if has_nav else '✗'}")
        self.add_finding(f"Input methods: text_input={'✓' if has_input else '✗'}, file_upload={'✓' if has_upload else '✗'}")
        self.add_finding(f"CSV export: {'✓' if has_download else '✗'}")
        self.add_finding(f"Metrics display (st.metric): {'✓' if has_metrics else '✗'}")
        self.add_finding(f"Expandable sections: {'✓' if has_expander else '✗'}")
        self.add_finding(f"Data preview: {'✓' if has_dataframe else '✗'}")
        self.add_finding(f"Loading indicators: {'✓' if has_spinner else '✗'}")

    def assess_user_flow(self, src: str):
        errors_handled = "error" in src and "st.error" in src
        success_feedback = "st.success" in src
        has_placeholder = "placeholder" in src
        has_validation = "predict_validated" in src or "Validation" in src
        has_batch = "Batch" in src

        self.add_finding(f"Error handling: {'✓' if errors_handled else '✗'}")
        self.add_finding(f"Success feedback: {'✓' if success_feedback else '✗'}")
        self.add_finding(f"Input placeholders: {'✓' if has_placeholder else '✗'}")
        self.add_finding(f"Validation flow: {'✓' if has_validation else '✗'}")
        self.add_finding(f"Batch processing: {'✓' if has_batch else '✗'}")
        self.add_finding("User journey: Single molecule → Batch → Validation — логичный прогресс")

    def assess_visualization(self, src: str):
        has_charts = "st.line_chart" in src or "st.bar_chart" in src or "plt" in src
        has_json = "st.json" in src
        has_radio = "st.radio" in src
        has_button = "st.button" in src

        self.add_finding(f"Charts/plots: {'✓' if has_charts else '✗ — добавить визуализацию распределений'}")
        self.add_finding(f"JSON export: {'✓' if has_json else '✗'}")
        self.add_finding(f"Radio buttons: {'✓' if has_radio else '✗'}")
        self.add_finding(f"Action buttons: {'✓' if has_button else '✗'}")

    def assess_branding(self):
        self.add_finding("Брендинг: отсутствует — дефолтный Streamlit, нет логотипа, favicon, кастомного CSS")
        self.add_finding("Название: 'ADME/Tox Predictor v2.0' — функционально, но не для маркетинга РФ")
        self.add_finding("Цветовая схема: дефолтная Streamlit — не адаптирована под российскую аудиторию")
        self.add_finding("Рекомендация по названию для РФ: 'ADMETox.AI' или 'Скрининг ADME/Tox'")

    def assess_mobile_responsiveness(self, src: str):
        has_responsive = "width='stretch'" in src or "use_container_width" not in src
        has_wide = "layout='wide'" in src
        self.add_finding(f"Wide mode: {'✓' if has_wide else '✗'}")
        self.add_finding(f"Responsive tables: {'✓' if has_responsive else '✗ — использовать width=\"stretch\"'}")
