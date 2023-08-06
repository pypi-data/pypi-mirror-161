from pathlib import Path
from typing import Dict, List

from rettij.topology.node_configurations.node_config import NodeConfig


class HostConfig(NodeConfig):
    """
    Empty Node configuration class used for node type "host".
    """

    def __init__(
        self,
        hooks: Dict[str, List],
        config_dir: Path = None,
    ):
        """
        Initialize a HostConfig object.

        :param hooks: Dictionary of hook types and registered hooks for the Node/Component.
        :param config_dir: Directory containing additional configuration files.
        """
        super().__init__(hooks, config_dir)
