import os

from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.topology_reader import TopologyReader
from rettij.topology.validators.route_validator import RouteValidator

from .validator_test_base import ValidatorTestBase


class RouteValidatorTest(ValidatorTestBase):
    """
    This TestCase contains tests regarding the RouteValidator class.
    """

    def test_gateway_nw_does_not_exist(self) -> None:
        """
        Verify that detection of non-existent gateways works by ensuring that a WARNING is logged.
        """
        topology_file_wrong_gateway_node: ValidatedFilePath = ValidatedFilePath(
            os.path.join(
                self.test_resources_path,
                "topology_with_non-existent_gateway_node.yml",
            )
        )
        topology = TopologyReader.load_yaml(topology_file_wrong_gateway_node)
        route_validator = RouteValidator(topology, topology_file_wrong_gateway_node)

        # Make sure wrong default gateway reference produces a warning
        with self.assertLogs(level="WARNING", logger="rettij") as gw_warning:
            route_validator._check_default_gateway_ip()

        # Make sure the warning message exists and is correct
        self.assertRegex(
            gw_warning.output[0],
            r"Default gateway [^\s]* of Node [^\s]* in [^\s]* lies outside the simulation or host network.",
            msg=f"[{self.__class__.__name__}.test_gateway_nw_does_not_exist]: "
            f"Testing for detection of non-existent gateway failed! "
            f"It should raise a WARNING containing a message like 'Gateway {{gateway_ip}} of Node {{node_id}} not found.', "
            f" but the message was '{gw_warning.output}' instead.",
        )

    def test_routes_correct_topology(self) -> None:
        """
        Verify that route validation works for a valid topology by ensuring that no WARNING is logged.
        """
        valid_topology_file: ValidatedFilePath = ValidatedFilePath(
            os.path.join(
                self.test_resources_path,
                "topology_with_valid_routes.yml",
            )
        )
        topology = TopologyReader.load_yaml(valid_topology_file)
        route_validator = RouteValidator(topology, valid_topology_file)
        # Make sure a topology file with correct default gateway addresses runs without any errors
        with self.assertLogs(level="INFO", logger="rettij") as gw_warning:
            self.logger.info("Testing route validation")
            route_validator._check_default_gateway_ip()

        self.assertTrue(
            len(gw_warning.output) == 1,
            msg=f"[{self.__class__.__name__}.test_gateway_ip_correct_topology]: "
            f"Testing of topology file with correct routes failed. A warning was raised: {gw_warning.output}",
        )
