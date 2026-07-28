#!/bin/bash
# NEXUS-17: THE HIVE V1.4 (CORE SERVER)

TOKEN=$(grep "Bot_Token" /path/to/system_credentials_example.md | awk '{print $NF}')
ID=$(grep "Chat_ID" /path/to/system_credentials_example.md | awk '{print $NF}')
OFFSET_FILE=".tg_offset"

echo "[NEXUS-17] Booting Hive Orchestrator..."

echo "[SYSTEM] Flushing old Telegram messages..."
LATEST_UPDATE=$(curl -s "https://api.telegram.org/bot$TOKEN/getUpdates" | grep -o '"update_id":[0-9]*' | tail -1 | cut -d':' -f2)
if [ ! -z "$LATEST_UPDATE" ]; then
OFFSET=$((LATEST_UPDATE + 1))
echo "$OFFSET" > "$OFFSET_FILE"
curl -s "https://api.telegram.org/bot$TOKEN/getUpdates?offset=$OFFSET" > /dev/null
echo "[+] Backlog cleared."
elif [ -f "$OFFSET_FILE" ]; then
OFFSET=$(cat "$OFFSET_FILE")
else
OFFSET=0
fi

send_msg() { curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" -d chat_id="$ID" --data-urlencode text="$1" > /dev/null; }
send_menu() { curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" -d chat_id="$ID" --data-urlencode text="$1" -d reply_markup="$2" > /dev/null; }

curl -s -X POST "https://api.telegram.org/bot$TOKEN/setMyCommands" -H "Content-Type: application/json" -d '{"commands": [{"command": "start", "description": "< Main Menu"}, {"command": "hunt", "description": "[ ACTOR ] Video Studio"}, {"command": "data", "description": "[ HUNTER ] B2B Leads"}, {"command": "jobs", "description": "[ HEADHUNTER ] Careers"}, {"command": "sync", "description": "[ LIBRARIAN ] Audit"}, {"command": "kill", "description": "[!] Emergency Stop"}]}' > /dev/null

# 🚨 THE MASTER MENU
MENU_MASTER='{"keyboard": [["[ ACTOR ] Video Studio", "[ HUNTER ] B2B Leads"], ["[ HEADHUNTER ] Job Scout", "[ LIBRARIAN ] Audit & Sync"], ["[ SYSTEM ] Shutdown"]], "resize_keyboard": true}'

# 🚨 THE ACTION MENU
MENU_ACTION='{"keyboard": [["> Render Video", "> Rewrite Script"], ["> Manual Override", "< Main Menu"]], "resize_keyboard": true}'
MENU_CLEAR='{"remove_keyboard": true}'

send_menu "[SYSTEM] Reset complete. The Hive is online." "$MENU_MASTER"
STATE="IDLE"

while true; do
UPDATES=$(curl -s "https://api.telegram.org/bot$TOKEN/getUpdates?offset=$OFFSET&timeout=30")
UPDATE_ID=$(echo "$UPDATES" | grep -o '"update_id":[0-9]*' | head -1 | cut -d':' -f2)
CMD_TEXT=$(echo "$UPDATES" | grep -o '"text":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ ! -z "$UPDATE_ID" ]; then
if [ "$STATE" == "MANUAL_EDIT" ] && [[ "$CMD_TEXT" != *"< Main Menu"* ]] && [[ "$CMD_TEXT" != *"/start"* ]]; then
echo -e "$CMD_TEXT" > pending_story.txt
STATE="IDLE"
CMD_TEXT="> Render Video"
fi

case "$CMD_TEXT" in
*"/start"* | *"< Main Menu"*)
STATE="IDLE"
send_menu "[THE HIVE] Core server standing by." "$MENU_MASTER"
;;
*"/kill"* | *"[ SYSTEM ] Shutdown"*)
send_msg "[!] EMERGENCY SHUTDOWN ACTIVATED."
send_menu "The Hive is going offline. Manual reboot required via host terminal." "$MENU_CLEAR"
pkill -f "ffmpeg" > /dev/null 2>&1
pkill -f "agent_actor_engine.py" > /dev/null 2>&1
pkill -f "agent_headhunter_scraper.py" > /dev/null 2>&1
pkill -f "agent_data_scraper.py" > /dev/null 2>&1
exit 0
;;

# 🎬 AGENT 1: THE ACTOR
*"/hunt"* | *"[ ACTOR ]"*)
send_msg "[PROCESS] ACTOR: Scouting source data and drafting script..."
STORY_DATA=$(python3 agents/agent_actor_engine.py hunt)
if [[ "$STORY_DATA" == *"[ERROR]"* ]]; then
send_menu "$STORY_DATA" "$MENU_MASTER"
else
send_msg "$STORY_DATA"
send_menu "[INFO] Payload loaded. Select next action:" "$MENU_ACTION"
fi
;;

