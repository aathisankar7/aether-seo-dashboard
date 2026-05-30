import asyncio
import aiohttp
import time
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TIMEOUT = aiohttp.ClientTimeout(total=60)

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

gemini_limiter = RateLimiter(30)

async def query_gemini(session: aiohttp.ClientSession, prompt: str) -> dict:
    if not GEMINI_API_KEY:
        return {"provider": "Gemini", "error": "No Key"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096}
    }
    headers = {"Content-Type": "application/json"}

    for attempt in range(4):
        await gemini_limiter.wait()
        start = time.monotonic()
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                elapsed = time.monotonic() - start
                if resp.status == 200:
                    data = await resp.json()
                    try:
                        response_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "provider": "Gemini",
                            "model": "gemini-2.5-flash",
                            "response": response_text,
                            "elapsed": elapsed
                        }
                    except KeyError:
                        return {"provider": "Gemini", "error": "Invalid API response structure", "details": data, "elapsed": elapsed}
                elif resp.status == 429:
                    wait = (2 ** attempt) * 5
                    await asyncio.sleep(wait)
                    continue
                else:
                    error_text = await resp.text()
                    return {"provider": "Gemini", "error": f"HTTP Error {resp.status}", "details": error_text, "elapsed": elapsed}
        except Exception as e:
            if attempt < 3:
                await asyncio.sleep(2 ** attempt)
                continue
            return {"provider": "Gemini", "error": str(e), "elapsed": time.monotonic() - start}

    return {"provider": "Gemini", "error": "Max retries exceeded (rate limited)"}

async def query_groq(session: aiohttp.ClientSession, prompt: str) -> dict:
    if not GROQ_API_KEY:
        return {"provider": "Groq", "error": "No Key"}

    start = time.monotonic()
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with session.post(url, json=payload, headers=headers) as resp:
            elapsed = time.monotonic() - start
            if resp.status == 200:
                data = await resp.json()
                try:
                    response_text = data["choices"][0]["message"]["content"]
                    return {
                        "provider": "Groq",
                        "model": "llama-3.3-70b-versatile",
                        "response": response_text,
                        "elapsed": elapsed
                    }
                except KeyError:
                    return {"provider": "Groq", "error": "Invalid response", "details": data, "elapsed": elapsed}
            else:
                return {"provider": "Groq", "error": f"HTTP {resp.status}", "details": await resp.text(), "elapsed": elapsed}
    except Exception as e:
        return {"provider": "Groq", "error": str(e), "elapsed": time.monotonic() - start}

async def race_models(prompt: str) -> dict:
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        tasks = [
            asyncio.create_task(query_groq(session, prompt)),
            asyncio.create_task(query_gemini(session, prompt))
        ]
        errors = []
        for coro in asyncio.as_completed(tasks):
            result = await coro
            if "response" in result:
                for t in tasks:
                    if not t.done():
                        t.cancel()
                return result
            else:
                errors.append(result)
        return errors[-1] if errors else {"error": "All models failed"}
