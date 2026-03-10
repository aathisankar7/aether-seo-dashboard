import asyncio
import aiohttp
import time
import os
import json
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY") # Routeway Key
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

TIMEOUT = aiohttp.ClientTimeout(total=45)

class RateLimiter:
    def __init__(self, rpm):
        self.rpm = rpm
        self.tokens = rpm
        self.last_update = time.monotonic()

    async def wait(self):
        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(self.rpm, self.tokens + elapsed * (self.rpm / 60.0))
        self.last_update = now
        
        if self.tokens < 1:
            wait_time = (1 - self.tokens) * (60.0 / self.rpm)
            await asyncio.sleep(wait_time)
            self.tokens = 0
        else:
            self.tokens -= 1

# Rate Limiters
groq_limiter = RateLimiter(30)
sambanova_limiter = RateLimiter(30)
cerebras_limiter = RateLimiter(30)
routeway_limiter = RateLimiter(20)
moonshot_limiter = RateLimiter(10)

async def query_groq(session: aiohttp.ClientSession, prompt: str) -> dict:
    if not GROQ_API_KEY: return {"provider": "Groq", "error": "No Key"}
    await groq_limiter.wait()
    start = time.monotonic()
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            elapsed = time.monotonic() - start
            if resp.status == 200:
                return {"provider": "Groq", "model": "llama-3.3-70b", "response": data["choices"][0]["message"]["content"], "elapsed": elapsed}
            return {"provider": "Groq", "error": data.get("error", "Unknown error"), "elapsed": elapsed}
    except Exception as e:
        return {"provider": "Groq", "error": str(e), "elapsed": time.monotonic() - start}

async def query_cerebras(session: aiohttp.ClientSession, prompt: str) -> dict:
    if not CEREBRAS_API_KEY: return {"provider": "Cerebras", "error": "No Key"}
    await cerebras_limiter.wait()
    start = time.monotonic()
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {CEREBRAS_API_KEY}"}
    payload = {
        "model": "llama3.1-8b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            elapsed = time.monotonic() - start
            if resp.status == 200:
                return {"provider": "Cerebras", "model": "llama3.1-8b", "response": data["choices"][0]["message"]["content"], "elapsed": elapsed}
            return {"provider": "Cerebras", "error": data.get("error", "Unknown error"), "elapsed": elapsed}
    except Exception as e:
        return {"provider": "Cerebras", "error": str(e), "elapsed": time.monotonic() - start}

async def query_sambanova(session: aiohttp.ClientSession, prompt: str) -> dict:
    if not SAMBANOVA_API_KEY: return {"provider": "SambaNova", "error": "No Key"}
    await sambanova_limiter.wait()
    start = time.monotonic()
    url = "https://api.sambanova.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {SAMBANOVA_API_KEY}"}
    payload = {
        "model": "Meta-Llama-3.3-70B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            elapsed = time.monotonic() - start
            if resp.status == 200:
                return {"provider": "SambaNova", "model": "Llama-3.3-70B", "response": data["choices"][0]["message"]["content"], "elapsed": elapsed}
            return {"provider": "SambaNova", "error": data.get("error", "Unknown error"), "elapsed": elapsed}
    except Exception as e:
        return {"provider": "SambaNova", "error": str(e), "elapsed": time.monotonic() - start}

async def query_routeway(session: aiohttp.ClientSession, prompt: str) -> dict:
    if not ZHIPU_API_KEY: return {"provider": "Routeway", "error": "No Key"}
    await routeway_limiter.wait()
    start = time.monotonic()
    url = "https://api.routeway.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {ZHIPU_API_KEY}"}
    payload = {
        "model": "glm-4.5-air:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            elapsed = time.monotonic() - start
            if resp.status == 200:
                return {"provider": "Routeway", "model": "glm-4.5-air:free", "response": data["choices"][0]["message"]["content"], "elapsed": elapsed}
            return {"provider": "Routeway", "error": data.get("error", "Unknown error"), "elapsed": elapsed}
    except Exception as e:
        return {"provider": "Routeway", "error": str(e), "elapsed": time.monotonic() - start}

async def query_ollama(session: aiohttp.ClientSession, prompt: str) -> dict:
    start = time.monotonic()
    url = f"{OLLAMA_URL}/api/generate"
    payload = {"model": "qwen2.5:7b", "prompt": prompt, "stream": False}
    try:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            elapsed = time.monotonic() - start
            return {"provider": "Ollama", "model": "Qwen 2.5 (Local)", "response": data.get("response", ""), "elapsed": elapsed}
    except Exception as e:
        return {"provider": "Ollama", "error": str(e), "elapsed": time.monotonic() - start}

async def query_moonshot(session: aiohttp.ClientSession, prompt: str) -> dict:
    if not MOONSHOT_API_KEY: return {"provider": "Moonshot", "error": "No Key"}
    await moonshot_limiter.wait()
    start = time.monotonic()
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MOONSHOT_API_KEY}"}
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            elapsed = time.monotonic() - start
            if resp.status == 200:
                return {"provider": "Moonshot", "model": "moonshot-v1", "response": data["choices"][0]["message"]["content"], "elapsed": elapsed}
            return {"provider": "Moonshot", "error": data.get("error", "Unknown error"), "elapsed": elapsed}
    except Exception as e:
        return {"provider": "Moonshot", "error": str(e), "elapsed": time.monotonic() - start}

async def race_models(prompt: str):
    """Run all AI providers in parallel and return the fastest successful result."""
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        tasks = [
            asyncio.create_task(query_groq(session, prompt)),
            asyncio.create_task(query_cerebras(session, prompt)),
            asyncio.create_task(query_sambanova(session, prompt)),
            asyncio.create_task(query_routeway(session, prompt)),
            asyncio.create_task(query_moonshot(session, prompt)),
            asyncio.create_task(query_ollama(session, prompt)),
        ]
        
        finished_results = []
        for future in asyncio.as_completed(tasks):
            res = await future
            if "response" in res:
                # Cancel pending
                for task in tasks:
                    if not task.done(): task.cancel()
                return res
            finished_results.append(res)
            
        # If all failed
        return {"error": "All models failed", "details": finished_results}
