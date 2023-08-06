import os
from typing import List

from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.validators.schema_validator import SchemaValidator
from rettij.exceptions.topology_exception import TopologyException
from rettij.topology.topology_reader import TopologyReader

from .validator_test_base import ValidatorTestBase


class SchemaValidatorTest(ValidatorTestBase):
    """
    This TestCase contains tests regarding the SchemaValidator class.
    """

    def test_schema_validation_correct_topology(self) -> None:
        """
        Verify that a valid topology passes the JSON schema validation without raising an exception.
        """
        schema_validator: SchemaValidator = SchemaValidator(
            self.topology, self.topology_file_path, self.schema_file_path
        )
        try:
            schema_validator.validate()
        except Exception as e:
            self.fail(
                msg=f"[{self.__class__.__name__}.test_schema_validation_correct_topology]: Testing validation of correct topology failed. "
                f"Error: {e}"
            )

    def test_schema_invalid_topology(self) -> None:
        """
        Verify that an invalid topology raises a TopologyException with the correct cause number.
        """
        invalid_topology_file: ValidatedFilePath = ValidatedFilePath(
            os.path.join(
                self.test_resources_path,
                "invalid_topology.yml",
            )
        )
        topology = TopologyReader.load_yaml(invalid_topology_file)
        schema_validator: SchemaValidator = SchemaValidator(topology, invalid_topology_file, self.schema_file_path)

        with self.assertRaises(
            TopologyException,
            msg=f"[{self.__class__.__name__}.test_schema_invalid_topology]: Testing for error capture on validating incorrect topology failed. "
            f"Should throw a TopologyException but didn't.",
        ) as assert_context:
            schema_validator.validate()

        self.assertEqual(
            assert_context.exception.cause_nbr,
            TopologyException.SCHEMA_VALIDATION_FAILED,
            msg=f"[{self.__class__.__name__}.test_schema_invalid_topology]: Testing for error capture on validating incorrect topology failed. "
            f"Should throw a TopologyException with cause {TopologyException.SCHEMA_VALIDATION_FAILED} rather than {assert_context.exception.cause_nbr}.",
        )

    def test_schema_validation_interfaces_required(self) -> None:
        """
        Verify that topologies with missing Node interfaces are handles correctly.

        Node types that should raise a TopologyException with the correct cause number (i.e. must have at least one interface):
        - switch
        - hub
        - router

        Node types that should pass validation without an exception (i.e. may have no interfaces):
        - container
        """
        invalid_topologies: List[ValidatedFilePath] = [
            ValidatedFilePath.join_paths(self.test_resources_path, "topology_with_missing_interfaces_switch.yml"),
            ValidatedFilePath.join_paths(self.test_resources_path, "topology_with_missing_interfaces_hub.yml"),
            ValidatedFilePath.join_paths(self.test_resources_path, "topology_with_missing_interfaces_router.yml"),
        ]

        # test for each node type that has to have an interface (hub, switch, router) if the correct exception is thrown
        for invalid_topology_file in invalid_topologies:
            topology = TopologyReader.load_yaml(invalid_topology_file)
            schema_validator: SchemaValidator = SchemaValidator(topology, invalid_topology_file, self.schema_file_path)

            with self.assertRaises(
                TopologyException,
                msg=f"[{self.__class__.__name__}.test_schema_validation_interfaces_required]: Testing for error capture on validating incorrect topology failed with topology-file {invalid_topology_file.path}. "
                f"It should throw a TopologyException but didn't.",
            ) as assert_context:
                schema_validator.validate()

            self.assertEqual(
                assert_context.exception.cause_nbr,
                TopologyException.SCHEMA_VALIDATION_FAILED,
                msg=f"[{self.__class__.__name__}.test_schema_validation_interfaces_required]: Testing for error capture on validating incorrect topology failed with topology-file {invalid_topology_file.path}. "
                f"It should throw a TopologyException with cause {TopologyException.SCHEMA_VALIDATION_FAILED} rather than {assert_context.exception.cause_nbr}.",
            )

        valid_topology: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path, "topology_with_missing_interfaces_container.yml"
        )
        topology = TopologyReader.load_yaml(valid_topology)
        schema_validator = SchemaValidator(topology, valid_topology, self.schema_file_path)
        try:
            schema_validator.validate()
        except Exception as e:
            self.fail(
                msg=f"[{self.__class__.__name__}.test_schema_validation_interfaces_required]: Testing validation of correct topology-file {valid_topology} failed. "
                f"Error: {e}"
            )
