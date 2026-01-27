import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import List, Tuple
from backend.config import OCR_LANG, OCR_PREPROCESS_DENOISE_KERNEL
from backend.utils import logger

class OCRHandler:
    def preprocess_image(self, pil_image) -> np.ndarray:
        img = np.array(pil_image)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Advanced preprocessing pipeline
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, OCR_PREPROCESS_DENOISE_KERNEL)
        gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1, 1), np.uint8)
        gray = cv2.dilate(gray, kernel, iterations=1)
        gray = cv2.erode(gray, kernel, iterations=1)
        logger.debug("Image preprocessing completed")
        return gray

    def perform_ocr(self, image) -> str:
        try:
            preprocessed = self.preprocess_image(image)
            text = pytesseract.image_to_string(preprocessed, lang=OCR_LANG, config='--psm 6')
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed on page: {e}")
            return ""

    def ocr_pdf_pages(self, images) -> List[Tuple[int, str]]:
        pages_text = []
        for idx, img in enumerate(images):
            logger.info(f"Performing OCR on page {idx+1}/{len(images)}")
            text = self.perform_ocr(img)
            pages_text.append((idx + 1, text))
        return pages_text