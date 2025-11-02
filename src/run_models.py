# src/run_models.py
"""
Weighted regression models linking dietary nutrients to lab biomarkers.
Handles missing data, infinite values, and robust SEs.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import yaml
from pathlib import Path


def standardize(series):
    """Standardize safely (ignore NaNs and avoid divide-by-zero)."""
    s = np.nanstd(series)
    return (series - np.nanmean(series)) / s if s != 0 else series * 0


def main():
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    tidy_path = Path(config["paths"]["tidy"]) / "diet_labs_analytic.csv"
    out_csv = Path(config["paths"]["reports"]) / "model_results.csv"
    fig_path = Path(config["paths"]["figs"]) / "forest_models.png"
    Path(config["paths"]["reports"]).mkdir(exist_ok=True)

    df = pd.read_csv(tidy_path)
    print(f"Loaded {len(df):,} rows for modeling")

    # Replace infinite values and drop obvious missing outcomes
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["hba1c", "hdl", "hscrp", "age", "bmi", "sex_female"])

    # Normalize weights
    df["wt"] = df["wt_diet_day1"] / np.nanmean(df["wt_diet_day1"])

    # Define model specs
    model_specs = {
        "hba1c": ["carb_pct", "fiber_density", "sugar_pct", "fat_pct", "age", "sex_female", "bmi"],
        "hdl": ["fat_pct", "fiber_density", "sugar_pct", "age", "sex_female", "bmi"],
        "hscrp": ["fiber_density", "age", "sex_female", "bmi"],
    }

    results = []

    for outcome, predictors in model_specs.items():
        print(f"\nRunning model for {outcome} ...")

        # Define dependent variable
        y = np.log(df[outcome]) if outcome == "hscrp" else df[outcome]

        # Drop missing rows for predictors/outcome
        sub = df[predictors + [outcome, "wt"]].dropna().copy()

        # Standardize predictors
        X = sub[predictors].apply(standardize)
        X = sm.add_constant(X)

        # Drop any remaining NaN/Inf rows in predictors
        mask = np.isfinite(X).all(axis=1)
        X = X.loc[mask]
        y = sub.loc[mask, outcome]
        w = sub.loc[mask, "wt"]

        # Weighted least squares with robust SEs
        model = sm.WLS(np.log(y) if outcome == "hscrp" else y, X, weights=w)
        res = model.fit(cov_type="HC3")

        # Collect results
        for term, beta, se, pval in zip(res.params.index, res.params, res.bse, res.pvalues):
            if term == "const":
                continue
            ci_low, ci_high = beta - 1.96 * se, beta + 1.96 * se
            results.append(
                {
                    "outcome": outcome,
                    "term": term,
                    "beta": beta,
                    "se": se,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "p": pval,
                    "n": int(res.nobs),
                    "r2": res.rsquared,
                }
            )

    results_df = pd.DataFrame(results)
    results_df.to_csv(out_csv, index=False)
    print(f"✅ Saved results to {out_csv}")

    # Forest plot
    plt.figure(figsize=(8, 6))
    for i, row in enumerate(results_df.itertuples()):
        plt.errorbar(
            row.beta,
            i,
            xerr=[[row.beta - row.ci_low], [row.ci_high - row.beta]],
            fmt="o",
            color="teal",
            ecolor="gray",
            capsize=3,
        )
    plt.axvline(0, color="black", linestyle="--", linewidth=1)
    plt.yticks(range(len(results_df)), results_df["outcome"] + " • " + results_df["term"])
    plt.xlabel("β (per 1 SD increase, HC3 robust SEs)")
    plt.title("Weighted Regression Results: Nutrients vs. Biomarkers")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=config["viz"]["dpi"])
    plt.show()
    print(f"✅ Forest plot saved to {fig_path}")


if __name__ == "__main__":
    main()
