import os
import sys
import json
import time
import urllib.request
import urllib.parse
import re
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

SHEET_ID = "YOUR_SHEET_ID_HERE"
TAB_NAME = "Leads_V1"

def get_keys():
    keys = {"gemini": None, "bot_token": None, "chat_id": None}
    try:
        with open('/path/to/system_credentials_example.md', 'r') as f:
            for line in f:
                if "Gemini_API" in line:
                    keys["gemini"] = ''.join(c for c in line.split(':', 1)[1] if c.isalnum() or c in '-_')
                elif "Bot_Token" in line:
                    keys["bot_token"] = ''.join(c for c in line.split(':', 1)[1] if c.isalnum() or c in '-_:')
                elif "Chat_ID" in line:
                    keys["chat_id"] = ''.join(c for c in line.split(':', 1)[1] if c.isalnum() or c in '-_')
        return keys
    except Exception as e:
        print(f"[ERROR] Key read fault - {e}")
        sys.exit(1)

KEYS = get_keys()

def send_live_update(message):
    print(f"[TELEGRAM] {message}", file=sys.stderr, flush=True)
    if not KEYS["bot_token"] or not KEYS["chat_id"]: return
    try:
        url = f"https://api.telegram.org/bot{KEYS['bot_token']}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': KEYS['chat_id'], 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except: pass

def push_to_sheets(leads):
    if not leads: return
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_path = '/path/to/GCP_SERVICE_ACCOUNT.json'
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(TAB_NAME)
        rows_to_insert = []
        today = datetime.now().strftime("%Y-%m-%d")
        for lead in leads:
            row = [
                today, lead.get("Council", "Unknown"), lead.get("Reference", "N/A"),
                lead.get("Address", "N/A"), lead.get("Description", "N/A"),
                lead.get("Architect", "TBC"), lead.get("Score", 0),
                lead.get("Reason", "N/A"), lead.get("Link", "N/A"), "New Lead"
            ]
            rows_to_insert.append(row)
        sheet.append_rows(rows_to_insert)
        send_live_update(f"[SUCCESS] CRM SYNCED: {len(rows_to_insert)} qualified leads pushed to Database.")
    except Exception as e:
        send_live_update(f"[ERROR] DATABASE SYNC FAULT: {e}")

def analyze_and_score(raw_text, council_name, council_url):
    leads = []
    refs = list(set(re.findall(r'\d{2}/\d{4,5}/[a-zA-Z0-9]+', raw_text)))
    for ref in refs:
        leads.append({
            "Reference": ref,
            "Address": "Manual Review Required",
            "Description": "AI Parsing Bypassed - Resource Optimization",
            "Architect": "N/A",
            "Score": "N/A",
            "Reason": "Bypassed - Click Link to View"
        })
    for lead in leads:
        lead["Council"] = council_name
        if council_name in ["City of London", "Greenwich"] and "Reference" in lead:
            encoded_ref = urllib.parse.quote(lead['Reference'])
            lead["Link"] = f"{council_url}simpleSearchResults.do?action=firstPage&searchCriteria.reference={encoded_ref}"
        else:
            lead["Link"] = council_url
    return leads

