# dice_auto_apply/utils/log_manager.py

import os
import logging
from datetime import datetime
import sys

def setup_logger():
    """Setup the application logger."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create log file with date and time in filename
    log_file = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure the logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log application start
    logging.info("Application started")
    
    return logging.getLogger()

def get_logger():
    """Get the application logger."""
    return logging.getLogger()
