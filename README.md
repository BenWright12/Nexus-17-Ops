# AI Systems & Autonomous Infrastructure | Ben Wright

A showcase of headless, multi agent microservice architectures, automated data extraction pipelines,and local server orchestrations. 

My work in this space focuses on **Separation of Concerns, ETL Pipeline Construction, Autonomous LLM Integration, and Secure Remote CLI Operations** deployed on resource constrained hardware.

---

## The AI Systems

* **[Nexus-17 (The Engine)](./nexus-17)** *(Active)*
  * *Tech:* Python, Bash, Playwright, FFmpeg, Google Gemini, Telegram API, Tailscale.
  * *Overview:* The autonomous engine executing the actual heavy lifting multi agent web scraping, career telemetry, and an automated vertical video production studio controlled via a secure Telegram CLI.

* **Aegis (The Security System)** *(In Development)*
  * *Tech:* [TBD - e.g., Python, FastAPI, Regex/LLM Guards]
  * *Overview:* The invisible guardrail. Monitors LLM response latency, tracks token usage and operational costs in real time, and actively intercepts prompt injections or anomalous inputs.

* **Overwatch (The Dashboard Overview)** *(In Development)*
  * *Tech:* [TBD - e.g., Streamlit / Dash / WebSockets]
  * *Overview:* The single pane of glass. A centralised command dashboard that visualises the telemetry from both The Engine and The Shield, giving the operator full visibility and manual override control.

---

## Core Technical Capabilities

* **Multi Agent Coordination:** Using lightweight Bash routers (`nexus_master.sh`) and modular Python scripts to manage isolated agent workflows.
* **Web Scraping & Telemetry:** Deploying headless Playwright and custom Regex pipelines to extract data from complex, dynamic web platforms.
* **Media & Content Pipelines:** Automating text to speech (Edge-TTS), neural subtitle generation (.ass), and video compositing via FFmpeg.
* **Security & Observability:** Building runtime guardrails for LLMs and unified dashboards for system wide telemetry.