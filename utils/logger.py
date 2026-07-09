# Centralized Logging and Exception Handling (Hardening Pass)
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import functools
import traceback

# Ensure log directory exists
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "healthcare.log")

# Structured formatting: Timestamp | Log Level | Module Name | Message
log_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Root logger setup
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# File Handler (Rotating)
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

# Stream Handler (console)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
root_logger.addHandler(stream_handler)

# Centralized Logger Fetcher
def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with structured console and file outputs."""
    return logging.getLogger(name)


# ─────────────────────────────────────────────
# CENTRALIZED EXCEPTION HANDLER DECORATOR
# ─────────────────────────────────────────────
def safe_execute(fallback=None, description=""):
    """
    Decorator to wrap functions in safety block.
    Logs exceptions with tracebacks and returns the fallback value.
    """
    def decorator(func):
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                err_msg = f"Exception in {func.__name__} {description}: {str(e)}"
                logger.error(err_msg)
                logger.error(traceback.format_exc())
                return fallback
        return wrapper
    return decorator
