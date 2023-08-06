import os
import unittest
from ipaddress import IPv4Address
from typing import List, Dict, Union, Any
from unittest.mock import MagicMock

import kubernetes
import kubernetes.client.rest
import yaml

from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.executor_not_available_exception import ExecutorNotAvailableException
from rettij.topology.node_configurations.kubernetes_pod_config import KubernetesPodConfig
from rettij.topology.network_components.node import Node
from rettij.topology.node_executors.kubernetes_pod_executor import KubernetesPodExecutor


class V1ContainerStateDummy:
    """
    Dummy of 'kubernetes.client.V1ContainerState'.
    """

    def __init__(self, running: bool, terminated: bool, waiting: bool) -> None:
        """
        Initialize a V1ContainerStateDummy object.

        :param running: Is the container running?
        :param terminated: Is the container terminated?
        :param waiting: Is the container waiting?
        """
        self.running: bool = running
        self.terminated: bool = terminated
        self.waiting: bool = waiting


class V1ContainerStatusDummy:
    """
    Dummy of 'kubernetes.client.V1ContainerStatus'.
    """

    def __init__(self, running: bool, terminated: bool, waiting: bool) -> None:
        """
        Initialize a V1ContainerStatusDummy object.

        :param running: Is the container running?
        :param terminated: Is the container terminated?
        :param waiting: Is the container waiting?
        """
        self.state: V1ContainerStateDummy = V1ContainerStateDummy(running, terminated, waiting)


class V1PodStatusDummy:
    """
    Dummy of 'kubernetes.client.V1PodStatus'.
    """

    pass


class V1PodStatusHealthyDummy(V1PodStatusDummy):
    """
    Concrete implementation of V1PodStatusDummy representing a healthy status.
    """

    def __init__(self) -> None:
        """
        Initialize a new PodStatus dummy with two healthy containers.

        * Container one is running, and therefore healthy.
        * Container two is also running, and therefore also healthy.
        """
        self.container_statuses: List[V1ContainerStatusDummy] = [
            V1ContainerStatusDummy(running=True, terminated=False, waiting=False),
            V1ContainerStatusDummy(running=True, terminated=False, waiting=False),
        ]


class V1PodStatusFaultyDummy(V1PodStatusDummy):
    """
    Concrete implementation of V1PodStatusDummy representing a faulty status.
    """

    def __init__(self) -> None:
        """
        Initialize a new PodStatus dummy with three containers, some of which are faulty.

        * Container one is running, and therefore healthy.
        * Container two is terminated, and therefore faulty.
        * Container three is waiting, and therefore also faulty (at least for some cases).
        """
        self.container_statuses: List[V1ContainerStatusDummy] = [
            V1ContainerStatusDummy(running=True, terminated=False, waiting=False),
            V1ContainerStatusDummy(running=False, terminated=True, waiting=False),
            V1ContainerStatusDummy(running=False, terminated=False, waiting=True),
        ]


class V1PodStatusIpDummy(V1PodStatusDummy):
    """
    Concrete implementation of V1PodStatusDummy containing an IP address.
    """

    def __init__(self, ip: str) -> None:
        """
        Initialize a V1PodStatusIpDummy object.

        :param ip: IP address for the Pod.
        """
        self.pod_ip = ip


class V1PodDummy(MagicMock):
    """
    Dummy of 'kubernetes.client.V1Pod'.
    """

    def __init__(self, status: V1PodStatusDummy) -> None:
        """
        Initialize a V1PodDummy object.

        :param status: V1PodStatusDummy object.
        """
        super().__init__()

        self.api_version: str = "v1"
        self.status: V1PodStatusDummy = status


class KubernetesApiDummy(MagicMock, kubernetes.client.CoreV1Api):
    """
    Dummy of 'kubernetes.client.CoreV1Api'.
    """

    def __init__(self, pod: V1PodDummy) -> None:
        """
        Initialize a KubernetesApiDummy object.

        :param pod: V1PodDummy object.
        """
        super().__init__()
        self.read_namespaced_pod = MagicMock(return_value=pod)


