# What You Eat, What Your Labs Say  
*NHANES 2017–2018 (Weighted Regression Summary)*  

This analysis linked day-1 dietary recall data from NHANES 2017–2018 to laboratory biomarkers of metabolic and cardiovascular health (HbA1c, HDL-cholesterol, and hs-CRP). After quality filtering and applying dietary weights (WTDRD1), 7,300 participants were included. Models were run using weighted least squares with HC3 robust standard errors, adjusting for age, sex, and BMI. Nutrient exposures were standardized to 1 SD for comparability.

---

## Key Findings

**Glycemic control (HbA1c):**  
Higher **BMI**, **age**, and **percent of calories from carbohydrate** were each associated with higher HbA1c, reflecting poorer long-term glucose regulation. Greater **fiber density (g/1000 kcal)** showed a weak protective trend toward lower HbA1c, consistent with improved glycemic response.

**Lipid profile (HDL-cholesterol):**  
HDL was **lower** among individuals with higher BMI and higher added-sugar intake, and **higher** among those with greater fiber and total-fat percentages. These associations align with established patterns linking refined carbohydrate intake to reduced HDL and fiber-rich diets to better lipid metabolism.

**Inflammation (hs-CRP):**  
BMI was the dominant predictor of higher hs-CRP, indicating elevated systemic inflammation with increasing adiposity. Fiber density was inversely related to hs-CRP, suggesting potential anti-inflammatory effects of high-fiber diets.

---

## Interpretation

Across models, **BMI**, **added sugar**, and **fiber** consistently differentiated healthier versus riskier metabolic profiles. Diets richer in fiber and unsaturated fats—and lower in added sugars—were associated with **better glucose, lipid, and inflammatory markers** even after adjusting for demographics.  

This project demonstrates that public NHANES data can reproducibly quantify diet-biomarker links using modern Python-based pipelines.  
*This report is for educational and analytic purposes only and does not constitute medical advice.*
