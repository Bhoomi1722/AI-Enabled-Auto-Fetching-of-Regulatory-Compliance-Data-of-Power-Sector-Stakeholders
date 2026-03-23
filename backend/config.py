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
        "pdf_pages": ["https://cercind.gov.in/recent_orders.html"],
        "pdf_prefixes": [
            "/2026/Orders/",
            "/2026/ROP/",
            "/2026/hearing_schedule/",
            "/2026/technical_validation/",
            "/2026/Orders/",
        ],
        "fallback_pdfs": [
            "https://cercind.gov.in/2026/Orders/89-MP-2026.pdf",
            "https://cercind.gov.in/2026/Orders/46-TD-2026.pdf",
            "https://cercind.gov.in/2026/Orders/532-TT-2025.pdf",
            "https://cercind.gov.in/2026/Orders/857-TL-2025.pdf",
            "https://cercind.gov.in/2026/Orders/1-SM-2026.pdf",
            "https://cercind.gov.in/2026/Orders/66-TD-2026.pdf",
        ],
        "limit": 8,
    },
    "CEA": {
        "base_url": "https://cea.nic.in/",
        "pdf_pages": [],
        "pdf_prefixes": [
            "/wp-content/uploads/notification/2026/",
            "/wp-content/uploads/notification/2025/",
            "/wp-content/uploads/rpm_division/2026/",
            "/wp-content/uploads/psp___a_ii/2026/",
        ],
        "fallback_pdfs": [
            "https://cea.nic.in/wp-content/uploads/notification/2026/03/Invitation_of_public_comment_on_Draft_Central_Electricity_Authority_Installation_and_Operation_of_Meters_Amendment_Regulations_2026_last_date_of_submission___26.03.2026.pdf",
            "https://cea.nic.in/wp-content/uploads/notification/2026/01/Roadmap_to_100_GW_of_Hydro_Pumped_Storage_Projects-2.pdf",
            "https://cea.nic.in/wp-content/uploads/notification/2026/01/Final_Type_Test_Guidelines_2026.pdf",
            "https://cea.nic.in/wp-content/uploads/notification/2026/02/Letter_to_GFM_Manufactureres.pdf",
            "https://cea.nic.in/wp-content/uploads/notification/2026/01/CEA_letter_dated_24.02.2026_to_Utilities_for_specifying_Std_rating_of_Tx.pdf",
        ],
        "limit": 8,
    }
}

TEXT_THRESHOLD_CHARS = 150
OCR_LANG = "eng"
OCR_PREPROCESS_DENOISE_KERNEL = 3