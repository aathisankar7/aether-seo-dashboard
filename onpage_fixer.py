"""
On-Page SEO Fixer — Reads the Website Audit sheet from the Marketing Master Tracker,
identifies pages with missing meta titles, descriptions, or alt tags,
and uses Local Llama3 to generate the missing elements.

Outputs: onpage_fixes.md
"""

import requests
import openpyxl
import os
from datetime import datetime

class OnPageFixer:
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
    
    def extract_audit_data(self, sheet_name="website Aduit"):
        """Read Website Audit data and identify gaps."""
        wb = openpyxl.load_workbook(self.tracker_path, data_only=True)
        ws = wb[sheet_name]
        
        pages = []
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
            url = str(row[2]).strip() if row[2] else ""
            if not url or not url.startswith("http"):
                continue
            
            page = {
                "type": str(row[1]) if row[1] else "",
                "url": url,
                "existing_title": str(row[3]) if row[3] else "",
                "keyword": str(row[4]) if row[4] else "",
                "existing_description": str(row[5]) if row[5] else "",
                "meta_title": str(row[6]) if row[6] else "",
                "meta_description": str(row[7]) if row[7] else "",
                "suggested_primary_kw": str(row[8]) if row[8] else "",
                "suggested_secondary_kw": str(row[9]) if row[9] else "",
                "alt_tags": str(row[10]) if row[10] else "",
                "h1": str(row[11]) if row[11] else "",
            }
            
            # Identify gaps
            gaps = []
            if not page["meta_title"] or page["meta_title"] == "None":
                gaps.append("Missing Meta Title")
            if not page["meta_description"] or page["meta_description"] == "None":
                gaps.append("Missing Meta Description")
            if page["alt_tags"] in ["NO", "None", ""]:
                gaps.append("Missing Alt Tags")
            if not page["suggested_primary_kw"] or page["suggested_primary_kw"] == "None":
                gaps.append("No Suggested Primary Keyword")
            if not page["suggested_secondary_kw"] or page["suggested_secondary_kw"] == "None":
                gaps.append("No Suggested Secondary Keyword")
            
            page["gaps"] = gaps
            pages.append(page)
        
        print(f"📋 Found {len(pages)} pages in website audit")
        pages_with_gaps = [p for p in pages if p["gaps"]]
        print(f"⚠️  {len(pages_with_gaps)} pages have SEO gaps that need fixing")
        
        return pages
    
    def generate_fixes(self, page):
        """Use Llama3 to generate fixes for a page's SEO gaps."""
        prompt = f"""You are an expert On-Page SEO Specialist for Cosmos Clinics (cosmosclinics.in).

Analyze this page and generate the missing SEO elements:

Page URL: {page['url']}
Page Type: {page['type']}
Current Title: {page['existing_title']}
Current Keyword: {page['keyword']}
Current Description: {page['existing_description']}
Current H1: {page['h1']}
Gaps Found: {', '.join(page['gaps'])}

Generate the following fixes:

1. **Optimized Meta Title** (under 60 characters, include primary keyword)
2. **Optimized Meta Description** (under 160 characters, include keyword and CTA)
3. **Suggested Primary Keyword** (1 main keyword to target)
4. **Suggested Secondary Keywords** (3-5 related keywords)
5. **Alt Tag Suggestions** (for 3-5 key images on this page)
6. **Quick Win Actions** (2-3 immediate changes to improve this page's SEO)

Format in Markdown. Be specific and actionable."""
        
        return self.query_llama(prompt)
    
    def run(self):
        """Main execution flow."""
        print(f"🔧 On-Page SEO Fixer — Powered by Local Llama3")
        print(f"📂 Reading tracker: {self.tracker_path}\n")
        
        pages = self.extract_audit_data()
        
        report_lines = ["# 🔧 On-Page SEO Fix Report\n"]
        report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        report_lines.append("---\n")
        
        # Summary table
        report_lines.append("## Overview\n")
        report_lines.append("| Page | URL | Gaps Found |")
        report_lines.append("|---|---|---|")
        for p in pages:
            gap_str = ", ".join(p["gaps"]) if p["gaps"] else "✅ All Good"
            report_lines.append(f"| {p['type']} | {p['url'][:50]} | {gap_str} |")
        report_lines.append("\n---\n")
        
        # Generate fixes for pages with gaps (capped at top 2)
        pages_with_gaps = [p for p in pages if p["gaps"]][:2]
        
        for i, page in enumerate(pages_with_gaps):
            print(f"\n  [{i+1}/{len(pages_with_gaps)}] Fixing: {page['url']}")
            print(f"     Gaps: {', '.join(page['gaps'])}")
            
            fixes = self.generate_fixes(page)
            
            report_lines.append(f"\n## {page['type']} — {page['url']}\n")
            report_lines.append(f"**Gaps:** {', '.join(page['gaps'])}\n\n")
            report_lines.append(fixes + "\n")
            report_lines.append("\n---\n")
        
        # Also generate suggested keywords for ALL pages (even those without gaps)
        pages_needing_kw = [p for p in pages if "No Suggested Primary Keyword" in p["gaps"]]
        if pages_needing_kw:
            report_lines.append("\n## 📋 Bulk Keyword Suggestions\n")
            for p in pages_needing_kw:
                report_lines.append(f"- **{p['url']}**: Needs primary & secondary keyword suggestions\n")
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = os.path.join(self.output_dir, f"onpage_fixes_{timestamp}.md")
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
        
        print(f"\n{'='*50}")
        print(f"📊 ON-PAGE FIX REPORT COMPLETE")
        print(f"{'='*50}")
        print(f"  Total Pages Audited: {len(pages)}")
        print(f"  Pages with Gaps: {len(pages_with_gaps)}")
        print(f"  Fixes Generated: {len(pages_with_gaps)}")
        print(f"\n✅ Report saved to {report_path}")
        
        return report_path


if __name__ == "__main__":
    tracker = "./cosmos_marketing_tracker.xlsx"
    fixer = OnPageFixer(tracker)
    fixer.run()
