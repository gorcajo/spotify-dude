"""Simple logger"""

import datetime
import pathlib

import confmanager as conf

LOGS_DIR = conf.get("LOGS_DIR")

pathlib.Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)

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
    log_name = datetime.datetime.now().strftime("%Y-%m-%d.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    full_msg = level + " | " + timestamp + " | " + str(msg)

    print(full_msg)

    with open(LOGS_DIR + "/" + log_name, "a") as file:
        file.write(full_msg + "\n")
