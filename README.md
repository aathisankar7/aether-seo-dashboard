# Aether SEO Engine

AI-powered SEO intelligence dashboard that fully automates website auditing, competitor discovery, keyword engineering, and on-page optimization in real time.

## Demo

🎬 [Watch Demo Video](https://drive.google.com/file/d/1biQmE1q44ev1TKvPlH0wK2SS0uQyYdM2/view?usp=sharing)

## What It Does

- **Strategic Profiling** — AI extracts niche, location, and transactional keywords from any website
- **Keyword Engineering** — Generates revenue drivers, viral clusters, golden-ratio long-tails, and local traces
- **On-Page Optimization** — AI-crafted title tags, meta descriptions, and structural recommendations
- **Competitor Discovery** — Runs 10 parallel Google searches via Serper to surface top competitors automatically
- **Battle Sheets** — Deep competitor analysis with keyword gaps and ninja tactics to outrank them
- **Backlink Targets** — AI-generated directory, guest post, and association link opportunities
- **Schema Engineering** — Organization, LocalBusiness, and Service schema JSON-LD generation
- **Ninja Strategies** — Unorthodox growth tactics tailored to the client niche
- **Real-Time Streaming** — Full intelligence log streamed live to the UI via Server-Sent Events (SSE)

## Architecture

```
Frontend (Vanilla JS + CSS)
        ↓ SSE Stream
FastAPI Backend
        ↓
Race Model Engine
   ├── Gemini 2.5 Flash  (Google AI)
   └── Groq LLaMA 3.3   (fastest wins)
        ↓
Serper API
   ├── Scrape API  (content extraction)
   └── Search API  (competitor discovery)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · Uvicorn |
| AI Models | Gemini 2.5 Flash · Groq LLaMA 3.3-70b |
| Search & Scrape | Serper Search API · Serper Scrape API |
| Streaming | Server-Sent Events (SSE) |
| Frontend | Vanilla HTML · CSS · JavaScript |

## Race Model Engine

Two AI models run simultaneously on every prompt — whichever responds first wins. This delivers the fastest possible response while providing automatic fallback if one model fails.

- **Gemini 2.5 Flash** — Google's fastest reasoning model
- **Groq LLaMA 3.3-70b-versatile** — Ultra-fast inference via Groq's LPU hardware
- **Rate limiting** — Token bucket rate limiter with exponential backoff on 429s
- **Auto-retry** — Up to 4 attempts with backoff on Gemini rate limit errors

## Setup

### Prerequisites
- Python 3.11+
- [Gemini API Key](https://aistudio.google.com/)
- [Groq API Key](https://console.groq.com/)
- [Serper API Key](https://serper.dev/)

### Install

```bash
git clone https://github.com/aathisankar7/aether-seo-dashboard
cd aether-seo-dashboard/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
SERPER_KEY=your_serper_key
```

### Run

```bash
source .venv/bin/activate
python api/index.py
```

Open **http://localhost:8000** in your browser.

## Project Structure

```
aether-seo-dashboard/
├── backend/
│   ├── agents/
│   │   └── seo_expert_agent.py   # Core audit workflow
│   ├── api/
│   │   └── index.py              # FastAPI server + SSE streaming
│   ├── core/
│   │   └── model_router.py       # Race model engine (Gemini + Groq)
│   ├── requirements.txt
│   └── .env
└── frontend/
    └── seo_dashboard.html        # Single-file UI
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/start_audit` | Start a new SEO audit, returns `job_id` |
| `GET` | `/api/stream/{job_id}` | SSE stream of real-time logs and report |

## License

MIT
