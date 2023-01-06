import logging
import sys


class CustomLogger(logging.Logger):  # NOSONAR
    """
    The logger for the converter

    Shadows builtin logging.Logger
    """

    def __init__(self, logging_level=logging.WARNING):
        super().__init__(__name__)
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s",
                                                           "%H:%M:%S"))

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging_level)
        self.logger.addHandler(self.stream_handler)

    def get_logger(self) -> logging.Logger:
        """
        Returns the logger
        """
        return self.logger

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
