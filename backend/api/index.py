from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import sys
import os
import asyncio
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.seo_expert_agent import SEOExpertAgent

app = FastAPI(title="SEO Expert AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_jobs = {}

@app.get("/")
async def serve_dashboard():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "seo_dashboard.html"))
    return FileResponse(html_path)

class AuditRequest(BaseModel):
    url: str

@app.get("/api/docs")
async def get_system_docs():
    return {
        "engine_logic": "Google Gemini 2.5 Flash reasoning model with Serper Search & Scrape REST Core",
        "fair_usage": "Free-tier API utilization. Please limit audits to 5 per hour per user.",
        "privacy_policy": "All search data is stored locally and processed securely via encrypted AI channels."
    }

async def log_generator(job_id):
    queue = active_jobs[job_id]["queue"]
    while True:
        msg = await queue.get()
        if msg == "__DONE__":
            if active_jobs[job_id].get("report"):
                yield {
                    "event": "report",
                    "data": json.dumps(active_jobs[job_id]["report"])
                }
            yield {"event": "done", "data": "Analysis complete"}
            break
        if msg.startswith("__ERROR__:"):
            yield {"event": "error", "data": msg.replace("__ERROR__:", "")}
            break
        if msg.startswith("__REVIEW__:"):
            yield {"event": "review_competitors", "data": msg.replace("__REVIEW__:", "")}
            continue
        yield {"event": "log", "data": msg}
        await asyncio.sleep(0.01)

async def run_agent_async(job_id, url):
    agent = SEOExpertAgent()
    queue = active_jobs[job_id]["queue"]

    def on_log(msg):
        queue.put_nowait(msg)

    agent.on_log(on_log)
    try:
        report = await agent.full_audit(url, job_context=active_jobs[job_id])
        active_jobs[job_id]["report"] = report
        await queue.put("__DONE__")
    except Exception as e:
        await queue.put(f"__ERROR__:{str(e)}")

@app.post("/api/start_audit")
async def start_audit(req: AuditRequest, background_tasks: BackgroundTasks):
    job_id = f"job_{id(req)}_{asyncio.get_event_loop().time()}"
    active_jobs[job_id] = {
        "url": req.url,
        "queue": asyncio.Queue(),
        "report": None,
        "review_event": asyncio.Event(),
        "approved_competitors": []
    }
    background_tasks.add_task(run_agent_async, job_id, req.url)
    return {"job_id": job_id, "status": "started"}

class ApproveCompetitorsRequest(BaseModel):
    competitors: list[str]

@app.post("/api/approve_competitors/{job_id}")
async def approve_competitors(job_id: str, req: ApproveCompetitorsRequest):
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    active_jobs[job_id]["approved_competitors"] = req.competitors
    active_jobs[job_id]["review_event"].set()
    return {"status": "resumed"}

@app.get("/api/stream/{job_id}")
async def stream_logs(job_id: str, request: Request):
    if job_id not in active_jobs:
        return {"error": "Invalid Job ID"}
    return EventSourceResponse(log_generator(job_id))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
