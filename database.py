import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_NAME = "carbon_footprint_responses"  # nombre de tu Google Sheet
WORKSHEET = "Sheet1"

def _get_sheet():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET)
    return sheet

def save_response(data):
    sheet = _get_sheet()
    # Si la hoja está vacía, agrega encabezados primero
    if sheet.row_count == 0 or sheet.cell(1, 1).value is None:
        sheet.append_row(list(data.keys()))
    sheet.append_row(list(data.values()))
