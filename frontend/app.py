# ======================================
# app.py  (Streamlit main)
# ======================================
import streamlit as st
import pandas as pd
from backend.fetcher import fetch_recent_pdfs, download_pdf
from backend.pdf_processor import PDFProcessor
from backend.utils import save_json, logger
from backend.compliance_extractor import extract_compliance_obligations

st.set_page_config(page_title="AI Regulatory Compliance Fetcher", layout="wide")
st.title("AI-Enabled Auto Fetching of Regulatory Compliance – Power Sector")
st.markdown("**CEA & CERC** • ~50% Prototype • Fetch + Extract + Structured Obligations")

if st.button("Fetch & Process Latest PDFs (CEA + CERC)", type="primary"):
    with st.spinner("Fetching recent PDFs and extracting obligations..."):
        processor = PDFProcessor()
        all_results = []
        all_obligations = []
        
        for source in ["CERC", "CEA"]:
            st.write(f"Processing {source}...")
            urls = fetch_recent_pdfs(source)
            
            for url in urls[:4]:  # limit per source
                path = download_pdf(url)
                if not path:
                    continue
                
                data = processor.process_pdf(path)
                data["source_name"] = source
                all_results.append(data)
                
                # Save per file
                save_json(data, data["filename"].replace(".pdf", ""))
                
                all_obligations.extend([
                    {**ob, "filename": data["filename"], "source": source}
                    for ob in data["obligations"]
                ])
        
        if all_results:
            st.success(f"Processed {len(all_results)} documents • Found {len(all_obligations)} potential obligations")
            
            tab1, tab2, tab3 = st.tabs(["📊 Obligations Table", "📄 Document Previews", "🔧 Raw Data"])
            
            with tab1:
                if all_obligations:
                    df = pd.DataFrame(all_obligations)
                    st.subheader("Extracted Compliance Obligations")
                    st.dataframe(
                        df[["filename", "source", "section", "obligation", "keywords", "confidence"]],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download All Obligations as CSV",
                        data=csv,
                        file_name="power_sector_compliance_obligations.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No obligations detected yet — patterns need tuning or LLM next.")
            
            with tab2:
                for res in all_results:
                    with st.expander(f"{res['filename']}  ({res['source_name']}) – {res['obligations_count']} obligations"):
                        st.write("**Text preview (first 500 chars):**")
                        st.code(res["preview"])
                        if res["obligations"]:
                            st.write("**Detected obligations:**")
                            for ob in res["obligations"]:
                                st.markdown(f"**{ob['section']}** – {ob['obligation'][:150]}...")
            
            with tab3:
                st.json(all_results)
        else:
            st.warning("No PDFs could be fetched or processed. Check logs / network.")

st.caption("50% Milestone • Reliable fetch + sentence-level obligation detection + table + export • Ready for LLM/OCR polish")