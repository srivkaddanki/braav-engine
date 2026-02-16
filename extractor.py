import os
from pypdf import PdfReader
from docx import Document
from logger import logger

class ChamchaExtractor:
    def __init__(self):
        self.ocr_reader = None  # Lazy-load on first use
    
    def _ensure_ocr_loaded(self):
        """Load OCR model only when needed"""
        if self.ocr_reader is None:
            logger.info("Loading EasyOCR (first use)...")
            import easyocr
            self.ocr_reader = easyocr.Reader(['en'])
            logger.info("EasyOCR ready")
    
    def extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        try:
            logger.info(f"Extracting text from {file_path}")
            if ext == ".pdf":
                reader = PdfReader(file_path)
                for page in reader.pages[:3]:
                    text += page.extract_text() + " "
            elif ext == ".docx":
                doc = Document(file_path)
                text = " ".join([p.text for p in doc.paragraphs[:20]])
            elif ext == ".txt":
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read(2000)
            elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
                # Lazy-load OCR only for images
                self._ensure_ocr_loaded()
                results = self.ocr_reader.readtext(file_path)
                text = "\n".join([result[1] for result in results])
            logger.info(f"Successfully extracted text from {file_path}")
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading {ext}: {str(e)}", exc_info=True)
            return f"Error reading {ext}: {str(e)}"
    
    def unload_ocr(self):
        """Manually free OCR from memory"""
        if self.ocr_reader is not None:
            self.ocr_reader = None
            logger.info("OCR unloaded from memory")