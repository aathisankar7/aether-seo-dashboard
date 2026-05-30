# Project Memory: Aether SEO SaaS Intelligence

This document serves as the "Long-Term Memory" for the Aether SEO project, designed to be fed into Windsurf or other AI coding assistants to provide instant context on architecture, progress, and technical specifications.

## 🏗️ Project Overview
**Aether SEO** is a high-performance, AI-driven SEO SaaS dashboard. It automates technical audits, competitor analysis, keyword research, and link prospecting using a distributed fleet of AI models (Groq, SambaNova, Local Qwen).

## 🚀 Key Milestones Reached
- [x] **Initial Audit Engine**: Built a multi-step SEO auditor utilizing SSE (Server-Sent Events) for real-time logging.
- [x] **Premium UI**: Developed a glassmorphic, CSS-vibrant dashboard with real-time "Health Rings" and terminal-style feedback.
- [x] **SaaS Migration**: Successfully migrated from local SQLite/single-user logic to a multi-tenant SaaS model.
- [x] **Database Evolution**: Switched from SQLite to **MongoDB** (using `motor` async driver) to support Vercel's serverless infrastructure.
- [x] **Professional Restructuring**: Reorganized the codebase into a modular `core`/`agents`/`public` hierarchy.
- [x] **API Research**: Integrated **Firecrawl** (fc-*) with 500+ credits for advanced scraping and crawling.
- [x] **Premium Scraping**: Added Firecrawl as a first-class scraper option in the AI Arsenal.

## 📂 Architecture & Directory Structure
The project follows a modular, serverless-ready Python architecture:

```
seo_project/
├── api/                    # Vercel Serverless entry points
│   └── index.py            # Primary FastAPI application
├── core/                   # Engine Room
│   ├── mongodb_manager.py  # Async MongoDB & JWT Auth Logic
│   └── model_router.py     # Intelligent LLM Task Routing
├── agents/                 # Specialized AI Fleet
│   ├── seo_expert_agent.py # Lead Orchestrator
│   └── *_analyzer.py       # Technical & Strategic Analyzers
├── public/                 # Premium Frontend
│   └── seo_dashboard.html  # Glassmorphic UI Dashboard
├── public-apis-clone/      # Research Library (1,400+ APIs)
├── requirements.txt        # Backend dependencies (fastapi, motor, bcrypt, jose)
├── vercel.json             # Deployment routing configuration
└── README.md               # User-facing documentation
```

## 🔒 Security & Identity
- **Authentication**: JWT-based session management. Tokens are salted/verified via `core/mongodb_manager.py`.
- **Encryption**: Passwords are hashed using **BCRYPT**.
- **Env Strategy**: All sensitive keys (Groq, SambaNova, MongoDB) are managed via `.env` (locally) or Environment Variables (prod).

## 🌐 Research & Future Expansion
We have identified the following APIs for Phase 2 integration:
- **Firecrawl**: INTEGRATED (fc-*) — Used for high-fidelity web scraping and crawling.
- **ScreenshotAPI.net**: To generate live visual previews of audited sites.
- **Open Page Rank**: To provide a proprietary "Authority Score".
- **Clearbit Logo API**: To automatically brand audit reports with client logos.
- **VirusTotal**: To add a "Security/Blacklist" check to every audit.

## 🛠️ Current Development Stack
- **Backend**: FastAPI, Uvicorn, SSE-Starlette.
- **Frontend**: TailwindCSS (Canvas-based rendering), Vanilla JavaScript.
- **Database**: MongoDB (Motor async wrapper).
- **Deployment**: Vercel (Production), Local Python 3.x (Development).

## ⚠️ Important Context for Windsurf
- **Absolute Paths**: When importing within the project, use `sys.path.append(os.path.dirname(os.path.dirname(__file__)))` patterns (seen in `api/index.py`) to maintain compatibility between local servers and Vercel serverless functions.
- **SSE Support**: High-intensity audits stream data via `EventSource`. The frontend expects standard JSON reports pushed via a `/stream` endpoint.
- **MongoDB**: The app WILL CRASH without a valid `MONGODB_URI` in the environment.

