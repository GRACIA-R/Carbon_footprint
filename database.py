from supabase import create_client
import streamlit as st


def _get_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def save_response(data: dict):
    """Guarda una respuesta en la tabla 'responses' de Supabase."""
    client = _get_client()
    # Convertir tipos numpy a Python nativo para compatibilidad con JSON
    clean = {k: (float(v) if hasattr(v, 'item') else v) for k, v in data.items()}
    client.table("responses").insert(clean).execute()
