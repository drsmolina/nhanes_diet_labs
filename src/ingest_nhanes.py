import argparse
import yaml
import pandas as pd
import pyreadstat
import requests
import io
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Ingest NHANES data and harmonize variables")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--vars", required=True, help="Path to var_map.yaml")
    return parser.parse_args()

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def download_xpt(url):
    resp = requests.get(url)
    resp.raise_for_status()
    df, meta = pyreadstat.read_xport(io.BytesIO(resp.content))
    return df

def standardize_columns(df, mapping):
    new_cols = {}
    for std_name, candidates in mapping.items():
        for cand in candidates:
            if cand in df.columns:
                new_cols[cand] = std_name
                break
    if new_cols:
        sub_df = df[list(new_cols.keys())].rename(columns=new_cols)
    else:
        sub_df = pd.DataFrame()
    return sub_df

def main():
    args = parse_args()
    config = load_yaml(args.config)
    var_map = load_yaml(args.vars)
    cycles = config["cycles"]
    files = config["files"]
    design_vars = config["design_vars"]
    # map cycle to suffix for NHANES 2017-2020
    cycle_suffix = {"2017_2018": "J", "2019_2020": "K"}
    all_records = []
    for cycle in cycles:
        suffix = cycle_suffix.get(cycle)
        base_url = f"https://wwwn.cdc.gov/Nchs/Nhanes/{cycle.replace('_','-')}/"
        # file names
        demo_file = f"{files['demo']}_{suffix}.XPT"
        diet_file = f"{files['diet_day1']}_{suffix}.XPT"
        body_file = f"{files['body']}_{suffix}.XPT"
        lab_files = {k: f"{v}_{suffix}.XPT" for k, v in files['labs'].items()}
        # download and standardize
        demo_df = download_xpt(base_url + demo_file)
        diet_df = download_xpt(base_url + diet_file)
        body_df = download_xpt(base_url + body_file)
        demo_std = standardize_columns(demo_df, var_map['demo'])
        diet_std = standardize_columns(diet_df, var_map['diet_day1'])
        body_std = standardize_columns(body_df, var_map['body'])
        merged = demo_std.merge(diet_std, on="SEQN", how="left").merge(body_std, on="SEQN", how="left")
        # labs
        for lab_key, lab_file in lab_files.items():
            lab_df = download_xpt(base_url + lab_file)
            lab_std = standardize_columns(lab_df, var_map['labs'][lab_key])
            merged = merged.merge(lab_std, on="SEQN", how="left")
        # attach design variables from original demo_df
        for var_key, col_name in design_vars.items():
            if col_name in demo_df.columns:
                merged[col_name] = demo_df[col_name]
        merged['cycle'] = cycle
        all_records.append(merged)
    combined = pd.concat(all_records, ignore_index=True)
    # write parquet
    tidy_path = Path(config['paths']['tidy'])
    tidy_path.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(tidy_path / "nhanes_raw_merged.parquet", index=False)

if __name__ == "__main__":
    main()
