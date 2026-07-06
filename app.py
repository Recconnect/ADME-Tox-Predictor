import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.predict import ADMETPredictor
from src.features import compute_rdkit_descriptors
from src.feature_importance import get_model_feature_importance
from src.config import VALIDATION_DRUGS, logger, MAX_UPLOAD_MB


def check_lipinski_rule_of_five(desc: dict | None) -> dict:
    if desc is None:
        return {"passed": False, "violations": [], "detail": "No descriptors"}
    violations = []
    if desc.get("MolWt", 0) > 500:
        violations.append(f"MolWt={desc['MolWt']:.0f} > 500")
    if desc.get("LogP", 0) > 5:
        violations.append(f"LogP={desc['LogP']:.2f} > 5")
    if desc.get("NumHDonors", 0) > 5:
        violations.append(f"HDonors={desc['NumHDonors']} > 5")
    if desc.get("NumHAcceptors", 0) > 10:
        violations.append(f"HAcceptors={desc['NumHAcceptors']} > 10")
    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "detail": f"{len(violations)} violation(s): " + "; ".join(violations) if violations else "Passes Lipinski Rule of Five",
    }


def color_class(val: str) -> str:
    good = {"Soluble", "High permeability", "Safe (low risk)"}
    bad = {"Poorly soluble", "Low permeability", "Toxic (high risk)"}
    if val in good:
        return "#00c853"
    if val in bad:
        return "#ff1744"
    return "#ffc107"


st.set_page_config(
    page_title="ADMETox.AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ADME/Tox Predictor")
st.markdown("AI-powered ADME/Tox screening for drug discovery. [ADMETox.AI](https://admetox.ai)")

@st.cache_resource
def get_predictor():
    predictor = ADMETPredictor()
    if not predictor.is_ready:
        st.error(
            "Models not found. Train first via: python run_train.py"
        )
    return predictor

predictor = get_predictor()

if not predictor.is_ready:
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Single Prediction", "Batch Prediction", "Validation", "Feature Importance"])

