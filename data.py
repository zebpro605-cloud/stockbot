from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import gspread
import json
import os

load_dotenv()

# Google Sheets setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

def get_creds():
    """Load credentials from env variable (Railway) or file (local)."""
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        # Railway: credentials stored as JSON string in env variable
        creds_dict = json.loads(creds_json)
        return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        # Local: credentials loaded from file path in .env
        return Credentials.from_service_account_file(
            os.getenv("CREDENTIALS_FILE"),
            scopes=SCOPES
        )

def get_sheet_data():
    creds = get_creds()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    worksheet = sheet.get_worksheet(0)
    records = worksheet.get_all_records()

    stocks_dict = {}
    for row in records:
        symbol = row.get("Symbol")
        suggestion = row.get("Suggestion")
        if symbol:
            stocks_dict[symbol] = suggestion

    return stocks_dict

def get_sheet_data_sell():
    creds = get_creds()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID2"))
    worksheet = sheet.get_worksheet(0)
    records = worksheet.get_all_records()

    stocks_dict = {}
    for row in records:
        symbol = row.get("Symbol")
        suggestion = row.get("Suggestion")
        if symbol:
            stocks_dict[symbol] = suggestion

    return stocks_dict

buy_data = get_sheet_data()
sell_data = get_sheet_data_sell()