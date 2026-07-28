import urllib.request
import urllib.parse
import urllib.error
import os

# This script validates Telegram bot credentials by transmitting a test telemetry message to the remote Telegram API.

def test_telegram():
    print("[INFO] CORE NETWORK DIAGNOSTIC TOOL")
    token, chat_id = None, None
    socials_path = '/path/to/system_credentials_example.md'
    
    if not os.path.exists(socials_path):
        print(f"[FATAL] Cannot locate credentials at {socials_path}")
        return

    try:
        with open(socials_path, 'r') as f:
            for line in f:
                if 'Bot_Token' in line:
                    token = line.strip().split()[-1].strip(' "\'\n')
                elif 'Chat_ID' in line:
                    chat_id = line.strip().split()[-1].strip(' "\'\n')
    except Exception as e:
        print(f"[ERROR] Failed reading credentials: {e}")
        return

    print(f" [PROCESS] Token Verification: {'[OK]' if token else '[FAIL]'} (Prefix: {token[:10] + '...' if token else 'N/A'})")
    print(f" [PROCESS] Chat ID Verification: {'[OK]' if chat_id else '[FAIL]'} (Value: {chat_id})")

    if not token or not chat_id:
        print("\n[FATAL] Key extraction failed. Diagnostic terminated.")
        return

    print("\n[PROCESS] Transmitting test packet to remote server...")
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': "[INFO] DIAGNOSTIC: Network connection established.", 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req, timeout=5)
        print(f"[SUCCESS] Handshake complete. Remote server responded: {response.getcode()}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"[ERROR] API HTTP FAULT [{e.code}]:\n{error_body}")
    except Exception as e:
        print(f"[ERROR] NETWORK FAULT: {e}")

if __name__ == "__main__":
    test_telegram()