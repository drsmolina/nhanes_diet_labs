import argparse
import yaml
import pandas as pd
import numpy as np
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Build features for NHANES diet-labs analysis")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    return parser.parse_args()

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    args = parse_args()
    config = load_yaml(args.config)
    tidy_dir = Path(config["paths"]["tidy"])
    df = pd.read_parquet(tidy_dir / "nhanes_raw_merged.parquet")
    # rename columns according to config
    feats = config["features"]
    rename_map = {
        feats["kcal_col"]: "energy_kcal",
        feats["carbs_g"]: "carbs_g",
        feats["protein_g"]: "protein_g",
        feats["fat_g"]: "fat_g",
        feats["fiber_g"]: "fiber_g",
        feats["added_sugar_g"]: "added_sugar_g",
        feats["sodium_mg"]: "sodium_mg",
    }
    df = df.rename(columns=rename_map)
    # compute nutrient features
    df["carb_pct"] = 4 * df["carbs_g"] / df["energy_kcal"]
    df["protein_pct"] = 4 * df["protein_g"] / df["energy_kcal"]
    df["fat_pct"] = 9 * df["fat_g"] / df["energy_kcal"]
    df["fiber_density"] = df["fiber_g"] / (df["energy_kcal"] / 1000)
    df["sugar_pct"] = np.where(df["added_sugar_g"].notna(), 4 * df["added_sugar_g"] / df["energy_kcal"], np.nan)
    df["sodium_density"] = df["sodium_mg"] / (df["energy_kcal"] / 2000)
    # encode sex_female (1 = female)
    if "sex" in df.columns:
        df["sex_female"] = np.where(df["sex"] == 2, 1, 0)
    # normalize weights
    wt_col = config["design_vars"]["weight_diet_day1"]
    if wt_col in df.columns:
        mean_wt = df[wt_col].mean(skipna=True)
        df["wt_diet_day1"] = df[wt_col] / mean_wt
    # outlier flags
    kcal_min, kcal_max = config["qa"]["kcal_range"]
    df["energy_outlier"] = ~df["energy_kcal"].between(kcal_min, kcal_max)
    df["lab_outlier"] = (df["hba1c"] > config["qa"]["max_hba1c"]) | (df["hdl"] <= 0) | (df["hscrp"] <= 0)
    df["kept_in_model"] = ~(df["energy_outlier"] | df["lab_outlier"])
    # filter rows
    df = df[df["kept_in_model"]].copy()
    # drop duplicates
    df = df.drop_duplicates(subset="SEQN")
    # save analytic dataset
    out_path = tidy_dir / "diet_labs_analytic.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

if __name__ == "__main__":
    main()
