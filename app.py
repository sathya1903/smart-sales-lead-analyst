"""
app.py
Streamlit UI for the Smart Sales Lead Analyst.
Provides PDF ingestion, natural language querying, and ranked lead display.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ingest import ingest_pdfs, PDF_DIR
from agent import analyze_leads
from vectorstore import is_vectorstore_populated, get_all_lead_names
from utils import parse_lead_scores, score_to_color


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart Sales Lead Analyst",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .lead-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 5px solid #7c3aed;
    }
    .score-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
        color: white;
    }
    .rank-number {
        font-size: 2rem;
        font-weight: 900;
        color: #7c3aed;
        margin-right: 12px;
    }
    .signal-bullet {
        padding: 4px 0;
        color: #a0aec0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/target.png", width=64)
    st.title("🎯 Sales Lead Analyst")
    st.markdown("---")

    st.markdown("### ⚙️ Configuration")

    api_key = st.text_input(
        "OPEN_API_KEY",
        type="password",
        value=os.getenv("OPEN_API_KEY", ""),
        help="Required to run analysis. Set in .env or enter here.",
    )
    if api_key:
        os.environ["OPEN_API_KEY"] = api_key

    st.markdown("---")
    st.markdown("### 📁 Data Status")

    populated = is_vectorstore_populated()
    if populated:
        st.success("✅ Vector DB loaded")
        lead_names = get_all_lead_names()
        if lead_names:
            st.markdown(f"**{len(lead_names)} leads found:**")
            for name in lead_names:
                st.markdown(f"- {name}")
    else:
        st.warning("⚠️ No data in Vector DB\nProcess PDFs to begin.")

    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown("""
1. Place PDF transcripts in `data/pdfs/`
2. Click **Process PDFs**
3. Ask your question
4. Agent searches transcripts + LinkedIn data
5. Get ranked leads with scores
    """)


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("🎯 Smart Sales Lead Analyst")
st.markdown(
    "AI-powered analysis of sales call transcripts to identify your **hottest leads** "
    "and predict who will close **within the next month**."
)

st.markdown("---")

# --- Ingestion Section ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📂 Step 1: Process Sales Transcripts")
    st.markdown(
        f"Place your PDF transcripts in `{PDF_DIR}` then click the button below. "
        "The system will extract text, chunk it, embed it, and store it in ChromaDB."
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    process_btn = st.button("⚡ Process PDFs", use_container_width=True)

if process_btn:
    if not os.getenv("OPEN_API_KEY"):
        st.error("❌ Please enter your Open API key in the sidebar first.")
    elif not os.path.exists(PDF_DIR) or not any(
        f.endswith(".pdf") for f in os.listdir(PDF_DIR)
    ):
        st.error(f"❌ No PDF files found in `{PDF_DIR}`. Please add transcripts first.")
    else:
        with st.spinner("🔄 Processing PDFs... this may take a minute..."):
            try:
                count = ingest_pdfs(PDF_DIR)
                st.success(f"✅ Processed and stored **{count} chunks** from your PDF transcripts!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Ingestion failed: {str(e)}")

st.markdown("---")

# --- Query Section ---
st.markdown("### 💬 Step 2: Ask Your Question")

default_question = "Which leads are most likely to buy in the next month? Rank them with scores."

question = st.text_area(
    "Manager's Question",
    value=default_question,
    height=80,
    help="Ask about leads, buying signals, or any specific concerns.",
)

analyze_btn = st.button("🔍 Analyze Leads", use_container_width=False)

if analyze_btn:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ Please enter your OpenAI API key in the sidebar first.")
    elif not is_vectorstore_populated():
        st.error("❌ No transcript data found. Please process your PDFs first.")
    elif not question.strip():
        st.error("❌ Please enter a question.")
    else:
        with st.spinner("🤖 Agent is analyzing transcripts and enriching with LinkedIn data..."):
            try:
                # Show live thought process in expander
                with st.expander("🔬 Agent Reasoning Log", expanded=False):
                    raw_output_placeholder = st.empty()

                raw_output = analyze_leads(question)

                # Display raw output in expander
                with st.expander("📄 Raw Agent Output", expanded=False):
                    st.text(raw_output)

                st.markdown("---")
                st.markdown("### 🏆 Ranked Lead Analysis")

                # Try structured parsing first
                leads = parse_lead_scores(raw_output)

                if leads:
                    for lead in leads:
                        score = lead["score"]
                        color = score_to_color(score)

                        st.markdown(
                            f"""
                            <div class="lead-card">
                                <div style="display:flex; align-items:center; margin-bottom:10px;">
                                    <span class="rank-number">#{lead['rank']}</span>
                                    <div>
                                        <span style="font-size:1.4rem; font-weight:700; color:#f1f5f9;">
                                            {lead['name']}
                                        </span><br>
                                        <span class="score-badge" style="background:{color};">
                                            Confidence: {score}/100
                                        </span>
                                    </div>
                                </div>
                                <div style="margin-top:10px;">
                                    {"".join(f'<div class="signal-bullet">• {r}</div>' for r in lead["reasoning"])}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    # Fallback: display the raw output cleanly
                    st.markdown(
                        f"""
                        <div class="lead-card">
                            <div style="white-space: pre-wrap; color: #e2e8f0; line-height: 1.6;">
                                {raw_output}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("---")
                st.caption(
                    "⚠️ Scores are AI-generated estimates based on transcript signals and simulated LinkedIn data. "
                    "Always apply human judgment before acting on recommendations."
                )

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.exception(e)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:0.85rem;'>"
    "Smart Sales Lead Analyst · Built with LangChain, ChromaDB, OpenAI & Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
