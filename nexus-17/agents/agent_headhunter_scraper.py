from playwright.sync_api import sync_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os
import sys
import time
import urllib.request
import urllib.parse

JOB_QUERY = "junior data analyst OR junior analyst OR data analyst"
LOCATION = "London"

SHEET_NAME = "YOUR_SPREADSHEET_NAME_HERE"
TAB_NAME = "Careers"
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/"

BANNED_WORDS = ["course", "training", "bootcamp", "academy", "placement", "unpaid", "senior", "lead", "manager", "principal", "head of", "become", "learn", "guarantee", "fee", "trainee", "training course", "enrol", "diploma", "study", "tuition"]
BANNED_EXP = ["2 years", "3 years", "4 years", "5 years", "2+ years", "3+ years", "2+ yrs", "3+ yrs"]
TARGET_KEYWORDS = ["1 year", "1 yr", "entry level", "junior", "graduate", "no experience"]
VALID_LOCATIONS = ["london", "hybrid", "remote", "office"]

def send_live_update(message):
    print(f"[TELEGRAM] Live Update: {message}", file=sys.stderr, flush=True)
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
    except Exception: pass

def update_google_sheet(new_leads):
    print("\n[PROCESS] Initiating Google Sheets Sync...", file=sys.stderr, flush=True)
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_path = '/path/to/GCP_SERVICE_ACCOUNT.json'
        if not os.path.exists(creds_path): return False
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(TAB_NAME)
        rows_to_insert = []
        date_str = datetime.now().strftime("%d/%m/%Y")
        for job in new_leads:
            rows_to_insert.append([date_str, job['source'], job['title'], job['company'], job['link'], job['status']])
        if rows_to_insert:
            sheet.append_rows(rows_to_insert)
            send_live_update(f"[SUCCESS] GOOGLE SHEETS UPDATED\nSuccessfully added {len(new_leads)} roles.\n[Link: {SHEET_URL}]")
        return True
    except Exception as e:
        print(f"[ERROR] GOOGLE SHEETS ERROR: {str(e)}", file=sys.stderr, flush=True)
        return False

