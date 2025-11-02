import pandas as pd

def test_positive_weights():
    df = pd.read_csv("data_tidy/diet_labs_analytic.csv")
    assert (df["wt_diet_day1"] > 0).sum() > 0
