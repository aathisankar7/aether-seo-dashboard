import asyncio
import json
from core.free_apis import FreeAPIManager

async def main():
    manager = FreeAPIManager()
    
    print("🚀 --- Ritz Intelligence: Free API Suite Demo ---\n")
    
    # 1. Hugging Face Sentiment (Great for Google Review Analysis)
    print("Testing Hugging Face Sentiment Analysis...")
    review = "The SEO services provided by Ritz Group were phenomenal. Our traffic grew by 300% in 2 months!"
    sentiment = await manager.analyze_sentiment(review)
    print(f"Post Analysis: {review}")
    print(f"Result: {json.dumps(sentiment, indent=2)}\n")
    
    # 2. Hugging Face Summarization (Great for Competitor Content Analysis)
    print("Testing Hugging Face Summarization...")
    long_text = """
    Search engine optimization (SEO) is the process of improving the quality and quantity of website traffic to a website or a web page from search engines. 
    SEO targets unpaid traffic (known as 'natural' or 'organic' results) rather than direct traffic or paid traffic. 
    Unpaid traffic may originate from different kinds of searches, including image search, video search, academic search, news search, and industry-specific vertical search engines. 
    As an Internet marketing strategy, SEO considers how search engines work, the computer-programmed algorithms that dictate search engine behavior, what people search for, the actual search terms or keywords typed into search engines, and which search engines are preferred by their targeted audience. 
    SEO is performed because a website will receive more visitors from a search engine when websites rank higher on the search engine results page (SERP). 
    These visitors can then potentially be converted into customers.
    """
    summary = await manager.generate_summary(long_text)
    print(f"Summary: {summary}\n")
    
    # 3. Google PageSpeed Insights (No-Auth Technical Audit)
    print("Testing Google PageSpeed Insights (Technical Audit)...")
    url = "https://google.com"
    audit = await manager.google_psi_audit(url)
    print(f"Target: {url}")
    print(f"Scores: Performance: {audit.get('performance')}, SEO: {audit.get('seo')}")
    print(f"FCP: {audit.get('first_contentful_paint')}\n")
    
    # 4. Zero-Auth Utilities
    print("Testing Zero-Auth Logo & Location...")
    domain = "tesla.com"
    logo = manager.get_logo_url(domain)
    ip_info = await manager.get_ip_info()
    
    print(f"Logo URL for {domain}: {logo}")
    print(f"Current IP Location: {ip_info.get('city')}, {ip_info.get('country_name')}\n")
    
    print("--- Demo Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
