from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.topology_exception import TopologyException
from rettij.topology.topology_reader import TopologyReader
from rettij.topology.validators.node_validator import NodeValidator
from .validator_test_base import ValidatorTestBase


class NodeValidatorTest(ValidatorTestBase):
    """
    This TestCase contains tests regarding the NodeValidator class.
    """

    def test_node_validation_correct_topology(self) -> None:
        """
        Verify that Node validation works for a valid topology by ensuring that no WARNING is logged.
        """
        with self.assertLogs(level="DEBUG", logger="rettij") as assert_log:
            self.logger.debug("DEBUG")  # ensure that a log message exists
            node_validator: NodeValidator = NodeValidator(self.topology, self.topology_file_path)
            node_validator.validate()

        # Make sure no warning is logged
        self.assertTrue(
            not any("WARNING:rettij.NodeValidator:" in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_node_validation_ip_correct_topology]: Testing for address "
            f"validation of correct topology failed due to incorrect node-validation warnings!",
        )

    def test_node_validation_duplicate_node_name(self) -> None:
        """
        Verify that duplicate Node name detection works by ensuring that a TopologyException with the correct cause number and message is raised.
        """
        topology_with_duplicate_node_ids: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path, "topology_with_duplicate_node_names.yml"
        )
        topology = TopologyReader.load_yaml(topology_with_duplicate_node_ids)
        node_validator: NodeValidator = NodeValidator(topology, topology_with_duplicate_node_ids)

        # Make sure the correct exception is thrown
        with self.assertRaises(
            TopologyException,
            msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_node_ids]: "
            f"Testing for detection of duplicate node names failed! "
            f"It should raise a TopologyException but did not do so.",
        ) as assert_context:
            node_validator._check_for_duplicate_node_ids()

        exception = assert_context.exception

        # Make sure the TopologyException is of type TopologyException.NODE_VALIDATION_FAILED
        self.assertEqual(
            exception.cause_nbr,
            TopologyException.NODE_VALIDATION_FAILED,
            msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_node_ids]: "
            f"Testing for detection of duplicate nodes names failed! It should raise a TopologyException "
            f"of type '{TopologyException.NODE_VALIDATION_FAILED}' but raised one of type '{exception.cause_nbr}' instead.",
        )

        # Make sure the exception message is correct
        if isinstance(exception.message, str):
            self.assertRegex(
                exception.message,
                r"Node .* is declared \d+ times.",
                msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_node_ids]: "
                f"Testing for detection of duplicate nodes names failed! It should raise a TopologyException containing"
                f"a message like '[...] is declared multiple times.', "
                f"but the message was '{exception.message}' instead.",
            )
        else:
            self.fail(
                msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_node_ids]: "
                f"Testing for detection of duplicate nodes names failed! It should raise a TopologyException containing"
                f"a message, but it did not have a message attribute."
            )

    def test_node_validation_duplicate_interface_ids(self) -> None:
        """
        Verify that duplicate Interface name detection works by ensuring that a TopologyException with the correct cause number and message is raised.
        """
        topology_with_duplicate_interface_ids: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path, "topology_with_duplicate_interface_names.yml"
        )
        topology = TopologyReader.load_yaml(topology_with_duplicate_interface_ids)
        node_validator = NodeValidator(topology, topology_with_duplicate_interface_ids)

        # Make sure the correct exception is thrown
        with self.assertRaises(
            TopologyException,
            msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_interface_ids]: "
            f"Testing for detection of missing channel declaration failed! "
            f"It should raise a TopologyException but did not do so.",
        ) as assert_context:
            node_validator._check_for_duplicate_interface_names()

        exception = assert_context.exception

        # Make sure the TopologyException is of type TopologyException.NODE_VALIDATION_FAILED
        self.assertEqual(
            exception.cause_nbr,
            TopologyException.NODE_VALIDATION_FAILED,
            msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_interface_ids]: "
            f"Testing for detection of duplicate interface ids failed! It should raise a TopologyException "
            f"of type '{TopologyException.NODE_VALIDATION_FAILED}' but raised one of type '{exception.cause_nbr}' instead.",
        )

        # Make sure the exception message is correct
        if isinstance(exception.message, str):
            self.assertRegex(
                exception.message,
                r"is declared multiple times.",
                msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_interface_ids]: "
                f"Testing for detection of duplicate interface ids failed! It should raise a TopologyException containing"
                f"a message like '[...] is declared multiple times.', "
                f"but the message was '{exception.message}' instead.",
            )
        else:
            self.fail(
                msg=f"[{self.__class__.__name__}.test_node_validation_duplicate_interface_ids]: "
                f"Testing for detection of duplicate interface ids failed! It should raise a TopologyException containing"
                f"a message, but it did not have a message attribute."
            )
