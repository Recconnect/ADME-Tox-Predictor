import io
import html
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.predict import ADMETPredictor
from src.features import compute_rdkit_descriptors, canonicalize_smiles
from src.feature_importance import get_model_feature_importance
from src.config import VALIDATION_DRUGS, logger, MAX_UPLOAD_MB
from src.i18n import t, translate_class, translate_prop_name, translate_model_name, get_lang, sidebar_lang_selector
from src.usage import get_stats
from src.radar import compute_scores, plot_radar
from src.pdf_report import generate_pdf

_CSS = """
<style>
.adme-card {
  padding: 14px 16px;
  border-radius: 10px;
  margin-bottom: 8px;
  border-left: 5px solid;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  transition: transform 0.1s;
}
.adme-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}
.adme-card .label {
  font-size: 0.8rem;
  color: #5a6a7a;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.adme-card .value {
  font-size: 1.1rem;
  font-weight: 700;
  margin-top: 2px;
}
.health-score {
  text-align: center;
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 16px;
}
.health-score .number {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1;
}
.health-score .label {
  font-size: 0.85rem;
  color: #5a6a7a;
  margin-top: 4px;
}
.health-score .desc {
  font-size: 1rem;
  font-weight: 600;
  margin-top: 2px;
}
.group-header {
  font-size: 0.95rem;
  font-weight: 600;
  color: #2c3e50;
  padding: 8px 0 4px 0;
  border-bottom: 2px solid #eef0f2;
  margin-top: 12px;
}
.progress-bg {
  height: 6px;
  background: #eef0f2;
  border-radius: 3px;
  margin-top: 6px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}
.chip-btn {
  display: inline-block;
  padding: 4px 14px;
  margin: 4px 6px 4px 0;
  border-radius: 20px;
  background: #eef0f2;
  font-size: 0.85rem;
  cursor: pointer;
  border: none;
  transition: background 0.15s;
}
.chip-btn:hover {
  background: #d5dbe0;
}
</style>
"""


def draw_molecule(smiles: str) -> bytes | None:
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        img = Draw.MolToImage(mol, size=(320, 240))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return None


def check_lipinski_rule_of_five(desc: dict | None) -> dict:
    if desc is None:
        return {"passed": False, "violations": [], "detail": "No descriptors"}
    lang = get_lang()
    violations = []
    if desc.get("MolWt", 0) > 500:
        violations.append(t("lipinski_molwt", lang, v=desc["MolWt"]))
    if desc.get("LogP", 0) > 5:
        violations.append(t("lipinski_logp", lang, v=desc["LogP"]))
    if desc.get("NumHDonors", 0) > 5:
        violations.append(t("lipinski_hdonors", lang, v=desc["NumHDonors"]))
    if desc.get("NumHAcceptors", 0) > 10:
        violations.append(t("lipinski_hacceptors", lang, v=desc["NumHAcceptors"]))
    if violations:
        detail = t("lipinski_violations", lang, n=len(violations), details="; ".join(violations))
    else:
        detail = t("lipinski_passes", lang)
    return {"passed": len(violations) == 0, "violations": violations, "detail": detail}


def color_class(val: str) -> str:
    good = {
        "Soluble", "High permeability", "Safe (low risk)", "Non-inhibitor (low risk)",
        "Non-inhibitor", "Non-mutagenic (negative)", "High",
        "Highly bound (>90%)",
    }
    bad = {
        "Poorly soluble", "Low permeability", "Toxic (high risk)", "Inhibitor (high risk)",
        "Inhibitor", "Mutagenic (positive)", "Low",
        "Weakly bound (<50%)",
    }
    if val in good:
        return "#00c853"
    if val in bad:
        return "#ff1744"
    return "#ffc107"


def compute_health_score(result: dict) -> tuple[int, str]:
    score = 0
    count = 0
    prop_checks = [
        ("Solubility (logS)", lambda v: v > -4),
        ("Caco-2 Permeability", lambda v: v > 0.5),
        ("hERG Toxicity Risk", lambda v: v < 0.5),
        ("Lipophilicity (logD)", lambda v: 0 < v < 5),
        ("P-gp Inhibition", lambda v: v < 0.5),
        ("CYP3A4 Inhibition", lambda v: v < 0.5),
        ("CYP2D6 Inhibition", lambda v: v < 0.5),
        ("Ames Mutagenicity", lambda v: v < 0.5),
        ("Bioavailability", lambda v: v > 0.5),
    ]
    for key, check in prop_checks:
        val = result.get(key)
        if val is not None:
            score += 1 if check(val) else 0
            count += 1
    pp_val = result.get("PPB (plasma binding)")
    if pp_val is not None:
        score += 1 if 50 <= pp_val <= 95 else 0
        count += 1
    pct = int(round(score / count * 100)) if count > 0 else 0
    lang = get_lang()
    if pct >= 80:
        level = t("health_excellent", lang)
    elif pct >= 60:
        level = t("health_good", lang)
    elif pct >= 40:
        level = t("health_fair", lang)
    else:
        level = t("health_poor", lang)
    return pct, level


