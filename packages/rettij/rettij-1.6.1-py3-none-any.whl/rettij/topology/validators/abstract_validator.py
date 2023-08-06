from abc import ABC, abstractmethod
from typing import Dict, Union, Any, Hashable

from rettij.common.logging_utilities import LoggingSetup


class AbstractValidator(ABC):
    """
    This class defines the abstract base used for all validators.
    """

    def __init__(self, topology: Union[Dict[Hashable, Any]], topology_file_path: str) -> None:
        """
        Initialize an AbstractValidator object.

        :param topology: Dict containing the topology.
        :param topology_file_path: Path to the topology file.
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        self.topology: Union[Dict[Hashable, Any]] = topology
        self.topology_file_path: str = topology_file_path

    @abstractmethod
    def validate(self) -> None:
        """
        Run the validation implemented by this validator.
        """
        raise NotImplementedError("This method has to be implemented!")
