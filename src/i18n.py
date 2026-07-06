STRINGS = {
    "en": {
        "app_title": "ADMETox.AI",
        "app_subtitle": "AI-powered ADME/Tox screening for drug discovery. [ADMETox.AI](https://admetox.ai)",
        "tab_single": "Single Prediction",
        "tab_batch": "Batch Prediction",
        "tab_validation": "Validation",
        "tab_features": "Feature Importance",
        "single_header": "Single Molecule Prediction",
        "single_input_label": "Enter SMILES",
        "single_placeholder": "CCO",
        "single_help": "Enter a valid SMILES string (e.g., CCO for ethanol)",
        "single_button": "Predict",
        "single_spinner": "Computing properties...",
        "single_success": "Prediction complete!",
        "single_expander": "View all RDKit descriptors",
        "desc_col_name": "Descriptor",
        "desc_col_value": "Value",
        "batch_header": "Batch Prediction",
        "batch_radio_label": "Input method:",
        "batch_radio_manual": "Manual input",
        "batch_radio_csv": "Upload CSV",
        "batch_textarea_placeholder": "CCO\nCC(=O)Oc1ccccc1C(=O)O\nCC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "batch_button": "Predict Batch",
        "batch_spinner": "Predicting {n} molecules...",
        "batch_uploader": "Upload CSV with a 'SMILES' column",
        "batch_error_size": "File too large. Max {n} MB.",
        "batch_error_column": "CSV must contain a 'SMILES' column",
        "batch_download": "Download CSV",
        "val_header": "Validation on Known Drugs",
        "val_button": "Run Validation",
        "val_spinner": "Validating on {n} known drugs...",
        "val_download": "Download Validation CSV",
        "fi_header": "Feature Importance",
        "fi_subtitle": "Top-10 RDKit descriptors driving each model's predictions:",
        "fi_not_available": "Feature importance not available for {label}",
        "fi_expander": "{label} — Top 10 Descriptors",
        "fi_col_name": "Descriptor",
        "fi_col_importance": "Importance",
        "fi_caption": "Fingerprint total importance: {value}",
        "sidebar_about": "About ADMETox.AI",
        "sidebar_property": "Property",
        "sidebar_metric": "Metric",
        "sidebar_built_with": "Built with LightGBM + RDKit",
        "sidebar_lipinski": "Lipinski Rule of Five",
        "sidebar_lipinski_rules": "- MolWt < 500\n- LogP < 5\n- H-Donors < 5\n- H-Acceptors < 10",
        "sidebar_examples": "Example SMILES",
        "sidebar_examples_code": "Ethanol: CCO\nAspirin: CC(=O)Oc1ccccc1C(=O)O\nCaffeine: CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "usage_title": "Usage Stats",
        "usage_total": "Total Predictions",
        "usage_7d": "Last 7 Days",
        "usage_users": "Unique Users",
        "usage_latency": "Avg Latency",
        "errors_models_not_found": "Models not found. Train first via: python run_train.py",
        "lipinski_info": "Lipinski Rule of Five: {detail}",
        "lipinski_warning": "Lipinski Rule of Five: {detail}",
        "lipinski_passes": "Passes Lipinski Rule of Five",
        "lipinski_violations": "{n} violation(s): {details}",
        "lipinski_molwt": "MolWt={v:.0f} > 500",
        "lipinski_logp": "LogP={v:.2f} > 5",
        "lipinski_hdonors": "HDonors={v} > 5",
        "lipinski_hacceptors": "HAcceptors={v} > 10",
        "lang_selector": "Language",
    },
    "ru": {
        "app_title": "ADMETox.AI — AI-скрининг ADME/Tox",
        "app_subtitle": "AI-скрининг ADME/Tox для drug discovery. [ADMETox.AI](https://admetox.ai)",
        "tab_single": "Один SMILES",
        "tab_batch": "Пакетный расчёт",
        "tab_validation": "Валидация",
        "tab_features": "Важность признаков",
        "single_header": "Предсказание одной молекулы",
        "single_input_label": "Введите SMILES",
        "single_placeholder": "CCO",
        "single_help": "Введите корректную SMILES-строку (например, CCO для этанола)",
        "single_button": "Рассчитать",
        "single_spinner": "Вычисление свойств...",
        "single_success": "Расчёт завершён!",
        "single_expander": "Все дескрипторы RDKit",
        "desc_col_name": "Дескриптор",
        "desc_col_value": "Значение",
        "batch_header": "Пакетный расчёт",
        "batch_radio_label": "Способ ввода:",
        "batch_radio_manual": "Ручной ввод",
        "batch_radio_csv": "Загрузить CSV",
        "batch_textarea_placeholder": "CCO\nCC(=O)Oc1ccccc1C(=O)O\nCC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "batch_button": "Рассчитать всё",
        "batch_spinner": "Расчёт {n} молекул...",
        "batch_uploader": "Загрузите CSV с колонкой 'SMILES'",
        "batch_error_size": "Файл слишком большой. Максимум {n} МБ.",
        "batch_error_column": "CSV должен содержать колонку 'SMILES'",
        "batch_download": "Скачать CSV",
        "val_header": "Валидация на известных лекарствах",
        "val_button": "Запустить валидацию",
        "val_spinner": "Валидация {n} известных лекарств...",
        "val_download": "Скачать CSV результатов",
        "fi_header": "Важность признаков",
        "fi_subtitle": "Топ-10 дескрипторов RDKit, влияющих на предсказания каждой модели:",
        "fi_not_available": "Важность признаков недоступна для {label}",
        "fi_expander": "{label} — Топ-10 дескрипторов",
        "fi_col_name": "Дескриптор",
        "fi_col_importance": "Важность",
        "fi_caption": "Суммарная важность fingerprint: {value}",
        "sidebar_about": "О ADMETox.AI",
        "sidebar_property": "Свойство",
        "sidebar_metric": "Метрика",
        "sidebar_built_with": "Создано с LightGBM + RDKit",
        "sidebar_lipinski": "Правило Липинского",
        "sidebar_lipinski_rules": "- MolWt < 500\n- LogP < 5\n- H-доноров < 5\n- H-акцепторов < 10",
        "sidebar_examples": "Примеры SMILES",
        "sidebar_examples_code": "Этанол: CCO\nАспирин: CC(=O)Oc1ccccc1C(=O)O\nКофеин: CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "usage_title": "Статистика",
        "usage_total": "Всего предсказаний",
        "usage_7d": "За 7 дней",
        "usage_users": "Пользователей",
        "usage_latency": "Средняя задержка",
        "errors_models_not_found": "Модели не найдены. Обучите через: python run_train.py",
        "lipinski_info": "Правило Липинского: {detail}",
        "lipinski_warning": "Правило Липинского: {detail}",
        "lipinski_passes": "Соответствует правилу Липинского",
        "lipinski_violations": "{n} нарушение(я): {details}",
        "lipinski_molwt": "MolWt={v:.0f} > 500",
        "lipinski_logp": "LogP={v:.2f} > 5",
        "lipinski_hdonors": "H-доноров={v} > 5",
        "lipinski_hacceptors": "H-акцепторов={v} > 10",
        "lang_selector": "Язык",
    },
}

