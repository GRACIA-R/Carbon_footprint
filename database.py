from supabase import create_client
import streamlit as st

def _get_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def save_response(data):
    client = _get_client()
    client.table("responses").insert(data).execute()
