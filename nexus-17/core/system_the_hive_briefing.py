import os
import sys
import json
import urllib.request
import urllib.parse
import html
from datetime import datetime
import random

def get_keys():
    keys = {"bot_token": None, "chat_id": None}
    try:
        with open('/path/to/system_credentials_example.md', 'r') as f:
            for line in f:
                if "Bot_Token" in line:
                    keys["bot_token"] = ''.join(c for c in line.split(':', 1)[1] if c.isalnum() or c in '-_:')
                elif "Chat_ID" in line:
                    keys["chat_id"] = ''.join(c for c in line.split(':', 1)[1] if c.isalnum() or c in '-_')
        return keys
    except: sys.exit(1)

now = datetime.now()
day_name = now.strftime("%A")
date_str = now.strftime("%d %B %Y")
time_str = now.strftime("%H:%M")

if now.hour < 12:
    greetings = [
        "Good morning, Admin.",
        "Good morning. Overnight intelligence compiled.",
        "System online. Morning sweeps have concluded."
    ]
elif now.hour < 18:
    greetings = [
        "Good afternoon, Admin.",
        "Midday protocols nominal.",
        "Good afternoon. Latest telemetry assembled for review."
    ]
else:
    greetings = [
        "Good evening, Admin.",
        "Evening data acquisition complete.",
        "Good evening. End-of-day dossier compiled."
    ]

status_quips = [
    f"All systems are nominal. Servers cycled successfully at <code>{time_str}</code>.",
    f"Network secure. All agents reporting in on this {day_name}.",
    f"System time logged at <code>{time_str}</code>. The Hive is awaiting commands.",
    f"Data acquisition successful. Synchronisation logged at <code>{time_str}</code>.",
    f"Full diagnostic complete. Architecture integrity verified."
]

sign_offs = [
    "Awaiting further inputs.",
    "The board is yours.",
    "Core functions standing by.",
    "All agents available for deployment.",
    "System nominal. Standing by."
]

def count_json_items(filepath):
    path = os.path.expanduser(filepath)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f: return len(json.load(f))
        except: return 0
    return 0

current_leads = count_json_items('/path/to/VAULT_DIR/pending/leads.json')
current_careers = count_json_items('/path/to/VAULT_DIR/careers.json')

memory_state_path = '/path/to/MEMORY_DIR/hive_state.json'
last_state = {"leads": 0, "careers": 0}
if os.path.exists(memory_state_path):
    try:
        with open(memory_state_path, 'r') as f: last_state = json.load(f)
    except: pass

new_leads = current_leads - last_state["leads"]
if new_leads < 0: new_leads = current_leads

new_careers = current_careers - last_state["careers"]
if new_careers < 0: new_careers = current_careers

os.makedirs(os.path.dirname(memory_state_path), exist_ok=True)
try:
    with open(memory_state_path, 'w') as f:
        json.dump({"leads": current_leads, "careers": current_careers}, f)
except: pass

if current_leads == 0:
    leads_status = "Lead Vault empty. Automated scouting protocols active."
elif new_leads == 0:
    leads_status = f"No new records. Vault holding <b>{current_leads}</b> total leads for review."
else:
    leads_status = f"Intercepted <b>{new_leads} new lead(s)</b>. Total Vault count: <b>{current_leads}</b>."

if current_careers == 0:
    careers_status = "Careers sector idle. Zero active opportunities logged."
elif new_careers == 0:
    careers_status = f"No new movements. Holding at <b>{current_careers}</b> total opportunities."
else:
    careers_status = f"Sourced <b>{new_careers} new prospect(s)</b>. Board total: <b>{current_careers}</b>."

error_count = 0
log_path = '/path/to/MEMORY_DIR/daily_logs.md'
if os.path.exists(log_path):
    try:
        with open(log_path, 'r') as f:
            for line in f.readlines()[-20:]:
                if "[ERROR]" in line or "[WARN]" in line: error_count += 1
    except: pass

health_status = "[OK] <b>System Health:</b> Optimised. Zero anomalies." if error_count == 0 else f"[WARN] <b>System Health:</b> Nominal. {error_count} background warnings suppressed."

memory_path = '/path/to/MEMORY_DIR/LONG_TERM_MEMORY.md'
last_intel = "• No intel recorded from previous cycle."
if os.path.exists(memory_path):
    try:
        with open(memory_path, 'r') as f:
            lines = f.readlines()
            if lines:
                clean_lines = []
                for line in lines[-6:]:
                    line = line.strip()
                    if not line or line.startswith('###'): continue
                    is_bullet = False
                    if line.startswith('- ') or line.startswith('* ') or line.startswith('• '):
                        line = line[2:].strip()
                        is_bullet = True
                    elif len(line) > 2 and line[0].isdigit() and line[1] in '.)':
                        line = line[3:].strip()
                        is_bullet = True
                    line = line.replace('**', '').replace('*', '').replace('`', '')
                    if is_bullet: line = '• ' + line
                    clean_lines.append(html.escape(line))
                if clean_lines: last_intel = "\n".join(clean_lines)
    except: pass

greeting = random.choice(greetings)
status = random.choice(status_quips)
sign_off = random.choice(sign_offs)

briefing = f"""
[ THE HIVE : DAILY BRIEFING ]
<b>{greeting}</b>
<i>{status}</i>

{health_status}

<b>[ TARGET ACQUISITION ]</b>
• <b>Leads:</b> {leads_status}
• <b>Careers:</b> {careers_status}

<b>[ INTELLIGENCE REPORT ]</b>
{last_intel}

<b>[ SCHEDULED OPERATIONS ]</b>
• <code>07:30</code> - Hunter: Portal Reconnaissance
• <code>08:30</code> - Headhunter: Morning Market Sweep
• <code>12:30</code> - Actor: Asset Production
• <code>16:30</code> - Headhunter: Afternoon Market Sweep
• <code>17:30</code> - Hunter: Final Portal Sweep
• <code>20:30</code> - Actor: Media Rendering Engine
• <code>23:00</code> - Librarian: System Audit & Sync

<i>{sign_off}</i>
"""

def send_hive_html(msg):
    keys = get_keys()
    url = f"https://api.telegram.org/bot{keys['bot_token']}/sendMessage"
    try:
        data = urllib.parse.urlencode({'chat_id': keys['chat_id'], 'text': msg, 'parse_mode': 'HTML'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            print("[SUCCESS] THE HIVE: Briefing delivered successfully.")
    except Exception as e:
        print(f"[WARN] THE HIVE: HTML formatting rejected: {e}")
        print("[PROCESS] Attempting raw text fallback...")
        try:
            data = urllib.parse.urlencode({'chat_id': keys['chat_id'], 'text': msg}).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=5) as response:
                print("[SUCCESS] Fallback raw briefing delivered.")
        except Exception as e2:
            print(f"[ERROR] CRITICAL: Could not transmit. Reason: {e2}")

if __name__ == "__main__":
    print("[PROCESS] THE HIVE: Accessing memory arrays...")
    print("[PROCESS] THE HIVE: Assembling dynamic briefing...")
    send_hive_html(briefing)