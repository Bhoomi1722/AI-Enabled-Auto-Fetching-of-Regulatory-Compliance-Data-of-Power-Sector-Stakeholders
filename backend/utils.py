import logging
import os
from pathlib import Path
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    pass

def cleanup_file(filepath: str):
    try:
        os.remove(filepath)
        logger.info(f"Cleaned: {filepath}")
    except Exception:
        pass

def save_json(data: Dict, filename: str):
    path = Path(__file__).parent.parent / "data" / "extracted" / f"{filename}.json"
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved JSON: {path}")