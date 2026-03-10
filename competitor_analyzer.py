"""
Competitor Analyzer — Reads competitor URLs from the Marketing Master Tracker,
scrapes their pages, and uses Local Llama3 to analyze their SEO strategy.

Outputs: competitor_analysis_report.md
"""

import requests
from bs4 import BeautifulSoup
import openpyxl
import os
from datetime import datetime

class CompetitorAnalyzer:
    def __init__(self, tracker_path, output_dir="./reports",
                 ollama_endpoint="http://localhost:11434/api/generate",
                 model="llama3"):
        self.tracker_path = tracker_path
        self.output_dir = output_dir
        self.ollama_endpoint = ollama_endpoint
        self.model = model
        os.makedirs(output_dir, exist_ok=True)
    
    def query_llama(self, prompt):
        """Send a prompt to the local Llama3 instance."""
        try:
            response = requests.post(self.ollama_endpoint, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }, timeout=120)
            return response.json().get("response", "Error: No response")
        except Exception as e:
            return f"Error: {e}"
    
    def extract_competitors(self, sheet_name="Competitor Keywords", max_urls=20):
        """Read unique competitor URLs from the tracker."""
        wb = openpyxl.load_workbook(self.tracker_path, data_only=True)
        ws = wb[sheet_name]
        
        urls = set()
        keywords = {}
        
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
            keyword = str(row[0]).strip() if row[0] else ""
            hyd_url = str(row[1]).strip() if row[1] else ""
            india_url = str(row[2]).strip() if row[2] else ""
            
            for url in [hyd_url, india_url]:
                if url and url.startswith("http") and url not in urls:
                    urls.add(url)
                    if keyword:
                        keywords[url] = keyword
        
        # Take top N
        competitor_list = []
        for url in list(urls)[:max_urls]:
            competitor_list.append({
                "url": url,
                "keyword": keywords.get(url, "General")
            })
        
        print(f"📋 Found {len(urls)} unique competitor URLs, analyzing top {len(competitor_list)}")
        return competitor_list
    
    def scrape_page(self, url):
        """Scrape text content from a competitor page."""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "lxml")
            
            # Extract key SEO elements
            title = soup.title.string if soup.title else "No title"
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")
            
            # Get H1, H2s
            h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
            h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
            
            # Get body text (truncated)
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)[:2000]
            
            return {
                "title": title,
                "meta_description": meta_desc,
                "h1": h1s,
                "h2": h2s[:5],
                "text": text
            }
        except Exception as e:
            return {"title": "Error", "meta_description": "", "h1": [], "h2": [], "text": str(e)}
    
    def analyze_competitor(self, url, scraped, keyword):
        """Use Llama3 to analyze a competitor page."""
        prompt = f"""You are an SEO Competitive Analyst for Cosmos Clinics (cosmosclinics.in), a premium dental clinic in Kukatpally, Hyderabad.

Analyze this competitor page and provide insights:

URL: {url}
Competing Keyword: {keyword}
Page Title: {scraped['title']}
Meta Description: {scraped['meta_description']}
H1 Tags: {scraped['h1']}
H2 Tags: {scraped['h2']}
Page Content (excerpt): {scraped['text'][:1500]}

Provide:
1. **Their Value Proposition** (1-2 sentences)
2. **Keywords They Target** (list 3-5)
3. **Their Strengths** vs Cosmos Clinics (2-3 points)
4. **Their Weaknesses** we can exploit (2-3 points)
5. **Action Items** for Cosmos Clinics to outrank them (2-3 specific steps)

Be concise and actionable. Format in Markdown."""
        
        return self.query_llama(prompt)
    
    def run(self, max_urls=20):
        """Main execution flow."""
        print(f"🔍 Competitor Analyzer — Powered by Local Llama3")
        print(f"📂 Reading tracker: {self.tracker_path}\n")
        
        competitors = self.extract_competitors(max_urls=max_urls)
        
        report_lines = ["# 🏆 Competitor Analysis Report\n"]
        report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        report_lines.append(f"*Competitors Analyzed: {len(competitors)}*\n")
        report_lines.append("---\n")
        
        for i, comp in enumerate(competitors):
            url = comp["url"]
            keyword = comp["keyword"]
            
            print(f"\n  [{i+1}/{len(competitors)}] Scraping: {url}...")
            scraped = self.scrape_page(url)
            
            if scraped["title"] == "Error":
                print(f"  ❌ Failed to scrape, skipping.")
                continue
            
            print(f"  🦙 Analyzing with Llama3...")
            analysis = self.analyze_competitor(url, scraped, keyword)
            
            report_lines.append(f"\n## {i+1}. [{url}]({url})\n")
            report_lines.append(f"**Competing Keyword:** {keyword}\n")
            report_lines.append(f"**Page Title:** {scraped['title']}\n\n")
            report_lines.append(analysis + "\n")
            report_lines.append("\n---\n")
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = os.path.join(self.output_dir, f"competitor_analysis_{timestamp}.md")
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
        
        print(f"\n✅ Competitor analysis report saved to {report_path}")
        return report_path


if __name__ == "__main__":
    tracker = "./cosmos_marketing_tracker.xlsx"
    analyzer = CompetitorAnalyzer(tracker)
    analyzer.run(max_urls=2)  # Start with top 2
