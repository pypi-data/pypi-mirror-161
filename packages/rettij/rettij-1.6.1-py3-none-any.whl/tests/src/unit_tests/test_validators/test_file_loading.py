from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.validators.schema_validator import SchemaValidator
from rettij.exceptions.topology_exception import TopologyException
from rettij.topology.topology_reader import TopologyReader
from rettij.topology.validators.interface_validator import InterfaceValidator

from .validator_test_base import ValidatorTestBase


class FileLoadingTest(ValidatorTestBase):
    """
    This TestCase contains tests regarding the YAML file loading.
    """

    def test_load_incorrect_schema(self) -> None:
        """
        Verify that using a faulty schema raises a TopologyException.

        Works by passing the topology file path as schema file path, since they're both YAML files.
        """
        with self.assertRaises(
            TopologyException,
            msg=f"[{self.__class__.__name__}.test_load_incorrect_schema]: Testing for error capture on incorrect schema file failed. "
            f"Should throw a TopologyException but didn't.",
        ) as assert_context:
            SchemaValidator(self.topology, self.topology_file_path, self.topology_file_path)

        # Make sure the TopologyException is of type TopologyException.SCHEMA_INVALID
        self.assertEqual(
            assert_context.exception.cause_nbr,
            TopologyException.SCHEMA_INVALID,
            msg=f"[{self.__class__.__name__}.test_load_incorrect_schema]: Testing for error capture on incorrect schema file failed. "
            f"Should throw a TopologyException with cause {TopologyException.SCHEMA_INVALID} rather than {assert_context.exception.cause_nbr}.",
        )

    def test_load_correct_schema(self) -> None:
        """
        Verify that a correct schema is loaded without error.
        """
        try:
            SchemaValidator(self.topology, self.topology_file_path, self.schema_file_path)
        except Exception as e:
            self.fail(
                msg=f"[{self.__class__.__name__}.test_load_correct_schema]: Testing for loading of correct schema file failed. "
                f"Error: {e}"
            )

    def test_load_incorrect_yaml(self) -> None:
        """
        Verify that a syntactically invalid YAML file throws a yaml.YAMLError on loading.
        """
        invalid_yaml_file: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path,
            "invalid_yaml.yml",
        )

        # Make sure corrupt yaml files raise a TopologyException
        with self.assertRaises(
            TopologyException,
            msg=f"[{self.__class__.__name__}.test_load_incorrect_yaml]: Testing for error capture on incorrect schema file failed. "
            f"Should throw a yaml.scanner.ScannerError but didn't.",
        ) as assert_context:
            TopologyReader.load_yaml(invalid_yaml_file)

        # Make sure the TopologyException is of type TopologyException.DATA_INVALID
        self.assertEqual(
            assert_context.exception.cause_nbr,
            TopologyException.DATA_INVALID,
            msg=f"[{self.__class__.__name__}.test_load_incorrect_schema]: Testing for error capture on incorrect schema file failed. "
            f"Should throw a ValidationException with cause {TopologyException.DATA_INVALID} rather than {assert_context.exception.cause_nbr}.",
        )

    def test_load_correct_yaml(self) -> None:
        """
        Verify that a syntactically invalid YAML file throws a yaml.YAMLError on loading.
        """
        try:
            InterfaceValidator(TopologyReader.load_yaml(self.topology_file_path), self.topology_file_path)
        except Exception as e:
            self.fail(
                msg=f"[{self.__class__.__name__}.test_load_correct_yaml]: Testing for loading of correct yaml file failed. "
                f"Error: {e}"
            )
