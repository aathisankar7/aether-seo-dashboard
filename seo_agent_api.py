"""
SEO Expert API — FastAPI server that runs the SEO Expert Agent
and streams real-time logs to the frontend dashboard using Server-Sent Events (SSE).
"""

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import asyncio
import json
from seo_expert_agent import SEOExpertAgent
import auth_manager
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

app = FastAPI(title="SEO Expert AI Agent API")

# Allow CORS for the frontend UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), request: Request = None):
    # Fallback to query param for SSE (EventSource doesn't support headers)
    if not token and request:
        token = request.query_params.get("token")
        
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    username = auth_manager.verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username

# In-memory store for agent streams and results
active_jobs = {}

@app.get("/")
async def serve_dashboard():
    """Serve the static SEO dashboard HTML."""
    return FileResponse("seo_dashboard.html")

class AuditRequest(BaseModel):
    url: str

class UserAuth(BaseModel):
    username: str
    email: str
    password: str

@app.post("/api/auth/register")
async def register(user: UserAuth):
    success = auth_manager.create_user(user.username, user.email, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"message": "User registered successfully"}

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_manager.get_user(form_data.username)
    if not user or not auth_manager.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth_manager.create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=timedelta(minutes=auth_manager.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user["username"]}

@app.get("/api/docs")
async def get_system_docs():
    """Return system transparency and fair usage documentation."""
    return {
        "engine_logic": "Multi-Model Neural Fleet (Groq, Cerebras, SambaNova, Routeway, Moonshot, Local Qwen)",
        "fair_usage": "Free-tier API utilization. Please limit audits to 5 per hour per user.",
        "privacy_policy": "All search data is stored locally and processed securely via encrypted AI channels."
    }

async def log_generator(job_id):
    """Generator for Server-Sent Events (SSE) stream."""
    queue = active_jobs[job_id]["queue"]
    
    while True:
        # Wait for log messages
        msg = await queue.get()
        
        # Check for termination signal
        if msg == "__DONE__":
            if active_jobs[job_id].get("report"):
                # Send the final JSON payload
                yield {
                    "event": "report",
                    "data": json.dumps(active_jobs[job_id]["report"])
                }
            yield {"event": "done", "data": "Analysis complete"}
            break
            
        if msg.startswith("__ERROR__:"):
            yield {"event": "error", "data": msg.replace("__ERROR__:", "")}
            break
            
        # Send streaming log
        yield {"event": "log", "data": msg}
        await asyncio.sleep(0.01)

async def run_agent_async(job_id, url):
    """Run the AI agent asynchronously and push logs to the queue."""
    agent = SEOExpertAgent()
    queue = active_jobs[job_id]["queue"]
    
    def on_log(msg):
        # Already in the main loop, can queue directly
        queue.put_nowait(msg)
        
    agent.on_log(on_log)
    
    try:
        report = await agent.full_audit(url)
        active_jobs[job_id]["report"] = report
        await queue.put("__DONE__")
    except Exception as e:
        await queue.put(f"__ERROR__:{str(e)}")

@app.post("/api/start_audit")
async def start_audit(req: AuditRequest, background_tasks: BackgroundTasks, current_user: str = Depends(get_current_user)):
    """Start the AI SEO process in the background and return a Job ID."""
    job_id = f"job_{id(req)}_{asyncio.get_event_loop().time()}"
    
    active_jobs[job_id] = {
        "url": req.url,
        "queue": asyncio.Queue(),
        "loop": asyncio.get_event_loop(),
        "report": None
    }
    
    # Run the async agent in the background
    background_tasks.add_task(run_agent_async, job_id, req.url)
    
    return {"job_id": job_id, "status": "started"}

@app.get("/api/stream/{job_id}")
async def stream_logs(job_id: str, request: Request, current_user: str = Depends(get_current_user)):
    """Stream real-time log updates for a given Job ID via SSE."""
    if job_id not in active_jobs:
        return {"error": "Invalid Job ID"}
        
    return EventSourceResponse(log_generator(job_id))

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