def hunt_jobs():
    vault_dir = '/path/to/VAULT_DIR'
    os.makedirs(vault_dir, exist_ok=True)
    vault_path = os.path.join(vault_dir, 'careers.json')
    existing_leads = []
    seen_jobs = set()
    if os.path.exists(vault_path):
        try:
            with open(vault_path, 'r') as f:
                existing_leads = json.load(f)
                seen_jobs = {f"{job['title']} | {job['company']}" for job in existing_leads}
        except json.JSONDecodeError: pass
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
            new_leads = []
            
            send_live_update("[TARGET 1] INDEED: Initiating deep scan...")
            indeed_leads = 0
            for page_num in range(5):
                if indeed_leads >= 5: break
                page.goto(f"https://uk.indeed.com/jobs?q={JOB_QUERY.replace(' ', '+')}&l={LOCATION}&start={page_num * 10}", wait_until="domcontentloaded")
                time.sleep(3)
                for card in page.query_selector_all('.job_seen_beacon'):
                    title_elem = card.query_selector('h2.jobTitle span[title]')
                    if not title_elem: continue
                    title = title_elem.inner_text().strip()
                    title_lower = title.lower()
                    card_text = card.inner_text().lower()
                    link_elem = card.query_selector('h2.jobTitle a')
                    href_lower = link_elem.get_attribute('href').lower() if link_elem else ""
                    
                    if "analyst" not in title_lower: continue
                    if not any(loc in card_text for loc in VALID_LOCATIONS): continue
                    if any(banned in title_lower for banned in BANNED_WORDS) or any(banned in href_lower for banned in BANNED_WORDS): continue
                    if any(banned in card_text for banned in BANNED_EXP): continue
                    
                    is_junior_title = any(kw in title_lower for kw in ["junior", "graduate", "entry"])
                    has_target_exp = any(kw in card_text for kw in TARGET_KEYWORDS)
                    if not (is_junior_title or has_target_exp): continue
                    
                    company_elem = card.query_selector('[data-testid="company-name"]')
                    company = company_elem.inner_text().strip() if company_elem else "Unknown Company"
                    job_id = f"{title} | {company}"
                    if job_id in seen_jobs: continue
                    
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        link = f"https://uk.indeed.com{href}" if href.startswith('/') else href
                        new_leads.append({"title": title, "company": company, "link": link, "source": "Indeed", "status": "Awaiting Pitch"})
                        seen_jobs.add(job_id)
                        indeed_leads += 1
                    if indeed_leads >= 5: break
            send_live_update(f"[SUCCESS] INDEED COMPLETE: Secured {indeed_leads} leads.")

            send_live_update("[TARGET 2] LINKEDIN: Initiating deep scan...")
            linkedin_leads = 0
            for page_num in range(5):
                if linkedin_leads >= 5: break
                page.goto(f"https://www.linkedin.com/jobs/search?keywords={JOB_QUERY.replace(' ', '%20')}&location={LOCATION}&start={page_num * 25}", wait_until="domcontentloaded")
                time.sleep(3)
                for card in page.query_selector_all('.base-card'):
                    title_elem = card.query_selector('.base-search-card__title')
                    if not title_elem: continue
                    title = title_elem.inner_text().strip()
                    title_lower = title.lower()
                    link_elem = card.query_selector('.base-card__full-link')
                    href_lower = link_elem.get_attribute('href').lower() if link_elem else ""
                    
                    if "analyst" not in title_lower: continue
                    if any(banned in title_lower for banned in BANNED_WORDS) or any(banned in href_lower for banned in BANNED_WORDS): continue
                    if not any(kw in title_lower for kw in ["junior", "graduate", "entry"]): continue
                    
                    company_elem = card.query_selector('.base-search-card__subtitle')
                    company = company_elem.inner_text().strip() if company_elem else "Unknown Company"
                    job_id = f"{title} | {company}"
                    if job_id in seen_jobs: continue
                    
                    if link_elem:
                        link = link_elem.get_attribute('href').split('?')[0]
                        new_leads.append({"title": title, "company": company, "link": link, "source": "LinkedIn", "status": "Awaiting Pitch"})
                        seen_jobs.add(job_id)
                        linkedin_leads += 1
                    if linkedin_leads >= 5: break
            send_live_update(f"[SUCCESS] LINKEDIN COMPLETE: Secured {linkedin_leads} leads.")

            send_live_update("[TARGET 3] REED: Initiating deep scan...")
            reed_leads = 0
            for page_num in range(1, 6):
                if reed_leads >= 5: break
                page.goto(f"https://www.reed.co.uk/jobs/data-analyst-jobs-in-{LOCATION}?pageno={page_num}", wait_until="domcontentloaded")
                time.sleep(3)
                for header in page.query_selector_all('h2, h3'):
                    link_tag = header.query_selector('a')
                    if not link_tag: continue
                    href = link_tag.get_attribute('href')
                    if not href or '/jobs/' not in href.lower(): continue
                    href_lower = href.lower()
                    title = link_tag.inner_text().strip()
                    title_lower = title.lower()
                    
                    if not title or "browse" in title_lower or "search" in title_lower: continue
                    if "analyst" not in title_lower: continue
                    if any(banned in title_lower for banned in BANNED_WORDS) or any(banned in href_lower for banned in BANNED_WORDS): continue
                    if not any(kw in title_lower for kw in ["junior", "graduate", "entry"]): continue
                    
                    job_id = f"{title} | Reed Scrape"
                    if job_id in seen_jobs: continue
                    
                    link = f"https://www.reed.co.uk{href}" if href.startswith('/') else href
                    new_leads.append({"title": title, "company": "See link for details", "link": link, "source": "Reed", "status": "Awaiting Pitch"})
                    seen_jobs.add(job_id)
                    reed_leads += 1
                    if reed_leads >= 5: break
            send_live_update(f"[SUCCESS] REED COMPLETE: Secured {reed_leads} leads.")

            browser.close()
            
            if not new_leads:
                return "[INFO] HEADHUNTER: Tri-Search complete. No new Junior jobs found."
            
            existing_leads.extend(new_leads)
            with open(vault_path, 'w') as f:
                json.dump(existing_leads, f, indent=4)
            update_google_sheet(new_leads)
            
            message = f"[SUCCESS] NEW ROLES SECURED: {len(new_leads)} opportunities found\n\n"
            for i, job in enumerate(new_leads, 1):
                message += f"{i}. [{job['source']}] {job['title']}\nCompany: {job['company']}\nLink: {job['link']}\n\n"
            return message
    except Exception as e:
        return f"[ERROR] HEADHUNTER SYSTEM CRASH: {str(e)}"

if __name__ == "__main__":
    print(hunt_jobs())