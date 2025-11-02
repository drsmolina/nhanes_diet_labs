import pandas as pd

def test_macro_sum_reasonable():
    df = pd.read_csv("data_tidy/diet_labs_analytic.csv")
    s = df["carb_pct"] + df["protein_pct"] + df["fat_pct"]
    assert (s.between(0.6, 1.4)).all()
