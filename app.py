import streamlit as st
import pandas as pd
import plotly.express as px

from calculator import calculate_footprint
from database import save_response
from analysis import load_data

st.title("University Carbon Footprint Project")

page = st.sidebar.selectbox(
    "Menu",
    ["Carbon Footprint Calculator", "University Dashboard"]
)

# ---------------------------------

if page == "Carbon Footprint Calculator":

    st.header("Calculate Your Carbon Footprint")

    gender = st.selectbox("Gender", ["Male", "Female"])

    age = st.slider("Age", 17, 40)

    transport = st.selectbox(
        "Main transport",
        ["Car", "Bus", "Bike", "Walk"]
    )

    distance = st.number_input(
        "Daily distance to university (km)",
        min_value=0.0
    )

    electricity = st.number_input(
        "Monthly electricity consumption (kWh)",
        min_value=0.0
    )

    diet = st.selectbox(
        "Diet type",
        ["Meat", "Vegetarian"]
    )

    flights = st.number_input(
        "Flights per year",
        min_value=0
    )

    if st.button("Calculate Footprint"):

        data = {
            "gender": gender,
            "age": age,
            "transport": transport,
            "distance": distance,
            "electricity": electricity,
            "diet": diet,
            "flights": flights
        }

        footprint = calculate_footprint(data)

        data["footprint"] = footprint

        save_response(data)

        st.success(f"Your carbon footprint: {footprint:.2f} ton CO₂/year")

# ---------------------------------

if page == "University Dashboard":

    st.header("University Carbon Footprint Analysis")

    df = load_data()

    if df.empty:
        st.warning("No data yet")
    else:

        st.metric(
            "Average footprint",
            f"{df['footprint'].mean():.2f} ton CO₂"
        )

        fig = px.histogram(
            df,
            x="footprint",
            title="Distribution of Carbon Footprint"
        )

        st.plotly_chart(fig)

        fig2 = px.box(
            df,
            x="gender",
            y="footprint",
            title="Footprint by Gender"
        )

        st.plotly_chart(fig2)

        fig3 = px.histogram(
            df,
            x="transport",
            title="Transport Distribution"
        )

        st.plotly_chart(fig3)
