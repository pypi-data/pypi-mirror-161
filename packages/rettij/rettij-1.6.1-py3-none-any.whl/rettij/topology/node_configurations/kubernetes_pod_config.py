from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from rettij.topology.node_configurations.node_config import NodeConfig


class KubernetesPodConfig(NodeConfig):
    """
    This NodeConfig subclass contains the configuration necessary to deploy a KubernetesPod executor.
    """

    __MAX_SERVICE_NAME_LENGTH = 20  # arbitrary value for now which should be long enough, though

    def __init__(self, pod_spec: Dict, hooks: Dict[str, List], execution_host: str = "", config_dir: Path = None):
        """
        Initialize a KubernetesPodConfig object.

        :param pod_spec: Dict containing the Kubernetes Pod specification.
        :param hooks: Dictionary of hook types and registered hooks for the Node/Component.
        :param execution_host: Kubernetes node / host to deploy the Pod on.
        :param config_dir: Path to the directory containing additional configuration files.
        """
        super().__init__(hooks, config_dir)
        self.pod_spec: Dict = pod_spec
        self.execution_host: str = execution_host
