import pandas as pd
import numpy as np
import yaml
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pathlib import Path

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_models(config):
    tidy_dir = config['paths']['tidy']
    df = pd.read_csv(f"{tidy_dir}/diet_labs_analytic.csv")
    outcomes = config['models']['outcomes']
    covariates = config['models']['covariates']
    results = []
    for outcome in outcomes:
        if outcome == 'hba1c':
            predictors = ['carb_pct','fiber_density','sugar_pct','fat_pct'] + covariates
            y = df[outcome]
        elif outcome == 'hdl':
            predictors = ['fat_pct','fiber_density','sugar_pct'] + covariates
            y = df[outcome]
        elif outcome == 'hscrp':
            predictors = ['fiber_density'] + covariates
            y = np.log(df['hscrp'])
        else:
            continue
        X = df[predictors]
        X_std = (X - X.mean()) / X.std()
        X_std = sm.add_constant(X_std)
        weights = df['wt_diet_day1']
        model = sm.WLS(y, X_std, weights=weights)
        res = model.fit(cov_type=config['models']['robust_se'])
        for term in res.params.index:
            beta = res.params[term]
            se = res.bse[term]
            ci_low, ci_high = res.conf_int().loc[term]
            p = res.pvalues[term]
            results.append({
                'outcome': outcome,
                'term': term,
                'beta': beta,
                'se': se,
                'ci_low': ci_low,
                'ci_high': ci_high,
                'p': p,
                'n': int(res.nobs),
                'r2': res.rsquared
            })
    results_df = pd.DataFrame(results)
    reports_dir = config['paths']['reports']
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    results_df.to_csv(Path(reports_dir) / 'model_results.csv', index=False)
    # create forest plot
    plot_df = results_df[results_df['term'] != 'const']
    fig, ax = plt.subplots(figsize=(8, max(3, len(plot_df)/3)))
    y_positions = range(len(plot_df))
    ax.errorbar(plot_df['beta'], y_positions, xerr=[plot_df['beta'] - plot_df['ci_low'], plot_df['ci_high'] - plot_df['beta']], fmt='o')
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(plot_df['outcome'] + ' - ' + plot_df['term'])
    ax.axvline(0, color='gray', linestyle='--')
    ax.set_xlabel('Beta per 1 SD')
    ax.set_title('Survey-weighted model coefficients')
    fig.tight_layout()
    figs_dir = config['paths']['figs']
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(Path(figs_dir) / 'forest_models.png', dpi=config['viz']['dpi'])
    plt.close(fig)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    run_models(config)

if __name__ == "__main__":
    main()
