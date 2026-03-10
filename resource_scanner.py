from duckduckgo_search import DDGS
import pandas as pd
import time
import os

class ResourceScanner:
    def __init__(self, output_dir="./seo_project/outreach_targets"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def scan_for_resource_pages(self, keyword, location, max_results=50):
        """
        Uses DuckDuckGo (Free) to find "resource" or "links" pages that list businesses 
        in our target industry/location. These are prime targets for automated backlink outreach.
        """
        # Broader Search Operators
        queries = [
            f'inurl:resources {keyword} {location}',
            f'"{keyword}" directory {location}',
            f'top {keyword} {location}',
            f'list of {keyword} in {location}'
        ]
        
        all_results = []
        visited_urls = set()
        
        print(f"🔍 Scanning DuckDuckGo for Resource Pages related to '{keyword}' in '{location}'...")
        
        with DDGS() as ddgs:
            for query in queries:
                print(f"  -> Running query: {query}")
                try:
                    # Search using DuckDuckGo (No API Key needed)
                    results = ddgs.text(query, max_results=20)
                    for r in results:
                        url = r.get('href')
                        if url and url not in visited_urls:
                            visited_urls.add(url)
                            all_results.append({
                                'Target_URL': url,
                                'Page_Title': r.get('title'),
                                'Snippet': r.get('body'),
                                'Search_Query': query,
                                'Keyword': keyword,
                                'Location': location,
                                'Status': 'Pending Outreach'
                            })
                    time.sleep(2) # Be polite to the engine
                except Exception as e:
                    print(f"  ❌ Error on query {query}: {e}")
                    
        # Filter down to absolute best targets
        df = pd.DataFrame(all_results)
        if not df.empty:
            df = df.head(max_results)
            
            filename = f"resource_targets_{keyword.replace(' ', '_')}_{location.replace(' ', '_')}.csv"
            output_path = os.path.join(self.output_dir, filename)
            
            df.to_csv(output_path, index=False)
            print(f"✅ Found {len(df)} High-Value Resource Pages! Saved to {output_path}")
            
            return output_path
        else:
            print("❌ No results found. Try broader keywords.")
            return None

if __name__ == "__main__":
    scanner = ResourceScanner("./seo_project/outreach_targets")
    
    # 1. Target: Dental Clinics Kukatpally
    scanner.scan_for_resource_pages("dental clinic", "Kukatpally", max_results=50)
    
    # 2. Target: Best Dentists Hyderabad
    scanner.scan_for_resource_pages("best dentists", "Hyderabad", max_results=50)
    
    print("\nNext Step: Import these CSVs into n8n and use the email API to send personalized outreach asking for a backlink!")
