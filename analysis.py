from supabase import create_client
import streamlit as st
import pandas as pd


def load_data() -> pd.DataFrame:
    """Carga todas las respuestas desde Supabase."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        client = create_client(url, key)
        result = client.table("responses").select("*").execute()
        df = pd.DataFrame(result.data)
        if df.empty:
            return df
        # Eliminar columnas internas de Supabase si existen
        for col in ["id", "created_at"]:
            if col in df.columns:
                df = df.drop(columns=[col])
        # Asegurar tipos numéricos
        numeric_cols = [
            "edad", "distancia_diaria_km", "dias_campus_semana",
            "num_vehiculos_hogar", "electricidad_kwh_mes", "gas_lp_kg_mes",
            "personas_hogar", "vuelos_cortos_anio", "vuelos_largos_anio",
            "correos_inbox", "streaming_horas_dia", "huella_ton_co2",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        return pd.DataFrame()
