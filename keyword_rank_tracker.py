"""
Keyword Rank Tracker — Reads trending keywords from the Marketing Master Tracker
and checks where ritzgroup.co ranks for each using DuckDuckGo.

Outputs: keyword_rankings.csv
"""

from duckduckgo_search import DDGS
import pandas as pd
import openpyxl
import os
import time
from datetime import datetime

class KeywordRankTracker:
    def __init__(self, tracker_path, target_domain="cosmosclinics.in", output_dir="./reports"):
        self.tracker_path = tracker_path
        self.target_domain = target_domain
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_keywords(self, sheet_name="Trending Keywords", max_keywords=50):
        """Read keywords from the Trending Keywords sheet."""
        wb = openpyxl.load_workbook(self.tracker_path, data_only=True)
        ws = wb[sheet_name]
        
        keywords = []
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
            keyword = str(row[1]).strip() if row[1] else ""
            volume = str(row[2]).strip() if row[2] else "0"
            difficulty = str(row[3]).strip() if row[3] else "0"
            
            if keyword and keyword != "None":
                keywords.append({
                    "Keyword": keyword,
                    "Search_Volume": volume,
                    "SEO_Difficulty": difficulty
                })
        
        # Sort by search volume descending, take top N
        try:
            keywords.sort(key=lambda x: int(x["Search_Volume"]), reverse=True)
        except ValueError:
            pass
        
        keywords = keywords[:max_keywords]
        print(f"📋 Loaded {len(keywords)} keywords (top {max_keywords} by search volume)")
        return keywords
    
    def check_ranking(self, keyword, max_results=50):
        """Search DuckDuckGo for a keyword and find where target_domain ranks."""
        try:
            with DDGS() as ddgs:
                results = ddgs.text(keyword, max_results=max_results)
                
                for i, result in enumerate(results):
                    url = result.get("href", "")
                    if self.target_domain in url:
                        return {
                            "Rank": i + 1,
                            "URL_Found": url,
                            "Title": result.get("title", "")
                        }
                
                return {"Rank": f">50", "URL_Found": "Not found", "Title": ""}
        except Exception as e:
            return {"Rank": "Error", "URL_Found": str(e), "Title": ""}
    
    def run(self, max_keywords=50):
        """Main execution flow."""
        print(f"🔍 Keyword Rank Tracker for {self.target_domain}")
        print(f"📂 Reading tracker: {self.tracker_path}\n")
        
        keywords = self.extract_keywords(max_keywords=max_keywords)
        
        results = []
        for i, kw in enumerate(keywords):
            keyword = kw["Keyword"]
            print(f"  [{i+1}/{len(keywords)}] Checking: {keyword}...", end=" ")
            
            ranking = self.check_ranking(keyword)
            kw.update(ranking)
            results.append(kw)
            
            print(f"Rank: {ranking['Rank']}")
            time.sleep(3)  # Polite delay
        
        # Save report
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = os.path.join(self.output_dir, f"keyword_rankings_{timestamp}.csv")
        df.to_csv(report_path, index=False)
        
        # Stats
        ranked = df[df["Rank"].apply(lambda x: str(x).isdigit())]
        print(f"\n{'='*50}")
        print(f"📊 KEYWORD RANKING REPORT")
        print(f"{'='*50}")
        print(f"  Total Keywords Checked: {len(df)}")
        print(f"  ✅ Ranking in Top 50: {len(ranked)}")
        print(f"  ❌ Not Found: {len(df) - len(ranked)}")
        if len(ranked) > 0:
            print(f"\n  🏆 Top Ranked Keywords:")
            top = ranked.sort_values("Rank", key=lambda x: pd.to_numeric(x))
            for _, row in top.head(5).iterrows():
                print(f"     #{row['Rank']} — \"{row['Keyword']}\" (Vol: {row['Search_Volume']})")
        
        print(f"\n✅ Report saved to {report_path}")
        return report_path


if __name__ == "__main__":
    tracker = "./cosmos_marketing_tracker.xlsx"
    ranker = KeywordRankTracker(tracker)
    ranker.run(max_keywords=4)  # Start with top 4
