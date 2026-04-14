from supabase import create_client
import streamlit as st
import pandas as pd

def load_data():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        client = create_client(url, key)
        result = client.table("responses").select("*").execute()
        return pd.DataFrame(result.data)
    except:
        return pd.DataFrame()