## System Intelligence: The SEO Bible (P1)
The core logic for competitor and keyword discovery is defined in `SEO_BIBLE.md`.
- **DNA Extraction**: Prioritizes branding-based transactional keywords.
- **Competitor Discovery**: Top **5** hyper-local verified competitors (no aggregators, no self-brand).
- **Keyword Merging**: Unified "Bible" output combining Client DNA, Competitor Spying, and AI Engineering.

### ⚠️ CRITICAL: Competitor Analysis Rules (NEVER CHANGE)
These rules were debugged and finalized on 2026-03-24. They MUST be followed:

1. **Serper API is PRIMARY** search engine. SerpApi is fallback only.
2. **Target = 5 competitors** always. Never fewer.
3. **Self-domain filter is TLD-agnostic**: Compare base names without TLD (e.g., `parthadental.com` vs `parthadental.in` → both have base `parthadental` → BLOCKED).
4. **Brand-name keyword cleaning**: Strip the client's brand name from search queries. "Partha Dental Hyderabad" → "Dental Hyderabad". Always inject generic niche queries like "best [niche] in [city]".
5. **Junk domains list** must include: `localo.site`, `apollo247`, `careinsurance`, `policybazaar`, `cybo.com`, plus all social, directory, and news sites.
6. **Graceful fill**: If AI verification finds < 5 competitors, fill remaining slots from top-scoring Google results (scrape-only, no AI verification needed).
7. **Verification confidence threshold = 0.5** (not higher — too many false rejections).
8. **Location check is SOFT**: Log a warning if city text is absent, but let AI decide — do NOT hard-reject.
9. **Candidate pool = top 20** from Google (sorted by score). Search **15 results per keyword**, up to **10 keywords**.
10. **Data keys**: Return both `competitor_analysis` (Aether Dashboard) and `competitor_intelligence` (Streamlit) in the final report. Each competitor object MUST have both `report` and `battle_sheet` keys.

### Startup Commands
```bash
# FastAPI Backend (port 8000) - Run from backend/ folder
cd backend
python3 -m uvicorn api.index:app --host 127.0.0.1 --port 8000

# Open frontend in default browser
open http://127.0.0.1:8000
```

## 🛠️ Upgrades Added (May 28-29, 2026)
We successfully performed a major architectural and connectivity overhaul:
1. **Repository Relocation & Restructuring:** Moved the entire project to `/Users/aathi/AI_lab/aether-seo-dashboard` and restructured the monorepo into two clean, isolated directories: `frontend/` (containing static dashboard page `seo_dashboard.html`) and `backend/` (containing API servers, model logic, agents, and test scripts).
2. **Vercel & Routing Updates:** Updated `vercel.json` and `backend/api/index.py` to seamlessly route static assets and serverless functions relative to their new separated directories.
3. **Google Gemini Integration:** Added official support for the `gemini-2.5-flash` model in `backend/core/model_router.py` using direct async REST calls. It is now the primary reasoning model and won the latency race (6.2s total cold-start inference time).
4. **Serper Scrape API Integration:** Replaced local `Crawl4AI` browser dependencies with high-performance `https://scrape.serper.dev` Cloud API scraper inside `backend/agents/seo_expert_agent.py`. This eliminates Playwright setup overhead, anti-bot blocks, and enables near-instant page parsing.
5. **Exclusive Serper Search:** Restricted the Google Search pipeline in `step_4_competitor_analysis` to exclusively use the Serper API, removing the fallback to SerpApi.
6. **Dynamic API Origin Resolution:** Updated `frontend/seo_dashboard.html` to resolve its endpoint to `window.location.origin + "/api"` dynamically. This prevents CORS loopback mismatches if accessing via `127.0.0.1` vs `localhost`.
7. **Configured Local Env:** Established the `.env` configuration file inside `backend/` containing active credentials for SerpApi, Serper, and your Gemini API Key.

---
*Created by Antigravity AI for Aathisankar's SEO Expansion Project.*



