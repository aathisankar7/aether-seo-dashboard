import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LocalSEOContentGenerator:
    def __init__(self, ollama_endpoint="http://localhost:11434/api/generate", model="llama3"):
        self.endpoint = ollama_endpoint
        self.model = model

    def query_llama(self, prompt, system_prompt="You are a Senior SEO Content Strategist."):
        """Helper to contact the local Ollama instance."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.6 # slightly more creative for content
            }
        }
        try:
            response = requests.post(self.endpoint, json=payload, timeout=240)
            if response.status_code == 200:
                return response.json().get("response", "No response from model.")
            else:
                return f"❌ Error: Local Llama returned status code {response.status_code}"
        except Exception as e:
            return f"❌ Error: Could not connect to Ollama. {str(e)}"

    def generate_blog_post(self, topic, keywords, target_audience="Investors and Business Owners"):
        """Generates a high-quality, SEO-optimized blog post."""
        prompt = f"""
        Act as a Senior SEO Content Strategist for Ritz Group (ritzgroup.co).
        Write a comprehensive, engaging, and professional blog post on the topic: "{topic}".
        
        Target Audience: {target_audience}
        Primary Keywords: {', '.join(keywords)}
        
        Requirements:
        1. Compelling H1 Title.
        2. Introduction that hooks the reader and includes the primary keyword.
        3. 3-4 Subheaders (H2/H3) with relevant content.
        4. Detailed, insightful body text (500+ words).
        5. Internal linking suggestions to other Ritz Group services.
        6. A strong Call to Action (CTA) at the end.
        7. Optimized Meta Title and Meta Description (under 160 chars).
        
        Format the output in professional Markdown.
        """
        
        print(f"🦙 Generating blog post on: {topic} via Local Llama...")
        return self.query_llama(prompt)

    def generate_service_description(self, service_name, key_features):
        """Generates an SEO-friendly service page description."""
        prompt = f"""
        Write a high-converting, SEO-optimized service page description for "{service_name}".
        
        Key Features: {', '.join(key_features)}
        
        Requirements:
        - Benefit-driven copy (Why choose Ritz Group?).
        - Bullet points for key features.
        - Semantic keyword integration.
        - JSON-LD Schema snippet (Product/Service) for this service.
        
        Format the output in Markdown with a separate section for the JSON-LD script.
        """
        
        print(f"🦙 Generating service description for: {service_name} via Local Llama...")
        return self.query_llama(prompt)

if __name__ == "__main__":
    generator = LocalSEOContentGenerator()
    
    # Generate Blog Post
    blog_topic = "Why Painless Dentistry is the Future of Dental Care"
    keywords = ["Dental Clinic in Kukatpally", "Painless Dentistry", "Best Dental Clinics in Hyderabad", "Cosmos Clinics"]
    
    blog_content = generator.generate_blog_post(blog_topic, keywords, target_audience="Patients seeking anxiety-free dental care")
    
    os.makedirs("./seo_content", exist_ok=True)
    with open("./seo_content/cosmos_painless_dentistry_blog.md", "w") as f:
        f.write(blog_content)
    
    # Generate Service Page
    service_name = "Smile Makeovers at Cosmos Clinics"
    features = ["Digital Smile Design", "Painless Procedure", "Veneers and Aligners", "Expert Orthodontists"]
    
    service_content = generator.generate_service_description(service_name, features)
    
    with open("./seo_content/cosmos_smile_makeovers_service.md", "w") as f:
        f.write(service_content)
        
    print("✅ Cosmos Clinics Content Generated.")
