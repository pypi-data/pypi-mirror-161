from typing import List, Dict

from rettij.common.constants import RESOURCES_DIR
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.validators.abstract_validator import AbstractValidator
from rettij.topology.validators.schema_validator import SchemaValidator
from rettij.topology.validators.version_validator import TopologyVersionValidator
from rettij.topology.validators.channel_validator import ChannelValidator
from rettij.topology.validators.interface_validator import InterfaceValidator
from rettij.topology.validators.node_validator import NodeValidator
from rettij.topology.validators.route_validator import RouteValidator


class ValidatorExecutor:
    """
    This class bundles all validators run on the topology.
    """

    def __init__(self, topology: Dict, topology_file_path: str, major_version: str, minor_version: str) -> None:
        """
        Initialize a ValidatorExecutor object.

        :param topology: Dictionary containing the topology.
        :param topology_file_path: Path to the topology file.
        :param major_version: Topology major version supported by rettij.
        :param minor_version: Topology minor version supported by rettij.
        """
        schema_file_path: ValidatedFilePath = ValidatedFilePath.join_paths(
            RESOURCES_DIR, "schemas", f"{major_version}-{minor_version}", "topology_schema.json"
        )
        self.__validators: List[AbstractValidator] = []
        # add validators, schema must be tested first
        self.__add_validator(SchemaValidator(topology, topology_file_path, schema_file_path))
        self.__add_validator(TopologyVersionValidator(topology, topology_file_path, major_version, minor_version))
        self.__add_validator(InterfaceValidator(topology, topology_file_path))
        self.__add_validator(ChannelValidator(topology, topology_file_path))
        self.__add_validator(NodeValidator(topology, topology_file_path))
        self.__add_validator(RouteValidator(topology, topology_file_path))

    def __add_validator(self, validator: AbstractValidator) -> None:
        """
        Register a validator to be run.

        :param validator: Validator to add.
        """
        self.__validators.append(validator)

    def run_validations(self) -> None:
        """
        Run all registered validators.
        """
        for validator in self.__validators:
            validator.validate()
