import logging
import os
import tempfile
import warnings
from enum import Enum
from typing import List, Tuple


class Loglevel(Enum):
    """
    This class defines an enumerator for logging levels for use with LoggingSetup.

    Log levels and their numeric values are identical to those from the built-in 'logging' module.
    """

    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    @classmethod
    def values(cls) -> List[int]:
        """
        Return a list of all unique enumeration values.

        :return: List of all enumeration values (i.e. [50, 40, 30, 20, 10, 0])
        """
        return [e.value for e in cls]

    @classmethod
    def members(cls) -> List:
        """
        Return a list of all enumeration members.

        :return: List of all enumeration members (i.e. ['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'NOTSET'])
        """
        return list(Loglevel.__members__)


class LoggingSetup:
    """
    Helper class to configure project-wide logging.
    """

    @classmethod
    def initialize_logging(cls, uid: str, file_loglevel: Loglevel, console_loglevel: Loglevel) -> None:
        """
        Initialize logging on the highest level.

        Sample usage: LoggingSetup.initialize_logging(self.uid, LoggingSetup.INFO)

        :param uid: UID for naming purposes.
        :param file_loglevel: Level for logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :param console_loglevel: Level for logging to console (disabled if NOTSET)
        """
        if type(file_loglevel) != Loglevel:
            raise AttributeError(f"file_loglevel has to be of type Loglevel, not {file_loglevel.__class__.__name__}!")
        if type(console_loglevel) != Loglevel:
            raise AttributeError(
                f"console_loglevel has to be of type Loglevel, not {console_loglevel.__class__.__name__}!"
            )

        logger: logging.Logger
        if file_loglevel == Loglevel.NOTSET and console_loglevel == Loglevel.NOTSET:
            logger = logging.getLogger(__name__)
        else:
            log_file: str
            logger, log_file = cls.__setup_logger(uid, file_loglevel, console_loglevel)
            logger.critical(
                f"Logging to console with loglevel {console_loglevel.name} and to {log_file} with loglevel "
                f"{file_loglevel.name}."
            )

        logger.critical(f"Simulation-UID: {uid}")

        # Suppress urllib3 api warnings (used by kubernetes API)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)
        # Suppress resource warnings
        warnings.simplefilter("ignore", ResourceWarning)
        # suppress warnings by PyYAML
        logging.getLogger("yaml").setLevel(logging.CRITICAL)
        # suppress debug messages by kubernetes.client.rest
        logging.getLogger("kubernetes.client.rest").setLevel(logging.WARNING)

    @staticmethod
    def __setup_logger(uid: str, file_loglevel: Loglevel, console_loglevel: Loglevel) -> Tuple[logging.Logger, str]:
        log_dir: str = os.path.join(tempfile.gettempdir(), "rettij-log")
        os.makedirs(log_dir, exist_ok=True)
        log_file: str = os.path.join(log_dir, f"{uid}.log")

        logger: logging.Logger = logging.getLogger("rettij")
        logger.setLevel(min(console_loglevel.value, file_loglevel.value))
        logger.propagate = False

        # This needs to be a while-loop as the actual length of the list changes with every handler that is removed.
        while len(logger.handlers) > 0:
            handler: logging.Handler = logger.handlers[0]
            logger.removeHandler(handler)

        formatter: logging.Formatter = logging.Formatter(
            "[%(asctime)s]:[%(name)s]:[%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        ch: logging.StreamHandler = logging.StreamHandler()
        ch.setLevel(console_loglevel.value)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        fh: logging.FileHandler = logging.FileHandler(log_file)
        fh.setLevel(file_loglevel.value)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        return logger, log_file

    @staticmethod
    def submodule_logging(module_name: str) -> logging.Logger:
        """
        Initialize a logger for a (sub-)module.

        Usage for __init__: self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        Usage for @classmethod: cls.logger = LoggingSetup.submodule_logging(cls.__name__)
        Usage for @staticmethod: logger = LoggingSetup.submodule_logging("<custom name>")

        :param module_name: Name for the module
        :return: Logger object
        """
        logger: logging.Logger = logging.getLogger(f"rettij.{module_name}")
        return logger
