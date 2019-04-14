"""Simple logger"""

import datetime
import pathlib

import confmanager as conf


class Logger(object):

    def __init__(self, verbose_mode: bool = True, silent_mode: bool = False):
        if verbose_mode and silent_mode:
            raise ValueError()

        self.verbose_mode = verbose_mode
        self.silent_mode = silent_mode

        log_pattern = conf.get("LOG_PATTERN")
        self.log_filename = datetime.datetime.now().strftime(log_pattern)

        directory = "/".join(self.log_filename.split("/")[:-1])
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)


    def debug(self, msg: str):
        """Logs a message with DEBUG level"""
        self._log("DEBUG", msg)


    def info(self, msg: str):
        """Logs a message with INFO level"""
        self._log("INFO ", msg)


    def warn(self, msg: str):
        """Logs a message with WARN level"""
        self._log("WARN ", msg)


    def error(self, msg: str):
        """Logs a message with ERROR level"""
        self._log("ERROR", msg)


    def _log(self, level: str, msg: str):
        """Logs a message with a level"""

        if level not in ["DEBUG", "INFO ", "WARN ", "ERROR"]:
            raise ValueError()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        full_msg = level + " | " + timestamp + " | " + msg

        with open(self.log_filename, "a") as file:
            file.write(full_msg + "\n")

        if not self.silent_mode:
            if self.verbose_mode or level in ["INFO ", "WARN ", "ERROR"]:
                print(full_msg)
