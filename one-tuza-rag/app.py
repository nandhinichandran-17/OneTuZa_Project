# app.py
import streamlit as st
from ingest import ingest_local_documents
from vectorstore import VectorStore
from web_search import web_retrieve
from planner import simple_plan
from synthesizer import build_report
import os
import time

st.set_page_config(page_title="OneTuZa RAG Research Agent", layout="wide")

# ------------------- Styled Main Header -------------------
st.markdown(
    """
    <div style="background: linear-gradient(90deg,#4e54c8,#8f94fb);
                padding: 25px; border-radius: 12px; color: white; text-align:center;">
        <h1 style="margin:0;">OneTuZa — Multi-Document Research Agent</h1>
        <p style="margin-top:5px;font-size:16px;">RAG + Planning for professional research reports</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- Sidebar Settings ----------------
st.sidebar.header("Settings")
docs_folder = st.sidebar.text_input("Local docs folder", "docs/")
top_k_local = st.sidebar.slider("Top-k local chunks", 1, 10, 5)
top_k_web = st.sidebar.slider("Top-k web results", 1, 5, 3)
use_existing_index = st.sidebar.checkbox(
    "Use prebuilt FAISS index (faiss.index)", value=False
)
build_index_btn = st.sidebar.button("(Re)build index now")

# ---------------- Build / Load Vectorstore ----------------
if "vs" not in st.session_state:
    st.session_state.vs = None

if build_index_btn or st.session_state.vs is None:
    with st.spinner("Ingesting local docs and building vector store..."):
        chunks = ingest_local_documents(docs_folder)
        vs = VectorStore()
        if chunks:
            vs.build(chunks)
            vs.save("faiss.index")
            st.session_state.vs = vs
            st.success(f"Built index with {len(chunks)} chunks.")
        else:
            st.warning("No chunks found in docs folder. Please add PDFs/MDs to `docs/`.")
else:
    if use_existing_index and os.path.exists("faiss.index"):
        vs = VectorStore()
        vs.load("faiss.index")
        st.session_state.vs = vs
    elif st.session_state.vs is None:
        if os.path.exists("faiss.index"):
            vs = VectorStore()
            vs.load("faiss.index")
            st.session_state.vs = vs
        else:
            st.info("No vector store found. Click '(Re)build index now' to ingest docs.")
            st.stop()
    else:
        vs = st.session_state.vs

# ------------------- Main Workflow -------------------
st.markdown("## 🔹 Enter Research Question")
question = st.text_area(
    "Your question:",
    height=120,
    value=""
)

if st.button("Run Research Agent"):
    if not question.strip():
        st.error("Please enter a research question.")
    else:
        # --- Planning ---
        with st.spinner("Planning research steps..."):
            plan = simple_plan(question)
            time.sleep(0.3)
        st.markdown("### 📝 Research Plan")
        for i, p in enumerate(plan):
            st.markdown(f"{i+1}. {p}")

        # --- Retrieval Results Layout ---
        col1, col2 = st.columns(2)

        # Local Retrieval
        with col1:
            st.markdown("### 📄 Local Document Results")
            with st.spinner("Retrieving local documents..."):
                progress_local = st.progress(0)
                local_hits = vs.query(question, top_k=top_k_local)
                for i in range(101):
                    progress_local.progress(i)
                    time.sleep(0.01)

            for h in local_hits:
                st.markdown(
                    f"""
                    <div style="box-shadow:0 2px 6px rgba(0,0,0,0.1); padding:10px; border-radius:8px; margin-bottom:8px;">
                        <strong>{h['source']}</strong> — Score: {h['score']:.3f}<br>
                        <details><summary>Snippet</summary>{h['text']}</details>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Web Retrieval
        with col2:
            st.markdown("### 🌐 Web Search Results")
            with st.spinner("Searching web sources..."):
                progress_web = st.progress(0)
                web_hits = web_retrieve(question, max_results=top_k_web)
                for i in range(101):
                    progress_web.progress(i)
                    time.sleep(0.01)

            for w in web_hits:
                title = w.get("title") or w.get("source")
                st.markdown(
                    f"""
                    <div style="box-shadow:0 2px 6px rgba(0,0,0,0.1); padding:10px; border-radius:8px; margin-bottom:8px;">
                        <strong>{title}</strong><br>
                        <details><summary>Snippet</summary>{w['text']}</details>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # --- Synthesis ---
        st.markdown("## 🖋️ Synthesizing Final Report")
        with st.spinner("Building structured report..."):
            report = build_report(question, plan, local_hits, web_hits)
            time.sleep(0.3)

        # Tabs for Report
        tab1, tab2, tab3 = st.tabs(["Summary", "Traceability", "Export"])
        with tab1:
            st.markdown(report["summary_markdown"])
        with tab2:
            for c in report["citations"]:
                st.markdown(f"- **{c['label']}**: {c['source_text_snippet']}")
        with tab3:
            st.download_button(
                label="Download Markdown",
                data=report["summary_markdown"],
                file_name="report.md",
                mime="text/markdown"
            )
