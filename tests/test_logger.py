import logging
import unittest

from app.utils.customlogger import CustomLogger


# pylint:disable=duplicate-code
# pylint:disable=too-many-public-methods

class TestLogger(unittest.TestCase):
    """
    Test the logger
    """

    def test_get_logger(self):
        """
        Test if `get_logger()` returns a logging.Logger instance
        """
        logger = CustomLogger(logging.DEBUG)

        self.assertIsInstance(logger.get_logger(), logging.Logger)

    def test_level(self):
        """
        Test if `logger.level` returns the correct logging level
        """
        logger = CustomLogger(logging.DEBUG)

        self.assertEqual(logger.get_logger().level, logging.DEBUG)

    def test_critical(self):
        """
        Test if `logger.critical` gets logged at the correct logging level
        """
        logger = CustomLogger(logging.CRITICAL)

        with self.assertLogs(logger.get_logger(), logging.CRITICAL):
            logger.critical("testing logging_mode critical")

    def test_error(self):
        """
        Test if `logger.error` gets logged at the correct logging level
        """
        logger = CustomLogger(logging.ERROR)

        with self.assertLogs(logger.get_logger(), logging.ERROR):
            logger.error("testing logging_mode error")

    def test_warning(self):
        """
        Test if `logger.warning` gets logged at the correct logging level
        """
        logger = CustomLogger(logging.WARNING)

        with self.assertLogs(logger.get_logger(), logging.WARNING):
            logger.warning("testing logging_mode warning")

    def test_info(self):
        """
        Test if `logger.info` gets logged at the correct logging level
        """
        logger = CustomLogger(logging.INFO)

        with self.assertLogs(logger.get_logger(), logging.INFO):
            logger.info("testing logging_mode info")

    def test_debug(self):
        """
        Test if `logger.debug` gets logged at the correct logging level
        """
        logger = CustomLogger(logging.DEBUG)

        with self.assertLogs(logger.get_logger(), logging.DEBUG):
            logger.debug("testing logging_mode debug")
