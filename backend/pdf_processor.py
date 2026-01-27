import pdfplumber
from pdf2image import convert_from_path
from backend.config import TEXT_THRESHOLD_CHARS, OCR_LANG
from backend.ocr_handler import OCRHandler  # assume same as before or copy
from backend.utils import logger

class PDFProcessor:
    def __init__(self):
        self.ocr = OCRHandler()

    def is_text_based(self, pdf_path: str) -> bool:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_text = ""
                for page in pdf.pages:
                    total_text += page.extract_text() or ""
            avg = len(total_text.strip()) / max(1, len(pdf.pages))
            return avg > TEXT_THRESHOLD_CHARS
        except Exception as e:
            logger.error(f"Type check failed: {e}")
            return False

    def extract_text(self, pdf_path: str) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
                return full_text.strip()
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""

    def process_pdf(self, pdf_path: str) -> dict:
        source = "unknown"
        text = ""

        if self.is_text_based(pdf_path):
            text = self.extract_text(pdf_path)
            source = "text"
        else:
            images = convert_from_path(pdf_path, dpi=250)
            text = self.ocr.ocr_pages(images)
            source = "ocr"

        # Placeholder structured data (future LLM)
        structured = {
            "compliance_type": "Unknown",
            "due_date": "N/A",
            "entity": "Power Sector Stakeholders",
            "reference": pdf_path.split("/")[-1],
            "risk_level": "Low"
        }

        return {
            "filename": pdf_path.split("/")[-1],
            "source": source,
            "text_length": len(text),
            "text_preview": text,
            "structured": structured
        }