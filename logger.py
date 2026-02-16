import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "braav_engine.log")
    logger = logging.getLogger("BraavEngine")
    logger.setLevel(logging.DEBUG)

    # 1. FILE HANDLER (For the history)
    file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024*5, backupCount=5, encoding='utf-8')
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    # 2. STREAM HANDLER (For your eyes in the terminal)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_format = logging.Formatter('%(levelname)s: %(message)s') # Keep it clean for console
    stream_handler.setFormatter(stream_format)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger

logger = setup_logger()