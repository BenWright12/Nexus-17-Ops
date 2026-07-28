import os
import sys
import json
import time
import urllib.request
import urllib.error

# This script sends a micro payload to the Gemini API to verify authentication is valid and measures network latency.

def get_gemini_key():
    print("[PROCESS] Extracting Gemini API Key from secure storage...")
    try:
        with open('/path/to/system_credentials_example.md', 'r') as f:
            for line in f:
                if "Gemini_API" in line:
                    key = ''.join(c for c in line.split(':', 1)[1] if c.isalnum() or c in '-_')
                    print(f"  [SUCCESS] Key acquired (Prefix: {key[:5]}...)")
                    return key
    except Exception as e:
        print(f"  [FATAL] Credential extraction failed: {e}")
    return None

def ping_llm():
    print("[INFO] INITIATING API LATENCY & AUTHENTICATION TEST")
    api_key = get_gemini_key()
    if not api_key:
        print("[FATAL] Cannot proceed without valid API key.")
        sys.exit(1)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    payload = {"contents": [{"parts": [{"text": "Reply with exactly one word: 'ACK'"}]}]}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)

    print("[PROCESS] Transmitting handshake packet to Google DeepMind servers...")
    start_time = time.time()
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            latency = (time.time() - start_time) * 1000  
            res = json.loads(response.read().decode())
            
            if 'candidates' in res:
                reply = res['candidates'][0]['content']['parts'][0]['text'].strip()
                print(f"  [SUCCESS] Handshake acknowledged. Payload response: '{reply}'")
                print(f"  [INFO] Network Latency: {latency:.2f} ms")
                if latency > 3000:
                    print("  [WARN] Latency is unusually high. Operations may be degraded.")
                else:
                    print("  [SUCCESS] Connection speed is optimal.")
            else:
                print("  [WARN] Unexpected JSON structure received.")
    except urllib.error.HTTPError as e:
        print(f"  [ERROR] API rejected connection. HTTP Fault: {e.code}")
        if e.code == 429:
            print("  [WARN] Diagnosis: Rate Limit Exceeded (429).")
        elif e.code == 403:
            print("  [WARN] Diagnosis: Invalid API Key (403).")
    except Exception as e:
        print(f"  [ERROR] Network fault: {e}")

if __name__ == "__main__":
    ping_llm()