def _prop_to_pct(key: str, result: dict) -> int | None:
    val = result.get(key)
    if val is None or not isinstance(val, (int, float)):
        return None
    ranges = {
        "Solubility (logS)": (-8, 2),
        "Caco-2 Permeability": (0, 1),
        "hERG Toxicity Risk": (0, 1),
        "Lipophilicity (logD)": (-2, 6),
        "P-gp Inhibition": (0, 1),
        "CYP3A4 Inhibition": (0, 1),
        "CYP2D6 Inhibition": (0, 1),
        "Ames Mutagenicity": (0, 1),
        "Bioavailability": (0, 1),
        "PPB (plasma binding)": (0, 100),
    }
    lo, hi = ranges.get(key, (0, 1))
    inv = key in ("hERG Toxicity Risk", "P-gp Inhibition", "CYP3A4 Inhibition", "CYP2D6 Inhibition", "Ames Mutagenicity")
    pct = (val - lo) / (hi - lo) * 100
    pct = max(0, min(100, pct))
    return 100 - int(pct) if inv else int(pct)


lang = get_lang()

st.set_page_config(
    page_title=t("app_title", lang),
    page_icon="\U0001f9ec",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(_CSS, unsafe_allow_html=True)

st.title(t("app_title", lang))
st.markdown(t("app_subtitle", lang))


@st.cache_resource
def get_predictor():
    predictor = ADMETPredictor()
    if not predictor.is_ready:
        st.error(t("errors_models_not_found", lang))
    return predictor


predictor = get_predictor()
if not predictor.is_ready:
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    t("tab_single", lang), t("tab_batch", lang),
    t("tab_validation", lang), t("tab_features", lang),
])

