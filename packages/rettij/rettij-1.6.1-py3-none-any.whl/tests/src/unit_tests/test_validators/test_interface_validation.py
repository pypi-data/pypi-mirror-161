import os

from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.topology_reader import TopologyReader
from rettij.topology.validators.interface_validator import InterfaceValidator
from .validator_test_base import ValidatorTestBase


class InterfaceValidatorTest(ValidatorTestBase):
    """
    This TestCase contains tests regarding the InterfaceValidator class.
    """

    def test_address_validation_ip_correct_topology(self) -> None:
        """
        Verify that IP validation works for a valid topology by ensuring that no WARNING is logged.
        """
        with self.assertLogs(level="DEBUG", logger="rettij") as assert_log:
            self.logger.debug("DEBUG")  # ensure that a log message exists
            interface_validator = InterfaceValidator(self.topology, self.topology_file_path)
            interface_validator._check_for_duplicate_ips()

        # Make sure no warning is logged
        self.assertTrue(
            not any("WARNING:rettij.InterfaceValidator:IP" in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_address_validation_ip_correct_topology]: Testing for address "
            f"validation of correct topology failed due to incorrect duplicate IP warnings!",
        )

    def test_address_validation_mac_correct_topology(self) -> None:
        """
        Verify that MAC validation works for a valid topology by ensuring that no WARNING is logged.
        """
        with self.assertLogs(level="DEBUG", logger="rettij") as assert_log:
            self.logger.debug("DEBUG")  # ensure that a log message exists
            interface_validator = InterfaceValidator(self.topology, self.topology_file_path)
            interface_validator._check_mac_addresses()

        self.assertTrue(
            not any("WARNING:rettij.InterfaceValidator:MAC" in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_address_validation_mac_correct_topology]: Testing for address "
            f"validation of correct topology failed due to incorrect duplicate MAC warnings!",
        )

    def test_address_validation_duplicate_ip(self) -> None:
        """
        Verify that duplicate IP detection works by ensuring that a WARNING is logged.
        """
        topology_file_duplicate_ip: ValidatedFilePath = ValidatedFilePath(
            os.path.join(
                self.test_resources_path,
                "topology_with_duplicate_ips.yml",
            )
        )

        topology = TopologyReader.load_yaml(topology_file_duplicate_ip)
        interface_validator = InterfaceValidator(topology, topology_file_duplicate_ip)

        # Make sure a warning is logged
        with self.assertLogs(level="WARNING", logger="rettij") as assert_log:
            interface_validator._check_for_duplicate_ips()

        # Make sure the logged warning is the correct one
        ip_warning = "WARNING:rettij.InterfaceValidator:IP 0.0.0.0/0 is assigned to multiple interfaces."
        self.assertTrue(
            any(ip_warning in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_address_validation_duplicate]: "
            f"Testing for duplicate IP detection failed! Expected warning containing '{ip_warning}' was not found in the log.",
        )

    def test_address_validation_multicast_macs(self) -> None:
        """
        Verify that multicast MAC detection works by ensuring that a WARNING is logged.
        """
        topology_file_multicast_mac: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path,
            "topology_with_multicast_mac.yml",
        )

        topology = TopologyReader.load_yaml(topology_file_multicast_mac)
        interface_validator = InterfaceValidator(topology, topology_file_multicast_mac)

        # Make sure a warning is logged
        with self.assertLogs(level="WARNING", logger="rettij") as assert_log:
            interface_validator._check_mac_addresses()

        # Make sure the logged warning is the correct one
        mac_warning = (
            "WARNING:rettij.InterfaceValidator:MAC 1F:00:00:00:00:00 is a multicast address and not a standard mac."
        )
        mac_warning_two = (
            "WARNING:rettij.InterfaceValidator:MAC 01:FF:FF:00:00:00 is a multicast address and not a standard mac."
        )
        self.assertTrue(
            any(mac_warning in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_address_validation_multicast_macs]: "
            f"Testing for multicast MAC detection failed! Expected warning containing '{mac_warning}' was not found in the log.",
        )
        self.assertTrue(
            any(mac_warning_two in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_address_validation_multicast_macs]: "
            f"Testing for multicast MAC detection failed! Expected warning containing '{mac_warning_two}' was not found in the log.",
        )

    def test_address_validation_duplicate_mac(self) -> None:
        """
        Verify that duplicate MAC detection works by ensuring that a WARNING is logged.
        """
        topology_file_duplicate_mac: ValidatedFilePath = ValidatedFilePath(
            os.path.join(
                self.test_resources_path,
                "topology_with_duplicate_ips.yml",
            )
        )
        topology = TopologyReader.load_yaml(topology_file_duplicate_mac)
        interface_validator = InterfaceValidator(topology, topology_file_duplicate_mac)

        # Make sure a warning is logged
        with self.assertLogs(level="WARNING", logger="rettij") as assert_log:
            interface_validator._check_mac_addresses()

        # Make sure the logged warning is the correct one
        mac_warning = "WARNING:rettij.InterfaceValidator:MAC 00:00:00:00:00:00 is assigned to multiple interfaces."
        self.assertTrue(
            any(mac_warning in output for output in assert_log.output),
            msg=f"[{self.__class__.__name__}.test_address_validation_duplicate_mac]: "
            f"Testing for duplicate MAC detection failed! Expected warning containing '{mac_warning}' was not found in the log.",
        )
