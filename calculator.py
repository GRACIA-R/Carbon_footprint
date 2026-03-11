import pandas as pd

factors = pd.read_csv("data/emission_factors.csv")
factors = dict(zip(factors.activity, factors.factor))

def calculate_footprint(data):

    transport = data["distance"] * factors["car"] * 200
    electricity = data["electricity"] * factors["electricity"] * 12
    flights = data["flights"] * 1000 * factors["flight"]

    if data["diet"] == "Meat":
        diet = factors["meat_diet"] * 365
    else:
        diet = factors["vegetarian_diet"] * 365

    total = transport + electricity + flights + diet

    return total / 1000
