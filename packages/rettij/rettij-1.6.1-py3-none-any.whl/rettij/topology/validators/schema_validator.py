import json
from typing import Dict

import jsonref
import jsonschema

from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.topology_exception import TopologyException
from rettij.topology.validators.abstract_validator import AbstractValidator


class SchemaValidator(AbstractValidator):
    """
    Validator class for the topology's JSON schema.
    """

    def __init__(self, topology: Dict, topology_file_path: str, schema_file_path: ValidatedFilePath) -> None:
        """
        Initialize a SchemaValidator object for the supplied topology and version (e.g. 1.0).

        :param topology: The topology to validate.
        :param topology_file_path: Path to the topology file.
        :param schema_file_path: Path to the JSON schema root file.
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        super().__init__(topology, topology_file_path)

        self.schema_file_path: ValidatedFilePath = schema_file_path

        self.schema: Dict = self.__load_json_schema(schema_file_path)

    def __load_json_schema(self, schema_file_path: ValidatedFilePath) -> Dict:
        """
        Load a json schema from a given filepath.

        :param schema_file_path: The file path of the schema file to validate against.
        :return: The json schema as a dictionary.
        :raises: FileNotFoundError, json.decoder.JSONDecodeError
        """
        self.logger.debug("Reading json-schema file " + schema_file_path)
        try:
            base_uri = "file://localhost/{}".format(schema_file_path.replace("\\", "/"))
            with open(schema_file_path) as schema_file:
                return jsonref.loads(schema_file.read(), base_uri=base_uri, jsonschema=True)
        except json.decoder.JSONDecodeError as e:
            self.logger.error(e)
            raise TopologyException(TopologyException.SCHEMA_INVALID, schema_file_path) from None

    def validate(self) -> None:
        """
        Validate that the topology matches the associated JSON schema.

        :raises: TopologyException
        """
        try:
            jsonschema.validate(self.topology, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            if isinstance(
                e.instance, dict
            ):  # if the instance on which the error occurred is a json node dict which will have a line number
                raise TopologyException(
                    TopologyException.SCHEMA_VALIDATION_FAILED,
                    topology_file_path=self.topology_file_path,
                    schema_file_path=self.schema_file_path,
                    message=f"{e.message} (Line: {e.instance.get('__line__')})",
                ) from None
            else:  # if the instance on which the error occurred is a str, list etc.
                raise TopologyException(
                    TopologyException.SCHEMA_VALIDATION_FAILED,
                    topology_file_path=self.topology_file_path,
                    schema_file_path=self.schema_file_path,
                    message=f"{e.message} (Context: {list(e.absolute_path)})",
                ) from None
