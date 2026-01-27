# AI-Enabled Auto Fetching of Regulatory Compliance Data of Power Sector Stakeholders

## Current Status – 20–25% Completion

### What has been implemented
- **Web scraping basics**  
  Fetching recent PDF/notification links from CEA and CERC homepages (using BeautifulSoup + requests with retries & browser-like headers)

- **PDF download & storage**  
  Downloads PDFs to `data/downloads/` folder (skips if already exists)

- **PDF type detection**  
  Automatically detects whether PDF is text-based (Unicode/digital) or image-based (scanned)

- **Text extraction**  
  - Direct text extraction from digital PDFs using `pdfplumber`  
  - OCR on scanned PDFs using Tesseract + OpenCV preprocessing

- **Basic structured output**  
  Placeholder JSON-like structure with filename, source type (text/ocr), text preview, and dummy compliance fields

- **Frontend dashboard**  
  Simple Streamlit interface to trigger fetching, show processing results, raw text previews, and dummy compliance table

- **Error handling & logging**  
  Basic logging + cleanup + exception catching

### What is still needed (remaining ~75–80%)
- **Real LLM integration**  
  Use open-source models (Mistral 7B, Phi-3, LLaMA-2 via Ollama/HuggingFace) to extract: compliance type, due dates, responsible entities, risk level, key clauses

- **Structured database storage**  
  Save extracted compliance data to MySQL / PostgreSQL / MongoDB instead of JSON files

- **Advanced scraping**  
  Use Scrapy or Playwright for robust crawling of multiple pages, handling pagination, JavaScript-rendered content, login-protected portals

- **Scheduled / periodic fetching**  
  Background job (APScheduler / Celery) to check for new documents daily/weekly

- **Compliance analytics dashboard**  
  Charts (Plotly/Chart.js): compliance status, upcoming deadlines, risk heatmaps, entity-wise filtering

- **Better OCR handling**  
  Support Indic languages if needed (hin/tel), fine-tune preprocessing, try IndicOCR or cloud OCR fallback

- **Authentication & security**  
  User login, role-based access, API key protection

- **Report generation**  
  PDF/Excel export of compliance summaries

- **Testing & evaluation**  
  Accuracy metrics for OCR + LLM, handling of large PDFs, edge cases (corrupted files, non-PDFs)

- **Deployment**  
  Dockerize, deploy on cloud (AWS/Heroku), production-grade error monitoring

## Project Structure
AI_Regulatory_Compliance/
├── frontend/
│   └── app.py                  # Streamlit dashboard
├── backend/
│   ├── init.py
│   ├── config.py
│   ├── fetcher.py             # Web scraping & download
│   ├── pdf_processor.py       # PDF type detection + extraction + OCR
│   ├── utils.py               # Helpers, logging, error handling
│   └── placeholder_llm.py     # Dummy for future LLM step
├── data/
│   ├── downloads/             # Downloaded PDFs
│   └── extracted/             # JSON files with extracted data
├── requirements.txt
└── README.md


## How to Run the Project

### 1. Prerequisites

- Python 3.9+
- Tesseract OCR installed + English language data  
  Windows: https://github.com/UB-Mannheim/tesseract/wiki  
  Ubuntu: `sudo apt install tesseract-ocr`  
  macOS: `brew install tesseract`

- Poppler (for pdf2image)  
  Windows: https://github.com/oschwartz10612/poppler-windows (add bin/ to PATH)  
  Ubuntu: `sudo apt install poppler-utils`  
  macOS: `brew install poppler`

### 2. Install dependencies

```bash
# Recommended: virtual environment
python -m venv venv
.\venv\Scripts\activate          # Windows
# or source venv/bin/activate    # Linux/macOS

pip install -r requirements.txt

# From project root folder
streamlit run frontend/app.py

python -m streamlit run frontend/app.py


Browser opens → http://localhost:8501
Click "Fetch Latest Regulatory PDFs (CEA & CERC)"
Watch logs in terminal for any scraping/download issues