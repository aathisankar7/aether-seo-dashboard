# 📖 The SEO Project Bible: Competitor & Keyword Intelligence

This document defines the core logic (P1) for the SEO Project's intelligence layer. It is the "Bible" for how the system identifies competitors and generates keyword strategies.

> **⚠️ STABILITY LOCK (2026-03-24): These rules are FINAL. Do NOT modify without explicit user approval.**

## 1. Business DNA Extraction (Strategic Profile)
- **Logic**: The system must extract the "Core Identity" from the client's website branding.
- **Source**: Prioritize `H1` tags, `Meta Titles`, and the first 2000 characters of home page text.
- **Goal**: Identify the exact transactional phrase the business uses to describe itself (e.g., "Best Dental Clinic in Hyderabad").
- **Domain Extraction**: Always extract and store the target domain in `profile['domain']` for self-filtering.

## 2. Hyper-Local Competitor Discovery

### 2.1 Search API Priority
| Priority | API | Notes |
|----------|-----|-------|
| 1st | **Serper API** | Primary. `SERPER_KEY` in `.env` |
| 2nd | SerpApi | Fallback only. `SERPAPI_KEY` in `.env` |

### 2.2 Search Query Rules
- Extract keywords from the website's DNA (Strategic Profile + Keyword Roadmap).
- **CRITICAL: Strip the client's brand name** from all search queries.
  - Example: `"Partha Dental Hyderabad"` → `"Dental Hyderabad"` or `"Dentist Hyderabad"`
- **Always inject generic niche queries**: `"best [niche] in [city]"`, `"top [niche] near [city]"`, `"[niche] [city]"`.
- Search up to **10 keywords**, **15 results per keyword**.

### 2.3 Filtering Rules
- **Self-Domain Filter (TLD-Agnostic)**: Compare base names without TLD.
  - `parthadental.com` vs `parthadental.in` → both have base `parthadental` → **BLOCKED**.
  - Strip hyphens/underscores for matching: `partha-dental` == `parthadental`.
- **Junk Filter**: Block directories, social media, news, insurance, Maps clones, national chains.
  - Must include: `localo.site`, `apollo247`, `careinsurance`, `practo`, `justdial`, `cybo.com`, etc.
- **Location Check is SOFT**: Log a warning if city text is absent, but let AI decide. Do NOT hard-reject.

### 2.4 Selection Rules
- **Target = 5 competitors**. Always. Never fewer.
- **Candidate Pool = Top 20** from Google (sorted by intersection score).
- **Intersection Multiplier**: Domains ranking for multiple keywords get score × (overlap_count ^ 1.5).
- **AI Verification Confidence Threshold = 0.5** (not higher — too many false rejections).
- **Graceful Fill**: If AI verification finds < 5, fill remaining slots from top-scoring Google results (scrape-only, no AI verification needed).

### 2.5 Neural Fallback
- If zero candidates found from Google search, ask AI for top 7 local competitors.
- Only triggered as last resort.

## 3. Battle Sheet Generation
- Generate a full Markdown battle sheet for **each of the 5 competitors**.
- Sections: Strategic Position, Target Keywords (5-7), Gap Analysis (Strengths/Weaknesses), Ninja Tactics (3 actions).
- Each competitor object MUST have both `report` and `battle_sheet` keys (cross-frontend compatibility).

## 4. High-Fidelity Keyword Extraction
- **The "Spy" Phase**: Every verified competitor is scraped specifically for their SEO keywords.
- **Logic**: Identify keywords used in their `H1`s and `Titles` to understand which "money terms" they are actively fighting for.

## 5. The Unified Keyword Roadmap (The Bible)
The final report merges three distinct intelligence streams into a single "Bible":
1. **Client DNA**: Keywords the business is already targeting.
2. **Competitor Intelligence**: Exact keywords pulled from the top 5 market leaders.
3. **AI Semantic Engineering**: Cluster suggestions (Golden Ratio, Viral Clusters) for topical authority.

## 6. Data Key Requirements
The final audit report MUST return:
| Key | Used By |
|-----|---------|
| `competitor_analysis` | Aether Dashboard (`seo_dashboard.html`) |
| `competitor_intelligence` | Streamlit Dashboard (`app.py`) |
| `strategic_profile` | Alias for `identity` (Streamlit) |

## 7. Stability & Enforcement
- All agent updates must respect this flow.
- The `SEOExpertAgent.full_audit` method is the source of truth for this integration.
- The `step_4_competitor_analysis` method is the source of truth for competitor discovery.
- **DO NOT** change the target from 5 competitors.
- **DO NOT** make Serper a fallback — it is PRIMARY.
- **DO NOT** raise the verification threshold above 0.5.
- **DO NOT** hard-reject candidates based on location text absence.
