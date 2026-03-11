import pandas as pd

FILE = "results/responses.csv"

def load_data():

    try:
        df = pd.read_csv(FILE)
        return df
    except:
        return pd.DataFrame()