CLASS_TRANSLATIONS = {
    "en": {
        "Soluble": "Soluble",
        "Poorly soluble": "Poorly soluble",
        "High permeability": "High permeability",
        "Low permeability": "Low permeability",
        "Safe (low risk)": "Safe (low risk)",
        "Toxic (high risk)": "Toxic (high risk)",
        "Non-inhibitor (low risk)": "Non-inhibitor (low risk)",
        "Inhibitor (high risk)": "Inhibitor (high risk)",
        "Inhibitor": "Inhibitor",
        "Non-inhibitor": "Non-inhibitor",
        "Mutagenic (positive)": "Mutagenic (positive)",
        "Non-mutagenic (negative)": "Non-mutagenic (negative)",
        "High": "High",
        "Low": "Low",
        "Highly bound (>90%)": "Highly bound (>90%)",
        "Moderately bound (50-90%)": "Moderately bound (50-90%)",
        "Weakly bound (<50%)": "Weakly bound (<50%)",
    },
    "ru": {
        "Soluble": "Растворимо",
        "Poorly soluble": "Плохо растворимо",
        "High permeability": "Высокая проницаемость",
        "Low permeability": "Низкая проницаемость",
        "Safe (low risk)": "Безопасно (низкий риск)",
        "Toxic (high risk)": "Токсично (высокий риск)",
        "Non-inhibitor (low risk)": "Не ингибитор (низкий риск)",
        "Inhibitor (high risk)": "Ингибитор (высокий риск)",
        "Inhibitor": "Ингибитор",
        "Non-inhibitor": "Не ингибитор",
        "Mutagenic (positive)": "Мутагенно (положительно)",
        "Non-mutagenic (negative)": "Не мутагенно (отрицательно)",
        "High": "Высокая",
        "Low": "Низкая",
        "Highly bound (>90%)": "Сильно связывается (>90%)",
        "Moderately bound (50-90%)": "Умеренно связывается (50-90%)",
        "Weakly bound (<50%)": "Слабо связывается (<50%)",
    },
}

