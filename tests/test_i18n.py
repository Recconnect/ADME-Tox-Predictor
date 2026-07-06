import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.i18n import t, translate_class, translate_prop_name, translate_model_name, STRINGS


def test_all_keys_present():
    en_keys = set(STRINGS["en"].keys())
    ru_keys = set(STRINGS["ru"].keys())
    missing_in_ru = en_keys - ru_keys
    missing_in_en = ru_keys - en_keys
    assert not missing_in_ru, f"Missing keys in ru: {missing_in_ru}"
    assert not missing_in_en, f"Missing keys in en: {missing_in_en}"


def test_t_function_en():
    assert t("app_title", "en") == "ADMETox.AI \u2014 AI Drug Screener"
    assert t("single_button", "en") == "Analyze"


def test_t_function_ru():
    title = t("app_title", "ru")
    assert isinstance(title, str) and len(title) > 0
    button = t("single_button", "ru")
    assert button == "Анализировать"


def test_t_with_format():
    msg = t("batch_spinner", "en", n=5)
    assert "5" in msg
    msg_ru = t("batch_spinner", "ru", n=10)
    assert "10" in msg_ru


def test_translate_class():
    assert translate_class("Soluble", "en") == "Soluble"
    assert translate_class("Soluble", "ru") == "Растворимо"
    assert translate_class("High permeability", "ru") == "Высокая проницаемость"
    assert translate_class("Unknown class", "ru") == "Unknown class"


def test_translate_prop_name():
    ru = translate_prop_name("Solubility (logS)", "ru")
    assert "Растворимость" in ru
    assert translate_prop_name("Solubility (logS)", "en") == "Water Solubility"


def test_translate_model_name():
    assert translate_model_name("solubility", "ru") == "Растворимость в воде"
    assert translate_model_name("caco2", "ru") == "Проницаемость кишечника (Caco-2)"
    assert translate_model_name("herg", "ru") == "Безопасность для сердца (hERG)"
    assert translate_model_name("solubility", "en") == "Water Solubility"


def test_fallback_key():
    assert t("nonexistent_key", "en") == "nonexistent_key"


def test_all_model_names_present():
    expected = {"solubility", "caco2", "herg", "lipophilicity", "pgp"}
    for m in expected:
        assert translate_model_name(m, "en") != m or m in STRINGS["en"]
