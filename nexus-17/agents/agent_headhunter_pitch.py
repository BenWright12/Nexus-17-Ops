import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import google.generativeai as genai

SHEET_ID = "YOUR_SHEET_ID_HERE"
TAB_NAME = "Careers"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/"

COL_STATUS = 6 
COL_AI_PITCH = 7

def send_live_update(message):
    try:
        token, chat_id = None, None
        with open('/path/to/system_credentials_example.md', 'r') as f:
            for line in f:
                if 'Bot_Token' in line: token = line.strip().split()[-1].strip(' "\'\n')
                elif 'Chat_ID' in line: chat_id = line.strip().split()[-1].strip(' "\'\n')
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown', 'disable_web_page_preview': 'true'}).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=5)
    except: pass

def update_sheet_cloud_sync(job_link, status_msg, pitch_msg=""):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_path = '/path/to/GCP_SERVICE_ACCOUNT.json'
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(TAB_NAME)
        links = sheet.col_values(5)
        row_num = None
        for i, sheet_link in enumerate(links):
            if job_link.strip() in sheet_link.strip():
                row_num = i + 1
                break
        if row_num:
            sheet.update_cell(row_num, COL_STATUS, status_msg)
            if pitch_msg:
                sheet.update_cell(row_num, COL_AI_PITCH, pitch_msg)
    except Exception as e:
        print(f"[WARN] Sheet Sync Error: {e}")

def get_keys():
    keys = {"gemini": None}
    try:
        with open('/path/to/system_credentials_example.md', 'r') as f:
            for line in f:
                if 'Gemini_API' in line: keys["gemini"] = line.strip().split()[-1].strip(' "\'\n')
    except: pass
    return keys

def get_cv_content():
    cv_path = '/path/to/USER_RESUME.md'
    if os.path.exists(cv_path):
        with open(cv_path, 'r') as f: return f.read()
    return "CV details not found."

def draft_pitches():
    vault_path = '/path/to/VAULT_DIR/careers.json'
    if not os.path.exists(vault_path): return "[WARN] Vault data missing."
    with open(vault_path, 'r') as f: leads = json.load(f)
    keys = get_keys()
    cv_text = get_cv_content()
    if not keys["gemini"]: return "[ERROR] API Key missing."
    
    genai.configure(api_key=keys["gemini"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    pitches_prepped = 0
    pitch_dir = '/path/to/OUTPUT_DIR/Pitches'
    os.makedirs(pitch_dir, exist_ok=True)
    
    for job in leads:
        if job.get('status') in ["Awaiting Pitch", "Quota Limit Hit"]:
            print(f"[PROCESS] Synthesizing pitch for: {job['title']}...")
            prompt = f"Write a 3-paragraph UK English outreach email for '{job['title']}' at '{job['company']}'. CV: {cv_text}. Under 150 words."
            try:
                response = model.generate_content(prompt)
                final_pitch = response.text.strip()
                final_status = "Pitch Auto-Generated"
                
                clean_name = "".join([c for c in f"{job['source']}_{job['company']}" if c.isalnum() or c==' ']).replace(' ','_')
                with open(os.path.join(pitch_dir, f"{clean_name}_Pitch.txt"), 'w') as f:
                    f.write(f"ROLE: {job['title']}\nLINK: {job['link']}\n\n{final_pitch}")
                
                update_sheet_cloud_sync(job['link'], final_status, final_pitch)
                job['status'] = final_status
                pitches_prepped += 1
                
                print("[SYSTEM] 30s rate-limit cooldown active...")
                time.sleep(30)

            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    update_sheet_cloud_sync(job['link'], "Quota Limit Hit (Pending Retry)")
                    send_live_update(f"[ERROR] QUOTA EXHAUSTED\nHit the limit at: {job['title']}.\nWaiting for next operational shift.")
                    job['status'] = "Quota Limit Hit"
                    with open(vault_path, 'w') as f: json.dump(leads, f, indent=4)
                    sys.exit("[FATAL] Quota empty. Statuses updated to 'Limit Hit'.")
                else:
                    update_sheet_cloud_sync(job['link'], f"Error: {str(e)[:20]}")
                    job['status'] = "Manual Pitch Required"

    if pitches_prepped > 0:
        with open(vault_path, 'w') as f: json.dump(leads, f, indent=4)
        send_live_update(f"[SUCCESS] ROUTINE COMPLETE\nProcessed {pitches_prepped} roles.\n[Link: {SHEET_URL}]")
    return "[INFO] Done."

if __name__ == "__main__":
    print(draft_pitches())