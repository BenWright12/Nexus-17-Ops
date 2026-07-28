import os
import shutil
import subprocess
import sys

# This script verifies that all external system binaries (like FFmpeg) and required directories exist on the host machine.

def check_command(cmd, name):
    print(f"[PROCESS] Verifying binary dependency: {name}...")
    if shutil.which(cmd):
        print(f"  [SUCCESS] {name} is installed and available in PATH.")
        return True
    else:
        print(f"  [ERROR] {name} not found. Pipeline will fail.")
        return False

def check_playwright():
    print("[PROCESS] Verifying Playwright Chromium binaries...")
    try:
        cache_path = os.path.expanduser('~/Library/Caches/ms-playwright')
        if os.path.exists(cache_path) and len(os.listdir(cache_path)) > 0:
            print("  [SUCCESS] Playwright browser binaries located.")
            return True
        else:
            print("  [WARN] Playwright binaries may be missing. Run 'playwright install'.")
            return False
    except Exception as e:
        print(f"  [ERROR] Playwright check failed: {e}")
        return False

def check_directories(dirs):
    all_good = True
    print("[PROCESS] Verifying Core Directory Structure...")
    for d in dirs:
        if os.path.exists(d):
            print(f"  [SUCCESS] Directory verified: {d}")
        else:
            print(f"  [WARN] Directory missing, creating now: {d}")
            try:
                os.makedirs(d)
                print(f"  [SUCCESS] Created: {d}")
            except Exception as e:
                print(f"  [ERROR] Failed to create {d}: {e}")
                all_good = False
    return all_good

def run_diagnostics():
    print("[INFO] INITIATING ENVIRONMENT DIAGNOSTICS")
    
    cmds_ok = all([
        check_command('ffmpeg', 'FFmpeg'),
        check_command('afinfo', 'Apple Audio Info (afinfo)'),
        check_command('edge-tts', 'Edge-TTS')
    ])
    
    pw_ok = check_playwright()
    
    core_dirs = [
        '/path/to/PROJECT_ROOT/vault',
        '/path/to/PROJECT_ROOT/vault/pending',
        '/path/to/PROJECT_ROOT/memory',
        '/path/to/PROJECT_ROOT/temp',
        '/path/to/OUTPUT_DIR/Videos',
        '/path/to/OUTPUT_DIR/Pitches',
        '/path/to/MEDIA_DIR/Backgrounds'
    ]
    dirs_ok = check_directories(core_dirs)
    
    print("\n[INFO] DIAGNOSTIC SUMMARY")
    if cmds_ok and pw_ok and dirs_ok:
        print("[SUCCESS] Environment is 100% compliant. Ready for deployment.")
    else:
        print("[WARN] Environment check completed with warnings or errors. Review logs above.")

if __name__ == "__main__":
    run_diagnostics()