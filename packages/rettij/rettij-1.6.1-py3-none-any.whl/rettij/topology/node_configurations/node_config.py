from abc import ABC
from logging import Logger
from pathlib import Path

from typing import Dict, List, Any, Optional

from rettij.common.logging_utilities import LoggingSetup


class NodeConfig(ABC):
    """
    This class contains the configuration parts common for all NodeExecutor classes.
    """

    def __init__(
        self,
        hooks: Dict[str, List[Any]],
        config_dir: Optional[Path] = None,
    ):
        """
        Initialize a NodeConfig object.

        :param hooks: Dictionary of hook types and registered hooks for the Node/Component.
        :param config_dir: Path to the directory containing additional configuration files.
        """
        logger: Logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        self.hooks: Dict[str, List[Any]] = hooks
        self.config_dir: Optional[Path] = config_dir
        if isinstance(config_dir, Path):
            if config_dir.exists():
                self.config_dir = config_dir
            else:
                logger.error(f"Configuration directory path {config_dir} does not exist!")
        elif not config_dir:
            # There should not be an error message if no configuration directory was read from the topology
            pass
        else:
            logger.error(f"{config_dir} is not a valid Path object!")
