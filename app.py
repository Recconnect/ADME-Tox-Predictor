import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.predict import ADMETPredictor
from src.features import compute_rdkit_descriptors, canonicalize_smiles
from src.feature_importance import get_model_feature_importance
from src.config import VALIDATION_DRUGS, logger, MAX_UPLOAD_MB
from src.i18n import t, translate_class, translate_prop_name, translate_model_name, get_lang, sidebar_lang_selector


def draw_molecule(smiles: str) -> str | None:
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        img = Draw.MolToImage(mol, size=(300, 200))
        import io
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


lang = get_lang()

st.set_page_config(
    page_title=t("app_title", lang),
    page_icon="\U0001f9ec",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

with tab1:
    st.header(t("single_header", lang))
    smiles = st.text_input(
        t("single_input_label", lang),
        placeholder=t("single_placeholder", lang),
        key="single_smiles",
        help=t("single_help", lang),
    )

    if st.button(t("single_button", lang), type="primary") and smiles:
        with st.spinner(t("single_spinner", lang)):
            result = predictor.predict_single(smiles)

        if "error" in result:
            st.error(result["error"])
        else:
            st.success(t("single_success", lang))

            col_left, col_right = st.columns([1, 2])
            with col_left:
                img_bytes = draw_molecule(smiles)
                if img_bytes:
                    st.image(img_bytes, caption=canonicalize_smiles(smiles) or smiles, width="stretch")

            with col_right:
                prop_cols = st.columns(2)
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
                for i, key in enumerate([k for k in prop_keys if k in result]):
                    with prop_cols[i % 2]:
                        val = result[key]
                        display = f"{val:.3f}" if isinstance(val, float) else str(val)
                        if "Class" in key:
                            bg = color_class(str(val))
                            label = translate_prop_name(key, lang)
                            st.markdown(
                                f'<div style="padding:12px;border-radius:8px;background:{bg}20;'
                                f'border-left:4px solid {bg}">'
                                f'<small>{label}</small><br><strong>{display}</strong></div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.metric(translate_prop_name(key, lang), display)

            lipinski = check_lipinski_rule_of_five(
                {k: v for k, v in result.items() if k in {
                    "MolWt", "LogP", "NumHDonors", "NumHAcceptors",
                }}
            )
            msg = t("lipinski_info", lang, detail=lipinski["detail"])
            if not lipinski["passed"]:
                st.warning(msg)
            else:
                st.info(msg)

            with st.expander(t("single_expander", lang)):
                prop_keys_set = set([
                    "Solubility (logS)", "SolubilityClass",
                    "Caco-2 Permeability", "Caco-2 Class",
                    "hERG Toxicity Risk", "hERG Class",
                    "Lipophilicity (logD)", "P-gp Inhibition", "P-gp Class",
                    "CYP3A4 Inhibition", "CYP3A4 Class",
                    "CYP2D6 Inhibition", "CYP2D6 Class",
                    "Ames Mutagenicity", "Ames Class",
                    "Bioavailability", "Bioavailability Class",
                    "PPB (plasma binding)", "PPB Class",
                ])
                desc_keys = [k for k in result.keys() if k not in prop_keys_set | {"error", "SMILES"}]
                desc_data = {k: result[k] for k in desc_keys if k in result}
                if desc_data:
                    desc_df = pd.DataFrame([desc_data]).T.reset_index()
                    desc_df.columns = [t("desc_col_name", lang), t("desc_col_value", lang)]
                    st.dataframe(desc_df, width="stretch")

with tab2:
    st.header(t("batch_header", lang))
    input_method = st.radio(
        t("batch_radio_label", lang),
        [t("batch_radio_manual", lang), t("batch_radio_csv", lang)],
        horizontal=True,
    )

    if input_method == t("batch_radio_manual", lang):
        batch_smiles = st.text_area(
            "SMILES (one per line)",
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
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
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
            df_input = pd.read_csv(uploaded_file)
            if "SMILES" not in df_input.columns:
                st.error(t("batch_error_column", lang))
                st.stop()
            smiles_list = df_input["SMILES"].dropna().astype(str).str.strip().tolist()
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
            st.markdown(df_output.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.download_button(
                t("batch_download", lang), df_output.to_csv(index=False).encode("utf-8"),
                "predictions.csv", "text/csv",
            )

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
            st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
            summary = {}
            if "Solubility (logS)" in df_val.columns:
                summary["Avg LogS"] = round(df_val["Solubility (logS)"].mean(), 3)
            if "Caco-2 Class" in df_val.columns:
                high = (df_val["Caco-2 Class"] == "High permeability").sum()
                summary["High Caco-2"] = f"{high}/{len(df_val)}"
            if "hERG Class" in df_val.columns:
                toxic = (df_val["hERG Class"] == "Toxic (high risk)").sum()
                summary["hERG Toxic"] = f"{toxic}/{len(df_val)}"
            if "Lipophilicity (logD)" in df_val.columns:
                summary["Avg LogD"] = round(df_val["Lipophilicity (logD)"].mean(), 3)
            if "P-gp Class" in df_val.columns:
                inhib = (df_val["P-gp Class"] == "Inhibitor (high risk)").sum()
                summary["P-gp Inhibitors"] = f"{inhib}/{len(df_val)}"
            st.json(summary)
            st.download_button(
                t("val_download", lang),
                df_val.to_csv(index=False).encode("utf-8"),
                "validation_results.csv", "text/csv",
            )

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
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.caption(t("fi_caption", lang, value=f"{imp['fingerprint_total_importance']:.2f}"))

with st.sidebar:
    sidebar_lang_selector()
    st.header(t("sidebar_about", lang))
    metrics_table = f"""
**{t('sidebar_about', lang)}**

| {t('sidebar_property', lang)} | {t('sidebar_metric', lang)} |
|---|---|---|
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

{t('sidebar_built_with', lang)}
"""
    st.markdown(metrics_table)
    st.header(t("sidebar_lipinski", lang))
    st.markdown(t("sidebar_lipinski_rules", lang))
    st.header(t("sidebar_examples", lang))
    st.code(t("sidebar_examples_code", lang))
