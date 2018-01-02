"""Simple logger"""

import datetime

def debug(msg):
    """Logs a message with timestamp and DEBUG level"""
    _log("DEBUG", msg)

def info(msg):
    """Logs a message with timestamp and INFO level"""
    _log("INFO ", msg)

def warn(msg):
    """Logs a message with timestamp and WARN level"""
    _log("WARN ", msg)

def error(msg):
    """Logs a message with timestamp and ERROR level"""
    _log("ERROR", msg)

def _log(level, msg):
    """Logs a message with timestamp"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(level + " | " + timestamp + " | " + str(msg))
