import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.predict import ADMETPredictor
from src.features import compute_rdkit_descriptors
from src.config import VALIDATION_DRUGS, logger, MAX_UPLOAD_MB

st.set_page_config(
    page_title="ADME/Tox Predictor v2.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ADME/Tox Predictor v2.0")
st.markdown("AI-powered ADME/Tox screening for drug discovery")

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

tab1, tab2, tab3 = st.tabs(["Single Prediction", "Batch Prediction", "Validation"])

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
                        st.metric(key, f"{val:.3f}" if isinstance(val, float) else str(val))
                    col_idx += 1

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
            st.dataframe(df, width="stretch")
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
            st.dataframe(df_output, width="stretch")
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
            st.dataframe(df_val[display_cols], width="stretch")

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

with st.sidebar:
    st.header("About")
    st.markdown("""
**ADME/Tox Predictor v2.0**

Predicts:
- Solubility (R²=0.826)
- Caco-2 Permeability (Acc=83%)
- hERG Toxicity (AUC=0.873)

Built with LightGBM + RDKit descriptors
""")
    st.header("Example SMILES")
    st.code("Ethanol: CCO\nAspirin: CC(=O)Oc1ccccc1C(=O)O\nCaffeine: CN1C=NC2=C1C(=O)N(C(=O)N2C)C")
