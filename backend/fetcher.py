import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from backend.config import SOURCES, DOWNLOAD_DIR
from backend.utils import logger

def fetch_recent_pdfs(source_name: str = "CERC") -> list[str]:
    if source_name not in SOURCES:
        raise ValueError("Unknown source")
    
    config = SOURCES[source_name]
    base_url = config["base_url"]
    pdf_links = []
    
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
    
    for prefix in config.get("pdf_prefixes", []):
        try:
            list_url = urljoin(base_url, prefix)
            resp = session.get(list_url, headers=headers, timeout=15, verify=False)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().endswith(".pdf"):
                    full = urljoin(list_url, href)
                    pdf_links.append(full)
        except Exception as e:
            logger.warning(f"Failed to scrape {prefix}: {e}")
    
    if not pdf_links:
        pdf_links = config.get("fallback_pdfs", [])[:config["limit"]]
        logger.info(f"Using fallback PDFs for {source_name}")
    else:
        pdf_links = pdf_links[:config["limit"]]
    
    logger.info(f"{source_name}: Collected {len(pdf_links)} PDF URLs")
    return pdf_links


def download_pdf(url: str) -> str | None:
    try:
        filename = url.split("/")[-1]
        path = DOWNLOAD_DIR / filename
        if path.exists():
            logger.info(f"Already downloaded: {filename}")
            return str(path)
        
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        session.mount('https://', HTTPAdapter(max_retries=retries))
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
        
        resp = session.get(url, headers=headers, timeout=30, stream=True, verify=False)
        resp.raise_for_status()
        
        with open(path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        logger.info(f"Downloaded: {filename}")
        return str(path)
    except Exception as e:
        logger.error(f"Download failed {url}: {e}")
        return None