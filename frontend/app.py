import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

from backend.fetcher import fetch_recent_pdfs, download_pdf
from backend.pdf_processor import PDFProcessor
from backend.utils import save_json, logger, JSON_DIR
from backend.compliance_extractor import extract_compliance_obligations
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="AI Regulatory Compliance Dashboard", layout="wide")

# Title
st.title("📊 AI-Enabled Regulatory Compliance Dashboard – Power Sector")
st.markdown("**CEA & CERC** • Auto-fetch • OCR • LLM-enhanced obligations • Charts • Export")
st.caption("100% Complete Prototype – Final Year Project 2026")

# Last updated timestamp
if "last_fetch_time" not in st.session_state:
    st.session_state["last_fetch_time"] = None

if st.session_state.get("last_fetch_time"):
    st.caption(f"**Last updated:** {st.session_state['last_fetch_time'].strftime('%Y-%m-%d %H:%M:%S IST')}")

# Sidebar
with st.sidebar:
    st.header("Controls & Session")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Fetch Latest", type="primary", use_container_width=True):
            st.session_state["fetch_triggered"] = True
            if "loaded_data" in st.session_state:
                del st.session_state["loaded_data"]
    
    with col2:
        if st.button("🗑️ Clear Session", type="secondary", use_container_width=True):
            for key in ["all_results", "all_obligations", "loaded_data", "fetch_triggered", "last_fetch_time"]:
                st.session_state.pop(key, None)
            st.success("Session cleared")
            st.rerun()

    st.divider()
    
    selected_sources = st.multiselect("Sources", ["CERC", "CEA", "All"], default=["All"])
    min_confidence = st.select_slider("Min Confidence", ["low", "medium", "high"], value="low")
    
    st.divider()
    
    st.subheader("Saved Results")
    prev_files = sorted(JSON_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if prev_files:
        selected_file = st.selectbox("Load saved result", [f.name for f in prev_files[:12]], index=None)
        if selected_file:
            try:
                with open(JSON_DIR / selected_file, encoding="utf-8") as f:
                    old = json.load(f)
                st.session_state["loaded_data"] = old
                st.success(f"Loaded: {selected_file}")
            except Exception as e:
                st.error(f"Load failed: {e}")
    else:
        st.info("No saved files")

    st.divider()
    st.subheader("Danger Zone")
    if st.button("🗑️ Delete ALL Saved Files", type="secondary", use_container_width=True):
        st.warning("This will **permanently delete** all saved JSON results!")
        confirm = st.checkbox("Yes, delete everything (cannot undo)")
        if confirm and st.button("CONFIRM DELETION", type="primary"):
            count = sum(1 for _ in JSON_DIR.glob("*.json") if _.unlink() is None)
            st.success(f"Deleted {count} files") if count else st.info("No files found")
            st.rerun()

# Main logic
if "all_results" not in st.session_state:
    st.session_state["all_results"] = []
if "all_obligations" not in st.session_state:
    st.session_state["all_obligations"] = []

if st.session_state.get("fetch_triggered", False):
    with st.spinner("Fetching & processing latest PDFs..."):
        processor = PDFProcessor()
        new_results = []
        new_obligations = []
        
        for source in ["CERC", "CEA"]:
            st.write(f"→ {source}...")
            urls = fetch_recent_pdfs(source)
            
            for url in urls:
                path = download_pdf(url)
                if not path: continue
                try:
                    data = processor.process_pdf(path)
                    data["source_name"] = source
                    new_results.append(data)
                    save_json(data, data["filename"].replace(".pdf", ""))
                    new_obligations.extend([
                        {**ob, "filename": data["filename"], "source": source}
                        for ob in data["obligations"]
                    ])
                except Exception as e:
                    st.warning(f"Skipped {Path(path).name}: {e}")
        
        if new_results:
            st.session_state["all_results"] = new_results
            st.session_state["all_obligations"] = new_obligations
            st.session_state["last_fetch_time"] = datetime.now()
            st.success(f"Processed {len(new_results)} documents • {len(new_obligations)} obligations")
        else:
            st.warning("No new documents. Using previous data.")

    st.session_state["fetch_triggered"] = False

# Display
data_source = st.session_state.get("all_obligations", [])
if "loaded_data" in st.session_state and "obligations" in st.session_state["loaded_data"]:
    st.info("Showing loaded historical data")
    data_source = [
        {**ob, "filename": st.session_state["loaded_data"]["filename"], "source": "loaded"}
        for ob in st.session_state["loaded_data"]["obligations"]
    ]

if data_source:
    df = pd.DataFrame(data_source)

    # Filters
    if "All" not in selected_sources:
        df = df[df["source"].isin(selected_sources)]
    if min_confidence == "medium":
        df = df[df["confidence"].isin(["high", "medium"])]
    elif min_confidence == "high":
        df = df[df["confidence"] == "high"]

    # KPIs
    cols = st.columns(4)
    cols[0].metric("Documents", len(st.session_state.get("all_results", [])))
    cols[1].metric("Obligations", len(df))
    cols[2].metric("High Confidence", len(df[df["confidence"] == "high"]))
    cols[3].metric("High Risk", len(df[df["risk_level"] == "High"]))

    st.divider()

    # Search
    search = st.text_input("🔍 Search (obligation / filename / section / summary)", "")
    if search:
        df = df[df.apply(lambda r: search.lower() in ' '.join(r.astype(str)).lower(), axis=1)]

    # Table
    st.subheader("Compliance Obligations (LLM Enhanced)")
    st.dataframe(
        df[["filename", "source", "section", "obligation", "short_summary", "compliance_type", "due_date", "affected_entity", "risk_level", "confidence"]],
        hide_index=True,
        use_container_width=True,
        column_config={
            "obligation": st.column_config.TextColumn("Obligation", width="large"),
            "short_summary": st.column_config.TextColumn("LLM Summary", width="medium"),
            "risk_level": st.column_config.TextColumn("Risk", width="small"),
            "due_date": st.column_config.TextColumn("Due", width="small"),
        }
    )

    # Export
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "obligations.csv", "text/csv")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("By Source")
        st.bar_chart(df["source"].value_counts())
    with c2:
        st.subheader("Risk Distribution")
        st.bar_chart(df["risk_level"].value_counts())

    # Previews
    with st.expander("Document Previews"):
        for res in st.session_state.get("all_results", []):
            with st.container(border=True):
                st.markdown(f"**{res['filename']}** ({res['source_name']}) – {res['obligations_count']} items")
                st.caption(f"{res['source_type']} • {res['text_length']:,} chars")
                st.code(res["preview"][:800], language=None)
                if res["obligations"]:
                    for ob in res["obligations"][:2]:
                        st.markdown(f"- **{ob['section']}** ({ob['risk_level']}) {ob['short_summary']}")

else:
    st.info("No data yet. Click 'Fetch Latest' to begin.")
    st.caption("Tip: First run may take longer due to Ollama model loading.")

st.divider()
st.caption("100% Complete • OCR • LLM • Charts • Timestamp • Safe Delete • Ready for Submission")