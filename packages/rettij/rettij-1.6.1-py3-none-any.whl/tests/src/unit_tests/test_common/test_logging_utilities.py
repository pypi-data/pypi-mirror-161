import os
import tempfile
import unittest

from rettij.common.logging_utilities import LoggingSetup, Loglevel


class TestLoggingSetup(unittest.TestCase):
    """
    This TestCase contains tests regarding the LoggingSetup class.
    """

    def test(self) -> None:
        """
        Verify that logging has the expected output (format).
        """
        uid: str = "010203"  # Arbitrary valid uid

        LoggingSetup.initialize_logging(uid, Loglevel.DEBUG, Loglevel.DEBUG)
        logger = LoggingSetup.submodule_logging("TestLoggingSetup")
        logger_sub = LoggingSetup.submodule_logging("TestLoggingSetup.SUB")

        logger.debug("Test DEBUG")
        logger.info("Test INFO")
        logger.warning("Test WARNING")
        logger.error("Test ERROR")
        logger.critical("Test CRITICAL")

        logger_sub.debug("Test DEBUG")
        logger_sub.info("Test INFO")
        logger_sub.warning("Test WARNING")
        logger_sub.error("Test ERROR")
        logger_sub.critical("Test CRITICAL")

        log_dir: str = os.path.join(tempfile.gettempdir(), "rettij-log")
        log_file: str = os.path.join(log_dir, f"{uid}.log")

        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as file:
            data = file.read()
        self.assertIn(":[rettij.TestLoggingSetup]:[DEBUG] Test DEBUG", data)
        self.assertIn(":[rettij.TestLoggingSetup]:[INFO] Test INFO", data)
        self.assertIn(":[rettij.TestLoggingSetup]:[WARNING] Test WARNING", data)
        self.assertIn(":[rettij.TestLoggingSetup]:[ERROR] Test ERROR", data)
        self.assertIn(":[rettij.TestLoggingSetup]:[CRITICAL] Test CRITICAL", data)
        self.assertIn(":[rettij.TestLoggingSetup.SUB]:[DEBUG] Test DEBUG", data)
        self.assertIn(":[rettij.TestLoggingSetup.SUB]:[INFO] Test INFO", data)
        self.assertIn(":[rettij.TestLoggingSetup.SUB]:[WARNING] Test WARNING", data)
        self.assertIn(":[rettij.TestLoggingSetup.SUB]:[ERROR] Test ERROR", data)
        self.assertIn(":[rettij.TestLoggingSetup.SUB]:[CRITICAL] Test CRITICAL", data)
