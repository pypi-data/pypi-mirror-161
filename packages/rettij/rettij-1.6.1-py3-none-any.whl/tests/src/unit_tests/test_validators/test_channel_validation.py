from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.topology_exception import TopologyException
from rettij.topology.topology_reader import TopologyReader
from rettij.topology.validators.channel_validator import ChannelValidator

from .validator_test_base import ValidatorTestBase


class ChannelValidatorTest(ValidatorTestBase):
    """
    This TestCase contains tests regarding the ChannelValidator class.
    """

    def test_valid_channels(self) -> None:
        """
        Verify that Channel validation works for a valid topology by ensuring that no WARNING is logged.
        """
        topology_file_misconfigured_channels: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path, "topology_with_undeclared_channels.yml"
        )

        topology = TopologyReader.load_yaml(topology_file_misconfigured_channels)

        with self.assertLogs(level="DEBUG", logger="rettij") as assert_log:
            self.logger.debug("DEBUG")  # ensure that a log message exists
            channel_validator: ChannelValidator = ChannelValidator(topology, topology_file_misconfigured_channels)
            channel_validator.validate()

        self.assertNotRegex(
            "\n".join(assert_log.output),
            r"\[WARNING\]",
            msg=f"[{self.__class__.__name__}.test_valid_channels]: "
            f"Testing valid channel definitions failed! Unexpected warning logged.",
        )

    def test_channel_validation_wrong_number_of_connections(self) -> None:
        """
        Verify that detection of Channels with the wrong number of endpoints works by ensuring that a WARNING is logged.
        """
        topology_file_misconfigured_channels: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path, "topology_with_wrong_number_of_connections.yml"
        )
        topology = TopologyReader.load_yaml(topology_file_misconfigured_channels)
        channel_validator: ChannelValidator = ChannelValidator(topology, topology_file_misconfigured_channels)

        # Make sure a warning is logged
        with self.assertLogs(level="WARNING", logger="rettij") as assert_log:
            channel_validator._check_channel_references()

        # Make sure the logged warning is the correct one
        channel_warning = "WARNING:rettij.ChannelValidator:Channel c0 has 1 connection(s) instead of 2."
        self.assertTrue(
            any(channel_warning in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_channel_validation_wrong_number_of_connections]: "
            f"Testing for wrong number of channel usage detection failed! Expected warning containing '{channel_warning}' was not found in the log.",
        )

    def test_channel_validation_duplicate_channel_declared(self) -> None:
        """
        Verify that duplicate Channel detection works by ensuring that a TopologyException with the correct cause number is raised.
        """
        topology_file_duplicate_channels: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path, "topology_with_duplicate_channels.yml"
        )
        topology = TopologyReader.load_yaml(topology_file_duplicate_channels)
        channel_validator: ChannelValidator = ChannelValidator(topology, topology_file_duplicate_channels)

        # Make sure a TopologyException is raised
        with self.assertRaises(TopologyException) as assert_context:
            channel_validator._check_for_duplicate_channels()

        # Make sure the exception has the correct cause number
        self.assertEqual(
            assert_context.exception.cause_nbr,
            TopologyException.CHANNEL_VALIDATION_FAILED,
            msg=f"[{self.__class__.__name__}.test_channel_validation_duplicate_channel_declared]: "
            f"Testing for wrong number of channel usage detection failed! "
            f"Expected TopologyException with cause number {TopologyException.CHANNEL_VALIDATION_FAILED}, "
            f"received {assert_context.exception.cause_nbr}.",
        )
