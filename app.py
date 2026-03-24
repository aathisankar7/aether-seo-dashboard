import streamlit as st
import asyncio
import json
import os
import sys
from datetime import datetime
import pandas as pd

# Path setup for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from agents.seo_expert_agent import SEOExpertAgent
from agents.seo_automator import LocalSEOAutomator
from agents.bulk_content_generator import BulkContentGenerator

# Page Config
st.set_page_config(page_title="Ritz Elite SEO Master Suite", page_icon="🥷", layout="wide")

# Theme Definitions
THEMES = {
    "Midnight Neon": {
        "bg": "#0e1117",
        "accent": "#ff4b4b",
        "card": "#1a1c24",
        "stat_border": "#ff4b4b"
    },
    "Cyberpunk Gold": {
        "bg": "#000000",
        "accent": "#fbc02d",
        "card": "#121212",
        "stat_border": "#fbc02d"
    },
    "Emerald Glass": {
        "bg": "#051612",
        "accent": "#00ffa3",
        "card": "#0a241f",
        "stat_border": "#00ffa3"
    },
    "Slate Minimalism": {
        "bg": "#1e293b",
        "accent": "#38bdf8",
        "card": "#334155",
        "stat_border": "#38bdf8"
    }
}

# Sidebar Theme Selector
st.sidebar.subheader("🎨 Visual Persona")
selected_theme = st.sidebar.selectbox("Select Theme", list(THEMES.keys()))
theme = THEMES[selected_theme]

# Premium CSS Injection
st.markdown(f"""
    <style>
    .main {{ background-color: {theme['bg']}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; white-space: pre-wrap; background-color: {theme['card']}; border-radius: 5px 5px 0 0; padding: 10px 20px; transition: 0.3s; }}
    .stTabs [aria-selected="true"] {{ background-color: {theme['accent']}; color: white; }}
    .stat-card {{ background-color: {theme['card']}; padding: 20px; border-radius: 10px; border-left: 5px solid {theme['accent']}; }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: {theme['bg']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🥷 Ritz SEO Master")
st.sidebar.markdown("---")
mode = st.sidebar.radio("Command Mode", ["Strategic Audit", "Technical Turbo", "Bulk Content Gen"])

st.sidebar.markdown("---")
st.sidebar.subheader("AI Arsenal Status")
st.sidebar.success("✅ Multi-Model Race Active")
st.sidebar.info("Providers: Groq, Cerebras, SambaNova, Routeway (GLM-4.5), Ollama")

# Global State
if 'logs' not in st.session_state: st.session_state.logs = []

def log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# Content Area
if mode == "Strategic Audit":
    st.title("🚀 Elite Strategic Audit")
    target_url = st.text_input("Target URL", "https://cosmosclinics.in/")
    if st.button("🔥 EXECUTE STRATEGIC INFUSION"):
        agent = SEOExpertAgent()
        agent.on_log(log)
        with st.status("🔍 Analyzing DNA & Competitors...", expanded=True) as status:
            report = asyncio.run(agent.full_audit(target_url))
            status.update(label="✅ Audit Complete", state="complete")
        
        # Display Results
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Brand DNA")
            st.json(report['strategic_profile'])
        with col2:
            st.subheader("Keywords")
            st.json(report['keywords'])
            
        st.subheader("⚔️ Competitor Battle Sheets")
        for comp in report['competitor_intelligence']:
            with st.expander(f"Competitor: {comp['url']}"):
                st.markdown(comp['battle_sheet'])

elif mode == "Technical Turbo":
    st.title("⚡ Technical Turbo Audit")
    target_url = st.text_input("Target URL", "https://cosmosclinics.in/")
    if st.button("🛠️ START TECHNICAL SCAN"):
        automator = LocalSEOAutomator([target_url])
        with st.status("🏗️ Running Lighthouse & AI Interpretation...", expanded=True) as status:
            st.write("Extracting technical metrics...")
            results = asyncio.run(automator.run_all())
            status.update(label="✅ Technical Audit Ready", state="complete")
            
        st.subheader("Expert Interpretation")
        st.markdown(results.get(target_url, "No data."))

elif mode == "Bulk Content Gen":
    st.title("📝 Parallel Content Infusion")
    cat = st.selectbox("Category", ["Dental", "Medical", "Tech", "Real Estate"])
    count = st.slider("Number of Posts", 1, 10, 3)
    
    if st.button("🏗️ MANUFACTURE CONTENT"):
        tracker = os.path.join(project_root, "cosmos_marketing_tracker.xlsx")
        generator = BulkContentGenerator(tracker)
        with st.status("🤖 AI Production Line Running...", expanded=True) as status:
            posts = asyncio.run(generator.run_parallel(count=count))
            status.update(label="✅ Content Ready", state="complete")
            
        for post in posts:
            with st.expander(f"Post: {post['keyword']}"):
                st.info(f"Saved to: {post['file']}")
                # We could read and show it here
                
# Logs Footer
st.markdown("---")
st.subheader("⚙️ Mission Logs")
st.code("\n".join(st.session_state.logs[-10:]))
