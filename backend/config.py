# ======================================
# backend/config.py
# ======================================
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR = DATA_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
JSON_DIR = DATA_DIR / "extracted"
JSON_DIR.mkdir(exist_ok=True)

SOURCES = {
    "CERC": {
        "base_url": "https://cercind.gov.in/",
        "pdf_prefixes": ["/2026/Orders/", "/2026/hearing_schedule/", "/2026/technical_validation/"],
        "fallback_pdfs": [
            "https://cercind.gov.in/2026/Orders/78-MP-2023.pdf",
            "https://cercind.gov.in/2026/Orders/211-TT-2024.pdf",
            "https://cercind.gov.in/2026/Orders/498-TT-2025.pdf",
            "https://cercind.gov.in/2026/Orders/310-AT-2025.pdf",
        ],
        "limit": 5,
    },
    "CEA": {
        "base_url": "https://cea.nic.in/",
        "pdf_prefixes": ["/wp-content/uploads/notification/2026/", "/wp-content/uploads/notification/2025/"],
        "fallback_pdfs": [
            "https://cea.nic.in/wp-content/uploads/notification/2026/01/Final_Type_Test_Guidelines_2026.pdf",
            "https://cea.nic.in/wp-content/uploads/notification/2026/01/CEA_letter_dated_24.02.2026_to_Utilities_for_specifying_Std_rating_of_Tx.pdf",
            "https://cea.nic.in/wp-content/uploads/notification/2026/02/Letter_to_GFM_Manufactureres.pdf",
        ],
        "limit": 5,
    }
}

TEXT_THRESHOLD_CHARS = 150
OCR_LANG = "eng"
OCR_PREPROCESS_DENOISE_KERNEL = 3