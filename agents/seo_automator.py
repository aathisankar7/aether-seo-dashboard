"""
Local SEO Automator (Elite Upgrade) — Technical Audit Summarization via AI Race.
Uses Lighthouse for raw data and our distributed AI arsenal for expert interpretation.
"""

import os
import json
import subprocess
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Import our advanced model router
from model_router import race_models

load_dotenv()

class LocalSEOAutomator:
    def __init__(self, target_urls):
        if isinstance(target_urls, str):
            self.target_urls = [target_urls]
        else:
            self.target_urls = target_urls
            
        self.reports_dir = "./reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    async def query_ai(self, prompt):
        """Helper to use the AI Race for technical interpretation."""
        result = await race_models(prompt)
        return result.get("response", f"Error interpreting data: {result.get('error')}")

    def run_lighthouse(self, url):
        """Runs a technical SEO audit using Lighthouse."""
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        report_path = os.path.join(self.reports_dir, f"seo_report_{filename}_{datetime.now().strftime('%Y%m%d')}.json")
        
        print(f"🚀 Running Lighthouse for {url}...")
        try:
            cmd = [
                "npx", "lighthouse", url, 
                "--output", "json", 
                "--output-path", report_path, 
                "--chrome-flags='--headless --no-sandbox'"
            ]
            subprocess.run(cmd, check=True)
            return report_path
        except Exception as e:
            print(f"❌ Lighthouse failed: {e}")
            return None

    async def get_ai_summary(self, report_path):
        """Interprets the report using the fastest available AI."""
        if not report_path or not os.path.exists(report_path):
            return "No report found."

        try:
            with open(report_path, 'r') as f:
                data = json.load(f)

            perf = data['categories']['performance']['score'] * 100
            seo = data['categories']['seo']['score'] * 100
            
            opps = []
            for audit in data['audits'].values():
                if audit.get('details', {}).get('type') == 'opportunity' and audit.get('score', 1) < 0.9:
                    opps.append(f"- {audit['title']}: {audit['description']}")
            
            prompt = f"""Act as a Senior SEO Engineer. Interpret these Lighthouse results:
            - Performance: {perf}
            - SEO: {seo}
            - Opportunities:
            {chr(10).join(opps[:5])}
            
            Provide:
            1. Executive Health Summary.
            2. Top 3 Technical Fixes.
            3. Developer Implemention Checklist.
            """
            return await self.query_ai(prompt)
        except Exception as e:
            return f"Error: {e}"

    async def run_all(self):
        """Execute audits and summaries in sequence."""
        results = {}
        for url in self.target_urls:
            report_path = self.run_lighthouse(url)
            if report_path:
                summary = await self.get_ai_summary(report_path)
                results[url] = summary
        return results

if __name__ == "__main__":
    targets = ["https://cosmosclinics.in/"]
    automator = LocalSEOAutomator(targets)
    asyncio.run(automator.run_all())
