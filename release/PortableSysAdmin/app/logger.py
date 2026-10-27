import logging
import os
from datetime import datetime


def setup_logger(project_root: str):
    from datetime import timezone
    import tempfile
    now = datetime.now(timezone.utc).astimezone()
    session_id = now.strftime("session-%Y%m%d-%H%M%S")
    
    # Try creating logs in project_root, fallback to tempdir if read-only / permission denied (common on USB drives)
    session_log_dir = None
    try:
        log_dir = os.path.join(project_root, "logs", now.strftime("%Y/%m/%d"))
        s_dir = os.path.join(log_dir, session_id)
        os.makedirs(s_dir, exist_ok=True)
        # Verify write capability
        test_file = os.path.join(s_dir, ".test_write")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_file)
        session_log_dir = s_dir
    except (OSError, PermissionError):
        temp_log_dir = os.path.join(tempfile.gettempdir(), "PortableSysAdmin", "logs", now.strftime("%Y/%m/%d"))
        session_log_dir = os.path.join(temp_log_dir, session_id)
        os.makedirs(session_log_dir, exist_ok=True)
    
    log_file = os.path.join(session_log_dir, "errors.log")
    
    logger = logging.getLogger("SysAdminToolkit")
    logger.setLevel(logging.DEBUG)
    
    # File handler with UTF-8 encoding to avoid Windows cp1252 UnicodeEncodeError
    try:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        logger.addHandler(logging.NullHandler())
    
    return logger, session_id, session_log_dir
