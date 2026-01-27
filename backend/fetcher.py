import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from backend.config import SOURCES, DOWNLOAD_DIR
from backend.utils import logger

def fetch_recent_pdfs(source_name: str = "CEA") -> list:
    if source_name not in SOURCES:
        raise ValueError("Unknown source")

    config = SOURCES[source_name]
    url = config["url"]
    selector = config["news_selector"]

    # Improved session with retries + better headers
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    try:
        resp = session.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        pdf_links = []
        for a in soup.select(selector)[:config["limit"]]:
            href = a.get("href")
            if href and href.lower().endswith(".pdf"):
                full_url = urljoin(url, href)
                pdf_links.append(full_url)

        logger.info(f"{source_name}: Found {len(pdf_links)} PDF links")
        return pdf_links
    except requests.exceptions.RequestException as e:
        logger.error(f"Fetch failed for {source_name}: {e}")
        return []

def download_pdf(url: str) -> str:
    try:
        filename = url.split("/")[-1]
        path = DOWNLOAD_DIR / filename
        if path.exists():
            logger.info(f"Already exists: {filename}")
            return str(path)

        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        session.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        resp = session.get(url, headers=headers, timeout=30, stream=True)
        resp.raise_for_status()
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded: {filename}")
        return str(path)
    except requests.exceptions.RequestException as e:
        logger.error(f"Download failed {url}: {e}")
        return ""