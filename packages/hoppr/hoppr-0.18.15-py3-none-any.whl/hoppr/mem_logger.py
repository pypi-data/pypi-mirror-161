"""
A logger that gets dumped to stdout when closed
"""

import inspect
import logging
import os
from logging.handlers import MemoryHandler
from typing import Optional


class MemoryLogger:
    """
    A logger that gets dumped to stdout when closed
    """

    def __init__(self, log_name: Optional[str] = None) -> None:
        if log_name is None:
            caller = inspect.stack()[1][0].f_locals["self"].__class__.__name__
            log_name = f"{caller}--{os.getpid()}"

        self._logger = logging.getLogger(log_name)

        self._logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        log_handler = MemoryHandler(
            10000, flushLevel=logging.CRITICAL, target=stream_handler
        )
        log_handler.setFormatter(formatter)
        self._logger.addHandler(log_handler)

    def flush(self) -> None:
        """
        Flush all handlers for this logger
        """
        for handler in self._logger.handlers:
            handler.flush()

    def close(self) -> None:
        """
        Close (and flush) all handlers for this logger
        """
        for handler in self._logger.handlers:
            handler.close()

    def clear_targets(self) -> None:
        """
        Makes the target for all Memory Handlers in this logger None

        Thus when these handlers are flushed, nothing will go to standard output
        """
        for handler in self._logger.handlers:
            if isinstance(handler, MemoryHandler):
                handler.setTarget(None)

    def debug(self, msg: str) -> None:
        """
        Wrapper function for debug messages
        """
        self._logger.debug(msg)

    def info(self, msg: str) -> None:
        """
        Wrapper function for info messages
        """
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        """
        Wrapper function for warn messages
        """
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        """
        Wrapper function for error messages
        """
        self._logger.error(msg)

    def fatal(self, msg: str) -> None:
        """
        Wrapper function for fatal messages
        """
        self._logger.fatal(msg)

    def critical(self, msg: str) -> None:
        """
        Wrapper function for critical messages
        """
        self._logger.critical(msg)
