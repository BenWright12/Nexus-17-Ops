import os
import sys
import json

# If a script crashes while writing to JSON, the file gets corrupted. 
# This test iterates through your vault directory, attempts to parse the JSON files, and counts the records, proving you understand local data integrity.

def verify_json(file_path):
    print(f"[PROCESS] Auditing data structure: {os.path.basename(file_path)}...")
    if not os.path.exists(file_path):
        print("  [INFO] File does not exist yet. Status: Clean/Empty.")
        return True
        
    if os.path.getsize(file_path) == 0:
        print("  [WARN] File exists but is exactly 0 bytes. Potential write fault.")
        return False
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            print(f"  [SUCCESS] JSON integrity verified. Valid array containing {len(data)} records.")
        elif isinstance(data, dict):
            print(f"  [SUCCESS] JSON integrity verified. Valid dictionary with {len(data.keys())} root keys.")
        else:
            print("  [WARN] JSON is valid, but root structure is not a List or Dictionary.")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  [FATAL] Data corruption detected. JSON Decode Fault: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Unexpected read fault: {e}")
        return False

def run_vault_audit():
    print("[INFO] INITIATING VAULT INTEGRITY AUDIT")
    
    targets = [
        '/path/to/PROJECT_ROOT/vault/careers.json',
        '/path/to/PROJECT_ROOT/vault/pending/leads.json',
        '/path/to/PROJECT_ROOT/memory/hive_state.json'
    ]
    
    faults = 0
    for target in targets:
        if not verify_json(target):
            faults += 1
            
    print("\n[INFO] AUDIT SUMMARY")
    if faults == 0:
        print("[SUCCESS] All local data structures passed integrity checks. Zero corruption detected.")
    else:
        print(f"[ERROR] Audit complete with {faults} structural fault(s). Manual intervention required.")

if __name__ == "__main__":
    run_vault_audit()