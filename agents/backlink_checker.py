"""
Backlink Health Checker — Reads all backlink URLs from the Marketing Master Tracker
and verifies which are still live via async HTTP HEAD requests.

Outputs: backlink_health_report.csv
"""

import asyncio
import aiohttp
import pandas as pd
import openpyxl
import os
import time
from datetime import datetime

class BacklinkChecker:
    def __init__(self, tracker_path, output_dir="./reports"):
        self.tracker_path = tracker_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Sheets that contain backlink data and their URL column index
        self.backlink_sheets = {
            "web 2.0 backlinks": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Directorites Submissions": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Classifieds Submissions": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Artical Submissions": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Pdf Submissions": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Image Submissions": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Profile Creations": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Social Bookmarks": {"url_col": 4, "da_col": 1, "pa_col": 2},
            "Business listing": {"url_col": 3, "da_col": None, "pa_col": None},
        }
    
    def extract_backlinks(self):
        """Read all backlink URLs from the tracker Excel file."""
        wb = openpyxl.load_workbook(self.tracker_path, data_only=True)
        all_links = []
        
        for sheet_name, config in self.backlink_sheets.items():
            if sheet_name not in wb.sheetnames:
                print(f"  ⚠️  Sheet '{sheet_name}' not found, skipping.")
                continue
            
            ws = wb[sheet_name]
            url_col = config["url_col"]
            da_col = config["da_col"]
            pa_col = config["pa_col"]
            
            count = 0
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=False):
                url_cell = row[url_col] if url_col < len(row) else None
                url = str(url_cell.value).strip() if url_cell and url_cell.value else ""
                
                # Skip empty, date-like, or non-URL entries
                if not url or not url.startswith("http"):
                    continue
                
                da = str(row[da_col].value) if da_col and da_col < len(row) and row[da_col].value else ""
                pa = str(row[pa_col].value) if pa_col and pa_col < len(row) and row[pa_col].value else ""
                
                all_links.append({
                    "Source_Sheet": sheet_name,
                    "Submitted_URL": url,
                    "DA": da,
                    "PA": pa,
                })
                count += 1
            
            print(f"  📑 {sheet_name}: extracted {count} URLs")
        
        print(f"\n📊 Total backlinks extracted: {len(all_links)}")
        return all_links
    
    async def check_url(self, session, url, timeout=10):
        """Check if a single URL is still live."""
        try:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=timeout), 
                                     allow_redirects=True, ssl=False) as response:
                return response.status
        except aiohttp.ClientError:
            try:
                # Fallback to GET if HEAD fails
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout),
                                       allow_redirects=True, ssl=False) as response:
                    return response.status
            except Exception:
                return 0
        except Exception:
            return 0
    
    async def check_all(self, links, concurrency=20):
        """Check all URLs concurrently with a semaphore limit."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_check(session, link):
            async with semaphore:
                status = await self.check_url(session, link["Submitted_URL"])
                link["HTTP_Status"] = status
                link["Is_Live"] = "✅ Yes" if 200 <= status < 400 else "❌ No"
                return link
        
        connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
        async with aiohttp.ClientSession(connector=connector, 
                                          headers={"User-Agent": "Mozilla/5.0 RitzSEOBot/1.0"}) as session:
            tasks = [bounded_check(session, link) for link in links]
            total = len(tasks)
            results = []
            
            # Process in batches for progress reporting
            batch_size = 50
            for i in range(0, total, batch_size):
                batch = tasks[i:i+batch_size]
                batch_results = await asyncio.gather(*batch)
                results.extend(batch_results)
                print(f"  🔍 Checked {min(i+batch_size, total)}/{total} URLs...")
            
            return results
    
    def generate_report(self, results):
        """Save the results to a CSV report."""
        df = pd.DataFrame(results)
        
        # Stats
        total = len(df)
        live = len(df[df["Is_Live"] == "✅ Yes"])
        dead = total - live
        
        print(f"\n{'='*50}")
        print(f"📊 BACKLINK HEALTH REPORT")
        print(f"{'='*50}")
        print(f"  Total Backlinks Checked: {total}")
        print(f"  ✅ Live: {live} ({live/total*100:.1f}%)")
        print(f"  ❌ Dead/Broken: {dead} ({dead/total*100:.1f}%)")
        
        # Save full report
        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = os.path.join(self.output_dir, f"backlink_health_report_{timestamp}.csv")
        df.to_csv(report_path, index=False)
        print(f"\n✅ Full report saved to {report_path}")
        
        # Save dead links separately for action
        if dead > 0:
            dead_df = df[df["Is_Live"] == "❌ No"]
            dead_path = os.path.join(self.output_dir, f"dead_backlinks_{timestamp}.csv")
            dead_df.to_csv(dead_path, index=False)
            print(f"⚠️  Dead links report saved to {dead_path}")
        
        return report_path
    
    def run(self):
        """Main execution flow."""
        print("🔗 Backlink Health Checker — Starting...")
        print(f"📂 Reading tracker: {self.tracker_path}\n")
        
        # Step 1: Extract all backlink URLs
        links = self.extract_backlinks()
        
        if not links:
            print("❌ No backlinks found in tracker.")
            return
        
        # Step 2: Check all URLs
        print(f"\n🌐 Checking {len(links)} URLs (this may take a minute)...\n")
        results = asyncio.run(self.check_all(links))
        
        # Step 3: Generate report
        self.generate_report(results)


if __name__ == "__main__":
    tracker = "./marketing_master_tracker.xlsx"
    checker = BacklinkChecker(tracker)
    checker.run()