class KubernetesApiErrorDummy(MagicMock, kubernetes.client.CoreV1Api):
    """
    Dummy of kubernetes.client.CoreV1Api that raises kubernetes.client.rest.ApiException.
    """

    def __init__(self, status: int) -> None:
        """
        Initialize a KubernetesApiErrorDummy object.

        :param status: Status code (for errors etc.)
        """
        super().__init__()
        self.status: int = status

    def read_namespaced_pod(self, **kwargs: Any) -> None:
        """
        Read a namespaced Pod.

        Overrides kubernetes.client.CoreV1Api.read_namespaced_pod() to always return an APIException.

        :param kwargs: Required by signature, not used.
        """
        raise kubernetes.client.rest.ApiException(status=self.status, reason="Test")


class TestPod(unittest.TestCase):
    """
    This TestCase contains tests regarding the KubernetesPod class.
    """

    def setUp(self) -> None:
        """
        Set up the TestCase instance variables.
        """
        self.test_base_path = os.path.dirname(os.path.realpath(__file__))

    def test_is_running(self) -> None:
        """
        Verify that Pod health states are properly processed by Pod.is_running().
        """
        # Create healthy Pod by creating a Pod dummy with a status "healthy" dummy
        self.healthy_pod_dummy: V1PodDummy = V1PodDummy(V1PodStatusHealthyDummy())
        healthy_api_dummy: KubernetesApiDummy = KubernetesApiDummy(self.healthy_pod_dummy)
        self.healthy_pod: KubernetesPodExecutor = KubernetesPodExecutor(name="healthy_pod")
        self.healthy_pod.initialize(manifest={}, api_instance=healthy_api_dummy)

        # Create faulty Pod by creating a Pod dummy with a status "faulty" dummy
        self.faulty_pod_dummy: V1PodDummy = V1PodDummy(V1PodStatusFaultyDummy())
        faulty_api_dummy: KubernetesApiDummy = KubernetesApiDummy(self.faulty_pod_dummy)
        self.faulty_pod: KubernetesPodExecutor = KubernetesPodExecutor(name="faulty_pod")
        self.faulty_pod.initialize(manifest={}, api_instance=faulty_api_dummy)

        self.assertTrue(self.healthy_pod.is_running())
        self.assertFalse(self.faulty_pod.is_running())

    def test_name(self) -> None:
        """
        Verify that the Pod name can be set.
        """
        pod_name: str = "test_pod"
        pod: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod.initialize(manifest={})
        self.assertEqual(pod.name, pod_name)

    def test_namespace(self) -> None:
        """
        Verify that the Pod namespace can be set.
        """
        pod_name: str = "test_pod"
        pod_namespace_id: str = "test_namespace_id"
        pod: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod.initialize(manifest={}, namespace_id=pod_namespace_id)
        self.assertEqual(pod.namespace_id, pod_namespace_id)

    def test_manifest(self) -> None:
        """
        Verify that the Pod manifest can be set.
        """
        pod_name: str = "test_pod"
        pod_manifest: Dict[str, Union[str, int, List, Dict]] = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "test_node_id"},
            "spec": "pod_spec_placeholder",
        }
        pod: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod.initialize(manifest=pod_manifest)
        self.assertEqual(pod.manifest, pod_manifest)

    def test_is_deployed(self) -> None:
        """
        Verify that the Pod deployment status can be set.
        """
        pod_name: str = "test_pod"
        pod: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod.initialize(manifest={})
        self.assertFalse(pod.is_deployed)
        pod.is_deployed = True
        self.assertTrue(pod.is_deployed)

    def test_api_pod(self) -> None:
        """
        Verify that the Pod API object can be set.
        """
        pod_name: str = "test_pod"
        pod_dummy: V1PodDummy = V1PodDummy(V1PodStatusHealthyDummy())

        api_dummy: KubernetesApiDummy = KubernetesApiDummy(pod_dummy)
        pod: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod.initialize(manifest={}, api_instance=api_dummy)
        self.assertIsInstance(pod.api_pod, V1PodDummy)

        api_404_dummy: KubernetesApiErrorDummy = KubernetesApiErrorDummy(404)
        pod_404: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod_404.initialize(manifest={}, api_instance=api_404_dummy)
        with self.assertRaises(ExecutorNotAvailableException):
            _ = pod_404.api_pod

        api_403_dummy: KubernetesApiErrorDummy = KubernetesApiErrorDummy(403)
        pod_403: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod_403.initialize(manifest={}, api_instance=api_403_dummy)
        with self.assertRaises(kubernetes.client.rest.ApiException):
            _ = pod_403.api_pod

    def test_ip(self) -> None:
        """
        Verify that the Pod IP address can be set.
        """
        pod_name: str = "test_pod"
        pod_ip: str = "10.0.0.1"
        pod_dummy: V1PodDummy = V1PodDummy(V1PodStatusIpDummy(pod_ip))
        api_dummy: KubernetesApiDummy = KubernetesApiDummy(pod_dummy)
        pod: KubernetesPodExecutor = KubernetesPodExecutor(name=pod_name)
        pod.initialize(manifest={}, api_instance=api_dummy)
        self.assertEqual(pod.ip, IPv4Address(pod_ip))

    def test_generate_config(self) -> None:
        """
        Verify that the Pod configuration can be generated and set.
        """
        node_name = "test_node"
        pod_namespace_id: str = "test_namespace_id"
        pod_spec_file = ValidatedFilePath.join_paths(self.test_base_path, "resources", "simple-runner.yaml")
        with open(pod_spec_file, "r") as fd:
            pod_spec: Dict = yaml.safe_load(fd)

        executor_config: KubernetesPodConfig = KubernetesPodConfig(
            pod_spec=pod_spec,
            hooks={"pre-deploy": [], "post-deploy": [], "pre-teardown": []},
            execution_host="k8s-worker-01",
        )

        node: Node = Node(KubernetesPodExecutor, name=node_name, node_type="container", executor_config=executor_config)

        kwargs: Dict = {"node": node, "namespace_id": pod_namespace_id}

        # Retrieved from the output of running Pod.generate_config() with the current configuration
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "test_node"},
            "spec": {
                "containers": [
                    {
                        "image": "frihsb/rettij_simple-runner:latest",
                        "name": "simple-runner",
                        "securityContext": {"privileged": True},
                        "tty": True,
                    }
                ],
                "nodeName": "k8s-worker-01",
            },
        }

        # Expected return values: (<node_name>, <pod_manifest>, <pod_namespace_id>
        pod_config = node.executor.generate_config(**kwargs)
        self.assertEqual(pod_config["manifest"], pod_manifest)
        self.assertEqual(pod_config["namespace_id"], pod_namespace_id)

    @unittest.skip("No mocking of API for Pod.copy_file_from_node() available.")
    def test_copy_file_from_node(self) -> None:
        """
        Verify that files can be retrieved from the Node.

        NOT IMPLEMENTED!
        """
        pass

    @unittest.skip("No mocking of API for Pod.copy_file_to_node() available.")
    def test_copy_file_to_node(self) -> None:
        """
        Verify that files can put on the Node.

        NOT IMPLEMENTED!
        """
        pass

    @unittest.skip("No mocking of API for Pod.write_value() available.")
    def test_write_value(self) -> None:
        """
        Verify that values can be written to the Node.

        NOT IMPLEMENTED!
        """
        pass

    @unittest.skip("No mocking of API for Pod.read_value() available.")
    def test_read_value(self) -> None:
        """
        Verify that values can be read from the Node.

        NOT IMPLEMENTED!
        """
        pass

    @unittest.skip("No mocking of API for Pod.execute_command() available.")
    def test_execute_command(self) -> None:
        """
        Verify that commands can be executed on the Node.

        NOT IMPLEMENTED!
        """
        pass
