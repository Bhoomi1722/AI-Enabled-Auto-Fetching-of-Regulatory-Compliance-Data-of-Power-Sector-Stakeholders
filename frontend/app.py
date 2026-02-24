import streamlit as st
import pandas as pd
import json
from pathlib import Path

from backend.fetcher import fetch_recent_pdfs, download_pdf
from backend.pdf_processor import PDFProcessor
from backend.utils import save_json, logger, JSON_DIR
from backend.compliance_extractor import extract_compliance_obligations

st.set_page_config(page_title="AI Regulatory Compliance Dashboard", layout="wide")

# ── Title & Description ─────────────────────────────────────────────────────────
st.title("📊 AI-Enabled Regulatory Compliance Dashboard")
st.markdown("**Power Sector – CEA & CERC** • Auto-fetch, extract obligations, analyze & export")
st.caption("Progress: ~70% • Interactive view + filters + summary • Ready for LLM/OCR next")

# ── Sidebar Controls ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls & Session")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Fetch Latest", type="primary", use_container_width=True):
            st.session_state["fetch_triggered"] = True
            # Optional: also clear previous loaded data when fetching new
            if "loaded_data" in st.session_state:
                del st.session_state["loaded_data"]
    
    with col_btn2:
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            keys_to_clear = [
                "all_results",
                "all_obligations",
                "loaded_data",
                "fetch_triggered"
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Session history cleared")
            st.rerun()   # force refresh to show empty state immediately

    st.divider()
    
    # Filters (if you have them)
    selected_sources = st.multiselect("Sources", ["CERC", "CEA"], default=["CERC", "CEA"])
    min_confidence = st.select_slider("Min Confidence", ["low", "medium", "high"], value="low")
    
    st.divider()
    
    st.subheader("Previously Processed")
    prev_files = sorted(JSON_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if prev_files:
        selected_file = st.selectbox(
            "Load old result",
            options=[f.name for f in prev_files[:10]],
            index=None,
            placeholder="Select a saved file..."
        )
        
        if selected_file:
            file_path = JSON_DIR / selected_file
            try:
                with open(file_path, encoding="utf-8") as f:
                    old_data = json.load(f)
                st.session_state["loaded_data"] = old_data
                st.success(f"Loaded: {selected_file}")
            except Exception as e:
                st.error(f"Failed to load file: {e}")
    else:
        st.info("No saved files yet")

# ── Main Area ───────────────────────────────────────────────────────────────────
if "all_results" not in st.session_state:
    st.session_state["all_results"] = []
if "all_obligations" not in st.session_state:
    st.session_state["all_obligations"] = []

# Trigger fetch if button pressed
if st.session_state.get("fetch_triggered", False):
    with st.spinner("Fetching & processing latest regulatory PDFs..."):
        processor = PDFProcessor()
        new_results = []
        new_obligations = []
        
        for source in ["CERC", "CEA"]:
            st.write(f"→ Processing {source}...")
            urls = fetch_recent_pdfs(source)
            
            for url in urls[:5]:  # adjustable limit
                path = download_pdf(url)
                if not path:
                    st.warning(f"Download skipped: {url}")
                    continue
                
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
                    st.error(f"Error processing {Path(path).name}: {e}")
        
        if new_results:
            st.session_state["all_results"] = new_results
            st.session_state["all_obligations"] = new_obligations
            st.success(f"Done! {len(new_results)} documents • {len(new_obligations)} obligations found")
        else:
            st.warning("No new documents processed. Using previous data if available.")
    
    st.session_state["fetch_triggered"] = False  # reset trigger

# ── Display Results (new or loaded) ─────────────────────────────────────────────
data_source = st.session_state.get("all_obligations", [])
if "loaded_data" in st.session_state:
    # Optional: merge or override with loaded
    st.info("Showing loaded historical data")
    # For simplicity we show loaded obligations if present
    if "obligations" in st.session_state["loaded_data"]:
        data_source = [
            {**ob, "filename": st.session_state["loaded_data"]["filename"], "source": "loaded"}
            for ob in st.session_state["loaded_data"].get("obligations", [])
        ]

if data_source:
    df = pd.DataFrame(data_source)

    # ── KPI Cards ───────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documents Processed", len(st.session_state.get("all_results", [])))
    with col2:
        st.metric("Total Obligations", len(df))
    with col3:
        st.metric("High Confidence", len(df[df["confidence"] == "high"]))
    with col4:
        st.metric("Sources Covered", df["source"].nunique())

    st.divider()

    # ── Search & Filter ─────────────────────────────────────────────────────────
    search_term = st.text_input("🔍 Search obligations / filename / section", "")
    if search_term:
        mask = df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)
        df = df[mask]

    # ── Interactive Table ───────────────────────────────────────────────────────
    st.subheader("Compliance Obligations Overview")

    st.dataframe(
        df[["filename", "source", "section", "obligation", "keywords", "confidence"]],
        hide_index=True,
        use_container_width=True,           # still ok in early 2026 – change to width="stretch" later
        column_config={
            "obligation": st.column_config.TextColumn(
                "Obligation Text",
                width="large",
                help="Extracted compliance sentence"
            ),
            "confidence": st.column_config.SelectboxColumn(
                "Confidence",
                options=["high", "medium", "low"],
                required=True
            ),
            "section": st.column_config.TextColumn("Section / Clause")
        }
    )

    # CSV Export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download All as CSV",
        csv,
        "compliance_obligations.csv",
        "text/csv",
        use_container_width=False
    )

    # ── Detailed Previews ───────────────────────────────────────────────────────
    with st.expander("📄 Document Previews & Details", expanded=False):
        for res in st.session_state.get("all_results", []):
            with st.container(border=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**{res['filename']}** ({res['source_name']}) – {res['obligations_count']} obligations")
                    st.caption(f"Type: {res['source_type']} • Text length: {res['text_length']:,} chars")
                with cols[1]:
                    if res["obligations"]:
                        st.metric("Detected", res["obligations_count"])

                st.markdown("**Preview (first 600 chars):**")
                st.code(res["preview"], language=None)

                if res["obligations"]:
                    st.markdown("**Sample obligations:**")
                    for ob in res["obligations"][:3]:  # show first 3
                        st.markdown(f"**{ob['section']}** – {ob['obligation'][:220]}...")

else:
    st.info("No data yet. Click 'Fetch & Process Latest' to start.")
    st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=200)  # optional fun placeholder

st.divider()
st.caption("Dashboard improvements • Summary metrics • Search • Filters • History • Better visuals")