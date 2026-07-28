import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import random
import time
import os
from playwright.sync_api import sync_playwright

API_KEY = None
BOT_TOKEN = None
CHAT_ID = None

try:
    with open('/path/to/system_credentials_example.md', 'r') as f:
        for line in f:
            if "Gemini_API" in line:
                raw_key = line.split(':', 1)[1]
                API_KEY = ''.join(c for c in raw_key if c.isalnum() or c in '-_')
            elif "Bot_Token" in line:
                raw_token = line.split(':', 1)[1]
                BOT_TOKEN = ''.join(c for c in raw_token if c.isalnum() or c in '-_:')
            elif "Chat_ID" in line:
                raw_id = line.split(':', 1)[1]
                CHAT_ID = ''.join(c for c in raw_id if c.isalnum() or c in '-_')
    if not API_KEY:
        print("[ERROR] 'Gemini_API' found, but the key is blank.", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Secrets file read failure - {e}", file=sys.stderr)
    sys.exit(1)

def send_live_update(message):
    if not BOT_TOKEN or not CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except: pass

SUBS = [
    "AmItheAsshole", "relationship_advice", "TrueOffMyChest", "EntitledParents",
    "pettyrevenge", "MaliciousCompliance", "talesfromtechsupport", "antiwork",
    "badroommates", "Glitch_in_the_Matrix"
]

HOOKS = {
    "AmItheAsshole": "Am I the asshole",
    "relationship_advice": "My relationship is completely falling apart",
    "TrueOffMyChest": "I need to get this off my chest right now",
    "EntitledParents": "You won't believe what this entitled parent actually tried to do",
    "pettyrevenge": "Here is exactly how I got the ultimate revenge",
    "MaliciousCompliance": "They told me to follow the rules, so I did exactly that",
    "talesfromtechsupport": "You won't believe the absolute idiot I dealt with at work today",
    "antiwork": "This is exactly why I am quitting my job",
    "badroommates": "My roommate is an absolute living nightmare",
    "Glitch_in_the_Matrix": "I think I just experienced a literal glitch in the matrix"
}

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    data = json.dumps(payload).encode('utf-8')
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode())
                if 'candidates' in res and len(res['candidates']) > 0:
                    candidate = res['candidates'][0]
                    if 'content' in candidate:
                        return candidate['content']['parts'][0]['text'].strip()
                    elif 'finishReason' in candidate:
                        send_live_update(f"[WARN] AI BLOCKED: Google refused to write this. Reason: {candidate['finishReason']}")
                        return f"[ERROR] AI Blocked: {candidate['finishReason']}"
                return "[ERROR] Unexpected empty response from Google."
        except urllib.error.HTTPError as e:
            if e.code == 429:
                send_live_update("[WARN] AI RATE LIMIT: Gemini is cooling down. Waiting 30s...")
                time.sleep(30)
                continue
            return f"[ERROR] AI HTTP Fault: {e.code}"
        except Exception as e:
            return f"[ERROR] AI Parse Fault: {e}"
    return "[ERROR] AI pipeline jammed."

def hunt():
    send_live_update("[PROCESS] ACTOR: Initiating Browser Ghost Protocol...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for attempt in range(3):
            sub = random.choice(SUBS)
            hook = HOOKS.get(sub, "Listen to this insane story")
            url = f"https://www.reddit.com/r/{sub}/top.json?t=month&limit=30"
            print(f"\n" + "="*40, file=sys.stderr, flush=True)
            print(f"[TARGET] ACQUIRED: r/{sub}", file=sys.stderr, flush=True)
            try:
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(3)
                raw_json_text = page.evaluate("document.body.innerText")
                data = json.loads(raw_json_text)
                valid_posts = [p['data'] for p in data.get('data', {}).get('children', []) if not p['data'].get('stickied') and len(p['data'].get('selftext', '')) > 100]
                if not valid_posts:
                    time.sleep(2)
                    continue
                post = random.choice(valid_posts[:5])
                title = post['title']
                raw_text = post['selftext'].strip()
                word_count = len(raw_text.split())
                send_live_update(f"[INFO] ASSET SECURED\nTitle: {title[:100]}...\nSource: r/{sub}\nLength: {word_count} words.")
                
                with open('raw_story.txt', 'w') as f:
                    f.write(f"HOOK: {hook}\nTITLE: {title}\n\nSTORY: {raw_text}")
                
                prompt = (
                    "Rewrite this Reddit story for a viral TikTok video using perfect British English (UK spelling and grammar).\n\n"
                    "RULES:\n"
                    "1. Format the output entirely as spoken text. No emojis, no stage directions, no hashtags. Do NOT use asterisk symbols.\n"
                    "2. Expand abbreviations and use commas for natural text-to-speech pauses (e.g., '31M' becomes 'I, a 31 year old male, ').\n"
                    "3. Do not over-compress the story. Keep the most dramatic details, the climax, and the resolution intact so the narrative makes perfect logical sense.\n"
                    f"4. CRITICAL: The very first sentence must be EXACTLY this hook: '{hook}.'\n"
                    "5. After the hook, start a new sentence and transition naturally into the context of the story.\n\n"
                    f"Title: {title}\nText: {raw_text}"
                )
                send_live_update("[PROCESS] CORE: Analysing text and synthesising cohesive script...")
                script = ask_gemini(prompt)
                
                if script.startswith("[ERROR]"):
                    send_live_update(script)
                    browser.close()
                    return script
                    
                with open('pending_story.txt', 'w') as f:
                    f.write(script)
                send_live_update(f"[SUCCESS] SCRIPT READY\n\n{script[:250]}...")
                browser.close()
                return f"[SUCCESS] ASSET SECURED & REWRITTEN\n\nGenre: r/{sub}\nTitle: {title}\n\nPreview:\n{script}"

            except Exception as e:
                print(f"[WARN] Browser Fetch Fault: {e}", file=sys.stderr)
                time.sleep(2)
                continue
        browser.close()
        return "[ERROR] Browser Ghost Protocol failed. Target rejected connections."

def rewrite():
    send_live_update("[PROCESS] ACTOR: Re-drafting narrative...")
    try:
        if not os.path.exists('raw_story.txt'):
            return "[ERROR] 'raw_story.txt' not found. Run standard acquisition first."
        with open('raw_story.txt', 'r') as f:
            lines = f.readlines()
            hook = lines[0].strip().replace("HOOK: ", "")
            raw_data = "".join(lines[1:])
        prompt = (
            "Rewrite this Reddit story to be punchier but maintain a cohesive, logical narrative. Use perfect British English.\n"
            "CRITICAL: Use commas around age/gender drops (e.g. 'I, a 25 year old male, ') for natural spoken pauses.\n"
            "CRITICAL: Output entirely as spoken text. No emojis, no stage directions.\n"
            f"CRITICAL: Start the very first sentence with the exact words '{hook}.'\n\n"
            f"{raw_data}"
        )
        send_live_update("[PROCESS] CORE: Generating secondary draft...")
        new_script = ask_gemini(prompt)
        if new_script.startswith("[ERROR]"): return new_script
        with open('pending_story.txt', 'w') as f: f.write(new_script)
        send_live_update(f"[SUCCESS] NEW DRAFT READY\n\n{new_script[:250]}...")
        return f"[SUCCESS] NEW DRAFT READY:\n\n{new_script}"
    except Exception as e: return f"[ERROR] Rewrite failure: {e}"

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "hunt"
    if mode == "rewrite":
        print(rewrite())
    else:
        print(hunt())