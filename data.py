from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import gspread
import os

load_dotenv()

# Google Sheets setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

def get_sheet_data():
    creds = Credentials.from_service_account_file(
        os.getenv("CREDENTIALS_FILE"),
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    worksheet = sheet.get_worksheet(0)  # First sheet
    records = worksheet.get_all_records()  # Returns list of dicts

    # Store Symbol and Suggestion in a dictionary
    stocks_dict = {}
    for row in records:
        symbol = row.get("Symbol")
        suggestion = row.get("Suggestion")
        if symbol:
            stocks_dict[symbol] = suggestion

    
    return stocks_dict

buy_data = get_sheet_data()

def get_sheet_data_sell():
    creds = Credentials.from_service_account_file(
        os.getenv("CREDENTIALS_FILE"),
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID2"))
    worksheet = sheet.get_worksheet(0)  # First sheet
    records = worksheet.get_all_records()  # Returns list of dicts

    # Store Symbol and Suggestion in a dictionary
    stocks_dict = {}
    for row in records:
        symbol = row.get("Symbol")
        suggestion = row.get("Suggestion")
        if symbol:
            stocks_dict[symbol] = suggestion

    
    return stocks_dict

sell_data = get_sheet_data_sell()
