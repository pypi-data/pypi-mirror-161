import os
import unittest
from datetime import datetime, timedelta
from ipaddress import IPv4Address
from pathlib import Path

from rettij import Rettij
from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.commands.ping_command import PingCommand
from rettij.commands.run_command import RunCommand
from rettij.common.constants import PROJECT_ROOT_DIR
from rettij.common.logging_utilities import Loglevel
from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.invalid_path_exception import InvalidPathException
from rettij.topology.network_components.node import NodeStatus, Node
from tests.src.utils.load_k8s_config import load_k8s_config


@unittest.skipIf(
    not load_k8s_config(),
    "No Kubernetes configuration found, skipping test.",
)
class TestRettij(unittest.TestCase):
    """
    This TestCase contains tests regarding the Rettij main class.
    """

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.test_base_path = os.path.dirname(os.path.realpath(__file__))
        self.topology_path: ValidatedFilePath = ValidatedFilePath(
            Path(self.test_base_path) / "resources" / "topology.yml"
        )
        self.scheduled_sequence_path: Path = Path(self.test_base_path) / "resources" / "scheduled_sequence.py"
        self.script_sequence_path: Path = Path(self.test_base_path) / "resources" / "script_sequence.py"

        self.rettij: Rettij = Rettij(file_loglevel=Loglevel.DEBUG, console_loglevel=Loglevel.DEBUG)

    def tearDown(self) -> None:
        """
        Clean up before TestCase instance is discarded.
        """
        self.rettij.finalize()

    def test_simulator(self) -> None:
        """
        Verify high-level rettij functionality.

        The following aspects are tested:
        - Node reboot
        - Sequence execution
        - Route setup
        - Interface utilization query
        - Traffic Control (tc) setup
        """
        # Try to load a local k3s.yaml for testing, otherwise pass empty path to load from environment
        try:
            kubeconfig_path = ValidatedFilePath.join_paths(PROJECT_ROOT_DIR, "k3s.yaml")
        except InvalidPathException:
            kubeconfig_path = ""

        self.rettij.init(self.topology_path, self.scheduled_sequence_path, kubeconfig_path=kubeconfig_path)

        self.rettij.create()

        self.mount()
        self.reboot()
        self.sequence_execution()
        self.route()
        self.utilization()
        self.tc()

    def mount(self) -> None:
        """
        Verify that directory mounting works.

        Currently verifies the following mechanisms:
        - Mounting via HostPath
        """
        node: Node = self.rettij.nodes["client01"]
        read_cmd: Command = node.run("cat /data/test.txt")
        self.assertEqual("test", read_cmd.result.std_out)

        write_cmd: Command = node.run(["/bin/sh", "-c", "echo test2 > /data/test2.txt"])
        self.assertEqual(0, write_cmd.result.exit_code)

        test2_path: Path = Path(__file__).parent / "resources" / "data" / "test2.txt"
        with open(test2_path, "r") as outfile:
            outfile_contents = outfile.read()
        os.remove(test2_path)
        self.assertEqual("test2\n", outfile_contents)

    def reboot(self) -> None:
        """
        Verify that a Node can be rebooted.

        Reboots client02.
        """
        node: Node = self.rettij.nodes["client02"]
        self.rettij.sm.stop_single_node(node=node)
        self.assertEqual(node.status, NodeStatus.DOWN)
        self.rettij.sm.start_single_node(node=node)
        self.assertEqual(node.status, NodeStatus.UP)

        start_time = datetime.now()
        self.rettij.sm.reboot_node(node=node, min_execution_time=10)
        # Make sure the execution is at least 10 seconds (full accuracy isn't possible).
        self.assertGreater((datetime.now() - start_time).seconds, 9)

    def sequence_execution(self) -> None:
        """
        Verify that a Sequence can be executed.

        TODO: Rework this, as it is both a test of the sequence and of the PingCommand
        Uses client01, client02 and client03.
        """
        # check the return_value of the step() method
        t_scheduled: int = self.rettij.step(0, {})
        self.assertEqual(list(self.rettij.sm.timed_steps.keys())[1], t_scheduled)

        self.rettij.step(1, {})

        ping_result_01 = self.rettij.sm.timed_steps[0].commands[0].result
        ping_result_02 = self.rettij.sm.timed_steps[1].commands[0].result

        self.assertEqual(ping_result_01.exit_code, 0)
        self.assertEqual(ping_result_01.values["transmitted"], 1)
        self.assertEqual(ping_result_01.values["received"], 1)
        self.assertEqual(ping_result_01.values["loss"], 0)

        self.assertEqual(ping_result_02.exit_code, 0)
        self.assertEqual(ping_result_02.values["transmitted"], 1)
        self.assertEqual(ping_result_02.values["received"], 1)
        self.assertEqual(ping_result_02.values["loss"], 0)

        self.rettij.load_sequence(self.script_sequence_path)
        self.rettij.step(2, {})

    def route(self) -> None:
        """
        Verify that routes are set correctly.

        Uses client01.
        """
        if len(self.rettij.nodes["client02"].routes) != 0:
            route_result: CommandResult = RunCommand(self.rettij.nodes["client02"].executor, ["route", "-n"]).execute()
            routing_table = route_result.std_out.split()
            self.assertTrue(self.rettij.nodes.client02.routes[0].gateway.compressed in routing_table)
            self.assertTrue(self.rettij.nodes.client02.routes[1].network.network_address.compressed in routing_table)
            self.assertTrue(self.rettij.nodes.client02.routes[1].gateway.compressed in routing_table)
            self.assertTrue(str(self.rettij.nodes.client02.routes[1].metric) in routing_table)
            self.assertTrue(self.rettij.nodes.client02.routes[2].network.network_address.compressed in routing_table)
            self.assertTrue(self.rettij.nodes.client02.routes[2].gateway.compressed in routing_table)
            self.assertTrue(str(self.rettij.nodes.client02.routes[2].metric) in routing_table)
        else:
            self.fail("Node 'client01' has no routes set.")

    def utilization(self) -> None:
        """
        Verify that the node utilization can be queried.

        Uses client02 and client01.
        """
        node = self.rettij.nodes.client02
        # Start a Ping asynchronously: docker02.i0 -> client01.i0
        client01_ip: str = self.rettij.nodes["client01"].ifaces["i0"].ip.compressed
        async_ping_cmd: Command = node.ping(target=client01_ip, detached=True)
        # Get utilization of docker2.i0
        utilization = node.ifaces["i0"].utilization()
        # Verify that all return values are integer
        self.assertIsInstance(utilization["rx"], int)
        self.assertIsInstance(utilization["tx"], int)
        self.assertIsInstance(utilization["total"], int)
        # Verify that return values for rx and tx are greater 0
        self.assertGreater(utilization["rx"], 0)
        self.assertGreater(utilization["tx"], 0)
        # Verify that total matches rx + tx
        self.assertEqual(utilization["total"], utilization["rx"] + utilization["tx"])
        # Stop asynchronous ping
        node.stop_detached(async_ping_cmd)

    def tc(self) -> None:
        """
        Verify that bandwidth and delay can be set.

        Uses client04 and client01.
        DOES NOT WORK ON DOCKER FOR WINDOWS WSL2. The kernel module for netem is missing from WSL2.
        """
        client04: Node = self.rettij.nodes["client04"]
        client01_ip: IPv4Address = self.rettij.nodes["client01"].ifaces["i0"].ip

        # Verify that the tc data was applied correctly
        tc_result = RunCommand(client04.executor, ["tc", "qdisc"]).execute()
        tc_result_stdout = tc_result.std_out.split(" ")
        iface_data_rate: str = tc_result_stdout[(tc_result_stdout.index("rate")) + 1].strip()
        iface_delay: str = tc_result_stdout[(tc_result_stdout.index("delay")) + 1].strip()
        self.assertEqual(iface_data_rate, "56Kbit")  # data rate is provided in Byte but printed in Bit, thus 8*10kbps
        self.assertEqual(iface_delay, "100.0ms")

        # Validate that the delay has an actual impact on communications
        delay = client04.ifaces["i0"].channel.delay
        if not delay:
            self.fail("Not delay set for interface 'i0' of node 'client04'. Delay is required for the test.")
        delay_ping_res = PingCommand(  # Send 1 regular packet (56 bytes) with a timeout of 10 sec
            client04.executor,
            target=client01_ip,
            c=1,
            W=10,
        ).execute()
        self.assertTrue(delay_ping_res.values["average"] >= float((delay.split("ms"))[0]))

        # Validate that the data rate has an actual impact on communications using a ping packet 2 times the size of the channels data rate
        # Since this is round trip, the total time is 4x the data rate.
        start_timestamp = datetime.now()
        PingCommand(  # Send 1 packet of 14 kbyte (= 112 kbit) with a timeout of 10 sec
            client04.executor,
            target=client01_ip,
            c=1,
            s=14000,
            W=10,
        ).execute()
        stop_timestamp = datetime.now()
        self.assertTrue((stop_timestamp - start_timestamp) >= timedelta(seconds=4))