def hunt_leads():
    send_live_update("[PROCESS] HUNTER: Initiating Multi-Page Sweep Protocol...")
    qualified_leads = []
    
    def sweep_pages(page_obj, max_pages=5):
        full_text = ""
        for i in range(1, max_pages + 1):
            page_obj.wait_for_timeout(2000)
            full_text += page_obj.evaluate("document.body.innerText") + f"\n\n--- END OF PAGE {i} ---\n\n"
            next_btn = page_obj.locator("a.next")
            if next_btn.count() > 0 and i < max_pages:
                send_live_update(f"[PROCESS] PAGINATION: Mining Page {i+1}...")
                next_btn.first.click()
                page_obj.wait_for_timeout(3000)
            else:
                break
        return full_text

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        send_live_update("[TARGET] SCOUTING: City of London (Deep Sweep)...")
        try:
            page.goto("https://www.planning2.cityoflondon.gov.uk/online-applications/search.do?action=weeklyList", timeout=60000)
            page.wait_for_timeout(3000)
            page.click("input.button.primary")
            page.wait_for_timeout(5000)
            raw_text = sweep_pages(page, 5)
            send_live_update("[PROCESS] SCORING: Regex extraction active...")
            leads = analyze_and_score(raw_text, "City of London", "https://www.planning2.cityoflondon.gov.uk/online-applications/")
            if leads:
                qualified_leads.extend(leads)
                send_live_update(f"[SUCCESS] YIELD: Extracted {len(leads)} raw references (London).")
            else:
                send_live_update("[INFO] NULL YIELD: No valid references found (London).")
        except Exception as e:
            send_live_update("[ERROR] LONDON FAULT: Navigation failed.")
            print(f"\n[ERROR] LONDON FAULT: {str(e)}\n", file=sys.stderr)

        print(f"[SYSTEM] Compliance Delay: 15s cooling protocol active...")
        time.sleep(15)

        send_live_update("[TARGET] SCOUTING: Royal Borough of Greenwich...")
        try:
            page.goto("https://planning.royalgreenwich.gov.uk/online-applications/search.do?action=weeklyList", timeout=60000)
            page.wait_for_timeout(3000)
            page.click("input.button.primary")
            page.wait_for_timeout(5000)
            raw_text = sweep_pages(page, 5)
            send_live_update("[PROCESS] SCORING: Regex extraction active...")
            leads = analyze_and_score(raw_text, "Greenwich", "https://planning.royalgreenwich.gov.uk/online-applications/")
            if leads:
                qualified_leads.extend(leads)
                send_live_update(f"[SUCCESS] YIELD: Extracted {len(leads)} raw references (Greenwich).")
            else:
                send_live_update("[INFO] NULL YIELD: No valid references found (Greenwich).")
        except Exception as e:
            send_live_update("[ERROR] GREENWICH FAULT: Navigation failed.")
            print(f"\n[ERROR] GREENWICH FAULT: {str(e)}\n", file=sys.stderr)

        send_live_update("[PROCESS] TEARDOWN: Closing browser, releasing resources...")
        context.close()
        browser.close()

    if qualified_leads:
        vault_dir = '/path/to/VAULT_DIR/pending'
        os.makedirs(vault_dir, exist_ok=True)
        vault_path = os.path.join(vault_dir, 'leads.json')
        existing_leads = []
        if os.path.exists(vault_path):
            with open(vault_path, 'r') as f:
                try: existing_leads = json.load(f)
                except: pass

        existing_refs = {lead.get("Reference") for lead in existing_leads if lead.get("Reference")}
        new_unique_leads = []
        for lead in qualified_leads:
            ref = lead.get("Reference")
            if ref and ref not in existing_refs:
                new_unique_leads.append(lead)
                existing_refs.add(ref)

        if new_unique_leads:
            existing_leads.extend(new_unique_leads)
            with open(vault_path, 'w') as f:
                json.dump(existing_leads, f, indent=4)
            push_to_sheets(new_unique_leads)
            send_live_update(f"[SUCCESS] VAULT UPDATE: Secured {len(new_unique_leads)} new unique leads. (Ignored {len(qualified_leads) - len(new_unique_leads)} duplicates).")
        else:
            send_live_update("[INFO] VAULT UPDATE: All intercepted leads were duplicates. No DB update required.")
            
    log_path = '/path/to/MEMORY_DIR/daily_logs.md'
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a') as f:
        f.write(f"\n- **{datetime.now().strftime('%Y-%m-%d %H:%M')}**: Data Agent scouted London/Greenwich. {len(qualified_leads)} leads extracted.")

    return "[SUCCESS] Precision Search Run Complete."

if __name__ == "__main__":
    print(hunt_leads())