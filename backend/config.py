from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DOWNLOAD_DIR = DATA_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

JSON_DIR = DATA_DIR / "extracted"
JSON_DIR.mkdir(exist_ok=True)

# Official sources (from recent crawl)
SOURCES = {
    "CEA": {
        "url": "https://cea.nic.in/?lang=en",
        "news_selector": "div.elementor-widget-container a[href$='.pdf']",  # approximate
        "limit": 3
    },
    "CERC": {
        "url": "https://cercind.gov.in/",
        "news_selector": "a[href$='.pdf']",  # approximate
        "limit": 3
    }
}

TEXT_THRESHOLD_CHARS = 150
OCR_LANG = "eng"  # can add hin if needed later
OCR_PREPROCESS_DENOISE_KERNEL = 3
TEXT_BASED_THRESHOLD_CHARS = 150  # already there