import pandas as pd
import os

FILE = "results/responses.csv"

def save_response(data):

    df = pd.DataFrame([data])

    if os.path.exists(FILE):
        df_old = pd.read_csv(FILE)
        df = pd.concat([df_old, df], ignore_index=True)

    df.to_csv(FILE, index=False)
