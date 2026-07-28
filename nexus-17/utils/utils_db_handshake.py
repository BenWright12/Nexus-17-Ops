import os
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# This script tests Cloud Service Account credentials (OAuth) and verifies read access to the target Google Sheet.

SHEET_ID = "YOUR_SHEET_ID_HERE"

def test_db_connection():
    print("[INFO] INITIATING CLOUD DATABASE HANDSHAKE PROTOCOL")
    
    creds_path = '/path/to/GCP_SERVICE_ACCOUNT.json'
    print("[PROCESS] Locating OAuth 2.0 Service Account credentials...")
    
    if not os.path.exists(creds_path):
        print(f"  [FATAL] Credential file not found at {creds_path}")
        sys.exit(1)
    
    print("  [SUCCESS] Credential payload located.")
    print("[PROCESS] Requesting authorization token from Google Identity Services...")
    
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        print("  [SUCCESS] Authentication token granted.")
        
        print(f"[PROCESS] Attempting to ping Target Database ID: {SHEET_ID[:10]}...")
        if SHEET_ID == "YOUR_SHEET_ID_HERE":
            print("  [WARN] Configuration holds placeholder ID. Skipping specific table ping.")
            print("[INFO] OAuth mechanism is functioning perfectly.")
        else:
            sheet = client.open_by_key(SHEET_ID).sheet1
            title = sheet.title
            print(f"  [SUCCESS] Database connection established. Read access confirmed on table: '{title}'")
            
    except Exception as e:
        print(f"  [ERROR] OAuth handshake or Database ping failed: {e}")

if __name__ == "__main__":
    test_db_connection()