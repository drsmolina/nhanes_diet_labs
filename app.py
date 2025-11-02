# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="If You Eat This...", page_icon="🥦", layout="centered")

# -----------------------------------------
# Load data
# -----------------------------------------
model_path = Path("reports/model_results.csv")
df = pd.read_csv(model_path)

st.title("🥦 What You Eat, What Your Labs Say")
st.caption("Based on NHANES 2017–2018 | Weighted regression models (HC3 robust SEs)")
st.markdown("---")

# -----------------------------------------
# Define baseline lab values (approximate)
# -----------------------------------------
base_values = {
    "hba1c": 5.5,   # %
    "hdl": 55.0,    # mg/dL
    "hscrp": 1.2    # mg/L
}

# Create lookup tables for coefficients
coeff = {
    "hba1c": df[df["outcome"] == "hba1c"].set_index("term")["beta"].to_dict(),
    "hdl": df[df["outcome"] == "hdl"].set_index("term")["beta"].to_dict(),
    "hscrp": df[df["outcome"] == "hscrp"].set_index("term")["beta"].to_dict()
}

# -----------------------------------------
# Tabs
# -----------------------------------------
tab1, tab2 = st.tabs(["📊 Explore", "💡 Insights"])

# -----------------------------------------
# TAB 1 — Explore
# -----------------------------------------
with tab1:
    st.sidebar.header("Adjust your diet 👇")
    fiber = st.sidebar.slider("Fiber density (g / 1000 kcal)", -2.0, 2.0, 0.0, 0.1)
    sugar = st.sidebar.slider("Added sugar % kcal", -2.0, 2.0, 0.0, 0.1)
    fat = st.sidebar.slider("Fat % kcal", -2.0, 2.0, 0.0, 0.1)
    carb = st.sidebar.slider("Carb % kcal", -2.0, 2.0, 0.0, 0.1)
    bmi = st.sidebar.slider("Body Mass Index (SD from mean)", -2.0, 2.0, 0.0, 0.1)
    age = st.sidebar.slider("Age (SD from mean)", -2.0, 2.0, 0.0, 0.1)
    st.sidebar.markdown("---")
    st.sidebar.caption("Each slider = ±1 SD from NHANES adult average values.")

    def predict_lab(outcome):
        """Predict lab change given slider inputs."""
        c = coeff[outcome]
        base = base_values[outcome]
        terms = ["fiber_density", "sugar_pct", "fat_pct", "carb_pct", "bmi", "age"]
        delta = sum(c.get(term, 0) * val for term, val in zip(terms, [fiber, sugar, fat, carb, bmi, age]))
        return base + delta

    labs = {k: predict_lab(k) for k in ["hba1c", "hdl", "hscrp"]}

    st.subheader("Predicted Lab Markers (±1 SD changes)")

    def lab_card(title, baseline, predicted, units, higher_is_better):
        change = predicted - baseline
        color = "#5cb85c" if (change > 0 and higher_is_better) or (change < 0 and not higher_is_better) else "#d9534f"
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=predicted,
            delta={"reference": baseline, "increasing": {"color": color}, "decreasing": {"color": color}},
            title={"text": f"<b>{title}</b><br>{units}"},
            number={"font": {"size": 40}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        lab_card("HbA1c", base_values["hba1c"], labs["hba1c"], "%", higher_is_better=False)
    with col2:
        lab_card("HDL", base_values["hdl"], labs["hdl"], "mg/dL", higher_is_better=True)
    with col3:
        lab_card("hs-CRP", base_values["hscrp"], labs["hscrp"], "mg/L", higher_is_better=False)

    st.markdown("---")
    st.image("figures/forest_models.png", caption="Regression forest plot (weighted, HC3 SEs)")
    st.image("figures/scatter_carb_hba1c.png", caption="Carb % vs HbA1c (colored by fiber density)")
    st.image("figures/corr_heatmap.png", caption="Nutrient–biomarker correlation heatmap")
    st.image("figures/pca_biplot.png", caption="PCA of nutrient densities (colored by HbA1c)")

# -----------------------------------------
# TAB 2 — Insights
# -----------------------------------------
with tab2:
    st.header("💡 What Do These Numbers Mean?")
    st.write("""
    This model uses NHANES data to show **how average shifts in diet** (measured in standard deviations, or SDs)
    can influence key lab biomarkers.  
    Each 1 SD roughly equals:
    - **+1 SD Fiber Density:** ≈ +7 grams more fiber per 1000 kcal (think: 2 more cups of veggies or 1 cup beans)
    - **+1 SD Sugar % kcal:** ≈ +8% more calories from added sugars (think: 2 cans of soda per day)
    - **+1 SD Fat % kcal:** ≈ +6% more fat calories (replacing refined carbs with fats like olive oil)
    - **+1 SD Carb % kcal:** ≈ +6% more carb calories (reducing protein/fat proportionally)
    """)

    st.subheader("🔬 Biomarker Cheat Sheet")
    st.markdown("""
    **HbA1c (Glycated Hemoglobin)**  
    Reflects average blood sugar over ~3 months.  
    - Lower = better glucose control.  
    - Typical healthy: 5.0–5.6%.  
    - Often rises with high sugar intake or excess calories.

    **HDL (High-Density Lipoprotein)**  
    “Good cholesterol.”  
    - Higher = protective against heart disease.  
    - Boosted by healthy fats and fiber; lowered by high sugar diets.

    **hs-CRP (High-Sensitivity C-Reactive Protein)**  
    Marker of inflammation.  
    - Lower = less chronic inflammation.  
    - Higher with obesity, smoking, poor diet, or infection.
    """)

    st.subheader("🧭 Interpreting Your Predictions")
    st.info("""
    This dashboard does **not** predict your personal lab values — it shows **average statistical shifts** seen across thousands of U.S. adults.
    It helps illustrate how population-level diet trends link to metabolic health, not diagnose individuals.
    """)

    st.subheader("📚 Data Source")
    st.caption("""
    • National Health and Nutrition Examination Survey (NHANES 2017–2018)  
    • CDC / NCHS public data: dietary recall (WWEIA/FNDDS) + laboratory panels  
    • Analysis and visualization by **Daphne Rose Molina**  
    • Educational use only – not medical advice
    """)
