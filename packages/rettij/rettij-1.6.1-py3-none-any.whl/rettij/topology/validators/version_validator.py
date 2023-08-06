from typing import Dict

from rettij.common.logging_utilities import LoggingSetup
from rettij.topology.validators.abstract_validator import AbstractValidator
from rettij.exceptions.topology_exception import TopologyException


class TopologyVersionValidator(AbstractValidator):
    """
    Validator class for the topology file format version.
    """

    def __init__(self, topology: Dict, topology_file_path: str, major_version: str, minor_version: str):
        """
        Initialize a TopologyVersionValidator object for the supplied topology and version (e.g. 1.0).

        :param topology: The topology to validate.
        :param topology_file_path: Path to the topology file.
        :param major_version: Major version of the topology file format.
        :param minor_version: Minor version of the topology file format.
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        super().__init__(topology, topology_file_path)

        self.major_version: str = major_version
        self.minor_version: str = minor_version

    def validate(self) -> None:
        """
        Validate the topology file format version.

        :raises: TopologyException
        """
        version: str = self.topology.get("version", "")
        major_version, minor_version = (version.split(".")) if version else (self.major_version, self.minor_version)

        if major_version != self.major_version:
            raise TopologyException(
                cause_nbr=TopologyException.VERSION_VALIDATION_FAILED,
                topology_file_path=self.topology_file_path,
                message=f"Topology version not supported. Given: {version}, supported: {self.major_version}.x",
            )

        if minor_version > self.minor_version:
            self.logger.warning(
                f"Topology version not fully supported. Given: {version}, fully supported: {self.minor_version}.0 - {self.major_version}.{self.minor_version}"
            )
