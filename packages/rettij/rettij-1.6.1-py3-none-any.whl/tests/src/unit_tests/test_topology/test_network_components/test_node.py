import os
import unittest
from ipaddress import IPv4Address
from typing import Dict
from unittest.mock import MagicMock, patch

import yaml
from rettij.commands.ping_command import PingCommand
from rettij.commands.run_command import RunCommand
from rettij.common.validated_path import ValidatedFilePath, ValidatedDirPath
from rettij.topology.network_components.node import Node, NodeStatus
from rettij.topology.node_configurations.kubernetes_pod_config import KubernetesPodConfig
from rettij.topology.node_executors.kubernetes_pod_executor import KubernetesPodExecutor


class TestNode(unittest.TestCase):
    """
    This TestCase contains tests regarding the Node class.
    """

    test_base_path: str
    test_resources_path: ValidatedDirPath
    hooks: dict

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.test_base_path = os.path.dirname(os.path.realpath(__file__))
        cls.test_resources_path = ValidatedDirPath.join_paths(cls.test_base_path, "resources")

        cls.hooks = {"pre-deploy": [], "post-deploy": [], "pre-teardown": []}

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        node_executor = MagicMock()
        config = MagicMock()
        # noinspection PyTypeChecker
        self.node: Node = Node(node_executor, "n0", "container", config)
        # specifically test use node with multiple interfaces
        channel0, channel1 = MagicMock(), MagicMock()
        iface0, iface1 = MagicMock(), MagicMock()
        iface0.name, iface1.name = "i0", "i1"
        self.node.add_interface(channel0, iface0)
        self.node.add_interface(channel1, iface1)

    def test_node_with_kompose_deployment(self) -> None:
        """
        Verify that a Node defined by a Kompose-generated deployment file can be parsed.
        """
        config_file_path = ValidatedFilePath.join_paths(self.test_resources_path, "simple-runner.kompose.yaml")
        with open(config_file_path, "r") as fd:
            pod_spec: Dict = yaml.safe_load(fd)
        config: KubernetesPodConfig = KubernetesPodConfig(pod_spec, self.hooks)
        node: Node = Node(KubernetesPodExecutor, "n0", "container", config)
        node.initiate_executor()

        if isinstance(node.executor, KubernetesPodExecutor):
            pod: KubernetesPodExecutor = node.executor
            self.assertIn("spec", pod.manifest)
            spec = pod.manifest.get("spec")
            if isinstance(spec, Dict):
                self.assertIn("containers", spec)
            else:
                self.fail("Pod spec is not a dictionary.")

    def test_node_with_kubectl_deployment(self) -> None:
        """
        Verify that a Node defined by a kubectl-generated deployment file can be parsed.
        """
        config_file_path = ValidatedFilePath.join_paths(self.test_resources_path, "simple-runner.kubectl.yaml")
        with open(config_file_path, "r") as fd:
            pod_spec: Dict = yaml.safe_load(fd)
        config: KubernetesPodConfig = KubernetesPodConfig(pod_spec, self.hooks)
        node: Node = Node(KubernetesPodExecutor, "n0", "container", config)
        node.initiate_executor()

        if isinstance(node.executor, KubernetesPodExecutor):
            pod: KubernetesPodExecutor = node.executor
            self.assertIn("spec", pod.manifest)
            spec = pod.manifest.get("spec")
            if isinstance(spec, Dict):
                self.assertIn("containers", spec)
            else:
                self.fail("Pod spec is not a dictionary.")

    def test_node_with_spec(self) -> None:
        """
        Verify that a Node defined by a component template can be parsed.
        """
        config_file_path = ValidatedFilePath.join_paths(self.test_resources_path, "simple-runner.spec.yaml")
        with open(config_file_path, "r") as fd:
            pod_spec: Dict = yaml.safe_load(fd)
        config: KubernetesPodConfig = KubernetesPodConfig(pod_spec, self.hooks)
        node: Node = Node(KubernetesPodExecutor, "n0", "container", config)
        node.initiate_executor()

        if isinstance(node.executor, KubernetesPodExecutor):
            pod: KubernetesPodExecutor = node.executor
            self.assertIn("spec", pod.manifest)
            spec = pod.manifest.get("spec")
            if isinstance(spec, Dict):
                self.assertIn("containers", spec)
            else:
                self.fail("Pod spec is not a dictionary.")

    def test_node_type(self) -> None:
        """
        Verify that a Node type handling works.

        Tested:
        - Valid Node type
        - Invalid Node type (raises ValueError)
        """
        invalid_node_type = "some-non-existant-type"
        valid_node_type = "container"
        with self.assertRaises(ValueError):
            self.node.node_type = invalid_node_type
        self.node.node_type = valid_node_type
        self.assertEqual(valid_node_type, self.node.node_type)

    def test_run(self) -> None:
        """
        Verify that the Node.run() method handles as expected.
        """
        # Basically replace the object at the given path by a Mock object. Later we use this variable p and do funny
        # stuff with it (i.e. give the execute_command() function a fixed return value for this test)
        with patch("rettij.topology.network_components.node.Node.executor") as p:
            command = RunCommand(p, ["foo"])
            self.assertEqual(command.result.exit_code, self.node.run("foo", exec_now=False).result.exit_code)

    def test_ping(self) -> None:
        """
        Verify that the Node.ping() method handles as expected.
        """
        # Basically replace the object at the given path by a Mock object. Later we use this variable p and do funny
        # stuff with it (i.e. give the execute_command() function a fixed return value for this test)
        with patch("rettij.topology.network_components.node.Node.executor") as p:
            ping_command = PingCommand(p, target=IPv4Address("10.1.1.1"), c=3)
            self.assertEqual(
                ping_command.result.exit_code, self.node.ping(target="10.1.1.1", c=3, exec_now=False).result.exit_code
            )

    def test_name(self) -> None:
        """
        Verify that a Node name handling works.

        Tested:
        - Valid Node names
        - Invalid node names
        """
        for valid_node_name in ["node123" "node-name123" "node.name.123"]:
            self.node.name = valid_node_name
            self.assertEqual(valid_node_name, self.node.name)

        for invalid_node_name in [
            "NodeWithCapitalLetters",  # name must be lowercase
            "node_with_underscores",  # name may not contain special characters except dashes and dots
            "-node-starts-with-dash",  # name may not start with a dash
            "node-ends-with-dash-",  # name may not end with a dash
            "node.with.too.many.dots",  # name may only consist of a maximum of 4 DNS labels separated by dots
        ]:
            with self.assertRaises(ValueError):
                self.node.name = invalid_node_name

    def test_status(self) -> None:
        """
        Verify that the initial Node status is set correctly.
        """
        self.assertEqual(NodeStatus.DOWN, self.node.status)

    def test_str(self) -> None:
        """
        Verify that the Node has the expected string representation.
        """
        node_str: str = r"""
                         Node: n0
                         ------------------------------
                         Interfaces: i0, i1
                         Attributes:
                           executor: .*
                           executor_config: .*
                           iface: Available interface names: i0, i1
                           ifaces: Available interface names: i0, i1
                           name: n0
                           node_type: container
                           routes: \[\]
                           status: NodeStatus\.DOWN
                         Methods: add_interface\(\), copy_file_from_node\(\), copy_file_to_node\(\), get_data\(\), initiate_executor\(\), ping\(\), reboot\(\), run\(\), set_data\(\), shell\(\), shutdown\(\), stop_detached\(\)
                         """.replace(
            "                         ", ""
        )  # Remove leading spaces

        self.assertRegex(str(self.node), node_str)

    def test_repr(self) -> None:
        """
        Verify that the Node has the expected __repr__ representation.
        """
        self.assertEqual(repr(self.node), str(self.node))

    def test_eq(self) -> None:
        """
        Verify that the Node equals() method works.
        """
        self.assertTrue(self.node == self.node)
        self.assertFalse(self.node == 1)

    def test_interface_container_str(self) -> None:
        """
        Verify that the InterfaceContainer has the expected string representation.
        """
        self.assertEqual("Available interface names: i0, i1", str(self.node.ifaces))

    def test_interface_container_repr(self) -> None:
        """
        Verify that the InterfaceContainer has the expected __repr__ representation.
        """
        self.assertEqual(str(self.node.ifaces), repr(self.node.ifaces))
