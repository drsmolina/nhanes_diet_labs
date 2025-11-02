# NHANES Diet Labs Analysis  

This repository contains code and analyses for linking daily nutrient intake patterns to laboratory biomarkers (HbA1c, lipids, hs-CRP) using data from the NHANES cycles 2017–2018 and 2019–2020. The project sets up a reproducible pipeline to download raw XPT files, harmonize variables, engineer nutrient features, perform exploratory data analysis, and run survey-weighted models with robust standard errors.  

## Quickstart  

1. Clone the repository.  
2. Install dependencies with `pip install -r requirements.txt`.  
3. Run the full pipeline via:  

```
make all
```  

   which will ingest data, build features, execute EDA notebooks, run models, and generate reports.  

Alternatively, run individual steps:  

- `make ingest` – download and harmonize raw NHANES data into tidy format.  
- `make features` – engineer nutrient features and output analytic dataset.  
- `make eda` – produce exploratory figures.  
- `make model` – run weighted OLS models.  
- `make report` – generate the summary report.  

## Data Sources  

This project uses publicly available NHANES data from the National Center for Health Statistics (NCHS). Please ensure you comply with NHANES data usage policies when downloading and using these datasets. Raw data files are not committed to this repository (see `.gitignore`); they will be downloaded into `data_raw/` during ingestion.  

## Disclaimer  

This repository is for educational and research purposes only. The analyses herein do not constitute medical advice. Interpretations are based on observational survey data and should not inform medical decisions. 
