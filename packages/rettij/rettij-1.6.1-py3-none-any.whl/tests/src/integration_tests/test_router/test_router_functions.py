import os
import unittest
from ipaddress import IPv4Address
from pathlib import Path

from rettij import Rettij
from rettij.commands.run_command import RunCommand
from rettij.commands.ping_command import PingCommand
from rettij.commands.update_router_config_file_command import UpdateRouterConfigFileCommand
from rettij.common.constants import PROJECT_ROOT_DIR
from rettij.common.logging_utilities import Loglevel
from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.invalid_path_exception import InvalidPathException
from rettij.topology.network_components.node import Node
from tests.src.utils.load_k8s_config import load_k8s_config


@unittest.skip("Only run by hand")
@unittest.skipIf(
    not load_k8s_config(),
    "No Kubernetes configuration found, skipping test.",
)
class TestRouterFunctions(unittest.TestCase):
    """
    Class for testing FRR routing functionalities.

    Includes:
    - static routing
    - rip
    - ospf
    - bgp
    - ipsec
    - snmp
    """

    rettij: Rettij
    test_base_path: Path
    test_resources_path: Path
    kubeconfig_path: str

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.test_base_path = Path(__file__).parent.absolute()
        cls.test_resources_path = cls.test_base_path.joinpath("resources")

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.rettij = Rettij(file_loglevel=Loglevel.DEBUG, console_loglevel=Loglevel.DEBUG)

        topology_path: ValidatedFilePath = ValidatedFilePath(
            os.path.join(self.test_resources_path, "double_router_topology.yml")
        )

        self.rettij.init(topology_path)
        self.rettij.create()

        self.router1: Node = self.rettij.nodes["router1"]
        self.router2: Node = self.rettij.nodes["router2"]
        self.client1: Node = self.rettij.nodes["client1"]
        self.client2: Node = self.rettij.nodes["client2"]

    def tearDown(self) -> None:
        """
        Clean up before TestCase instance is discarded.
        """
        if self.rettij:
            self.rettij.finalize()

    def test_01_static(self) -> None:
        """
        Verify that static routing works.
        """
        # Configure static routes on router1
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router1.executor, ValidatedFilePath(self.test_resources_path / "static" / "router1.conf")
            )
            .execute(0)
            .exit_code,
        )

        # Configure static routes on router2
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router2.executor, ValidatedFilePath(self.test_resources_path / "static" / "router2.conf")
            )
            .execute(0)
            .exit_code,
        )

        # ping client1 -> (router1 -> router2) -> client2
        self.assertEqual(
            0, PingCommand(self.client1.executor, IPv4Address(self.client2.ifaces["i0"].ip), c=1).execute(0).exit_code
        )

    def test_02_rip(self) -> None:
        """
        Verify that RIP routing works.
        """
        # Configure rip routing on router1
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router1.executor, ValidatedFilePath(self.test_resources_path / "rip" / "router1.conf")
            )
            .execute(0)
            .exit_code,
        )

        # Configure rip routing on router2
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router2.executor, ValidatedFilePath(self.test_resources_path / "rip" / "router2.conf")
            )
            .execute(0)
            .exit_code,
        )

        RunCommand(
            self.router1.executor,
            [
                "bash",
                "-c",
                "{ sleep 60; echo show ip rip; } | vtysh",
            ],
        ).execute(0)

        # ping client1 -> (router1 -> router2) -> client2
        self.assertEqual(
            0, PingCommand(self.client1.executor, IPv4Address(self.client2.ifaces["i0"].ip), c=1).execute(0).exit_code
        )

    def test_03_ospf(self) -> None:
        """
        Verify that OSPF routing works.
        """
        # Configure ospf routing on router1
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router1.executor, ValidatedFilePath(self.test_resources_path / "ospf" / "router1.conf")
            )
            .execute(0)
            .exit_code,
        )

        # Configure ospf routing on router2
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router2.executor, ValidatedFilePath(self.test_resources_path / "ospf" / "router2.conf")
            )
            .execute(0)
            .exit_code,
        )

        RunCommand(
            self.router1.executor,
            [
                "bash",
                "-c",
                "{ sleep 60; echo show ip ospf; } | vtysh",
            ],
        ).execute(0)

        # ping client1 -> (router1 -> router2) -> client2
        self.assertEqual(
            0, PingCommand(self.client1.executor, IPv4Address(self.client2.ifaces["i0"].ip), c=1).execute(0).exit_code
        )

    def test_04_bgp(self) -> None:
        """
        Verify that BGP routing works.
        """
        # Configure bgp routing on router1
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router1.executor, ValidatedFilePath(self.test_resources_path / "bgp" / "router1.conf")
            )
            .execute(0)
            .exit_code,
        )

        # Configure bgp routing on router2
        self.assertEqual(
            0,
            UpdateRouterConfigFileCommand(
                self.router2.executor, ValidatedFilePath(self.test_resources_path / "bgp" / "router2.conf")
            )
            .execute(0)
            .exit_code,
        )

        RunCommand(
            self.router1.executor,
            [
                "bash",
                "-c",
                "{ sleep 60; echo show ip bgp; } | vtysh",
            ],
        ).execute(0)

        # ping client1 -> (router1 -> router2) -> client2
        self.assertEqual(
            0, PingCommand(self.client1.executor, IPv4Address(self.client2.ifaces["i0"].ip), c=1).execute(0).exit_code
        )

    def test_05_ipsec(self) -> None:
        """
        Verify that IPSEC tunneling works.
        """
        ipsec_setup_router1_path = ValidatedFilePath(self.test_resources_path / "ipsec" / "ipsec_setup_router1.sh")
        ipsec_setup_router2_path = ValidatedFilePath(self.test_resources_path / "ipsec" / "ipsec_setup_router2.sh")

        self.router1.executor.copy_file_to_node(ipsec_setup_router1_path)
        self.router2.executor.copy_file_to_node(ipsec_setup_router2_path)

        # Configure ipsec on router1
        self.assertEqual(
            0,
            RunCommand(self.router1.executor, ["bash", "-c", "/ipsec_setup_router1.sh"]).execute(0).exit_code,
        )

        # Configure ipsec on router2
        self.assertEqual(
            0,
            RunCommand(self.router2.executor, ["bash", "-c", "/ipsec_setup_router2.sh"]).execute(0).exit_code,
        )

        self.assertEqual(0, RunCommand(self.router1.executor, ["bash", "-c", "ipsec status"]).execute(0).exit_code)

        self.assertEqual(0, RunCommand(self.router2.executor, ["bash", "-c", "ipsec status"]).execute(0).exit_code)

        # ping client1 -> (router1 -> router2) -> client2
        self.assertEqual(
            0, PingCommand(self.client1.executor, IPv4Address(self.client2.ifaces["i0"].ip), c=1).execute(0).exit_code
        )

    def test_06_snmp(self) -> None:
        """
        Verify that the FRR SNMP agent works.
        """
        # Check logfiles for SNMP log messages
        zebra_log: str = RunCommand(self.router1.executor, ["cat", "/var/log/frr/zebra.log"]).execute(0).std_out

        self.assertIn("AgentX subagent connected", zebra_log)

        # Test if snmpwalk prints information
        snmpwalk_stdout: str = (
            RunCommand(
                self.router1.executor,
                ["snmpwalk", "-c", "public", "-v1", "localhost", ".1.3.6.1.2.1"],
            )
            .execute(0)
            .std_out
        )

        self.assertIn('iso.3.6.1.2.1.1.5.0 = STRING: "router1"', snmpwalk_stdout)


