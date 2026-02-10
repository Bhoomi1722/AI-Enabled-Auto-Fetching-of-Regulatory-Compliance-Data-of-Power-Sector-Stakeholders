# backend/pdf_processor.py

import pdfplumber
from pathlib import Path                  # ← ADD THIS LINE
from typing import Dict, List
from backend.config import TEXT_THRESHOLD_CHARS
from backend.utils import logger
# If you still have OCR parts, keep their imports here too
# from pdf2image import convert_from_path
# import pytesseract, cv2, numpy as np, etc.

from backend.compliance_extractor import extract_compliance_obligations   # assuming this exists

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
        filename = Path(pdf_path).name                 # ← this line now works
        text = self.extract_text(pdf_path) if self.is_text_based(pdf_path) else "[OCR would be here]"
        source_type = "text" if self.is_text_based(pdf_path) else "ocr"
        
        obligations = extract_compliance_obligations(text)
        
        structured = {
            "filename": filename,
            "source_type": source_type,
            "text_length": len(text),
            "obligations_count": len(obligations),
            "obligations": obligations,
            "preview": text[:400] + "..." if len(text) > 400 else text
        }
        
        return structured