from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import gspread
import os

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",  # Full access for deletion
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    """Reusable authenticated gspread client."""
    creds = Credentials.from_service_account_file(
        os.getenv("CREDENTIALS_FILE"),
        scopes=SCOPES
    )
    return gspread.authorize(creds)


def get_sheet_data(sheet_id):
    """Get symbol->suggestion dict from a sheet."""
    client = get_client()
    worksheet = client.open_by_key(sheet_id).get_worksheet(0)
    records = worksheet.get_all_records()

    stocks_dict = {}
    for row in records:
        symbol = row.get("Symbol")
        suggestion = row.get("Suggestion")
        if symbol:
            stocks_dict[symbol] = suggestion

    return stocks_dict


def remove_bought_symbols_from_suggestions():
    """
    Reads bought symbols from Sheet 2 (GOOGLE_SHEET_ID2),
    then deletes any matching rows from Sheet 1 (GOOGLE_SHEET_ID - suggestions).
    """
    client = get_client()

    # --- Sheet 2: Bought symbols (source of truth) ---
    bought_sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID2")).get_worksheet(0)
    bought_records = bought_sheet.get_all_records()
    bought_symbols = {row.get("Symbol") for row in bought_records if row.get("Symbol")}

    print(f"Bought symbols: {bought_symbols}")

    # --- Sheet 1: Suggestions sheet (delete from here) ---
    suggestion_sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).get_worksheet(0)
    suggestion_records = suggestion_sheet.get_all_records()

    # Find row indices to delete (1-based, +2 for header offset)
    rows_to_delete = []
    for i, row in enumerate(suggestion_records):
        symbol = row.get("Symbol")
        if symbol in bought_symbols:
            actual_row_number = i + 2  # +1 for 0-index, +1 for header row
            rows_to_delete.append(actual_row_number)
            print(f"Marking '{symbol}' for deletion at row {actual_row_number}")

    # Delete in REVERSE order to prevent row index shifting
    for row_num in sorted(rows_to_delete, reverse=True):
        suggestion_sheet.delete_rows(row_num)
        print(f"Deleted row {row_num}")

    print(f"\nDone. Removed {len(rows_to_delete)} symbol(s) from suggestions sheet.")
    return len(rows_to_delete)


# --- Run ---
buy_data = get_sheet_data(os.getenv("GOOGLE_SHEET_ID"))   # Suggestions
sell_data = get_sheet_data(os.getenv("GOOGLE_SHEET_ID2")) # Bought

print("Suggestions:", buy_data)
print("Bought:", sell_data)

#remove_bought_symbols_from_suggestions()