# ───────── Tab 1: Single Molecule ─────────
with tab1:
    st.header(t("single_header", lang))

    # Initialize selected SMILES in session state
    if "selected_smiles" not in st.session_state:
        st.session_state["selected_smiles"] = ""
    
    drug_names = sorted(VALIDATION_DRUGS.keys(), key=str.lower)
    drug_names.insert(0, "")
    selected_drug = st.selectbox(
        t("single_drug_selector", lang),
        options=drug_names,
        key="drug_selector",
    )
    if selected_drug:
        st.session_state["selected_smiles"] = VALIDATION_DRUGS[selected_drug]

    smiles = st.text_input(
        t("single_input_label", lang),
        value=st.session_state["selected_smiles"],
        placeholder="CCO",
        help=t("single_help", lang),
    )

    chips_cols = st.columns(4)
    example_drugs = {"Aspirin": VALIDATION_DRUGS["Aspirin"], "Caffeine": VALIDATION_DRUGS["Caffeine"], "Ibuprofen": VALIDATION_DRUGS["Ibuprofen"], "Paracetamol": VALIDATION_DRUGS["Paracetamol"]}
    for i, (name, smi) in enumerate(example_drugs.items()):
        if chips_cols[i % 4].button(name, key=f"chip_{name}", width="stretch"):
            st.session_state["selected_smiles"] = smi
            st.rerun()

    if st.button(t("single_button", lang), type="primary", key="predict_btn") and smiles:
        with st.spinner(t("single_spinner", lang)):
            result = predictor.predict_single(smiles)

        if "error" in result:
            st.error(result["error"])
        else:
            st.success(t("single_success", lang))

            pct, level = compute_health_score(result)
            score_color = "#00c853" if pct >= 60 else "#ffc107" if pct >= 40 else "#ff1744"
            st.markdown(
                f'<div class="health-score">'
                f'<div class="number" style="color:{score_color}">{pct}%</div>'
                f'<div class="label">{t("health_score", lang)}</div>'
                f'<div class="desc" style="color:{score_color}">{level}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

            col_left, col_right = st.columns([1, 1.6])
            with col_left:
                img_bytes = draw_molecule(smiles)
                if img_bytes:
                    st.image(img_bytes, caption=canonicalize_smiles(smiles) or smiles)

            with col_right:
                prop_keys = [
                    "Solubility (logS)", "SolubilityClass",
                    "Caco-2 Permeability", "Caco-2 Class",
                    "hERG Toxicity Risk", "hERG Class",
                    "Lipophilicity (logD)",
                    "P-gp Inhibition", "P-gp Class",
                    "CYP3A4 Inhibition", "CYP3A4 Class",
                    "CYP2D6 Inhibition", "CYP2D6 Class",
                    "Ames Mutagenicity", "Ames Class",
                    "Bioavailability", "Bioavailability Class",
                    "PPB (plasma binding)", "PPB Class",
                ]
                groups = {
                    "group_absorption": ["Solubility (logS)", "SolubilityClass", "Caco-2 Permeability", "Caco-2 Class", "Lipophilicity (logD)"],
                    "group_safety": ["hERG Toxicity Risk", "hERG Class", "Ames Mutagenicity", "Ames Class"],
                    "group_metabolism": ["P-gp Inhibition", "P-gp Class", "CYP3A4 Inhibition", "CYP3A4 Class", "CYP2D6 Inhibition", "CYP2D6 Class"],
                    "group_pk": ["Bioavailability", "Bioavailability Class", "PPB (plasma binding)", "PPB Class"],
                }
                for group_key, keys in groups.items():
                    available = [k for k in keys if k in result]
                    if not available:
                        continue
                    st.markdown(f'<div class="group-header">{t(group_key, lang)}</div>', unsafe_allow_html=True)
                    cols = st.columns(2)
                    for i2, key in enumerate(available):
                        with cols[i2 % 2]:
                            val = result[key]
                            is_class = "Class" in key
                            pct_val = _prop_to_pct(key, result)
                            bg_color = color_class(str(val)) if is_class else "#1a5276"
                            display = f"{val:.3f}" if isinstance(val, float) else str(val)
                            label = translate_prop_name(key, lang)
                            progress = (
                                f'<div class="progress-bg"><div class="progress-fill" '
                                f'style="width:{pct_val}%;background:{bg_color}"></div></div>'
                            ) if pct_val is not None else ""
                            st.markdown(
                                f'<div class="adme-card" style="border-left-color:{bg_color}">'
                                f'<div class="label">{label}</div>'
                                f'<div class="value" style="color:{bg_color}">{display}</div>'
                                f"{progress}</div>",
                                unsafe_allow_html=True,
                            )

            lipinski = check_lipinski_rule_of_five(
                {k: v for k, v in result.items() if k in {"MolWt", "LogP", "NumHDonors", "NumHAcceptors"}}
            )
            msg = t("lipinski_info", lang, detail=lipinski["detail"])
            if not lipinski["passed"]:
                st.warning(msg)
            else:
                st.info(msg)

            scores = compute_scores({k: v for k, v in result.items() if isinstance(v, (int, float))})
            if any(s > 0 for s in scores):
                fig = plot_radar(scores, lang)
                st.caption(t("radar_title", lang))
                st.pyplot(fig)

            if st.download_button(
                t("pdf_download", lang),
                data=generate_pdf(smiles, result, lang),
                file_name=f"admetox_{smiles[:20]}.pdf".replace("/", "_"),
                mime="application/pdf",
            ):
                pass

            with st.expander(t("single_expander", lang)):
                prop_keys_set = set(prop_keys)
                desc_keys = [k for k in result.keys() if k not in prop_keys_set | {"error", "SMILES"}]
                desc_data = {k: result[k] for k in desc_keys if k in result}
                if desc_data:
                    desc_df = pd.DataFrame([desc_data]).T.reset_index()
                    desc_df.columns = [t("desc_col_name", lang), t("desc_col_value", lang)]
                    st.dataframe(desc_df, width="stretch")

# ───────── Tab 2: Batch ─────────
with tab2:
    st.header(t("batch_header", lang))
    input_method = st.radio(
        t("batch_radio_label", lang),
        [t("batch_radio_manual", lang), t("batch_radio_csv", lang)],
        horizontal=True,
    )

    if input_method == t("batch_radio_manual", lang):
        batch_smiles = st.text_area(
            t("batch_textarea_label", lang),
            placeholder=t("batch_textarea_placeholder", lang),
            height=200,
        )
        if st.button(t("batch_button", lang), type="primary") and batch_smiles:
            smiles_list = [s.strip() for s in batch_smiles.split("\n") if s.strip()]
            with st.spinner(t("batch_spinner", lang, n=len(smiles_list))):
                results = predictor.predict_batch(smiles_list)
            df = pd.DataFrame(results)
            df.insert(0, "SMILES", smiles_list[:len(df)])
            for col in ["SolubilityClass", "Caco-2 Class", "hERG Class", "P-gp Class"]:
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda v, c=col: f'<span style="color:{color_class(str(v))};font-weight:700">'
                        f'{translate_class(str(v), lang)}</span>'
                    )
                    df = df.rename(columns={col: translate_prop_name(col, lang)})
            df_to_show = df.copy()
            if "SMILES" in df_to_show.columns:
                df_to_show["SMILES"] = df_to_show["SMILES"].apply(html.escape)
            st.markdown(df_to_show.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.download_button(
                t("batch_download", lang), df.to_csv(index=False).encode("utf-8"),
                "predictions.csv", "text/csv",
            )
    else:
        uploaded_file = st.file_uploader(
            t("batch_uploader", lang), type=["csv"],
        )
        if uploaded_file is not None:
            if uploaded_file.size > MAX_UPLOAD_MB * 1024 * 1024:
                st.error(t("batch_error_size", lang, n=MAX_UPLOAD_MB))
                st.stop()
            raw_bytes = uploaded_file.read()
            try:
                raw_text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                st.error("File must be UTF-8 encoded.")
                st.stop()
            if "\x00" in raw_text:
                st.error("File contains invalid null bytes.")
                st.stop()
            if len(raw_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
                st.error(t("batch_error_size", lang, n=MAX_UPLOAD_MB))
                st.stop()
            uploaded_file.seek(0)
            df_input = pd.read_csv(uploaded_file)
            if df_input.shape[1] > 100:
                st.error("CSV has too many columns (max 100).")
                st.stop()
            if "SMILES" not in df_input.columns:
                st.error(t("batch_error_column", lang))
                st.stop()
            smiles_list = df_input["SMILES"].dropna().astype(str).str.strip().tolist()
            if len(smiles_list) > 10000:
                st.error("Too many rows (max 10000).")
                st.stop()
            with st.spinner(t("batch_spinner", lang, n=len(smiles_list))):
                results = predictor.predict_batch(smiles_list)
            df_output = pd.DataFrame(results)
            df_output.insert(0, "SMILES", smiles_list[:len(df_output)])
            for col in ["SolubilityClass", "Caco-2 Class", "hERG Class", "P-gp Class"]:
                if col in df_output.columns:
                    df_output[col] = df_output[col].apply(
                        lambda v: f'<span style="color:{color_class(str(v))};font-weight:700">'
                        f'{translate_class(str(v), lang)}</span>'
                    )
                    df_output = df_output.rename(columns={col: translate_prop_name(col, lang)})
            df_to_show = df_output.copy()
            if "SMILES" in df_to_show.columns:
                df_to_show["SMILES"] = df_to_show["SMILES"].apply(html.escape)
            st.markdown(df_to_show.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.download_button(
                t("batch_download", lang), df_output.to_csv(index=False).encode("utf-8"),
                "predictions.csv", "text/csv",
            )

# ───────── Tab 3: Validation / Known Drugs ─────────
with tab3:
    st.header(t("val_header", lang))
    if st.button(t("val_button", lang), type="primary"):
        with st.spinner(t("val_spinner", lang, n=len(VALIDATION_DRUGS))):
            df_val = predictor.predict_validated(VALIDATION_DRUGS)
        if not df_val.empty:
            display_cols = [
                "Drug", "Solubility (logS)", "SolubilityClass",
                "Caco-2 Permeability", "Caco-2 Class",
                "hERG Toxicity Risk", "hERG Class",
                "Lipophilicity (logD)",
                "P-gp Inhibition", "P-gp Class",
            ]
            display_cols = [c for c in display_cols if c in df_val.columns]
            df_display = df_val[display_cols].copy()
            for col in ["SolubilityClass", "Caco-2 Class", "hERG Class", "P-gp Class"]:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(
                        lambda v: f'<span style="color:{color_class(str(v))};font-weight:700">'
                        f'{translate_class(str(v), lang)}</span>'
                    )
                    df_display = df_display.rename(columns={col: translate_prop_name(col, lang)})
            rename_map = {k: translate_prop_name(k, lang) for k in df_display.columns if k != "Drug"}
            df_display = df_display.rename(columns=rename_map)
            df_to_show = df_display.copy()
            if "Drug" in df_to_show.columns:
                df_to_show["Drug"] = df_to_show["Drug"].apply(html.escape)
            st.markdown(df_to_show.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.subheader("Summary" if lang == "en" else "Сводка")
            sc1, sc2, sc3, sc4, sc5 = st.columns(5)
            n_drugs = len(df_val)
            if "Solubility (logS)" in df_val.columns:
                avg = round(df_val["Solubility (logS)"].mean(), 3)
                sc1.metric("Avg Water Solubility" if lang == "en" else "Ср. растворимость", avg)
            if "Caco-2 Class" in df_val.columns:
                high = (df_val["Caco-2 Class"] == "High permeability").sum()
                sc2.metric("High Gut Absorption" if lang == "en" else "Высокое всасывание", f"{high}/{n_drugs}")
            if "hERG Class" in df_val.columns:
                toxic = (df_val["hERG Class"] == "Toxic (high risk)").sum()
                sc3.metric("Cardiotoxicity Risk" if lang == "en" else "Риск для сердца", f"{toxic}/{n_drugs}")
            if "Lipophilicity (logD)" in df_val.columns:
                avg = round(df_val["Lipophilicity (logD)"].mean(), 3)
                sc4.metric("Avg Fat Solubility" if lang == "en" else "Ср. жирорастворимость", avg)
            if "P-gp Class" in df_val.columns:
                inhib = (df_val["P-gp Class"] == "Inhibitor (high risk)").sum()
                sc5.metric("Drug Resistance Risk" if lang == "en" else "Риск устойчивости", f"{inhib}/{n_drugs}")
            st.download_button(
                t("val_download", lang),
                df_val.to_csv(index=False).encode("utf-8"),
                "validation_results.csv", "text/csv",
            )

# ───────── Tab 4: How It Works ─────────
with tab4:
    st.header(t("fi_header", lang))
    st.markdown(t("fi_subtitle", lang))
    for key in ["solubility", "caco2", "herg", "lipophilicity", "pgp"]:
        imp = get_model_feature_importance(key)
        if imp is None:
            st.warning(t("fi_not_available", lang, label=translate_model_name(key, lang)))
            continue
        with st.expander(
            t("fi_expander", lang, label=translate_model_name(key, lang)),
            expanded=False,
        ):
            df = pd.DataFrame(imp["descriptor_importance"])
            df.columns = [t("fi_col_name", lang), t("fi_col_importance", lang)]
            st.dataframe(df, hide_index=True, width="stretch")
            st.caption(t("fi_caption", lang, value=f"{imp['fingerprint_total_importance']:.2f}"))

# ───────── Sidebar ─────────
with st.sidebar:
    sidebar_lang_selector()
    st.header(t("sidebar_about", lang))
    metrics_table = f"""
| {t('sidebar_property', lang)} | {t('sidebar_metric', lang)} |
|---|---|
| {translate_model_name('solubility', lang)} | R² = **0.806** |
| {translate_model_name('caco2', lang)} | AUC = **0.932** |
| {translate_model_name('herg', lang)} | AUC = **0.846** |
| {translate_model_name('lipophilicity', lang)} | R² = **0.651** |
| {translate_model_name('pgp', lang)} | AUC = **0.964** |
| {translate_model_name('cyp3a4', lang)} | AUC = **0.903** |
| {translate_model_name('cyp2d6', lang)} | AUC = **0.883** |
| {translate_model_name('ames', lang)} | AUC = **0.884** |
| {translate_model_name('bioavailability', lang)} | AUC = **0.701** |
| {translate_model_name('ppbr', lang)} | R² = **0.425** |
    """
    st.markdown(metrics_table)
    st.header(t("sidebar_lipinski", lang))
    st.markdown(t("sidebar_lipinski_rules", lang))
    st.header(t("sidebar_examples", lang))
    st.code(t("sidebar_examples_code", lang))

    with st.expander(t("usage_title", lang)):
        try:
            stats = get_stats(30)
            st.metric(t("usage_total", lang), stats["total_predictions"])
            st.metric(t("usage_7d", lang), stats["predictions_7d"])
            if stats["unique_users"]:
                st.metric(t("usage_users", lang), stats["unique_users"])
            if stats["avg_latency_ms"]:
                st.metric(t("usage_latency", lang), f"{stats['avg_latency_ms']:.0f} ms")
        except Exception:
            pass
