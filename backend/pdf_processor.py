import pdfplumber
from pathlib import Path
from typing import Dict

from backend.config import TEXT_THRESHOLD_CHARS
from backend.utils import logger
from backend.compliance_extractor import extract_compliance_obligations
from pdf2image import convert_from_path
from backend.ocr_handler import OCRHandler

class PDFProcessor:
    def is_text_based(self, pdf_path: str) -> bool:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = "".join(page.extract_text() or "" for page in pdf.pages)
                avg = len(text.strip()) / max(1, len(pdf.pages))
                return avg > TEXT_THRESHOLD_CHARS
        except Exception as e:
            logger.error(f"PDF type check failed: {e}")
            return False

    def extract_text(self, pdf_path: str) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return "".join(page.extract_text() or "" for page in pdf.pages).strip()
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""

    def process_pdf(self, pdf_path: str) -> Dict:
        filename = Path(pdf_path).name
        text = ""
        source_type = "unknown"

        try:
            if self.is_text_based(pdf_path):
                text = self.extract_text(pdf_path)
                source_type = "text"
            else:
                images = convert_from_path(pdf_path, dpi=300)
                ocr_handler = OCRHandler()
                pages = ocr_handler.ocr_pdf_pages(images)
                text = "\n\n".join([f"[Page {pg}]\n{txt}" for pg, txt in pages if txt.strip()])
                source_type = "ocr"

        except Exception as e:
            logger.error(f"Full extraction failed for {filename}: {e}")
            text = f"[Extraction error: {str(e)}]"
            source_type = "error"

        obligations = extract_compliance_obligations(text)

        structured = {
            "filename": filename,
            "source_type": source_type,
            "text_length": len(text),
            "obligations_count": len(obligations),
            "obligations": obligations,
            "preview": text[:800] + "..." if len(text) > 800 else text
        }
        return structured