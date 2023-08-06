import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml

from rettij.common.constants import TESTS_DIR
from rettij.common.logging_utilities import Loglevel, LoggingSetup
from rettij.common.validated_path import ValidatedDirPath, ValidatedFilePath
from rettij.exceptions.invalid_path_exception import InvalidPathException
from rettij.exceptions.topology_exception import TopologyException
from rettij.topology.hooks.abstract_connect_hook import AbstractConnectHook
from rettij.topology.hooks.abstract_post_connect_hook import AbstractPostConnectHook
from rettij.topology.hooks.abstract_post_deploy_hook import AbstractPostDeployHook
from rettij.topology.hooks.abstract_pre_deploy_hook import AbstractPreDeployHook
from rettij.topology.hooks.abstract_pre_teardown_hook import AbstractPreTeardownHook
from rettij.topology.node_configurations.kubernetes_pod_config import KubernetesPodConfig
from rettij.topology.node_executors.kubernetes_pod_executor import KubernetesPodExecutor
from rettij.topology.topology_exporter_mermaid import TopologyExporterMermaid
from rettij.topology.topology_reader import TopologyReader


class TopologyReaderTest(unittest.TestCase):
    """
    This TestCase contains tests regarding the TopologyReader.
    """

    test_base_path: str
    test_resources_path: ValidatedDirPath
    topo_path: ValidatedFilePath
    topo_valid_gw: ValidatedFilePath
    topo_invalid_gw: ValidatedFilePath
    topo_invalid_gw_nw: ValidatedFilePath
    topo_without_mac_path: ValidatedFilePath
    topo_with_invalid_mac_path: ValidatedFilePath
    wrong_path: str
    invalid_topo_path: ValidatedFilePath

    custom_components_dir_path: ValidatedDirPath
    custom_components_topology_path: ValidatedFilePath

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.test_base_path = os.path.dirname(os.path.realpath(__file__))
        cls.test_resources_path = ValidatedDirPath.join_paths(cls.test_base_path, "resources")

        cls.topo_path = ValidatedFilePath.join_paths(
            TESTS_DIR, "shared_resources", "topologies", "topology_with_host.yml"
        )
        cls.topo_valid_gw = ValidatedFilePath.join_paths(cls.test_resources_path, "topology_with_valid_gateways.yml")
        cls.topo_invalid_gw = ValidatedFilePath.join_paths(
            cls.test_resources_path, "topology_with_invalid_gateways.yml"
        )
        cls.topo_invalid_gw_nw = ValidatedFilePath.join_paths(
            cls.test_resources_path, "topology_with_invalid_gateway_network.yml"
        )
        cls.topo_without_mac_path = ValidatedFilePath.join_paths(cls.test_resources_path, "topology_without_mac.yml")
        cls.topo_with_invalid_mac_path = ValidatedFilePath.join_paths(
            cls.test_resources_path, "topology_with_invalid_mac.yml"
        )
        cls.wrong_path = "wrong_path"
        cls.invalid_topo_path = ValidatedFilePath.join_paths(cls.test_resources_path, "invalid_topology.yml")

        cls.custom_components_dir_path = ValidatedDirPath.join_paths(TESTS_DIR, "shared_resources", "custom_components")
        cls.custom_components_topology_path = ValidatedFilePath.join_paths(
            cls.test_base_path, "resources", "custom_components_topology.yml"
        )

        uid: str = datetime.now().strftime("%H%M%S")
        print(f"Test timestamp: {uid}")
        LoggingSetup.initialize_logging(uid, Loglevel.DEBUG, Loglevel.DEBUG)

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.topo_reader: TopologyReader = TopologyReader()

    def test_reader_with_valid_topo(self) -> None:
        """
        Verify that a valid topology can be parsed and exported as Mermaid diagram.
        """
        try:
            nodes, channels = self.topo_reader.read(self.topo_path)
            self.assertIn("c0", channels)
            self.assertEqual(len(channels["c0"].connected_node_names_and_data_rates), 2)
            self.assertIn("c1", channels)
            self.assertEqual(len(channels["c1"].connected_node_names_and_data_rates), 2)
            test_node_type1 = nodes.switch0.node_type
            test_node_type2 = nodes.client1.node_type
            self.assertEqual("switch", test_node_type1)
            self.assertEqual("container", test_node_type2)

            TopologyExporterMermaid(nodes, channels).export(
                Path(tempfile.mkdtemp()) / "test_reader_with_valid_topo.mermaid"
            )
        except Exception as e:
            self.fail(msg=str(e))

    def test_reader_with_invalid_topo(self) -> None:
        """
        Verify that an invalid topology raises a TopologyException.
        """
        self.assertRaises(TopologyException, self.topo_reader.read, self.invalid_topo_path)

    def test_reader_with_invalid_topo_path(self) -> None:
        """
        Verify that an invalid path to a topology file raises an InvalidPathException.
        """
        with self.assertRaises(InvalidPathException):
            # noinspection PyTypeChecker
            # PyTypeChecker disabled because the wrong data type is intentional
            self.topo_reader.read(self.wrong_path)  # type: ignore

    def test_reader_with_invalid_component_path(self) -> None:
        """
        Verify that an invalid path to a component file raises a ValueError.
        """
        topo_path: ValidatedFilePath = ValidatedFilePath.join_paths(
            TESTS_DIR, "shared_resources", "topologies", "topology_wrong_service.yml"
        )

        with self.assertRaises(ValueError):
            self.topo_reader.read(topo_path)

    def test_reader_with_single_node_and_no_interface(self) -> None:
        """
        Verify that a single Node with no interfaces can be parsed and exported.
        """
        topo_path: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path, "topology_with_single_node_and_no_interface.yml"
        )

        try:
            nodes, channels = self.topo_reader.read(topo_path)
            ifaces_length: int = len(nodes["n0"].ifaces)
            self.assertEqual(
                ifaces_length,
                0,
                msg=f"[{self.__class__.__name__}.test_reader_with_various_configs]: Testing reading of correct topology without interfaces failed. "
                f"Length of dictionary 'interfaces' of Node 'n0' should be 0, but is {ifaces_length}",
            )

            TopologyExporterMermaid(nodes, channels).export(
                Path(tempfile.mkdtemp()) / "test_reader_with_no_interfaces.mermaid"
            )
        except Exception as e:
            self.fail(
                msg=f"[{self.__class__.__name__}.test_reader_with_various_configs]: Testing reading of correct topology without interfaces failed. "
                f"Error: {e}"
            )

    def test_reader_with_invalid_ips(self) -> None:
        """
        Verify that invalid IP addresses raise TopologyExceptions.
        """
        topology_file_invalid_ip: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path,
            "topology_with_invalid_ip.yml",
        )
        topology_file_invalid_subnet: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_resources_path,
            "topology_with_invalid_subnet_mask.yml",
        )

        with self.assertRaises(TopologyException):
            self.topo_reader.read(topology_file_invalid_ip)

        with self.assertRaises(TopologyException):
            self.topo_reader.read(topology_file_invalid_subnet)

    def test_reader_without_mac(self) -> None:
        """
        Verify that Interface MACs are both properly parsed and auto-generated if not present, as well as exported as Mermaid diagram.
        """
        try:
            nodes, channels = self.topo_reader.read(self.topo_without_mac_path)

            # test if mac was generated succesfully
            self.assertNotEqual(None, nodes["n1"].ifaces["i0"].mac)
            # test if explicitly defined mac is not overwritten
            self.assertEqual("1A:2B:3C:4D:5E:02", nodes["n2"].ifaces["i0"].mac)

            TopologyExporterMermaid(nodes, channels).export(
                Path(tempfile.mkdtemp()) / "test_reader_without_mac.mermaid"
            )
        except Exception as e:
            self.fail(msg=str(e))

    def test_reader_with_invalid_mac(self) -> None:
        """
        Verify that an invalid MAC address raise a TopologyException.
        """
        self.assertRaises(TopologyException, self.topo_reader.read, self.topo_with_invalid_mac_path)

    def test_file_path_class(self) -> None:
        """
        Verify that the ValidatedFilePath class is represented as string.
        """
        file_path = ValidatedFilePath(self.topo_path)

        self.assertIsInstance(file_path.__repr__(), str)
        self.assertIsInstance(file_path.__str__(), str)

    def test_relative_path_replacement(self) -> None:
        """
        Verify that relative path replacement during topology parsing is functioning correctly.

        Uses the `rettij/tests/src/unit_tests/test_topology/resources/custom_components_topology.yml` topology.
        """
        nodes, channels = self.topo_reader.read(self.custom_components_topology_path, self.custom_components_dir_path)
        self.assertEqual(
            (Path(self.custom_components_topology_path).parent / ".." / "some-path" / "abc").resolve().as_posix(),
            nodes["n0"].custom_config["some_path"],
        )

    def test_valid_custom_components(self) -> None:
        """
        Verify that valid custom components are parsed and exported as Mermaid diagram.
        """
        try:
            nodes, channels = self.topo_reader.read(
                self.custom_components_topology_path, self.custom_components_dir_path
            )
            if not isinstance(nodes["n0"].executor_config, KubernetesPodConfig):
                raise RuntimeError("test_valid_custom_components can only be used on Kubernetes nodes!")
            n0_config: KubernetesPodConfig = nodes["n0"].executor_config
            if not isinstance(nodes["n1"].executor_config, KubernetesPodConfig):
                raise RuntimeError("test_valid_custom_components can only be used on Kubernetes nodes!")
            n1_config: KubernetesPodConfig = nodes["n1"].executor_config
            self.assertIsInstance(n0_config.pod_spec, Dict)
            self.assertIsInstance(n1_config.pod_spec, Dict)

            TopologyExporterMermaid(nodes, channels).export(
                Path(tempfile.mkdtemp()) / "test_valid_custom_components.mermaid"
            )
        except Exception as e:
            self.fail(msg=str(e))

    def test_valid_gateways(self) -> None:
        """
        Verify that valid routes are parsed and exported as Mermaid diagram.
        """
        try:
            nodes, channels = self.topo_reader.read(self.topo_valid_gw)
            self.assertEqual(nodes["router1"].routes[0].gateway.compressed, "10.1.10.1")
            self.assertEqual(nodes["client1"].routes[0].gateway.compressed, "10.1.10.1")
            self.assertTrue(len(nodes["client2"].routes) == 0)

            TopologyExporterMermaid(nodes, channels).export(Path(tempfile.mkdtemp()) / "test_valid_gateways.mermaid")
        except Exception as e:
            self.fail(msg=str(e))

    def test_invalid_gateways(self) -> None:
        """
        Verify that invalid routes are logged with level WARNING.
        """
        with self.assertLogs(level="WARNING", logger="rettij") as assert_inv_gw:
            self.topo_reader.read(self.topo_invalid_gw_nw)
            self.assertTrue(
                any("Default gateway" in output for output in assert_inv_gw.output),
                msg=f"[{self.__class__.__name__}.test_invalid_gateways]: "
                f"Testing for invalid gateway address detection failed! Expected warning was not found in the log.",
            )

    def test_missing_custom_components(self) -> None:
        """
        Verify that missing custom components raise a ValueError.
        """
        custom_components_topology_path: ValidatedFilePath = ValidatedFilePath.join_paths(
            self.test_base_path, "resources", "missing_components_topology.yml"
        )
        with self.assertRaises(ValueError):
            self.topo_reader.read(custom_components_topology_path, self.custom_components_dir_path)

    def test_nonexistent_custom_components_dir(self) -> None:
        """
        Verify that an invalid path to the custom components directory raises an InvalidPathException.
        """
        with self.assertRaises(InvalidPathException):
            ValidatedDirPath.join_paths(self.test_base_path, "resources", "non-existent_folder")

    def test_component_hooks(self) -> None:
        """
        Verify that component hooks are parsed and exported as Mermaid diagram.
        """
        try:
            nodes, channels = self.topo_reader.read(
                self.custom_components_topology_path, self.custom_components_dir_path
            )

            n0_hooks = nodes["n0"].executor_config.hooks
            self.assertIsInstance(n0_hooks, dict)

            self.assertIn("pre-deploy", n0_hooks.keys())
            self.assertIn("post-deploy", n0_hooks.keys())
            self.assertIn("connect", n0_hooks.keys())
            self.assertIn("post-connect", n0_hooks.keys())
            self.assertIn("pre-teardown", n0_hooks.keys())

            self.assertIsInstance(n0_hooks["pre-deploy"][0], AbstractPreDeployHook)
            self.assertIsInstance(n0_hooks["post-deploy"][0], AbstractPostDeployHook)
            self.assertIsInstance(n0_hooks["connect"][0], AbstractConnectHook)
            self.assertIsInstance(n0_hooks["post-connect"][0], AbstractPostConnectHook)
            self.assertIsInstance(n0_hooks["pre-teardown"][0], AbstractPreTeardownHook)

            TopologyExporterMermaid(nodes, channels).export(Path(tempfile.mkdtemp()) / "test_component_hooks.mermaid")

        except InvalidPathException as e:
            self.fail(msg=str(e))

    def test_inplace_components(self) -> None:
        """
        Verify that in-place components (defined directly in the topology, no component file) are parsed and exported as Mermaid diagram.
        """
        try:
            nodes, channels = self.topo_reader.read(
                ValidatedFilePath.join_paths(self.test_base_path, "resources", "topology_with_inline_components.yml")
            )

            # TODO: Check node configuration
            node1 = nodes["node1"]
            node2 = nodes["node2"]
            node3 = nodes["node3"]

            node1.initiate_executor(namespace_id="test")
            node2.initiate_executor(namespace_id="test")
            node3.initiate_executor(namespace_id="test")

            assert isinstance(node1.executor, KubernetesPodExecutor)
            assert isinstance(node2.executor, KubernetesPodExecutor)
            assert isinstance(node3.executor, KubernetesPodExecutor)
            node1_executor: KubernetesPodExecutor = node1.executor
            node2_executor: KubernetesPodExecutor = node2.executor
            node3_executor: KubernetesPodExecutor = node3.executor

            node1_pod_manifest = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": "node1"},
                "spec": {
                    "containers": [
                        {
                            "image": "frihsb/rettij_simple-runner:latest",
                            "name": "rettij-simple-runner",
                            "securityContext": {"privileged": True},
                            "tty": True,
                        }
                    ]
                },
            }
            node2_pod_manifest = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": "node2"},
                "spec": {
                    "containers": [
                        {
                            "image": "frihsb/rettij_simple-runner:latest",
                            "name": "simple-runner",
                            "securityContext": {"privileged": True},
                            "tty": True,
                        }
                    ]
                },
            }
            node3_pod_manifest = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": "node3"},
                "spec": {
                    "containers": [
                        {
                            "image": "nginx",
                            "name": "nginx",
                            "securityContext": {"privileged": True},
                            "tty": True,
                        }
                    ]
                },
            }

            self.assertEqual(node1_executor.manifest, node1_pod_manifest)
            self.assertEqual(node2_executor.manifest, node2_pod_manifest)
            self.assertEqual(node3_executor.manifest, node3_pod_manifest)

            TopologyExporterMermaid(nodes, channels).export(
                Path(tempfile.mkdtemp()) / "test_inplace_components.mermaid"
            )
        except Exception as e:
            self.fail(msg=str(e))

        with self.assertRaises(TopologyException):
            self.topo_reader.read(
                ValidatedFilePath.join_paths(
                    self.test_base_path, "resources", "topology_with_faulty_inline_components.yml"
                )
            )

    def test_topology_version(self) -> None:
        """
        Verify the topology version handling.

        The following scenarios are tested:

            - topology major version too low
            - topology major version too high
            - topology minor version too low
            - topology version valid

        """
        topo_tmp_dir_path: Path = Path(tempfile.mkdtemp())

        maj_low_topo_version_file_path = topo_tmp_dir_path / "maj_low_version_topology.yml"
        maj_high_topo_version_file_path = topo_tmp_dir_path / "maj_high_version_topology.yml"
        min_high_topo_version_file_path = topo_tmp_dir_path / "min_high_version_topology.yml"
        correct_topo_version_file_path = topo_tmp_dir_path / "correct_version_topology.yml"

        with open(self.topo_path, "r") as topo_file:
            topology = yaml.safe_load(topo_file)

        print("Test topology major version LOWER than supported versions")
        with open(maj_low_topo_version_file_path, "w") as topo_file:
            topo_version: str = f"{int(self.topo_reader.MAJOR_VERSION) - 1}.0"
            topology["version"] = topo_version
            yaml.dump(topology, stream=topo_file)

        with self.assertRaises(
            TopologyException,
            msg=f"{self.__class__}.test_topology_version failed: "
            f"No error was raised when topology major version was lower than supported version (should raise TopologyException).",
        ):
            self.topo_reader.read(ValidatedFilePath(maj_low_topo_version_file_path))

        print("Test topology major version HIGHER than supported versions")
        with open(maj_high_topo_version_file_path, "w") as topo_file:
            topo_version = f"{int(self.topo_reader.MAJOR_VERSION) + 1}.0"
            topology["version"] = topo_version
            yaml.dump(topology, stream=topo_file)

        with self.assertRaises(
            TopologyException,
            msg=f"{self.__class__}.test_topology_version failed: "
            f"No error was raised when topology major version was higher than supported version (should raise TopologyException).",
        ):
            self.topo_reader.read(ValidatedFilePath(maj_high_topo_version_file_path))

        print("Test topology minor version HIGHER than supported versions")
        with open(min_high_topo_version_file_path, "w") as topo_file:
            topo_version = f"{self.topo_reader.MAJOR_VERSION}.{int(self.topo_reader.MINOR_VERSION) + 1}"
            topology["version"] = topo_version
            yaml.dump(topology, stream=topo_file)

        with self.assertLogs(
            "rettij",
            level="WARNING",
        ):
            self.topo_reader.read(ValidatedFilePath(min_high_topo_version_file_path))

        print("Test topology version matching supported versions")
        with open(correct_topo_version_file_path, "w") as topo_file:
            topo_version = f"{self.topo_reader.MAJOR_VERSION}.{int(self.topo_reader.MINOR_VERSION)}"
            topology["version"] = topo_version
            yaml.dump(topology, stream=topo_file)

        try:
            self.topo_reader.read(ValidatedFilePath(correct_topo_version_file_path))
        except ValueError as e:
            self.fail(
                f"{self.__class__}.test_topology_version failed: "
                f"Correct version topology should have been parsed, but an error was raised: {e}"
            )

    def test_reader_with_unconnected_channels(self) -> None:
        """
        Verify that a valid topology containing unconnected Channels (only one end connected) can be parsed and and exported as Mermaid diagram.
        """
        try:
            nodes, channels = self.topo_reader.read(
                ValidatedFilePath.join_paths(self.test_base_path, "resources", "topology_with_unconnected_channels.yml")
            )

            TopologyExporterMermaid(nodes, channels).export(
                Path(tempfile.mkdtemp()) / "test_reader_with_unconnected_channels.mermaid"
            )
        except Exception as e:
            self.fail(msg=str(e))


# def testMosaikDataFieldGetter(self) -> None:
#     topo_store: TopologyStorage = self.topo_reader.read(self.simple_topo_path)
#     is_power = topo_store.nodes["n0"].getMosaikData("power")
#     is_bananensaft = topo_store.nodes["n0"].getMosaikData("bananensaft")
#     self.assertEqual(4, is_power)
#     self.assertEqual(2, is_bananensaft)


# def testMosaikDataFieldSetter(self) -> None:
#     topo_store: TopologyStorage = self.topo_reader.read(self.simple_topo_path)
#     topo_store.nodes["n0"].setMosaikData("power", 42)
#     topo_store.nodes["n0"].setMosaikData("bananensaft", 23)
#
#     is_power = topo_store.nodes["n0"].getMosaikData("power")
#     is_bananensaft = topo_store.nodes["n0"].getMosaikData("bananensaft")
#
#     self.assertEqual(42, is_power)
#     self.assertEqual(23, is_bananensaft)
