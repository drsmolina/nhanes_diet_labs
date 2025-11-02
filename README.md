# 🥦 What You Eat, What Your Labs Say  
**An interactive dashboard linking diet patterns to lab biomarkers**  
*Built with NHANES 2017–2018 data and Streamlit*

![App Screenshot](figures/forest_models.png)

---

## 🌍 Live Demo
**👉 Try the interactive site:**  
[https://nhanesdietlabs.streamlit.app)

Explore how changing your diet (fiber, sugar, fat, carbs, BMI, age) influences predicted lab markers —  
**HbA1c**, **HDL**, and **hs-CRP** — based on real U.S. national data.  

---

## 📘 Overview
This project analyzes NHANES data to reveal how everyday nutrient intake patterns relate to key health biomarkers.  
It merges dietary recall (WWEIA/FNDDS) and lab data (HbA1c, HDL, hs-CRP), builds weighted regression models, and then turns them into an interactive tool.

---

## 🧩 Pipeline
1. **Ingestion & Harmonization**  
   Load and merge DEMO, DR1TOT, GHB, HDL, HSCRP, and BMX data.  
2. **Feature Engineering**  
   Compute normalized nutrient metrics (fiber density, sodium density, %kcal carbs/fats/protein).  
3. **Exploratory Data Analysis**  
   Generate histograms, correlation maps, PCA nutrient plots.  
4. **Modeling**  
   Weighted least squares with robust HC3 SEs for HbA1c, HDL, and hs-CRP.  
5. **Interactive Visualization**  
   Streamlit web app with real-time predictions and educational “Insights” tab.

---

## 💡 Key Findings
| Outcome | Predictor | Direction | Meaning |
|----------|------------|------------|----------|
| **HbA1c** | Higher added sugar | 🔺 | Higher average blood sugar |
| **HbA1c** | Higher fiber | 🔻 | Better glycemic control |
| **HDL** | Higher sugar intake | 🔻 | Lower “good” cholesterol |
| **HDL** | Higher fat & fiber | 🔺 | Healthier lipid profile |
| **hs-CRP** | Higher BMI | 🔺 | More inflammation |
| **hs-CRP** | Higher fiber | 🔻 | Less inflammation |

---

## 📊 Outputs
| File | Description |
|------|--------------|
| `data_tidy/diet_labs_analytic.csv` | Clean analytic dataset |
| `figures/hists_labs.png` | Lab distributions |
| `figures/corr_heatmap.png` | Nutrient–lab correlations |
| `figures/scatter_carb_hba1c.png` | Carbs vs HbA1c |
| `figures/pca_biplot.png` | PCA nutrient pattern |
| `figures/forest_models.png` | Regression forest plot |
| `reports/summary.md` | Narrative report |
| `app.py` | Streamlit dashboard |

---

## ⚙️ Running Locally
```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run full analysis pipeline
make all

# Launch interactive dashboard
streamlit run app.py