@unittest.skip("Only run by hand")
@unittest.skipIf(
    not load_k8s_config(),
    "No Kubernetes configuration found, skipping test.",
)
class TestRouterVLAN(unittest.TestCase):
    """
    Class for testing FRR VLAN functionalities.
    """

    rettij: Rettij
    test_base_path: Path
    test_resources_path: Path
    kubeconfig_path: str

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.test_base_path = Path(__file__).parent.absolute()
        cls.test_resources_path = cls.test_base_path.joinpath("resources")

        try:
            cls.kubeconfig_path = ValidatedFilePath.join_paths(PROJECT_ROOT_DIR, "k3s.yaml")
        except InvalidPathException:
            cls.kubeconfig_path = ""

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.rettij = Rettij(file_loglevel=Loglevel.DEBUG, console_loglevel=Loglevel.DEBUG)

        topology_path: ValidatedFilePath = ValidatedFilePath(
            os.path.join(self.test_resources_path, "single_router_vlan_topology.yml")
        )

        self.rettij.init(topology_path)
        self.rettij.create()

        self.router1: Node = self.rettij.nodes["router1"]
        self.switch1: Node = self.rettij.nodes["switch1"]
        self.client1: Node = self.rettij.nodes["client1"]
        self.client2: Node = self.rettij.nodes["client2"]

    def tearDown(self) -> None:
        """
        Clean up before TestCase instance is discarded.
        """
        if self.rettij:
            self.rettij.finalize()

    def test_vlan(self) -> None:
        """
        Verify that 802.1q VLAN works.
        """
        vlan_setup_router1_path = ValidatedFilePath(self.test_resources_path / "vlan" / "vlan_setup_router1.sh")
        vlan_setup_switch1_path = ValidatedFilePath(self.test_resources_path / "vlan" / "vlan_setup_switch1.sh")

        self.router1.executor.copy_file_to_node(vlan_setup_router1_path)
        self.switch1.executor.copy_file_to_node(vlan_setup_switch1_path)

        # Configure vlan on router1
        self.assertEqual(
            0,
            RunCommand(self.router1.executor, ["bash", "-c", "/vlan_setup_router1.sh"]).execute(0).exit_code,
        )

        # Configure vlan on switch1
        self.assertEqual(
            0,
            RunCommand(self.switch1.executor, ["bash", "-c", "/vlan_setup_switch1.sh"]).execute(0).exit_code,
        )

        # Verify 802.1q configuration on router1

        self.assertIn(
            "vlan protocol 802.1Q id 10",
            RunCommand(self.router1.executor, ["/sbin/ip", "-d", "a", "show", "i0.10"]).execute(0).std_out,
        )

        self.assertIn(
            "vlan protocol 802.1Q id 20",
            RunCommand(self.router1.executor, ["/sbin/ip", "-d", "a", "show", "i0.20"]).execute(0).std_out,
        )

        # Verify bridge configuration on switch1
        bridge_stdout: str = RunCommand(self.switch1.executor, ["/sbin/bridge", "vlan"]).execute(0).std_out
        self.assertIn("\t 1 PVID Egress Untagged\n\t 10\n\t 20\n\n", bridge_stdout)
        self.assertIn("i1\t 1 Egress Untagged\n\t 10 PVID Egress Untagged\n\n", bridge_stdout)
        self.assertIn("i2\t 1 Egress Untagged\n\t 20 PVID Egress Untagged\n\n", bridge_stdout)

        # ping client1 -> (router1) -> client2
        self.assertEqual(
            0, PingCommand(self.client1.executor, IPv4Address(self.client2.ifaces["i0"].ip), c=1).execute(0).exit_code
        )

        # traceroute client1 -> (router1) -> client2
        self.assertEqual(
            0,
            RunCommand(self.client1.executor, ["/usr/sbin/traceroute", self.client2.ifaces["i0"].ip.compressed])
            .execute(0)
            .exit_code,
        )
