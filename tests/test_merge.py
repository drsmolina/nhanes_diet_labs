import pandas as pd

def test_unique_seqn():
    df = pd.read_csv("data_tidy/diet_labs_analytic.csv")
    assert df["SEQN"].is_unique