with tab1:
    st.header("Single Molecule Prediction")

    smiles = st.text_input(
        "Enter SMILES",
        placeholder="CCO",
        key="single_smiles",
        help="Enter a valid SMILES string (e.g., CCO for ethanol)",
    )

    if st.button("Predict", type="primary") and smiles:
        with st.spinner("Computing properties..."):
            result = predictor.predict_single(smiles)

        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Prediction complete!")

            prop_cols = st.columns(3)
            col_idx = 0
            prop_keys = [
                "Solubility (logS)", "SolubilityClass",
                "Caco-2 Permeability", "Caco-2 Class",
                "hERG Toxicity Risk", "hERG Class",
            ]
            for key in prop_keys:
                if key in result:
                    with prop_cols[col_idx % 3]:
                        val = result[key]
                        display = f"{val:.3f}" if isinstance(val, float) else str(val)
                        if "Class" in key:
                            bg = color_class(str(val))
                            st.markdown(
                                f'<div style="padding:12px;border-radius:8px;background:{bg}20;'
                                f'border-left:4px solid {bg}">'
                                f'<small>{key}</small><br><strong>{display}</strong></div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.metric(key, display)
                    col_idx += 1

            lipinski = check_lipinski_rule_of_five(
                {k: v for k, v in result.items() if k in {
                    "MolWt", "LogP", "NumHDonors", "NumHAcceptors",
                }}
            )
            if not lipinski["passed"]:
                st.warning(f"Lipinski Rule of Five: {lipinski['detail']}")
            else:
                st.info(f"Lipinski Rule of Five: {lipinski['detail']}")

            with st.expander("View all RDKit descriptors"):
                desc_keys = [
                    k for k in result.keys()
                    if k not in prop_keys + ["error", "SMILES"]
                ]
                desc_data = {k: result[k] for k in desc_keys if k in result}
                if desc_data:
                    desc_df = pd.DataFrame([desc_data]).T.reset_index()
                    desc_df.columns = ["Descriptor", "Value"]
                    st.dataframe(desc_df, width="stretch")

with tab2:
    st.header("Batch Prediction")

    input_method = st.radio(
        "Input method:", ["Manual input", "Upload CSV"], horizontal=True
    )

    if input_method == "Manual input":
        batch_smiles = st.text_area(
            "SMILES (one per line)",
            placeholder="CCO\nCC(=O)Oc1ccccc1C(=O)O\nCC(C)Cc1ccc(C(C)C(=O)O)cc1",
            height=200,
        )

        if st.button("Predict Batch", type="primary") and batch_smiles:
            smiles_list = [s.strip() for s in batch_smiles.split("\n") if s.strip()]
            with st.spinner(f"Predicting {len(smiles_list)} molecules..."):
                results = predictor.predict_batch(smiles_list)
            df = pd.DataFrame(results)
            df.insert(0, "SMILES", smiles_list[:len(df)])
            for col in ["SolubilityClass", "Caco-2 Class", "hERG Class"]:
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda v: f'<span style="color:{color_class(str(v))};font-weight:700">{v}</span>'
                    )
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.download_button(
                "Download CSV", df.to_csv(index=False).encode("utf-8"),
                "predictions.csv", "text/csv",
            )

    else:
        uploaded_file = st.file_uploader(
            "Upload CSV with a 'SMILES' column",
            type=["csv"],
        )
        if uploaded_file is not None:
            if uploaded_file.size > MAX_UPLOAD_MB * 1024 * 1024:
                st.error(f"File too large. Max {MAX_UPLOAD_MB} MB.")
                st.stop()

            df_input = pd.read_csv(uploaded_file)
            if "SMILES" not in df_input.columns:
                st.error("CSV must contain a 'SMILES' column")
                st.stop()

            smiles_list = df_input["SMILES"].dropna().astype(str).str.strip().tolist()
            with st.spinner(f"Predicting {len(smiles_list)} molecules..."):
                results = predictor.predict_batch(smiles_list)
            df_output = pd.DataFrame(results)
            df_output.insert(0, "SMILES", smiles_list[:len(df_output)])
            for col in ["SolubilityClass", "Caco-2 Class", "hERG Class"]:
                if col in df_output.columns:
                    df_output[col] = df_output[col].apply(
                        lambda v: f'<span style="color:{color_class(str(v))};font-weight:700">{v}</span>'
                    )
            st.markdown(df_output.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.download_button(
                "Download CSV", df_output.to_csv(index=False).encode("utf-8"),
                "predictions.csv", "text/csv",
            )

with tab3:
    st.header("Validation on Known Drugs")

    if st.button("Run Validation", type="primary"):
        with st.spinner(f"Validating on {len(VALIDATION_DRUGS)} known drugs..."):
            df_val = predictor.predict_validated(VALIDATION_DRUGS)

        if not df_val.empty:
            display_cols = [
                "Drug", "Solubility (logS)", "SolubilityClass",
                "Caco-2 Permeability", "Caco-2 Class",
                "hERG Toxicity Risk", "hERG Class",
            ]
            display_cols = [c for c in display_cols if c in df_val.columns]
            df_display = df_val[display_cols].copy()
            for col in ["SolubilityClass", "Caco-2 Class", "hERG Class"]:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(
                        lambda v: f'<span style="color:{color_class(str(v))};font-weight:700">{v}</span>'
                    )
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
            st.json(summary)

            st.download_button(
                "Download Validation CSV",
                df_val.to_csv(index=False).encode("utf-8"),
                "validation_results.csv", "text/csv",
            )

with tab4:
    st.header("Feature Importance")
    st.markdown("Top-10 RDKit descriptors driving each model's predictions:")

    model_names = {
        "solubility": "Solubility (logS)",
        "caco2": "Caco-2 Permeability",
        "herg": "hERG Toxicity",
    }

    for key, label in model_names.items():
        imp = get_model_feature_importance(key)
        if imp is None:
            st.warning(f"Feature importance not available for {label}")
            continue
        with st.expander(f"{label} — Top 10 Descriptors", expanded=False):
            df = pd.DataFrame(imp["descriptor_importance"])
            df.columns = ["Descriptor", "Importance"]
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.caption(f"Fingerprint total importance: {imp['fingerprint_total_importance']:.2f}")

with st.sidebar:
    st.header("About ADMETox.AI")
    st.markdown("""
**AI-powered ADME/Tox screening**

| Property | Metric |
|---|---|
| Solubility | R² = **0.806** |
| Caco-2 | AUC = **0.932** |
| hERG | AUC = **0.846** |

Built with LightGBM + RDKit
""")
    st.header("Lipinski Rule of Five")
    st.markdown("""
- MolWt < 500
- LogP < 5
- H-Donors < 5
- H-Acceptors < 10
""")
    st.header("Example SMILES")
    st.code("Ethanol: CCO\nAspirin: CC(=O)Oc1ccccc1C(=O)O\nCaffeine: CN1C=NC2=C1C(=O)N(C(=O)N2C)C")
