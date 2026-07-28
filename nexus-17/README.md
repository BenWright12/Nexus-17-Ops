# Nexus-17 v1.4 (Codename: The Hive)

> An integrated, multi agent microservice architecture for automated data acquisition, media synthesis, and job market telemetry.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-Scripting-4EAA25?logo=gnu-bash&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Web_Scraping-2EAD33?logo=playwright&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Media_Rendering-007808?logo=ffmpeg&logoColor=white)
![Gemini](https://img.shields.io/badge/LLM-Google_Gemini-8E75B2?logo=google&logoColor=white)

*[PLACEHOLDER: Insert a 10 second GIF here showing the Telegram UI in action]*

## Overview

Nexus-17 is a headless, fully automated AI operations hub hosted on a decommissioned 2017 Intel based server, managed securely via Tailscale tunneling and AlDente thermal/battery integration. 

Operating via a central Bash engine, it establishes a long polling connection with the Telegram API, serving as a remote Command Line Interface (CLI). From this interface, the Admin deploys specialised Python microservices to scrape the web, synthesise media, analyse data via LLMs, and sync telemetry to Google Cloud.

This repository demonstrates **Separation of Concerns**, **ETL Pipeline Construction**, **OAuth 2.0 Integration**, and **Prompt Engineering** within a secure, resource constrained environment.

---

## System Architecture & Agents

The core of Nexus-17 is **nexus_master.sh**, a lightweight router that listens for commands and triggers isolated agents. State is maintained locally via JSON data vaults and synced remotely to Google Sheets.

### 1. `[ ACTOR ]` Media Synthesis Engine

An automated vertical video production studio.

* **Protocol:** Navigates dynamic social aggregators (Reddit) using headless Chromium browsers.
* **Pipeline:** Scraped text is ingested by the Gemini 2.5 LLM, rewritten for pacing and hooks, and piped through Edge-TTS for audio synthesis. Generates .ass subtitle tracks with neural pause weighting and utilises native FFmpeg to composite the final 9:16 MP4 asset.

### 2. `[ HUNTER ]` B2B Data Acquisition

A high yield residential lead generator.

* **Protocol:** Deploys headless Playwright instances to navigate complex UK council planning portals.
* **Pipeline:** Utilises a custom pagination sweeper and Regex pipeline to extract approved/pending residential planning applications. Bypasses basic API limiters, validates data integrity, and synchronises qualified leads to an external CRM (Google Sheets).

### 3. `[ HEADHUNTER ]` Job Market Telemetry

An automated career deployment specialist.

* **Protocol:** Scrapes aggregated job boards (Indeed, LinkedIn, Reed) based on predefined VIP parameters, explicitly filtering out bloated or irrelevant metadata.
* **Pipeline:** Validated roles trigger an LLM driven generation sequence to draft context aware, 150 word outreach emails based on the Admin's configured skill profile. Syncs the live pipeline to Google Cloud via OAuth 2.0 Service Accounts.

### 4. `[ LIBRARIAN ]` Internal DevOps & Auditing

The system's self maintaining memory and deployment auditor.

* **Protocol:** Monitors CPU thermals and active system PIDs (psutil).
* **Pipeline:** If the system is nominal, it parses daily log arrays, utilises Gemini to distill logs into high level operational bullet points, flushes temporary caches, and initiates a secure git push to maintain a public system heartbeat.

---

## Development Philosophy & AI Integration

Nexus-17 was conceptualised, architected, and deployed entirely by myself. However, as an advocate for modern, AI augmented engineering, Generative AI (LLMs) were utilised during development as advanced pair programming tools.

Specifically, AI was leveraged to:

* Accelerate the generation of Python templates and error handling loops.

* Refine the complex Regex targeting for the UK Council scraping pipelines.

* Ensure strict UK English standardisation and formatting across the system documentation.

Every agent, Bash routing command, hardware constraint, and security protocol within this repository has been manually engineered, logically verified, and structured by myself to adhere to strict enterprise standards (Separation of Concerns, secure environment variables, and modularity). This project demonstrates my ability to build complex, production ready systems while accelerating development cycles using AI.

---

## Repository Structure

nexus-17/

├── nexus_master.sh 

├── system_credentials_example.md

├── public_status.md

├── requirements.txt 

├── README.md                       

├── agents/

│ ├── agent_actor_engine.py

│ ├── agent_actor_subtitles.py

│ ├── agent_data_scraper.py

│ ├── agent_headhunter_pitch.py

│ ├── agent_headhunter_scraper.py

│ └── agent_librarian.py

├── core/

│ └── system_the_hive_briefing.py

├── docs/

│ ├── agent_protocols.md

│ └── architecture.md 

├── media/

│ └── backgrounds/ 

├── utils/

│ ├── utils_db_handshake.py

│ ├── utils_env_diagnostic.py

│ ├── utils_llm_ping.py

│ ├── utils_telegram_test.py 

│ └── utils_vault_integrity.py

├── vault/

│ ├── careers_example.json        

│ ├── pending/

│ │ └── leads_example.json