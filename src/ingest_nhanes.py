# src/ingest_nhanes.py
import argparse
from pathlib import Path
import pandas as pd
import yaml


def main():
    parser = argparse.ArgumentParser(description="Ingest NHANES CSVs for 2017–2018")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--vars", required=True, help="Path to var_map.yaml")
    args = parser.parse_args()

    # Load YAMLs
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    # Paths
    tidy_dir = Path(config["paths"]["tidy"])
    tidy_dir.mkdir(parents=True, exist_ok=True)

    base_path = Path("data_raw") / "2017_2018"
    suffix = "J"

    # --- Load CSVs ---
    demo = pd.read_csv(base_path / f"DEMO_{suffix}.csv", low_memory=False)
    diet = pd.read_csv(base_path / f"DR1TOT_{suffix}.csv", low_memory=False)
    body = pd.read_csv(base_path / f"BMX_{suffix}.csv", low_memory=False)
    ghb = pd.read_csv(base_path / f"GHB_{suffix}.csv", low_memory=False)
    hscrp = pd.read_csv(base_path / f"HSCRP_{suffix}.csv", low_memory=False)
    hdl = pd.read_csv(base_path / f"HDL_{suffix}.csv", low_memory=False)
    trig = pd.read_csv(base_path / f"TRIGLY_{suffix}.csv", low_memory=False)

    # --- DEMOGRAPHICS ---
    demo = demo.rename(columns={
        "RIDAGEYR": "age",
        "RIAGENDR": "sex",
        "RIDRETH3": "raceeth",
        "INDFMPIR": "pir"
    })
    demo_keep = ["SEQN", "age", "sex", "raceeth", "pir",
                 "WTMEC2YR", "SDMVSTRA", "SDMVPSU"]
    demo = demo[demo_keep]

    # --- DIET TOTALS ---
    diet = diet.rename(columns={
        "DR1TKCAL": "energy_kcal",
        "DR1TCARB": "carbs_g",
        "DR1TPROT": "protein_g",
        "DR1TTFAT": "fat_g",
        "DR1TFIBE": "fiber_g",
        "DR1TSODI": "sodium_mg",
        # using total sugar as proxy for added sugar
        "DR1TSUGR": "added_sugar_g"
    })
    diet_keep = ["SEQN", "energy_kcal", "carbs_g", "protein_g",
                 "fat_g", "fiber_g", "added_sugar_g",
                 "sodium_mg", "WTDRD1"]
    diet = diet[diet_keep]

    # --- BODY MEASURES ---
    body = body.rename(columns={"BMXBMI": "bmi"})
    body = body[["SEQN", "bmi"]]

    # --- LABS ---
    ghb = ghb.rename(columns={"LBXGH": "hba1c"})[["SEQN", "hba1c"]]
    hscrp = hscrp.rename(columns={"LBXHSCRP": "hscrp"})[["SEQN", "hscrp"]]
    hdl = hdl.rename(columns={"LBDHDD": "hdl"})[["SEQN", "hdl"]]
    trig = trig.rename(columns={"LBXTR": "trig"})[["SEQN", "trig"]]

    # --- MERGE ---
    merged = (
        demo
        .merge(diet, on="SEQN", how="left")
        .merge(body, on="SEQN", how="left")
        .merge(ghb, on="SEQN", how="left")
        .merge(hscrp, on="SEQN", how="left")
        .merge(hdl, on="SEQN", how="left")
        .merge(trig, on="SEQN", how="left")
    )
    merged["cycle"] = "2017_2018"

    # --- SAVE ---
    out_path = tidy_dir / "nhanes_raw_merged.parquet"
    merged.to_parquet(out_path, index=False)
    print(f"✅ Done! {len(merged)} rows, {len(merged.columns)} columns written to {out_path}")


if __name__ == "__main__":
    main()
