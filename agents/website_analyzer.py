import os
import requests
from bs4 import BeautifulSoup
import json

class LocalWebsiteAnalyzer:
    def __init__(self, ollama_endpoint="http://localhost:11434/api/generate", model="llama3"):
        self.endpoint = ollama_endpoint
        self.model = model

    def query_llama(self, prompt, system_prompt="You are an expert SEO Strategist."):
        """Helper to contact the local Ollama instance."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2 # Keep it analytical
            }
        }
        try:
            response = requests.post(self.endpoint, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json().get("response", "No response from model.")
            else:
                return f"❌ Error: Local Llama returned status code {response.status_code}: {response.text}"
        except requests.exceptions.ConnectionError:
            return f"❌ Error: Could not connect to Ollama at {self.endpoint}. Is the server running?"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def fetch_website_content(self, url):
        """Fetches the HTML of the website and extracts visible text."""
        print(f"🌐 Fetching content from {url}...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.extract()
                
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            print(f"✅ Successfully extracted {len(clean_text)} characters of text.")
            return clean_text
            
        except Exception as e:
            print(f"❌ Failed to fetch website: {e}")
            return None

    def analyze_content(self, url, content_text):
        """Uses Local Llama to analyze the website text."""
        # Truncate content so it fits in Llama3's context window (usually 8k tokens, ~30k chars is safe)
        truncated_content = content_text[:20000] 
        
        print(f"🦙 Asking local {self.model} to analyze the website data... (This might take a moment)")
        
        prompt = f"""
        Act as an elite SEO Strategist. I have scraped the homepage of {url}.
        
        Here is the raw text extracted from the page:
        ---
        {truncated_content}
        ---
        
        Based on this content, tell me "what is needed" to improve this site's SEO and structure.
        Provide the following details in professional Markdown:
        1. **Core Value Proposition**: What is the site explicitly about based on the text?
        2. **Missing Content**: What crucial information is missing?
        3. **Keyword Opportunities**: What 3-5 primary keywords should this page target?
        4. **Immediate Action Items**: 3 concrete steps to improve on-page content.
        """
        
        result_text = self.query_llama(prompt)
        
        print("\n==================================================")
        print(f"📊 LOCAL LLAMA ANALYSIS FOR {url}")
        print("==================================================\n")
        print(result_text)
        
        if not result_text.startswith("❌"):
            os.makedirs("./reports", exist_ok=True)
            report_path = "./reports/website_analysis_llama.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(result_text)
            print(f"\n✅ Analysis saved to {report_path}")

if __name__ == "__main__":
    analyzer = LocalWebsiteAnalyzer()
    target_url = "https://cosmosclinics.in/"
    
    extracted_text = analyzer.fetch_website_content(target_url)
    
    if extracted_text:
        analyzer.analyze_content(target_url, extracted_text)
