import logging
import os
from datetime import datetime

def setup_logger(project_root: str):
    log_dir = os.path.join(project_root, "logs", datetime.now().strftime("%Y/%m/%d"))
    session_id = datetime.now().strftime("session-%Y%m%d-%H%M%S")
    session_log_dir = os.path.join(log_dir, session_id)
    
    os.makedirs(session_log_dir, exist_ok=True)
    
    log_file = os.path.join(session_log_dir, "errors.log")
    
    logger = logging.getLogger("SysAdminToolkit")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    
    return logger, session_id, session_log_dir
