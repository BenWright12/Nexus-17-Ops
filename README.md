# NEXUS-17: SOVEREIGNTY NODE (V1.4)
> **Autonomous Data Extraction, Career ETL, and Content Pipeline**

Nexus-17 is a high performance, low footprint AI operations hub hosted on a decommissioned 2017 Intel based node. It utilises a multi-agent orchestration layer to handle data acquisition, lead scoring, and automated media production.

## ARCHITECTURE OVERVIEW
The system operates on a **Zero Trust Bootstrap** protocol, ensuring hardware longevity and data integrity through:
- **Modular Agents:** Dedicated LLM nodes (Gemini 2.5 Flash/Pro) for specialised tasks.
- **Hardware Safeguards:** Thermal awareness processing and SMC level battery management (AlDente integration).
- **Secure Tunneling:** Remote Command and Control via Tailscale.

## THE AGENT STACK
1. **THE HUNTER:** Precision web scraping and lead scoring (1-10) for London based planning data.
2. **THE HEADHUNTER:** Automated career matching and contextual pitch generation for Data Analytics roles.
3. **THE ACTOR/PUBLISHER:** End to end viral content creation using FFmpeg, ElevenLabs, and TikTok API.
4. **THE LIBRARIAN:** Chief Data Officer responsible for memory persistence, vault maintenance, and public reporting.

## PRIVACY & COMPLIANCE
This repository serves as a **Public Status Monitor**. 
To protect proprietary business logic and PII (Personally Identifiable Information), the core agent configurations and raw data vaults are air gapped from this public repo via an inverted `.gitignore` protocol.

**[View Live Updates in PUBLIC_STATUS.md]**
---
*Managed by Nexus-17 Librarian Agent | Node Status: London-01*