*"> Rewrite Script"*)
send_msg "[PROCESS] ACTOR: Re-drafting narrative..."
STORY_DATA=$(python3 agents/agent_actor_engine.py rewrite)
if [[ "$STORY_DATA" == *"[ERROR]"* ]]; then
send_menu "$STORY_DATA" "$MENU_MASTER"
else
send_msg "$STORY_DATA"
send_menu "[INFO] New draft loaded. Select action:" "$MENU_ACTION"
fi
;;

*"> Manual Override"*)
STATE="MANUAL_EDIT"
send_menu "[INPUT REQUIRED] Manual Override: Paste raw script data below." '{"keyboard": [["< Main Menu"]], "resize_keyboard": true}'
;;

*"> Render Video"*)
send_menu "[PROCESS] ACTOR Stage 1/4: Audio Synthesis" "$MENU_CLEAR"
python3 -m edge_tts --voice en-GB-SoniaNeural --rate=+15% -f pending_story.txt --write-media voiceover_fast.mp3
while [ ! -s voiceover_fast.mp3 ]; do sleep 0.5; done
send_msg "[PROCESS] ACTOR Stage 2/4: Subtitle Generation"
python3 agents/agent_actor_subtitles.py
if [ ! -f "captions.ass" ]; then
send_menu "[ERROR] Subtitle generation failed." "$MENU_MASTER"
else
send_msg "[PROCESS] ACTOR Stage 3/4: Media Rendering"
mkdir -p /path/to/OUTPUT_DIR/Videos
BG_CLIP=$(ls /path/to/MEDIA_DIR/Backgrounds/*.mp4 2>/dev/null | python3 -c "import sys, random; lines = sys.stdin.readlines(); print(random.choice(lines).strip()) if lines else print('')")
if [ -z "$BG_CLIP" ]; then
send_menu "[ERROR] Source media not found." "$MENU_MASTER"
else
FILE_NAME="reddit_$(date +%s).mp4"
ffmpeg -i "$BG_CLIP" -i voiceover_fast.mp3 -filter_complex "[0:v]setpts=0.8*PTS,crop=ih*(9/16):ih,scale=1080:1920,subtitles=captions.ass[v]" -map "[v]" -map 1:a -c:v libx264 -preset superfast -crf 22 -shortest -aspect 9:16 -y /path/to/OUTPUT_DIR/Videos/$FILE_NAME > /dev/null 2>&1

if [ $? -eq 0 ]; then
send_menu "[SUCCESS] Render complete. Asset saved: $FILE_NAME" "$MENU_MASTER"
else
send_menu "[ERROR] Render engine failed." "$MENU_MASTER"
fi
fi
fi
rm -f voiceover.aiff voiceover_fast.mp3 captions.ass
;;

# 🏹 AGENT 2: THE HEADHUNTER
*"/jobs"* | *"[ HEADHUNTER ]"*)
send_msg "[PROCESS] HEADHUNTER: Initiating multi-board data sweep..."
JOB_DATA=$(python3 agents/agent_headhunter_scraper.py)
send_msg "$JOB_DATA"
if [[ "$JOB_DATA" == *"[SUCCESS] NEW ROLES SECURED"* ]]; then
send_msg "[PROCESS] HEADHUNTER: Generating dynamic pitches..."
PITCH_DATA=$(python3 agents/agent_headhunter_pitch.py)
send_msg "$PITCH_DATA"
fi
send_menu "[SYSTEM] Headhunter operations concluded." "$MENU_MASTER"
;;

# 🕵️ AGENT 3: THE DATA ACQUISITION SPECIALIST
*"/data"* | *"[ HUNTER ]"*)
send_msg "[PROCESS] HUNTER: Booting Precision Search Protocol...\nStandby for live telemetry."
LEAD_DATA=$(python3 agents/agent_data_scraper.py)
send_msg "$LEAD_DATA"
send_menu "[SYSTEM] Acquisition run complete." "$MENU_MASTER"
;;

# 📚 AGENT 4: THE LIBRARIAN (Manual Force Sync)
*"/sync"* | *"[ LIBRARIAN ]"*)
send_msg "[PROCESS] LIBRARIAN: Executing unified system audit & remote sync..."
LIB_DATA=$(python3 agents/agent_librarian.py)
send_menu "[SYSTEM] Maintenance complete." "$MENU_MASTER"
;;
esac
OFFSET=$((UPDATE_ID + 1))
echo "$OFFSET" > "$OFFSET_FILE"
fi
sleep 1
done