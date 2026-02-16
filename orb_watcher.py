import time
import os
from watchdog.events import FileSystemEventHandler
import datetime
from extractor import ChamchaExtractor
import threading
from logger import logger

WATCH_DIR = os.path.join(os.path.expanduser("~"), "ORB_VOID")
DAIRY_WATCH_DIR = os.path.join(os.path.expanduser("~"), "ORB_DAIRY")
os.makedirs(WATCH_DIR, exist_ok=True)
os.makedirs(DAIRY_WATCH_DIR, exist_ok=True)

class OrbVoidHandler(FileSystemEventHandler):
    def __init__(self, brain):
        self.brain = brain
        self.extractor = ChamchaExtractor()

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            logger.info(f"Watcher: Detected {os.path.basename(file_path)}")
            time.sleep(1) 
            self.process_void_file(file_path)
    
    def process_void_file(self, file_path):
        """Extract text from void file and log to brain"""
        logger.info(f"Processing void file: {os.path.basename(file_path)}")
        
        text = self.extractor.extract_text(file_path)
        
        if text.startswith("Error"):
            logger.error(f"Error processing file: {text}")
            return
        
        # Log to brain as a thought
        try:
            self.brain.log_stream(text)
        except Exception as e:
            logger.error(f"Brain Log Error: {e}", exc_info=True)


class DairyHandler(FileSystemEventHandler):
    def __init__(self, brain):
        self.brain = brain
        self.extractor = ChamchaExtractor()
        self.ocr_shutdown_timer = None
        self.OCR_IDLE_TIMEOUT = 300  # 5 minutes in seconds

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            logger.info(f"Dairy detected: {os.path.basename(file_path)}")
            time.sleep(1)
            self.process_diary_file(file_path)

    def process_diary_file(self, file_path):
        """Extract text from dairy image/document and add to DB"""
        logger.info(f"Processing dairy: {os.path.basename(file_path)}")
        
        # Reset shutdown timer (file detected = activity)
        self._reset_ocr_timer()
        
        # Extract text from image/document
        text = self.extractor.extract_text(file_path)
        
        if text.startswith("Error"):
            logger.error(f"Error processing dairy file: {text}")
            return
        
        # Add to database as thought
        try:
            vector = self.brain.get_embedding(text)
            self.brain.db.table("thoughts").insert({
                "content": text,
                "embedding": vector,
                "metadata": {
                    "source_file": os.path.basename(file_path),
                    "source_type": "dairy_entry",
                    "processed_at": datetime.datetime.utcnow().isoformat()
                },
                "created_at": datetime.datetime.utcnow().isoformat()
            }).execute()
            logger.info(f"Dairy saved: {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"DB Error: {e}", exc_info=True)
    
    def _reset_ocr_timer(self):
        """Reset the OCR shutdown timer"""
        # Cancel existing timer
        if self.ocr_shutdown_timer is not None:
            self.ocr_shutdown_timer.cancel()
        
        # Start new timer
        self.ocr_shutdown_timer = threading.Timer(
            self.OCR_IDLE_TIMEOUT,
            self._shutdown_ocr
        )
        self.ocr_shutdown_timer.daemon = True
        self.ocr_shutdown_timer.start()
        logger.info(f"OCR will auto-shutdown in {self.OCR_IDLE_TIMEOUT//60} mins if idle")
    
    def _shutdown_ocr(self):
        """Unload OCR from memory after idle timeout"""
        logger.info(f"{self.OCR_IDLE_TIMEOUT//60} mins passed with no activity")
        self.extractor.unload_ocr()