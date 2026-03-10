"""
SEO Expert Agent — The core orchestration engine for the AI SEO Dashboard (Elite Upgrade).
High-Fidelity Scraping via Crawlee & Multi-Model AI Intelligence (Groq, Cerebras, SambaNova, Routeway).
"""

import json
import os
import asyncio
import time
import re
from datetime import datetime, timedelta
import pandas as pd
import aiohttp
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from googlesearch import search # Crucial and Verified
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Import from our advanced model router
from model_router import race_models

class SEOExpertAgent:
    def __init__(self):
        self.log_callbacks = []
        self.reports_dir = "./reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def on_log(self, callback):
        """Register a callback for real-time logging (used by SSE)."""
        self.log_callbacks.append(callback)
    
    def log(self, message):
        """Send a log message to all registered callbacks."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        print(formatted_msg)
        for cb in self.log_callbacks:
            try:
                cb(formatted_msg)
            except:
                pass

    async def query_ai(self, prompt, context_name="Task"):
        """Execute a parallel AI race and log the winner."""
        self.log(f"🧠 Racing models for: {context_name}...")
        result = await race_models(prompt)
        if "response" in result:
            model_name = result.get('model', result['provider'])
            self.log(f"🏆 Winner: {result['provider']} ({result.get('elapsed', 0):.1f}s)")
            self.log(f"__MODEL__:{model_name}")
            return result["response"]
        else:
            self.log(f"❌ AI Race Failed: {result.get('error')}")
            return ""

    async def scrape_text(self, url, crawler=None):
        """Ultra High-Fidelity scraping using Crawl4AI."""
        self.log(f"🚀 Scraping: {url}")
        scraped_data = {"title": "", "meta_description": "", "text": ""}
        
        run_config = CrawlerRunConfig(
            cache_mode="BYPASS",
            remove_overlay_elements=True,
            excluded_tags=["nav", "footer", "aside", "script", "style"]
        )

        try:
            if crawler:
                result = await crawler.arun(url=url, config=run_config)
            else:
                browser_config = BrowserConfig(headless=True)
                async with AsyncWebCrawler(config=browser_config) as local_crawler:
                    result = await local_crawler.arun(url=url, config=run_config)
            
            if result.success:
                scraped_data["title"] = result.metadata.get("title", "")
                scraped_data["meta_description"] = result.metadata.get("description", "")
                scraped_data["text"] = result.markdown
                self.log(f"✅ Scrape Success: {len(scraped_data['text'])} chars.")
                return scraped_data
            else:
                self.log(f"⚠️ Scraper Failed: {result.error_message}. Triggering Fallback...")
        except Exception as e:
            self.log(f"⚠️ Scraper Exception: {e}. Triggering Fallback...")

        # Fallback: aiohttp + BeautifulSoup
        try:
            async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
                async with session.get(url, timeout=10) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    scraped_data["title"] = soup.title.string if soup.title else ""
                    m_desc = soup.find('meta', attrs={'name': 'description'})
                    scraped_data["meta_description"] = m_desc['content'] if m_desc else ""
                    for s in soup(['script', 'style', 'nav', 'footer']): s.extract()
                    scraped_data["text"] = soup.get_text(separator=' ', strip=True)
                    self.log(f"🛡️ Fallback Success: {len(scraped_data['text'])} chars.")
            return scraped_data
        except Exception as e:
            self.log(f"❌ Scraping Fatal for {url}: {e}")
            return scraped_data

    def parse_json_response(self, text):
        """Robustly parse JSON even if wrapped in markdown code blocks."""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except:
            return None

    async def step_1_strategic_profile(self, url, scraped_data):
        """DNA extraction using the AI race."""
        prompt = f"""You are an Expert Business Analyst. Analyze this raw website data and return a JSON Strategic Profile.
        
        Url: {url}
        Metadata: {scraped_data['title']} | {scraped_data['meta_description']}
        Text: {scraped_data['text'][:5000]}
        
        JSON Format:
        {{
          "niche": "string (Specific Niche, e.g. Pediatric Dentist)",
          "location": "string (City, Country)",
          "transactional_keywords": ["3 specific buyer-intent keywords for discovery"],
          "technical_health_prediction": {{"speed": "0-100", "seo": "0-100"}},
          "content_gaps": ["list"]
        }}
        
        CRITICAL: Identify 'transactional_keywords' that someone would use to hire/buy from this business."""
        
        raw_res = await self.query_ai(prompt, "Strategic Profile")
        profile = self.parse_json_response(raw_res)
        return profile or {"niche": "Unknown", "business_model": "General", "content_gaps": []}

    async def step_2_keyword_roadmap(self, profile):
        """Engineering keywords based on strategy."""
        prompt = f"""Engineering a keyword roadmap for:
        Niche: {profile.get('niche', 'Generic')}
        Location: {profile.get('location', 'Global')}
        Intent: {profile.get('intent', 'General')}
        Gaps: {profile.get('content_gaps', [])}
        
        CRITICAL: Generate keywords that a real person in {profile.get('location', 'Global')} would search for. No generic 'SEO' fillers.
        
        Return JSON with: 
        'primary_keywords' (5), 
        'trending_keywords' (5), 
        'long_tail_keywords' (5),
        'local_keywords' (5)."""
        
        raw_res = await self.query_ai(prompt, "Keyword Roadmap")
        return self.parse_json_response(raw_res) or {
            "primary_keywords": ["SEO"],
            "trending_keywords": [],
            "long_tail_keywords": [],
            "local_keywords": []
        }

    async def step_3_onpage_optmization(self, url, scraped_data):
        """Generating actionable on-page fixes."""
        prompt = f"""You are a Senior On-Page SEO Specialist. Analyze this page content and generate optimized elements.
        URL: {url}
        Current Title: {scraped_data['title']}
        Current Meta: {scraped_data['meta_description']}
        Text Snippet: {scraped_data['text'][:3000]}
        
        Return JSON with:
        'optimized_title': (under 60 chars),
        'optimized_description': (under 160 chars),
        'structural_recommendations': [list of 5 specific actions for H1, Alt Tags, and content structure]"""
        
        raw_res = await self.query_ai(prompt, "On-Page Optimization")
        return self.parse_json_response(raw_res) or {"optimized_title": scraped_data['title'], "optimized_description": scraped_data['meta_description'], "structural_recommendations": []}

    async def step_4_competitor_analysis(self, keywords, profile, crawler=None):
        """Robust Multi-Engine Market Intelligence Engine (Guaranteed Discovery)."""
        self.log(f"\n🥷 [Step 4] Launching Dual-Engine Intelligence Engine...")
        
        comp_intel = []
        niche = profile.get('niche', 'business')
        location = profile.get('location', '')
        user_domain = profile.get('domain', '').lower()
        
        # 1. Multi-Stage Query Strategy
        base_kw = keywords.get('primary_keywords', [niche])[0]
        
        # Stage definitions: (query_template, weight, label)
        stages = [
            (f'best {base_kw} {location}', 1.2, "Stage 1: Local Precision"),
            (f'"{base_kw}" clinic {location} services', 1.5, "Stage 2: Commercial Intent"),
            (f'top {base_kw} companies near {location}', 1.0, "Stage 3: Broad Market")
        ]

        # 2. Advanced Junk Controls (Weaponized)
        JUNK_DOMAINS = {
            "facebook.com", "instagram.com", "linkedin.com", "twitter.com", "youtube.com", "pinterest.com",
            "wikipedia.org", "quora.com", "reddit.com", "yelp.com", "tripadvisor.com", "indiamart.com", 
            "justdial.com", "yellowpages.com", "glassdoor.com", "forbes.com", "medium.com", "business.site",
            "dictionary.com", "merriam-webster.com", "cambridge.org", "britannica.com", "zhihu.com", "ndtv.com", "timesofindia.com"
        }
        
        # Hard-block patterns in domain/URL
        JUNK_PATTERNS = [
            "dictionary.", "wiki.", "forum.", ".edu", ".gov", "blog.", "/article", "/news", "/press", "/journal", "zhihu.com", "quora.com"
        ]

        potential_competitors = {} # domain -> data
        
        # 3. Dual-Engine Discovery Loop
        for query_tpl, weight, label in stages:
            self.log(f"🔎 Scanning [{label}]: '{query_tpl}'")
            
            # Sub-Engine 1: Google (Primary/Highly Local)
            try:
                # googlesearch-python returns a generator of URLs
                google_results = list(search(query_tpl, num_results=8, lang="en", region="in"))
                self.log(f"   - Google Engine found {len(google_results)} hits.")
                for idx, url in enumerate(google_results):
                    url = url.lower()
                    domain = url.split("//")[-1].split("/")[0].replace("www.", "").lower()
                    # Weaponized Filtering
                    if any(junk in domain for junk in JUNK_DOMAINS): continue
                    if any(p in domain or p in url for p in JUNK_PATTERNS): continue
                    if user_domain and user_domain in domain: continue
                    
                    p_score = ((10 - idx) / 10.0) * weight * 1.2 # Bonus for Google results
                    if domain not in potential_competitors:
                        potential_competitors[domain] = {"url": url, "title": domain.upper(), "snippet": "", "score": p_score}
                    else:
                        potential_competitors[domain]["score"] += p_score
            except Exception as e:
                self.log(f"   ⚠️ Google Engine throttle: {str(e)}")

            # Sub-Engine 2: DDG Fallback (Snippet-Rich)
            if len(potential_competitors) < 5:
                try:
                    with DDGS() as ddgs:
                        ddg_results = list(ddgs.text(query_tpl, max_results=10))
                        self.log(f"   - DDG Engine found {len(ddg_results)} hits.")
                        for idx, r in enumerate(ddg_results):
                            url = (r.get('href') or r.get('url', '')).lower()
                            domain = url.split("//")[-1].split("/")[0].replace("www.", "").lower()
                            # Weaponized Filtering
                            if any(junk in domain for junk in JUNK_DOMAINS): continue
                            if any(p in domain or p in url for p in JUNK_PATTERNS): continue
                            if user_domain and user_domain in domain: continue
                            
                            p_score = ((10 - idx) / 10.0) * weight
                            if domain not in potential_competitors:
                                potential_competitors[domain] = {
                                    "url": url, "title": r.get('title', ''), "snippet": r.get('body', ''), "score": p_score
                                }
                            else:
                                potential_competitors[domain]["score"] += p_score
                except Exception as e:
                    self.log(f"   ⚠️ DDG Engine error: {str(e)}")
            
        if not potential_competitors:
            self.log("⚠️ Traditional search engines returned 0 results. Activating Neural Discovery Fallback...")
            discovery_prompt = f"""Identify the top 8 REAL, well-known business competitors for a '{niche}' located in '{location}'.
            For each, provide their business name and their likely primary website domain.
            Focus on actual service providers, not news sites or directories.
            
            Return JSON list of objects: [{{"name": string, "domain": string, "reason": string}}]
            """
            
            neural_discovery = self.parse_json_response(await self.query_ai(discovery_prompt, "Neural Discovery"))
            if neural_discovery:
                for nd in neural_discovery:
                    domain = nd.get('domain', '').lower().replace('https://', '').replace('http://', '').split('/')[0]
                    if not domain: continue
                    potential_competitors[domain] = {
                        "url": f"https://{domain}",
                        "title": nd.get('name', domain).upper(),
                        "snippet": nd.get('reason', 'Identified via Neural Market Knowledge.'),
                        "score": 1.0 # Base score for neural hits
                    }
        
        if not potential_competitors:
            self.log("❌ CRITICAL: No candidates found across Search or Neural Discovery.")
            return []

        # 4. Neural Intent Verification (Post-Discovery)
        # Process top 8 candidates (whether from search or neural discovery)
        sorted_candidates = sorted(potential_competitors.items(), key=lambda x: x[1]["score"], reverse=True)[:8]
        self.log(f"🧠 Validating {len(sorted_candidates)} candidates via Commercial Neural Sensing...")
        
        verified_picks = []
        for domain, data in sorted_candidates:
            if len(verified_picks) >= 3: break
            
            self.log(f"   🤖 Auditing: {domain}...")
            # STRICT AUDIT: Explicitly warning against educational/informational portals
            intent_prompt = f"""STRICT AUDIT: Is this domain a REAL SERVICE-PROVIDING BUSINESS or an Information/Educational/Q&A portal?
            Domain: {domain}
            Context: {data['title']} | {data['snippet']}
            Target Niche: {niche} in {location}

            REJECTION CRITERIA (Mark as 'editorial'):
            - It's a dictionary or wiki.
            - It's a Q&A site like Quora, Reddit, or Zhihu.
            - It's a news article or press release.
            - It's a broad directory that doesn't provide the service directly.
            - It's an educational (.edu) or gov site.

            APPROVAL CRITERIA (Mark as 'commercial'):
            - It is an actual clinic, center, or agency providing the service.
            - Mentions 'booking', 'clinics', 'treatments', 'pricing', 'about our team'.

            Return JSON: {{"is_commercial_business": boolean, "type": "commercial|editorial|directory", "confidence": 0-1}}
            """
            
            intent_res = self.parse_json_response(await self.query_ai(intent_prompt, f"Audit: {domain}"))
            
            if intent_res and intent_res.get("is_commercial_business") and intent_res.get("type") == "commercial":
                self.log(f"      ✅ VERIFIED: Real business player.")
                verified_picks.append((domain, data))
            else:
                self.log(f"      🗑️ REJECTED: Informational/Editorial signal ({domain}).")

        if not verified_picks:
            self.log("⚠️ No high-intent candidates passed neural check. Using top search hits.")
            verified_picks = sorted_candidates[:3]

        # 5. Deep Intelligence & Battle Sheet Generation
        self.log(f"🛡️ Isolated {len(verified_picks)} competitors. Extracting Intelligence...")
        for domain, data in verified_picks:
            url = data['url']
            self.log(f"⚡ Deep Scanning: {domain}...")
            
            try:
                comp_data = await self.scrape_text(url, crawler=crawler)
                content = comp_data.get('text', '')[:8000]
                
                if len(content) < 400:
                    self.log(f"   ⚠️ Content blocked. Using snippet data.")
                    content = data['snippet'] or data['title']
                
                battle_prompt = f"""Generate a MARKET BATTLE SHEET comparing our user niche '{niche}' vs '{domain}'.
                URL: {url}
                Content Analysis: {content}
                
                Format in Markdown:
                1. **Strategic Position**: Their core USP/market angle.
                2. **Target Keywords**: What are they fighting for in SERPs?
                3. **Our Gap vs Them**: Strengths/Weaknesses comparison.
                4. **Ninja Tactics**: 3 concrete actions to outrank them.
                """
                
                report = await self.query_ai(battle_prompt, f"Battle Sheet: {domain}")
                comp_intel.append({
                    "name": domain.upper(),
                    "url": url,
                    "report": report,
                    "score": round(data['score'], 2)
                })
            except Exception as e:
                self.log(f"   ⚠️ Analysis failure for {domain}: {str(e)}")

        self.log(f"✅ Competitive loop complete: {len(comp_intel)} reports ready.")
        return comp_intel

    async def step_5_backlink_prospecting(self, profile):
        """Finding high-authority backlink targets."""
        prompt = f"""Find 5 hyper-relevant sub-niche directory sites, industry associations, or local guest post opportunities for:
        Industry: {profile.get('niche', 'Generic')}
        Location: {profile.get('location', 'Global')}
        
        Return JSON list of objects: {{"title": "Site Name", "url": "URL", "category": "Directory|IndustryBody|LocalBlog", "analysis": "Why is this a high-authority target for {profile.get('niche')} in {profile.get('location')}?"}}"""
        
        raw_res = await self.query_ai(prompt, "Backlink Prospecting")
        return self.parse_json_response(raw_res) or []

    async def step_6_ninja_strategies(self, profile):
        """Generating high-level growth hacker SEO tactics."""
        prompt = f"""Provide 3 'Ninja' SEO strategies for dominance in {profile['niche']}.
        Focus on non-traditional link building or psychological UX hacks. Return Markdown."""
        return await self.query_ai(prompt, "Ninja Strategies")

    async def step_7_schema_engineering(self, url, profile):
        """Generating JSON-LD schemas."""
        prompt = f"""Generate professional JSON-LD schemas (Organization, LocalBusiness, Service) for:
        URL: {url}
        Niche: {profile['niche']}
        Return JSON object with the schemas."""
        
        raw_res = await self.query_ai(prompt, "Schema Engineering")
        return self.parse_json_response(raw_res) or {}

    async def step_8_link_bait_ideation(self, profile):
        """Generating data-driven link bait ideas."""
        prompt = f"""Brainstorm 3 data-driven 'Link Bait' report topics that would attract journalists in the {profile['niche']} industry.
        Return Markdown list with Topic and Brief Methodology."""
        return await self.query_ai(prompt, "Link Bait Ideation")

    async def full_audit(self, url):
        """The Elite Unified Audit Workflow."""
        self.log(f"\n🚀 STARTING ELITE SEO AUDIT: {url}\n")
        
        browser_config = BrowserConfig(headless=True)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 0. High-Fidelity Scrape
            scraped = await self.scrape_text(url, crawler=crawler)
            
            # 1. Strategic Profiling
            profile = await self.step_1_strategic_profile(url, scraped)
            
            # 2. Keyword Engineering
            keywords = await self.step_2_keyword_roadmap(profile)
            
            # 3. On-Page Optimization
            onpage = await self.step_3_onpage_optmization(url, scraped)
            
            # 4. Competitor Intelligence (Top 3)
            competitors = await self.step_4_competitor_analysis(keywords, profile, crawler=crawler)
            
            # 5. Backlink Targets
            backlinks = await self.step_5_backlink_prospecting(profile)
            
            # 6. Ninja Strategies
            ninja = await self.step_6_ninja_strategies(profile)
            
            # 7. Schema Engineering
            schemas = await self.step_7_schema_engineering(url, profile)
            
            # 8. Link Bait Ideation
            link_bait = await self.step_8_link_bait_ideation(profile)
            
            final_report = {
                "identity": profile,
                "onpage": onpage,
                "keywords": keywords,
                "competitor_analysis": competitors,
                "backlink_targets": backlinks,
                "ninja_strategies": ninja,
                "schemas": schemas,
                "link_bait_ideas": link_bait
            }
            
            self.log("\n🎉 FULL AUDIT COMPLETE! Intelligence Consolidated.")
            return final_report

if __name__ == "__main__":
    import sys
    agent = SEOExpertAgent()
    target = sys.argv[1] if len(sys.argv) > 1 else "https://cosmosclinics.in/"
    report = asyncio.run(agent.full_audit(target))
    
    with open("seo_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Saved results to seo_report.json")
