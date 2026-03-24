import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

class FreeAPIManager:
    """Manages high-yield free APIs for SEO and Intelligence."""
    
    @staticmethod
    async def hf_inference(model_id: str, inputs: dict or str) -> dict:
        """Call Hugging Face Inference API."""
        if not HF_API_KEY:
            return {"error": "Missing Hugging Face API Key"}
            
        url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": inputs}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        error_text = await resp.text()
                        return {"error": f"HF Error {resp.status}", "details": error_text}
            except Exception as e:
                return {"error": str(e)}

    @staticmethod
    async def analyze_sentiment(text: str):
        """Analyze sentiment using a specialized HF model."""
        # Using a multi-lingual sentiment model
        result = await FreeAPIManager.hf_inference("lxyuan/distilbert-base-multilingual-cased-sentiments-student", text)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result

    @staticmethod
    async def generate_summary(text: str):
        """Generate a concise summary using HF."""
        # Using BART for summarization
        # Limit text to avoid payload issues
        text_chunk = text[:1024]
        result = await FreeAPIManager.hf_inference("facebook/bart-large-cnn", text_chunk)
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("summary_text", "")
        return result

    @staticmethod
    async def google_psi_audit(url: str):
        """Fetch PageSpeed Insights data (No key version)."""
        # PSI has a free tier that doesn't strictly require a key for low volume
        # but one can be added later.
        psi_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=PERFORMANCE&category=SEO"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(psi_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        lighthouse = data.get("lighthouseResult", {})
                        categories = lighthouse.get("categories", {})
                        
                        return {
                            "performance": categories.get("performance", {}).get("score", 0) * 100,
                            "seo": categories.get("seo", {}).get("score", 0) * 100,
                            "first_contentful_paint": lighthouse.get("audits", {}).get("first-contentful-paint", {}).get("displayValue", "N/A"),
                            "speed_index": lighthouse.get("audits", {}).get("speed-index", {}).get("displayValue", "N/A"),
                            "screenshot": lighthouse.get("audits", {}).get("final-screenshot", {}).get("details", {}).get("data", "")
                        }
                    else:
                        return {"error": f"PSI Error {resp.status}"}
            except Exception as e:
                return {"error": str(e)}

    @staticmethod
    async def duckduckgo_instant_answer(query: str):
        """Get instant answers from DuckDuckGo."""
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {"error": "DDG Error"}
            except Exception as e:
                return {"error": str(e)}

    @staticmethod
    async def get_ip_info():
        """Get public IP and location (Free tier)."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://ipapi.co/json/") as resp:
                    return await resp.json()
            except:
                return {"error": "Failed to fetch IP info"}

    @staticmethod
    def get_logo_url(domain: str):
        """Get company logo via Clearbit (Zero-Auth)."""
        return f"https://logo.clearbit.com/{domain}"

    @staticmethod
    def get_qr_code_url(data: str):
        """Generate QR code URL (Zero-Auth)."""
        import urllib.parse
        encoded = urllib.parse.quote(data)
        return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={encoded}"

if __name__ == "__main__":

    # Test
    async def test():
        manager = FreeAPIManager()
        print("Testing Sentiment...")
        print(await manager.analyze_sentiment("This website is amazing and very fast!"))
        
        print("\nTesting PSI (this might take a few seconds)...")
        # print(await manager.google_psi_audit("https://google.com"))
        
    asyncio.run(test())
