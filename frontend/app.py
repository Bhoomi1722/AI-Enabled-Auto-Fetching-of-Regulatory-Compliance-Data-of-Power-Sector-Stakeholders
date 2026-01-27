import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
import streamlit as st
from backend.fetcher import fetch_recent_pdfs, download_pdf
from backend.pdf_processor import PDFProcessor
from backend.utils import save_json
import time

st.set_page_config(page_title="AI Regulatory Compliance Fetcher", layout="wide")
st.title("AI-Enabled Regulatory Compliance Data Fetcher")
st.markdown("**Power Sector – CEA & CERC** (20% Prototype)")

if st.button("Fetch Latest Regulatory PDFs (CEA & CERC)", type="primary"):
    with st.spinner("Fetching & Processing..."):
        processor = PDFProcessor()
        results = []

        for source in ["CEA", "CERC"]:
            links = fetch_recent_pdfs(source)
            for url in links[:2]:  # limit for demo
                path = download_pdf(url)
                if path:
                    data = processor.process_pdf(path)
                    results.append(data)
                    # Save extracted
                    save_json(data, data["filename"].replace(".pdf", ""))

        if results:
            st.success(f"Processed {len(results)} documents")

            tab1, tab2 = st.tabs(["📊 Compliance Overview", "📄 Raw Extracts"])

            with tab1:
                st.subheader("Dummy Structured Compliance")
                for r in results:
                    with st.expander(r["filename"]):
                        st.json(r["structured"])

            with tab2:
                for r in results:
                    with st.expander(f"{r['filename']} – {r['source'].upper()}"):
                        st.write(f"**Preview (first 400 chars):**")
                        st.code(r["text_preview"])
        else:
            st.warning("No PDFs found or download failed.")

st.caption("20% complete • Fetch + Extract pipeline • Ready for LLM integration")