PROP_NAMES = {
    "en": {
        "Solubility (logS)": "Solubility (logS)",
        "SolubilityClass": "Solubility Class",
        "Caco-2 Permeability": "Caco-2 Permeability",
        "Caco-2 Class": "Caco-2 Class",
        "hERG Toxicity Risk": "hERG Toxicity Risk",
        "hERG Class": "hERG Class",
        "Lipophilicity (logD)": "Lipophilicity (logD)",
        "P-gp Inhibition": "P-gp Inhibition",
        "P-gp Class": "P-gp Class",
        "CYP3A4 Inhibition": "CYP3A4 Inhibition",
        "CYP3A4 Class": "CYP3A4 Class",
        "CYP2D6 Inhibition": "CYP2D6 Inhibition",
        "CYP2D6 Class": "CYP2D6 Class",
        "Ames Mutagenicity": "Ames Mutagenicity",
        "Ames Class": "Ames Class",
        "Bioavailability": "Bioavailability",
        "Bioavailability Class": "Bioavailability Class",
        "PPB (plasma binding)": "PPB (plasma binding)",
        "PPB Class": "PPB Class",
    },
    "ru": {
        "Solubility (logS)": "Растворимость (logS)",
        "SolubilityClass": "Класс растворимости",
        "Caco-2 Permeability": "Проницаемость Caco-2",
        "Caco-2 Class": "Класс Caco-2",
        "hERG Toxicity Risk": "Риск токс. hERG",
        "hERG Class": "Класс hERG",
        "Lipophilicity (logD)": "Липофильность (logD)",
        "P-gp Inhibition": "Ингибирование P-gp",
        "P-gp Class": "Класс P-gp",
        "CYP3A4 Inhibition": "Ингибирование CYP3A4",
        "CYP3A4 Class": "Класс CYP3A4",
        "CYP2D6 Inhibition": "Ингибирование CYP2D6",
        "CYP2D6 Class": "Класс CYP2D6",
        "Ames Mutagenicity": "Мутагенность Ames",
        "Ames Class": "Класс Ames",
        "Bioavailability": "Биодоступность",
        "Bioavailability Class": "Класс биодоступности",
        "PPB (plasma binding)": "Связь с белками плазмы",
        "PPB Class": "Класс PPB",
    },
}

MODEL_NAMES = {
    "en": {
        "solubility": "Solubility (logS)",
        "caco2": "Caco-2 Permeability",
        "herg": "hERG Toxicity",
        "lipophilicity": "Lipophilicity (logD)",
        "pgp": "P-gp Inhibition",
        "cyp3a4": "CYP3A4 Inhibition",
        "cyp2d6": "CYP2D6 Inhibition",
        "ames": "Ames Mutagenicity",
        "bioavailability": "Bioavailability",
        "ppbr": "PPB (plasma binding)",
    },
    "ru": {
        "solubility": "Растворимость (logS)",
        "caco2": "Проницаемость Caco-2",
        "herg": "Токсичность hERG",
        "lipophilicity": "Липофильность (logD)",
        "pgp": "Ингибирование P-gp",
        "cyp3a4": "Ингибирование CYP3A4",
        "cyp2d6": "Ингибирование CYP2D6",
        "ames": "Мутагенность Ames",
        "bioavailability": "Биодоступность",
        "ppbr": "Связь с белками плазмы",
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    val = STRINGS.get(lang, STRINGS["en"]).get(key, key)
    if kwargs:
        try:
            return val.format(**kwargs)
        except KeyError:
            return val
    return val


def translate_class(val: str, lang: str = "en") -> str:
    return CLASS_TRANSLATIONS.get(lang, CLASS_TRANSLATIONS["en"]).get(val, val)


def translate_prop_name(val: str, lang: str = "en") -> str:
    return PROP_NAMES.get(lang, PROP_NAMES["en"]).get(val, val)


def translate_model_name(key: str, lang: str = "en") -> str:
    return MODEL_NAMES.get(lang, MODEL_NAMES["en"]).get(key, key)


def get_lang() -> str:
    import streamlit as st
    return st.session_state.get("lang", "ru")


def sidebar_lang_selector():
    import streamlit as st
    lang = get_lang()
    selected = st.selectbox(
        STRINGS[lang]["lang_selector"],
        options=["ru", "en"],
        format_func=lambda x: "Русский" if x == "ru" else "English",
        key="lang_select",
    )
    if selected != st.session_state.get("lang"):
        st.session_state.lang = selected
        st.rerun()
