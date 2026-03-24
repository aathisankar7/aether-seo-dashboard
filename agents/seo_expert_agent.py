"""
SEO Expert Agent — The core orchestration engine for the AI SEO Dashboard (Elite Upgrade).
High-Fidelity Scraping via Crawlee & Multi-Model AI Intelligence (Groq, Cerebras, SambaNova, Routeway).
"""

import json
import os
import sys
import asyncio
import time
import re
from datetime import datetime, timedelta
import pandas as pd
import aiohttp
import requests
import urllib.parse
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# Path setup for running as script
if __name__ == "__main__" or __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from googlesearch import search # Crucial and Verified
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Import from our advanced model router
from core.model_router import race_models
from core.free_apis import FreeAPIManager
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPER_KEY = os.getenv("SERPER_KEY")


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
        # Detect if we are on a generic subpage (e.g. contactus, about)
        is_subpage = url.count('/') > 3 or any(x in url.lower() for x in ['contact', 'about', 'legal', 'privacy', 'terms'])
        
        prompt = f"""You are an Expert Business Analyst. Analyze this raw website data and return a JSON Strategic Profile.
        
        Url: {url}
        Metadata: {scraped_data['title']} | {scraped_data['meta_description']}
        Text: {scraped_data['text'][:5000]}
        
        CRITICAL: Extract the EXACT SEO keywords this business is targeting based on its physical branding. 
        Look at the H1s, Titles, and bold text. 
        Example: If it's a dentist in Hyderabad and the title says "Best Dental Clinic in Hyderabad", the transactional keyword MUST be "Best Dental Clinic in Hyderabad".
        
        JSON Format:
        {{
          "niche": "string (Specific Niche, e.g. Pediatric Dentist)",
          "location": "string (City, Country - e.g. Hyderabad, India)",
          "transactional_keywords": ["Exact phrase 1 from branding", "Exact phrase 2 from branding", "High-intent keyword 3"],
          "technical_health_prediction": {{"speed": "0-100", "seo": "0-100"}},
          "content_gaps": ["list"]
        }}
        
        CRITICAL: The 'transactional_keywords' MUST reflect the primary service + location if present (e.g. 'best dental clinic in hyderabad')."""
        
        raw_res = await self.query_ai(prompt, "Strategic Profile")
        profile = self.parse_json_response(raw_res)
        
        # [ELITE HEURISTIC] DNA-First Fallback: If no keywords extracted, pull from Title/Metadata
        if not profile or not profile.get('transactional_keywords'):
            profile = profile or {}
            title_parts = scraped_data['title'].split('|')[0].split('-')[0].strip()
            if len(title_parts) > 3:
                self.log(f"   🧬 Title DNA Extraction: Found '{title_parts}'")
                profile['transactional_keywords'] = [title_parts]
                profile['revenue_drivers'] = [title_parts] # Also add to roadmap drivers
                if 'niche' not in profile or profile['niche'] == "Unknown":
                    profile['niche'] = title_parts

        # Fallback if niche is still unknown but we have a title/URL
        if not profile or profile.get('niche') == "Unknown":
            # Heuristic: try to extract keywords from title if AI failed
            title = scraped_data['title'].lower()
            if 'fashion' in title or 'clothing' in title:
                profile = profile or {}
                profile['niche'] = "Fashion Store"
                profile['location'] = profile.get('location', 'Unknown')
        
        return profile or {"niche": "Unknown", "business_model": "General", "content_gaps": []}

    async def step_2_keyword_roadmap(self, profile):
        """Engineering keywords based on strategy."""
        niche = profile.get('niche', 'Generic Business')
        location = profile.get('location', 'Your City')
        
        prompt = f"""You are a Local SEO & Viral Growth Expert. Engineer an ELITE keyword roadmap for this specific business:
        Niche: {niche}
        Location: {location}
        Intent: {profile.get('intent', 'High-Conversion Local Growth')}
        
        CRITICAL RULES:
        1. Generate REAL keywords that a high-value customer/patient in {location} would type into Google to find {niche}.
        2. DO NOT use generic placeholders. Focus ONLY on the business identity.
        3. 'Viral Clusters' should be questions or trending topics (e.g. "Is [Service] worth it in {location}?") that drive top-of-funnel traffic.
        4. All results must be hyper-local or high-intent.
        
        Return exactly this JSON format:
        {{
            "revenue_drivers": ["primary keyword 1", "primary keyword 2", "primary keyword 3", "primary keyword 4", "primary keyword 5"],
            "viral_clusters": ["trending/question 1", "trending/question 2", "trending/question 3", "trending/question 4", "trending/question 5"],
            "golden_ratio": ["long-tail phrase 1", "long-tail phrase 2", "long-tail phrase 3", "long-tail phrase 4", "long-tail phrase 5"],
            "local_traces": ["local near me 1", "local near me 2", "local near me 3", "local near me 4", "local near me 5"]
        }}"""
        
        raw_res = await self.query_ai(prompt, "Keyword Roadmap")
        parsed = self.parse_json_response(raw_res)
        
        # Robust fallback if AI hallucinated non-niche queries
        if not parsed or 'revenue_drivers' not in parsed or not parsed['revenue_drivers'] or 'artificial intelligence' in str(parsed).lower():
            self.log("⚠️ AI generated generic/invalid keywords. Using hard fallback.")
            parsed = {
                "revenue_drivers": [f"{niche} in {location}", f"best {niche} {location}"],
                "viral_clusters": [f"is {niche} worth it in {location}?", f"how to find top {niche} in {location}"],
                "golden_ratio": [f"affordable {niche} services {location}"],
                "local_traces": [f"{niche} near me", f"top rated {niche} {location}"]
            }
            
        return parsed

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

    async def _verify_competitor_by_scrape(self, domain, profile, crawler):
        """Phase 4: Scrape the candidate and verify it's a true niche and location match."""
        niche = profile.get('niche', '')
        location = profile.get('location', '')
        target_city = location.split(",")[0].strip().lower() if location else ""
        url = f"https://{domain}"

        self.log(f"   🔬 Scrape-verifying: {domain}...")
        comp_data = await self.scrape_text(url, crawler=crawler)
        content = comp_data.get('text', '')

        if len(content) < 200:
            self.log(f"   ⚠️ Could not scrape {domain}. Skipping.")
            return None

        # Soft location check: only reject if city is VERY clearly absent and the content is large enough
        content_lower = content[:5000].lower()
        if target_city and len(target_city) > 3 and len(content) > 2000:
            if target_city not in content_lower and target_city not in domain:
                # Don't hard-reject, just log a warning — let AI verification decide
                self.log(f"   ⚠️ Location hint missing for '{target_city}' — AI will decide.")

        verify_prompt = f"""Does this website DIRECTLY offer '{niche}' services IN OR NEAR '{location}'?
Scraped content from {domain}:
{content[:3000]}

Answer ONLY with JSON:
{{
  "is_same_niche": boolean, 
  "is_correct_location": boolean, 
  "confidence": 0.0-1.0, 
  "ranking_keywords": ["List 5 high-value SEO keywords this competitor is clearly targeting"],
  "services_found": ["list of services you identified"]
}}

CRITICAL: 
1. Only return true if the site DIRECTLY provides '{niche}' services. 
2. Only return true for location if they serve '{location}'.
3. In 'ranking_keywords', identify the specific phrases they use in H1s and Titles (e.g., 'Best Dentist in Gachibowli')."""

        res = self.parse_json_response(await self.query_ai(verify_prompt, f"Verify & Extract: {domain}"))

        if res and res.get("is_same_niche") and res.get("confidence", 0) >= 0.5:
            confidence = res.get("confidence", 0)
            services = res.get("services_found", [])
            keywords = res.get("ranking_keywords", [])
            self.log(f"   ✅ VERIFIED: {domain} matches {location} (conf: {confidence:.2f})")
            self.log(f"   📊 Extracted Competitor Keywords: {keywords}")
            return {"content": content, "keywords": keywords}
        else:
            conf = res.get("confidence", 0) if res else "N/A"
            reason = "Location Mismatch" if (res and not res.get("is_correct_location")) else "Niche Mismatch"
            self.log(f"   🗑️ REJECTED: {reason} ({domain}, conf: {conf}).")
            return None

    async def step_4_competitor_analysis(self, keywords, profile, scraped_data=None, crawler=None):
        """5-Competitor Discovery Engine — Bible-Aligned, Serper-First."""
        TARGET_COMPETITORS = 5
        self.log(f"\n🥷 [Step 4] Launching Competitor Discovery Engine (Target: {TARGET_COMPETITORS})...")

        comp_intel = []
        niche = profile.get('niche', 'business')
        location = profile.get('location', '')
        user_domain = profile.get('domain', '').lower()

        # ── Phase 1: Hard-coded Blacklists ──────────────────────────────────
        JUNK_BRANDS = {
            # Social / Q&A / Content
            "facebook", "instagram", "linkedin", "twitter", "x.com", "youtube", "pinterest", 
            "wikipedia", "quora", "reddit", "medium", "tumblr",
            # Directories & Aggregators
            "yelp", "tripadvisor", "indiamart", "justdial", "sulekha", "yellowpages", 
            "glassdoor", "practo", "lybrate", "1mg", "indiatimes", "timesofindia", 
            "hindustantimes", "thehindu", "ndtv", "economictimes", "moneycontrol",
            "businessinsider", "forbes", "bloomberg", "reuters", "indiatoday",
            # National Hospital chains (too big to be local competitors)
            "apollohospitals", "narayanahealth", "maxhealthcare", "fortishealthcare", 
            "manipalhospitals", "aster.in", "yashoda", "care-hospitals", "carehospitals",
            # Health directories
            "healthgrades", "zocdoc", "netmeds", "pharmeasy", "mouthshut",
            # Local listing / Maps clones
            "localo.site", "localsearch", "cybo.com", "placedigger", "tupalo",
            "brownbook", "hotfrog", "foursquare", "mapquest", "waze",
            # Other junk
            "google.com", "google.co.in", "bing.com", "yahoo.com",
            "amazon", "flipkart", "nykaa", "zomato", "swiggy",
            "careinsurance", "policybazaar", "apollo247"
        }
        JUNK_URL_PATTERNS = [
            "?gclid", "?gad_source", "?gbraid", "/landing", "/campaign",
            "/lp/", "/ads/", "dictionary.", ".edu", ".gov", "/news/", "/article/",
        ]
        CONTENT_JUNK_WORDS = [
            "toto", "macau", "togel", "casino", "betting", "gambling", "poker", "slot machine"
        ]

        # ── Phase 2: Keyword Roadmap Extraction ─────────────────────────────
        # Use keywords from the website's DNA (Strategic Profile) and the engineered roadmap
        ai_queries = []
        
        # Extract the business brand name for filtering
        brand_words = set()
        if user_domain:
            # Extract brand from domain: 'parthadental.com' -> ['partha', 'dental']
            import re as _re
            base = user_domain.split('.')[0]
            # Split by camelCase, hyphens, underscores
            parts = _re.split(r'[-_]', base)
            for part in parts:
                # Also split camelCase
                sub_parts = _re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', part)
                if sub_parts:
                    brand_words.update(w.lower() for w in sub_parts if len(w) > 2)
                else:
                    brand_words.add(part.lower())
        
        # 1. From Strategic Profile (Website's direct DNA)
        if profile.get('transactional_keywords'):
            ai_queries.extend(profile['transactional_keywords'])
            
        # 2. From Engineered Roadmap
        if keywords:
            for k in keywords.get("revenue_drivers", []) + keywords.get("local_traces", []):
                if isinstance(k, dict) and "keyword" in k:
                    ai_queries.append(k["keyword"])
                elif isinstance(k, str):
                    ai_queries.append(k)
        
        # Fallback if no keywords were generated
        if not ai_queries:
            ai_queries = [f"{niche} in {location}", f"best {niche} near {location}"]
        
        # CRITICAL: Remove brand-specific keywords to find COMPETITORS, not the client's own listings
        # e.g. "Partha Dental Hyderabad" -> "Dental Hyderabad" or drop entirely
        cleaned_queries = []
        brand_name_lower = user_domain.split('.')[0].lower() if user_domain else ""
        for q in ai_queries:
            q_lower = q.lower()
            # Skip if query is basically just the brand name
            if brand_name_lower and brand_name_lower in q_lower.replace(' ', ''):
                # Strip the brand name out and keep the rest
                import re as _re
                # Remove brand words from query
                cleaned = q
                for bw in sorted(brand_words, key=len, reverse=True):
                    cleaned = _re.sub(r'\b' + _re.escape(bw) + r'\b', '', cleaned, flags=_re.IGNORECASE)
                cleaned = ' '.join(cleaned.split()).strip(' ,.-')
                if len(cleaned) > 5:  # Only keep if meaningful content remains
                    cleaned_queries.append(cleaned)
                    self.log(f"   🔄 Brand-cleaned: '{q}' → '{cleaned}'")
            else:
                cleaned_queries.append(q)
        
        # Add generic niche + location queries to ensure we find real competitors
        if location:
            generic_queries = [
                f"best {niche} in {location.split(',')[0].strip()}",
                f"top {niche} near {location.split(',')[0].strip()}",
                f"{niche} {location.split(',')[0].strip()}"
            ]
            for gq in generic_queries:
                if gq.lower() not in [q.lower() for q in cleaned_queries]:
                    cleaned_queries.append(gq)
        
        ai_queries = cleaned_queries
            
        # Filter and De-duplicate
        ai_queries = [q for q in ai_queries if 'unknown' not in q.lower() and 'your city' not in q.lower()]
        ai_queries = list(dict.fromkeys(ai_queries))[:10] # Top unique keywords
        
        self.log(f"🎯 Local Rival Intersection Analysis across {len(ai_queries)} Website-Derived Keywords")

        # ── Phase 3: The Intersection Matrix ────────────────────────────────
        potential_competitors = {}
        domain_overlap = {}

        # Extract specific city for query enhancement
        target_location = location.lower()
        target_city = location.split(",")[0].strip().lower() if location else ""

        def _extract_base_name(domain):
            """Extract the brand/base name from a domain, stripping TLD."""
            # e.g. 'parthadental.com' -> 'parthadental', 'partha-dental.co.in' -> 'partha-dental'
            parts = domain.split('.')
            if len(parts) >= 3 and parts[-2] in ('co', 'com', 'org', 'net', 'ac'):
                return parts[-3]  # e.g. example.co.in -> example
            elif len(parts) >= 2:
                return parts[-2]  # e.g. example.com -> example
            return domain

        user_base_name = _extract_base_name(user_domain) if user_domain else ""
        # Also strip hyphens and common words for fuzzy brand matching
        user_brand_clean = user_base_name.replace('-', '').replace('_', '').lower() if user_base_name else ""
        self.log(f"🛡️ Self-Domain Filter: '{user_domain}' (brand: '{user_brand_clean}')")

        def _is_junk(domain, url):
            if any(brand in domain for brand in JUNK_BRANDS):
                return True
            if any(p in url for p in JUNK_URL_PATTERNS):
                return True
            if user_domain:
                # Exact domain match
                if user_domain in domain or domain in user_domain:
                    return True
                # TLD-agnostic brand match (parthadental.com vs parthadental.in)
                candidate_base = _extract_base_name(domain)
                candidate_clean = candidate_base.replace('-', '').replace('_', '').lower()
                if user_brand_clean and candidate_clean and user_brand_clean == candidate_clean:
                    self.log(f"   🛡️ Blocked same-brand domain: {domain} (brand: '{candidate_clean}')")
                    return True
            return False

        for idx_q, query in enumerate(ai_queries):
            # HYPER-LOCAL ENHANCEMENT:
            # Strictly pair with the discovered city to find local rivals
            search_query = query
            if target_city and target_city not in query.lower():
                search_query = f"{query} {target_city}"
            elif not target_city and target_location and target_location not in query.lower():
                search_query = f"{query} {target_location}"

            self.log(f"🔎 Keyword [{idx_q+1}/{len(ai_queries)}]: '{search_query}'")

            # Serper (Primary) / SerpApi (Fallback) — Google Search
            try:
                results = []
                
                try:
                    # 1. PRIMARY: Serper API
                    if not SERPER_KEY:
                        raise ValueError("No SERPER_KEY")
                    serper_url = "https://google.serper.dev/search"
                    payload = json.dumps({"q": search_query, "location": location, "num": 15, "gl": "in"})
                    headers = {'X-API-KEY': SERPER_KEY, 'Content-Type': 'application/json'}
                    res = requests.post(serper_url, headers=headers, data=payload, timeout=15)
                    data = res.json()
                    if "organic" in data and data["organic"]:
                        for organic in data["organic"]:
                            link = organic.get("link")
                            if link:
                                results.append(link)
                        self.log(f"   ✅ Serper: {len(results)} results")
                    else:
                        raise ValueError("Serper empty")
                        
                except Exception as e:
                    self.log(f"   ⚠️ Serper Issue: {e}. Falling back to SerpApi...")
                    # 2. FALLBACK: SerpApi
                    if not SERPAPI_KEY:
                        self.log("   ❌ Fallback aborted: Missing SERPAPI_KEY")
                    else:
                        encoded_query = urllib.parse.quote(search_query)
                        url = f"https://serpapi.com/search.json?q={encoded_query}&engine=google&gl=in&hl=en&num=15&api_key={SERPAPI_KEY}"
                        res = requests.get(url, timeout=15)
                        data = res.json()
                        if "organic_results" in data:
                            for organic in data["organic_results"]:
                                link = organic.get("link")
                                if link:
                                    results.append(link)
                            self.log(f"   ✅ SerpApi: {len(results)} results")

                # Process whatever results we got from the active API
                for idx_r, result_url in enumerate(results[:15]):
                    result_url_lower = result_url.lower()
                    # Strip to root domain (ignore landing page params)
                    root_url = result_url.split("?")[0].split("#")[0]
                    domain = root_url.split("//")[-1].split("/")[0].replace("www.", "").lower()

                    if _is_junk(domain, result_url_lower):
                        continue

                    # Snippet content junk check
                    if any(junk in domain for junk in CONTENT_JUNK_WORDS):
                        continue

                    if domain not in potential_competitors:
                        potential_competitors[domain] = {"url": f"https://{domain}", "score": 0.0, "overlap_keywords": set(), "overlap_count": 0}
                        domain_overlap[domain] = 0

                    potential_competitors[domain]["overlap_keywords"].add(query)
                    domain_overlap[domain] += 1

                    # 1. Base rank score (higher is better)
                    rank_score = (15 - idx_r) / 15.0
                    
                    # 2. Location domain hint boost
                    city_hint = location.split(",")[0].lower().strip()
                    if city_hint and city_hint in domain:
                        rank_score += 0.5

                    potential_competitors[domain]["score"] += rank_score

            except Exception as e:
                self.log(f"   ⚠️ Google query error: {e}")

        # ── Phase 3B: Apply Intersection Multiplier ────────────────────────
        # Domains ranking for multiple keywords get a massive score multiplier
        for domain, data in potential_competitors.items():
            overlap_count = domain_overlap[domain]
            # Multiply base score by the overlap count to heavily favor intersection
            data["score"] = data["score"] * (overlap_count ** 1.5)
            data["overlap_count"] = overlap_count


        self.log(f"📊 Discovery complete: {len(potential_competitors)} raw candidates found.")

        # ── Neural Fallback if discovery failed ─────────────────────────────
        if not potential_competitors:
            self.log("⚠️ Zero candidates from search. Activating Neural Market Knowledge Fallback...")
            fallback_prompt = f"""Name the top 7 REAL, LOCAL competitor businesses (same as '{niche}') near '{location}'.
            They must be actual local service providers with their own websites, not chains or directories.
            Return JSON: [{{"name": "string", "domain": "example.com"}}]"""
            fallback = self.parse_json_response(await self.query_ai(fallback_prompt, "Neural Fallback"))
            if fallback:
                for item in fallback:
                    d = item.get("domain", "").replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower()
                    if d:
                        potential_competitors[d] = {"url": f"https://{d}", "snippet": "", "score": 1.0}

        if not potential_competitors:
            self.log("❌ No competitors found after all attempts.")
            return {"competitors": [], "competitor_keywords": []}

        # ── Phase 4: Scrape + Verify Top Candidates ─────────────────────────
        top_candidates = sorted(potential_competitors.items(), key=lambda x: x[1]["score"], reverse=True)[:20]
        self.log(f"🧬 Verifying top {min(len(top_candidates), 20)} candidates to find {TARGET_COMPETITORS} competitors...")
        for domain, data in top_candidates[:10]:
            kw_list = list(data.get('overlap_keywords', set()))[:3]
            self.log(f"   📌 {domain} (score: {data['score']:.1f}, keywords: {', '.join(kw_list) if kw_list else 'N/A'})")

        verified_picks = []
        competitor_keywords = []
        
        for domain, data in top_candidates:
            if len(verified_picks) >= TARGET_COMPETITORS:
                break
            
            # Scrape and Verify
            verification_result = await self._verify_competitor_by_scrape(domain, profile, crawler)
            
            if verification_result:
                verified_picks.append((domain, data, verification_result["content"]))
                # Collect keywords for the "Bible"
                competitor_keywords.extend(verification_result.get("keywords", []))

        # ── Fill remaining slots if we have fewer than TARGET ───────────────
        if len(verified_picks) < TARGET_COMPETITORS:
            remaining = TARGET_COMPETITORS - len(verified_picks)
            self.log(f"⚠️ Only {len(verified_picks)} verified. Filling {remaining} more from top scorers...")
            already_picked = {d for d, _, _ in verified_picks}
            
            for domain, data in top_candidates:
                if len(verified_picks) >= TARGET_COMPETITORS:
                    break
                if domain in already_picked:
                    continue
                if _is_junk(domain, data.get('url', '')):
                    continue

                try:
                    comp_data = await self.scrape_text(data["url"], crawler=crawler)
                    content = comp_data.get("text", "")
                    if len(content) >= 200:
                        verified_picks.append((domain, data, content))
                        already_picked.add(domain)
                        self.log(f"   📥 Filled slot [{len(verified_picks)}/{TARGET_COMPETITORS}]: {domain}")
                    else:
                        self.log(f"   ⚠️ Scrape too short for {domain}, skipping.")
                except Exception as e:
                    self.log(f"   ⚠️ Error scraping {domain}: {e}")
                    continue

        self.log(f"📊 Final competitor count: {len(verified_picks)}")

        # ── Battle Sheet Generation ─────────────────────────────────────────
        self.log(f"⚔️ Generating Battle Sheets for {len(verified_picks)} verified competitors...")
        for domain, data, content in verified_picks:
            try:
                battle_prompt = f"""You are an elite SEO strategist. Generate a precise MARKET BATTLE SHEET.

Our Client: {niche} in {location}
Competitor: {domain}
Competitor Content: {content[:5000]}

Write in Markdown with these exact sections:
## 1. Strategic Position
(What is their core USP and market angle? What patients/customers do they target?)

## 2. Target Keywords
(List 5-7 specific keywords they are ranking for based on their content)

## 3. Our Gap vs Them
**Strengths** (What they do well):
**Weaknesses** (Where we can beat them):

## 4. Ninja Tactics
(3 specific, actionable steps to outrank this competitor in {location})"""

                report = await self.query_ai(battle_prompt, f"Battle Sheet: {domain}")
                comp_intel.append({
                    "name": domain.upper(),
                    "url": f"https://{domain}",
                    "report": report,
                    "battle_sheet": report, # Alias for Streamlit Compatibility
                    "score": round(data["score"], 2)
                })
                self.log(f"✅ Battle Sheet ready for {domain}.")
            except Exception as e:
                self.log(f"⚠️ Battle Sheet failed for {domain}: {e}")

        self.log(f"🏆 Competitive Intelligence complete: {len(comp_intel)} Battle Sheets generated.")
        return {"competitors": comp_intel, "competitor_keywords": list(set(competitor_keywords))}

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
            
            # [ENHANCEMENT] Extract domain for self-competitor filtering
            curr_domain = url.split("//")[-1].split("/")[0].replace("www.", "").lower()
            profile['domain'] = curr_domain
            self.log(f"🧬 Identity Established: {curr_domain}")
            
            # [ENHANCEMENT] If location is missing, try to find About/Contact pages
            if not profile.get('location') or profile.get('location') == "Unknown":
                self.log("🔍 Location missing. Searching for 'About' or 'Contact' pages...")
                links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+|/[^\)]+)\)', scraped.get('text', ''))
                about_url = None
                for text, lk in links:
                    if any(x in text.lower() for x in ['about', 'contact', 'location', 'reach us']):
                        about_url = lk if lk.startswith('http') else urllib.parse.urljoin(url, lk)
                        break
                
                if not about_url:
                    # Guess common paths
                    base_url = "/".join(url.split("/")[:3])
                    # Prioritize contact pages for location
                    for path in ['/contactus', '/contact-us', '/contact', '/about-us', '/aboutus', '/about', '/reach-us']:
                        try:
                            check_url = urllib.parse.urljoin(base_url, path)
                            self.log(f"   Trying guess: {check_url}")
                            async with aiohttp.ClientSession() as session:
                                async with session.get(check_url, timeout=5) as resp:
                                    if resp.status == 200:
                                        # Verify content length before accepting
                                        temp_scraped = await self.scrape_text(check_url, crawler=crawler)
                                        if len(temp_scraped.get('text', '')) > 200:
                                            about_url = check_url
                                            about_scraped = temp_scraped
                                            break
                        except:
                            continue
                
                if about_url:
                    if 'about_scraped' not in locals():
                        about_scraped = await self.scrape_text(about_url, crawler=crawler)
                    
                    self.log(f"   Extracting location from: {about_url}")
                    loc_prompt = f"""Analyze this page and extract the business's physical location (City, Country).
                    Only return the main headquarters or primary service area.
                    
                    Text: {about_scraped['text'][:5000]}
                    
                    Return ONLY a JSON object: {{"location": "City, Country" or "Unknown"}}"""
                    
                    loc_res = await self.query_ai(loc_prompt, "Extract Location")
                    loc_data = self.parse_json_response(loc_res)
                    if loc_data and loc_data.get('location') != "Unknown":
                        profile['location'] = loc_data['location']
                        self.log(f"   📍 Found Location: {profile['location']}")

            # 2. Keyword Engineering
            keywords = await self.step_2_keyword_roadmap(profile)
            
            # 3. On-Page Optimization
            onpage = await self.step_3_onpage_optmization(url, scraped)
            
            # 4. Competitor Intelligence (DNA-First — Top 3)
            comp_result = await self.step_4_competitor_analysis(keywords, profile, scraped_data=scraped, crawler=crawler)
            competitors = comp_result.get("competitors", [])
            comp_keywords = comp_result.get("competitor_keywords", [])

            # ── [ELITE ENHANCEMENT] The SEO Bible: Unified Keyword Intelligence ─────
            # Merge client-claimed keywords, AI-engineered keywords, and competitor keywords
            all_keywords = {
                "revenue_drivers": list(set(keywords.get('revenue_drivers', []) + profile.get('transactional_keywords', []))),
                "viral_clusters": keywords.get('viral_clusters', []),
                "golden_ratio": keywords.get('golden_ratio', []),
                "local_traces": keywords.get('local_traces', []),
                "competitor_extracted": comp_keywords,
                "ai_suggested_clusters": keywords.get('golden_ratio', []) + keywords.get('viral_clusters', []) # Merged for Bible
            }
            
            # 5. Backlink Targets
            backlinks = await self.step_5_backlink_prospecting(profile)
            
            # 6. Ninja Strategies
            ninja = await self.step_6_ninja_strategies(profile)
            
            # 7. Schema Engineering
            schemas = await self.step_7_schema_engineering(url, profile)
            
            # 8. Link Bait Ideation
            link_bait = await self.step_8_link_bait_ideation(profile)
            
            # 9. [ELITE ADDITION] Zero-Auth Technical & Sentiment Intelligence
            self.log("🔍 Extracting Technical Merit & Sentiment Analysis...")
            free_api = FreeAPIManager()
            technical_audit = await free_api.google_psi_audit(url)
            sentiment_summary = await free_api.analyze_sentiment(scraped.get('text', '')[:500])
            
            final_report = {
                "identity": profile,
                "strategic_profile": profile, # Alias for Streamlit Compatibility
                "onpage": onpage,
                "keywords": all_keywords,
                "competitor_analysis": competitors,     # Key for Aether Dashboard (seo_dashboard.html)
                "competitor_intelligence": competitors, # Key for Streamlit Dashboard (app.py)
                "backlink_targets": backlinks,
                "ninja_strategies": ninja,
                "schemas": schemas,
                "link_bait_ideas": link_bait,
                "technical_merit": technical_audit,
                "brand_sentiment": sentiment_summary
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
