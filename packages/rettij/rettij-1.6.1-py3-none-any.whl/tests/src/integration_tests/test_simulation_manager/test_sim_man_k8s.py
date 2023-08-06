import os
import tempfile
import unittest
from datetime import datetime
from typing import Dict

import yaml

import kubernetes
import kubernetes.client.rest
from rettij.commands.command import Command
from rettij.common.constants import COMPONENTS_DIR
from rettij.common.logging_utilities import LoggingSetup, Loglevel
from rettij.common.uid import UID
from rettij.common.validated_path import ValidatedFilePath
from rettij.simulation_manager import SimulationManager
from rettij.topology.network_components.node import Node
from rettij.topology.node_configurations.kubernetes_pod_config import KubernetesPodConfig
from rettij.topology.node_executors.kubernetes_pod_executor import KubernetesPodExecutor
from rettij.topology.node_executors.node_executor import NodeExecutor
from tests.src.utils.load_k8s_config import load_k8s_config


@unittest.skipIf(not load_k8s_config(), "No Kubernetes configuration found, skipping test.")
class TestSimulationManagerKubernetes(unittest.TestCase):
    """
    This TestCase contains tests regarding Kubernetes functionality of the SimulationManager.
    """

    test_base_path: str

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.test_base_path = os.path.dirname(os.path.realpath(__file__))

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.uid: str = datetime.now().strftime("%H%M%S")
        print(f"Test timestamp: {self.uid}")

        LoggingSetup.initialize_logging(self.uid, Loglevel.DEBUG, Loglevel.DEBUG)
        self.logger = LoggingSetup.submodule_logging(self._testMethodName)

        self.sm = SimulationManager(uid=self.uid)
        namespace: kubernetes.client.V1Namespace = self.sm._create_k8s_namespace(f"rettij-{self.uid}")
        self.namespace_id = namespace.metadata.name

        # Ensure the simulation network exists
        try:
            self.sm.kubernetes_api.read_namespace(self.namespace_id)
        except kubernetes.client.rest.ApiException as e:
            if e.status == 404:
                self.fail(msg=f"Namespace {self.namespace_id} was not found in the list of networks!")
            else:
                self.fail(msg=f"Kubernetes API error when running 'read_namespace({self.namespace_id})'!")

    def tearDown(self) -> None:
        """
        Clean up before TestCase instance is discarded.
        """
        self.logger.info("### Cleaning up test environment... ###")
        self.sm.cleanup(f"rettij-{self.uid}")
        self.logger.info("### Test environment cleaned up! ###")

    def test_sim_man(self) -> None:
        """
        Verify SimulationManager functionality.

        The following aspects are tested:
        - Node deployment (Kubernetes)
        - Asynchronous / detached command execution
        - File copy between the local machine and the Nodes
        - Value exchange between rettij and the Nodes
        - Node deployment (Kubernetes, multiple containers in a component)
        """
        self.step_deploy_regular_node()
        self.step_async()
        self.step_copy()
        self.step_value_rw()
        self.step_deploy_multiple_services()

    def step_deploy_regular_node(self) -> None:
        """
        Verify that a regular Node can be deploy in Kubernetes.
        """
        self.logger.debug("Running step_deploy_regular_node...")

        pod_spec_file = ValidatedFilePath.join_paths(
            COMPONENTS_DIR,
            "simple-runner",
            "simple-runner.yaml",
        )

        with open(pod_spec_file, "r") as fd:
            pod_spec: Dict = yaml.safe_load(fd)

        self.test_node: Node = Node(
            KubernetesPodExecutor,
            f"test-node-{UID.generate_uid()}",
            "container",
            executor_config=KubernetesPodConfig(
                pod_spec=pod_spec, hooks={"pre-deploy": [], "post-deploy": [], "pre-teardown": []}
            ),
        )
        self.test_node.initiate_executor(namespace_id=self.namespace_id)

        # Deploy the default test node
        self.assertIsInstance(
            self.sm._deploy_pod_by_node(self.test_node, self.namespace_id),
            kubernetes.client.V1Pod,
            msg=f"The deployment test for regular node {self.test_node.name} failed.",
        )

    def step_async(self) -> None:
        """
        Verify that commands can be executed asynchronously.
        """
        self.logger.debug("Running step_async...")

        # Start async command
        async_cmd: Command = self.test_node.run(["bash", "-c", "while true; do date; sleep 2; done;"], detached=True)

        # Check if result has exit code 0
        exit_code: int = async_cmd.result.exit_code
        self.assertEqual(
            exit_code,
            0,
            msg=f"Testing the interaction exit code for the AsyncScriptCommand failed, as exit code was {exit_code} rather than 0. Result: {async_cmd.result}",
        )

        # Kill async command
        kill_cmd = self.test_node.stop_detached(async_cmd)

        # Check if command was executed properly
        self.assertEqual(kill_cmd.result.exit_code, 0, msg="KillSessionCommand failed, as the exit code was not 0.")

    def step_copy(self) -> None:
        """
        Verify that files can be copied between the local machine and the Nodes.
        """
        self.logger.debug("Running step_copy...")

        # Test with plain text on different paths
        self._copy_plain("/test", "test.txt")
        self._copy_plain("/", "test.txt")

        # Test with binary pcap file
        test_file_name: str = "test.pcap"
        test_file_path: ValidatedFilePath = ValidatedFilePath.join_paths(self.test_base_path, "resources", "test.pcap")
        self.assertTrue(
            self.test_node.copy_file_to_node(test_file_path),
            msg=f"Testing copying a binary pcap file to container {self.test_node.executor.name} failed.",
        )
        with tempfile.TemporaryDirectory() as dst_dir:
            # Get file from container
            self.test_node.copy_file_from_node(f"/{test_file_name}", dst_dir=dst_dir)
            test_out_path: str = os.path.join(dst_dir, test_file_name)
            # Check if local file was created
            self.assertTrue(
                os.path.exists(test_out_path),
                msg=f"Testing copying a binary file from container {self.test_node.executor.name} failed, as there was no local file created.",
            )
            # Check if local file has correct contents
            import filecmp

            self.assertTrue(
                filecmp.cmp(
                    test_file_path, test_out_path, shallow=False  # Compare actual contents, not just signatures
                ),
                msg=f"Testing copying a file from container {self.test_node.executor.name} failed, as the copied file contents are incorrect.",
            )

    def _copy_plain(self, cont_file_dir: str, test_file_name: str) -> None:
        """
        Copy a file to and from the Node.

        :param cont_file_dir: File base directory in the container (both for placement and retrieval).
        :param test_file_name: File name (both local and remote).
        """
        # Put file in container
        test_file_path = ValidatedFilePath.join_paths(self.test_base_path, "resources", test_file_name)
        self.assertTrue(
            self.test_node.copy_file_to_node(test_file_path, dst_dir=cont_file_dir),
            msg=f"Testing copying a plain text file to container {self.test_node.executor.name} failed.",
        )

        with tempfile.TemporaryDirectory() as dst_dir:
            # Get file from container
            self.test_node.copy_file_from_node(f"{os.path.join(cont_file_dir, test_file_name)}", dst_dir=dst_dir)
            test_out_path: str = os.path.join(dst_dir, test_file_path)
            # Check if local file was created
            self.assertTrue(
                os.path.exists(test_out_path),
                msg=f"Testing copying a file from container {self.test_node.executor.name} failed, as there was no local file created.",
            )
            # Check if local file has correct contents
            with open(test_out_path, "r") as f:
                content = f.read()
                self.assertEqual(
                    content,
                    "Test Archive\nHow's it going?",
                    msg=f"Testing copying a file from container {self.test_node.executor.name} failed, as the copied file contents are incorrect.",
                )

    def step_value_rw(self) -> None:
        """
        Verify that data can be exchanged between the local machine and the Nodes.
        """
        test_key = "test_key"
        test_value_01 = "test_value_01"
        test_value_02 = "test_value_02"

        test_kv_01: dict = {test_key: test_value_01}
        test_kv_02: dict = {test_key: test_value_02}

        executor: NodeExecutor = self.test_node.executor

        # Try to read a value without writing one first. Should log a info message.
        with self.assertLogs(level="INFO", logger="rettij") as assert_log:
            executor.read_values(file="values.txt")
        self.assertTrue(
            any("No attributes stored on" in output for output in assert_log.output),
        )

        # test writing a new key and reading it
        executor.write_values(test_kv_01, file="values.txt")
        return_value = executor.read_values([test_key], file="values.txt")[test_key]
        self.assertEqual(test_value_01, return_value)

        # test updating existing key
        executor.write_values(test_kv_02, file="values.txt")
        return_value = executor.read_values([test_key], file="values.txt")[test_key]
        self.assertNotEqual(test_value_01, return_value, msg=f"Value was not updated!  Current value: {return_value}")
        self.assertEqual(test_value_02, return_value, msg=f"New value was not written! Current value: {return_value}")

        # Try to write without supplying a key. Should raise a ValueError.
        with self.assertRaises(ValueError):
            executor.write_values({}, file="values.txt")

        # Try to read a non-existent key. Should log a warning.
        key = "abc"
        with self.assertLogs(level="WARNING", logger="rettij") as assert_log:
            executor.read_values([key], file="values.txt")
        self.assertTrue(
            any(f"Attribute key {key} not found on" in output for output in assert_log.output),
        )

    def step_deploy_multiple_services(self) -> None:
        """
        Verify that a Node whose component contains multiple containers can be deploy in Kubernetes.
        """
        pod_spec_file = ValidatedFilePath.join_paths(
            self.test_base_path,
            "resources",
            "multiple-services.yaml",
        )

        with open(pod_spec_file, "r") as fd:
            pod_spec: Dict = yaml.safe_load(fd)

        self.logger.debug("Running step_deploy_multiple_services...")
        test_node_multiple_containers = Node(
            KubernetesPodExecutor,
            "test-node-mult-svcs",
            "container",
            executor_config=KubernetesPodConfig(
                pod_spec=pod_spec, hooks={"pre-deploy": [], "post-deploy": [], "pre-teardown": []}
            ),
        )
        test_node_multiple_containers.initiate_executor(namespace_id=self.namespace_id)
        self.assertIsInstance(
            self.sm._deploy_pod_by_node(test_node_multiple_containers, self.namespace_id),
            kubernetes.client.V1Pod,
            msg=f"The deployment test for regular node {test_node_multiple_containers.name} failed.",
        )
        if isinstance(test_node_multiple_containers.executor, KubernetesPodExecutor):
            pod: KubernetesPodExecutor = test_node_multiple_containers.executor
            num_cont: int = len(pod.api_pod.spec.containers)
            self.assertEqual(
                num_cont,
                2,
                msg=f"The deployment test for regular node {test_node_multiple_containers.name} failed. The pod contained {num_cont} containers when it should contain 2.",
            )
