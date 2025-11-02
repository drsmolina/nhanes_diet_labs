# src/build_features.py
import argparse
from pathlib import Path
import pandas as pd
import yaml
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Feature engineering for NHANES diet-lab dataset")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    tidy_path = Path(config["paths"]["tidy"]) / "nhanes_raw_merged.parquet"
    df = pd.read_parquet(tidy_path)
    print(f"Loaded {len(df)} rows from {tidy_path}")

    # --- Basic cleaning ---
    df = df.copy()
    df = df.replace({".": np.nan, " ": np.nan})
    numeric_cols = [
        "energy_kcal", "carbs_g", "protein_g", "fat_g",
        "fiber_g", "added_sugar_g", "sodium_mg",
        "hba1c", "hscrp", "hdl", "trig", "bmi"
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # --- Derived nutrient features ---
    df["carb_pct"] = 4 * df["carbs_g"] / df["energy_kcal"]
    df["protein_pct"] = 4 * df["protein_g"] / df["energy_kcal"]
    df["fat_pct"] = 9 * df["fat_g"] / df["energy_kcal"]
    df["fiber_density"] = df["fiber_g"] / (df["energy_kcal"] / 1000)
    df["sugar_pct"] = 4 * df["added_sugar_g"] / df["energy_kcal"]
    df["sodium_density"] = df["sodium_mg"] / (df["energy_kcal"] / 2000)

    # --- Encode sex ---
    df["sex_female"] = np.where(df["sex"] == 2, 1, 0)

    # --- Normalize dietary weights ---
    df["wt_diet_day1"] = df["WTDRD1"] / np.nanmean(df["WTDRD1"])

    # --- Outlier filters ---
    df["energy_outlier"] = ~df["energy_kcal"].between(500, 6000)
    df["lab_outlier"] = df["hba1c"] > 15
    df["kept_in_model"] = ~(df["energy_outlier"] | df["lab_outlier"])

    analytic = df[df["kept_in_model"]].copy()
    print(f"After filtering: {len(analytic)} rows remain.")

    # --- Save ---
    out_path = Path(config["paths"]["tidy"]) / "diet_labs_analytic.csv"
    analytic.to_csv(out_path, index=False)
    print(f"✅ Saved {out_path}")


if __name__ == "__main__":
    main()
