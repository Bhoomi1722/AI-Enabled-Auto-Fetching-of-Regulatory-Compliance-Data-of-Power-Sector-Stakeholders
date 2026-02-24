import logging
from pathlib import Path
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

JSON_DIR = Path(__file__).parent.parent / "data" / "extracted"

def save_json(data: dict, filename: str):
    path = JSON_DIR / f"{filename}.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved JSON: {path}")
    except Exception as e:
        logger.error(f"Failed to save JSON {path}: {e}")

def cleanup_file(filepath: str):
    try:
        Path(filepath).unlink()
        logger.info(f"Cleaned up: {filepath}")
    except Exception:
        pass