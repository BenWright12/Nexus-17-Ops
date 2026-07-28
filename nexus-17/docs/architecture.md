# SYSTEM ARCHITECTURE

Nexus-17 (Codename: The Hive) is a multi agent orchestrated system designed for fully automated data acquisition, media synthesis, and job market telemetry. 

The architecture relies on a central Bash driven loop communicating with specialised Python microservices via a headless Telegram interface.

## Core Orchestration (nexus_master.sh)
The master orchestrator is written in Bash. It establishes a long polling connection with the Telegram API to listen for Admin commands. Upon receiving a command, the Bash script acts as a router, deploying the appropriate Python agent, awaiting its exit code, and reporting the telemetry back to the user interface.

## Agent Microservices
The system relies on strict Separation of Concerns. Each agent operates in total isolation, communicating state changes exclusively through local JSON vaults and cloud databases.

### 1. [ ACTOR ] Media Synthesis Agent
* **Tech Stack:** `playwright`, `google-generativeai`, `edge-tts`, `ffmpeg`
* **Protocol:** Navigates dynamic social aggregators (Reddit) using headless Chromium browsers. Acquired text is sanitised and rewritten by the Gemini LLM for pacing. The agent utilises Edge-TTS for audio synthesis, generates subtitle tracks (.ass), and calls native FFmpeg binaries to composite the final 9:16 vertical video asset.

### 2. [ HUNTER ] B2B Lead Generation
* **Tech Stack:** `playwright`, `re` (Regex)
* **Protocol:** Bypasses basic API limitations by deploying headless Chromium instances directly to UK council planning portals. Uses a custom pagination sweeper and Regex pipeline to extract approved/pending residential planning applications, scoring and saving them to local leads.json arrays before syncing to Google Cloud.

### 3. [ HEADHUNTER ] Market Telemetry
* **Tech Stack:** `playwright`, `gspread`, `oauth2client`
* **Protocol:** Scrapes aggregated job boards (Indeed, LinkedIn, Reed) based on predefined VIP parameters (e.g., bypassing "senior" or "unpaid" tags). Validated roles trigger a secondary Gemini API call to draft context aware 150 word outreach emails based on the Admin's configured skill profile, pushing the drafted pitches directly to a linked Google Sheet.

### 4. [ LIBRARIAN ] System Auditing
* **Tech Stack:** `psutil`, `subprocess`
* **Protocol:** The internal DevOps agent. Monitors CPU thermals and active process IDs (psutil). If the system is nominal, it parses the daily logging arrays, uses the LLM to distill the logs into three high level operational bullet points, and initiates a secure git push to maintain the public system heartbeat.