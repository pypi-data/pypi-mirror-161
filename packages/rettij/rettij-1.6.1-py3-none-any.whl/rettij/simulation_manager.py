from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Tuple, Any, Callable

import kubernetes.client
import kubernetes.client.rest
import urllib3
from kubernetes.client import V1Namespace

from rettij.commands.command import Command
from rettij.common.is_suited_host_system import is_suited_host_system
from rettij.common.logging_utilities import LoggingSetup
from rettij.exceptions.host_not_available_exception import HostNotAvailableException
from rettij.exceptions.namespace_exception import NamespaceException
from rettij.network_manager import NetworkManager
from rettij.step import Step
from rettij.topology.hooks.abstract_connect_hook import AbstractConnectHook
from rettij.topology.hooks.abstract_post_connect_hook import AbstractPostConnectHook
from rettij.topology.hooks.abstract_post_deploy_hook import AbstractPostDeployHook
from rettij.topology.hooks.abstract_pre_deploy_hook import AbstractPreDeployHook
from rettij.topology.hooks.abstract_pre_teardown_hook import AbstractPreTeardownHook
from rettij.topology.network_components.channel import Channel
from rettij.topology.network_components.node import NodeStatus, Node
from rettij.topology.node_configurations.kubernetes_pod_config import KubernetesPodConfig
from rettij.topology.node_container import NodeContainer
from rettij.topology.node_executors.host_executor import Host
from rettij.topology.node_executors.kubernetes_pod_executor import KubernetesPodExecutor


class SimulationManager:
    """
    This class manages most of the simulation handling.
    """

    namespace: V1Namespace

    def __init__(self, uid: str) -> None:
        """
        Initialize a SimulationManager object.

        :param uid: Session identifier for this simulation run.
        """
        self.lock = Lock()
        self.is_finalized: bool = False

        self.uid = uid
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        self.timed_steps: Dict[int, Step] = {}
        self.current_time: int = 0

        self.kubernetes_api = kubernetes.client.CoreV1Api()

        self.__network_manager = NetworkManager()

        self.channels: Dict[str, Channel] = {}
        self.nodes: NodeContainer = NodeContainer()

        # Flag set when all Nodes are deployed
        self.all_nodes_deployed: bool = False
        # Storage for connection parameters passed via .connect()
        self.connections_parameters: List[Tuple[Node, Node, Any]] = []

        self.logger.debug(f"Simulation manager created with uid {self.uid}.")

    # ######### Start simulation managements functions ######### #

    def create_simulation(self) -> None:
        """
        Create the simulation environment.

        Method execution is synchronized on the SimulationManager lock.
        """
        if not isinstance(self.nodes, NodeContainer):
            raise ValueError("Parameter 'nodes' must be of type 'NodeContainer'!")

        self._check_api_available(error_on_fail=True)

        self.namespace: kubernetes.client.V1Namespace = self._create_k8s_namespace(f"rettij-{self.uid}")

        # Deploy all nodes
        for node_id, node in self.nodes.items():
            node.status = NodeStatus.STARTING
            self._deploy_single_node(node)

        # Build VXLAN tunnels for all nodes
        for node_id, node in self.nodes.items():
            self._connect_single_node(node)

        # Run all hooks that require all nodes to be fully connected
        for node_id, node in self.nodes.items():
            self._run_single_node_online_hooks(node)
            node.status = NodeStatus.UP

        self.all_nodes_deployed = True

        # kubectl exec commands to connect directly to the containers
        self.logger.info("Commands to connect directly to the simulation nodes:")
        for node in list(self.nodes.values()):
            if isinstance(node.executor, KubernetesPodExecutor):
                self.logger.info(
                    f"{node.name}: kubectl exec -it --namespace={self.namespace.metadata.name} {node.executor.name} -- /bin/bash"
                )
            if isinstance(node.executor, Host):
                self.logger.info(f"{node.name}: host system (just open a shell)")

    def _check_api_available(self, error_on_fail: bool = False) -> bool:
        """
        Check if the Kubernetes API is available.

        :param error_on_fail: When True, raise a HostNotAvailableException if the API is not available. Default: False.
        :return: True if the API is available, else False.
        :raise: HostNotAvailableException
        """
        try:
            self.kubernetes_api.get_api_resources()
            return True
        except Exception as e:
            if error_on_fail:
                raise HostNotAvailableException(self.kubernetes_api.api_client.configuration.host, str(e)) from None
            else:
                return False

    def start_single_node(self, node: Node) -> None:
        """
        Start a single node during the simulation runtime.

        :param node: Node to start.
        """
        node.status = NodeStatus.STARTING
        self._deploy_single_node(node)
        self._connect_single_node(node, rebuild_tunnels=True)
        self._run_single_node_online_hooks(node)
        node.status = NodeStatus.UP

    def _deploy_single_node(self, node: Node) -> None:
        """
        Start a single node.

        Method execution is synchronized on the SimulationManager lock.

        :param node: Node to start.
        """
        # Run pre-deploy hooks
        self._execute_node_pre_deploy_hooks(node)

        # Stop execution if simulation is finalized
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            self.logger.debug(f"Starting single node {node.name}...")

            if node.node_type != "host":
                node.initiate_executor(namespace_id=self.namespace.metadata.name)

                started: bool = False
                while not started:
                    try:
                        self._deploy_pod_by_node(node, namespace_id=self.namespace.metadata.name)
                        started = True
                    except kubernetes.client.rest.ApiException as e:
                        # If we delete and re-create in quick succession, the deletion might not be finished yet.
                        if e.status == 409 and e.body["reason"] == "AlreadyExists":
                            time.sleep(1)
                        else:
                            raise e

            elif node.node_type == "host":
                # Ensure all scripts on the host are executable
                if is_suited_host_system():
                    from rettij.common.constants import RESOURCES_DIR
                    import subprocess

                    for path in (Path(RESOURCES_DIR) / "scripts").glob("*.sh"):
                        result = subprocess.run(["chmod", "+x", path.as_posix()])
                        if result.returncode != 0:
                            raise RuntimeError(str(result))

            self.logger.debug(f"Single node {node.name} started.")

        finally:
            # Make sure the lock is always released.
            # Will even be called when returning or raising an error.
            self.lock.release()

    def _connect_single_node(self, node: Node, rebuild_tunnels: bool = False) -> None:
        """
        Create the VXLAN tunnels for a single node.

        Method execution is synchronized on the SimulationManager lock.

        :param node: Node to create VXLAN interfaces for.
        :param rebuild_tunnels: Also rebuild tunnel interfaces of neighboring nodes.
        """
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            # Build VXLAN tunnels to/with all neighbours
            self.__network_manager.connect_node_neighbours(node, self.nodes, rebuild_tunnel=rebuild_tunnels)
        finally:
            self.lock.release()

    def _run_single_node_online_hooks(self, node: Node) -> None:
        """
        Run all hooks for a node that require all nodes to be fully connected.

        :param node: Node to run hooks for.
        """
        # Run post-deploy hooks
        self._execute_node_post_deploy_hooks(node)
        # Run connect hooks
        self._setup_connections(node)
        # Run post-connect hooks
        self._execute_node_post_connect_hooks(node)

    def stop_single_node(self, node: Node, namespace_id: str = "") -> None:
        """
        Stop a single node during the simulation runtime.

        Method execution is synchronized on the SimulationManager lock.

        :param node: Node to stop.
        :param namespace_id: Namespace of the Node Pod
        :raises: kubernetes.client.rest.ApiException
        """
        node.status = NodeStatus.STOPPING
        if not namespace_id:
            namespace_id = self.namespace.metadata.name

        # Run pre-teardown hooks
        self._execute_node_pre_teardown_hooks(node)

        # Stop execution if simulation is finalized
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            self.logger.debug(f"Stopping single node {node.name}...")

            try:
                self.logger.info(f"Logs for {node.name}:\n{node.executor.logs}")
                self.kubernetes_api.delete_namespaced_pod(
                    name=node.name, namespace=namespace_id, grace_period_seconds=0
                )
                node.status = NodeStatus.DOWN
            except kubernetes.client.rest.ApiException as e:
                if e.status != 404:
                    raise e
            except Exception as e:
                self.logger.warning(f"Error stopping {node.name}: '{e.__class__}:{e}'")

            self.logger.debug(f"Single node {node.name} stopped.")
        finally:
            # Make sure the lock is always released.
            # Will even be called when returning or raising an error.
            self.lock.release()

    def reboot_node(self, node: Node, min_execution_time: int = 30) -> None:
        """
        Reboot a single Node in (somewhat) fixed time.

        Reboots a single Node using the `start_single_node()` and `stop_single_node()` commands.
        In order to simplify co-simulation, this method will only return once the minimum execution time is reached.
        It may run longer though, depending on the time it takes to restart the Node.

        :param node: Node to restart.
        :param min_execution_time: Minimum execution time in seconds.
        """
        # Store the current time
        start_time = datetime.now()

        # Stop and then start the Node
        self.stop_single_node(node)
        self.start_single_node(node)

        # Calculate the difference between the minimum execution time and the time passed since start_time
        # Then wait for that difference if the current execution time is smaller than the minimum execution time
        wait_time = min_execution_time - (datetime.now() - start_time).seconds
        if wait_time > 0:
            time.sleep(wait_time)

    def cleanup(self, namespace_id: str = "", kubernetes_api: Optional[kubernetes.client.CoreV1Api] = None) -> None:
        """
        Clean up the simulation environment.

        :param namespace_id: (Optional) Namespace id.
        :param kubernetes_api: (Optional) Kubernetes API client to use for cleanup. Required if called during `sys.exit`.
        """
        if kubernetes_api:
            self.kubernetes_api = kubernetes_api

        self.all_nodes_deployed = False

        self.logger.info("Removing remaining simulation artifacts...")

        for node in self.nodes.values():
            try:
                self.stop_single_node(node, namespace_id)
                if node.node_type == "host":
                    self._cleanup_rettij_host_interfaces(node)
                node.status = NodeStatus.DOWN
            except Exception:
                pass  # if Node cannot be stopped individually, simply continue as the namespace will be deleted anyways
        self._remove_k8s_namespace(namespace_id, detached=True)

        self.logger.info("Simulation artifacts removed!")

    def connect(self, source_node: Node, target_node: Node, **kwargs: Any) -> None:
        """
        Connect one Node to another.

        :param source_node: Base Node that the connection is initiated on
        :param target_node: Node to connect the base Node to
        :param kwargs: Custom parameters. Contents depend on the specific implementation.
        """
        self.connections_parameters.append((source_node, target_node, kwargs))

        if self.all_nodes_deployed:
            self._setup_connections()

    def _setup_connections(self, node: Optional[Node] = None) -> None:
        """
        Run ConnectHooks for all connections stored in self.connections_parameters.

        :param node: Only run connect hooks for this specific node.
        """
        # Iterate through all parameter set in reversed order, so indices in the list that have not yet been access are preserved when removing an element.
        # Basically, we only remove elements with indices higher than the ones we still want to access, therefore indices moving up.
        for parameters in reversed(self.connections_parameters):
            source_node, target_node, kwargs = parameters
            if node:
                if source_node == node:
                    # Remove the specific parameter set to avoid executing them multiple times
                    self.connections_parameters.remove(parameters)
                    self._execute_node_connect_hooks(source_node, target_node, **kwargs)
            else:
                self._execute_node_connect_hooks(source_node, target_node, **kwargs)
                # Remove the specific parameter set to avoid executing them multiple times
                self.connections_parameters.remove(parameters)

    def _execute_node_pre_deploy_hooks(self, node: Node) -> None:
        """
        Execute the pre-deploy hooks defined in the Node's component.

        :param node: Node to execute the hooks for.
        """
        # Stop execution if simulation is finalized
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            for hook in node.executor_config.hooks["pre-deploy"]:
                self.logger.debug(f"Executing pre-connect hook for Node {node.name}...")
                if isinstance(hook, AbstractPreDeployHook):
                    hook.execute(node, self.nodes)
        finally:
            # Make sure the lock is always released.
            # Will even be called when returning or raising an error.
            self.lock.release()

    def _execute_node_post_deploy_hooks(self, node: Node) -> None:
        """
        Execute the post-deployment hooks defined in the Node's component.

        :param node: Node to execute the hooks for.
        """
        # Stop execution if simulation is finalized
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            for hook in node.executor_config.hooks["post-deploy"]:
                self.logger.debug(f"Executing post-deploy hook for Node {node.name}...")
                if isinstance(hook, AbstractPostDeployHook):
                    hook.execute(node, self.nodes)
        finally:
            # Make sure the lock is always released.
            # Will even be called when returning or raising an error.
            self.lock.release()

    def _execute_node_connect_hooks(self, source_node: Node, target_node: Node, **kwargs: Any) -> None:
        """
        Execute the post-connect hooks defined in the Node's component.

        :param source_node: Base Node that the connection is initiated on.
        :param target_node: Node to connect the base Node to.
        :param kwargs: Custom parameters. Contents depend on the specific implementation.
        """
        # Stop execution if simulation is finalized
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            for hook in source_node.executor_config.hooks["connect"]:
                self.logger.debug(f"Executing connect hook for Node {source_node.name}...")
                if isinstance(hook, AbstractConnectHook):
                    hook.execute(source_node, target_node, **kwargs)
        finally:
            # Make sure the lock is always released.
            # Will even be called when returning or raising an error.
            self.lock.release()

    def _execute_node_post_connect_hooks(self, node: Node) -> None:
        """
        Execute the post-connect hooks defined in the Node's component.

        :param node: Node to execute the hooks for.
        """
        # Stop execution if simulation is finalized
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            for hook in node.executor_config.hooks["post-connect"]:
                self.logger.debug(f"Executing post-connect hook for Node {node.name}...")
                if isinstance(hook, AbstractPostConnectHook):
                    hook.execute(node)
        finally:
            # Make sure the lock is always released.
            # Will even be called when returning or raising an error.
            self.lock.release()

    def _execute_node_pre_teardown_hooks(self, node: Node) -> None:
        """
        Execute the pre-teardown hooks defined in the Node's component.

        :param node: Node to execute the hooks for.
        """
        # Stop execution if simulation is finalized
        if not self.is_finalized:
            self.lock.acquire()
        else:
            return None
        try:
            for hook in node.executor_config.hooks["pre-teardown"]:
                self.logger.debug(f"Executing pre-teardown hook for Node {node.name}...")
                if isinstance(hook, AbstractPreTeardownHook):
                    hook.execute(node, self.nodes)
        finally:
            # Make sure the lock is always released.
            # Will even be called when returning or raising an error.
            self.lock.release()

    # ######### Start simulation managements functions ######### #

    # ######### Start Host management methods ######### #

    def _cleanup_rettij_host_interfaces(self, node: Node) -> None:
        """
        Remove the host system interface created by rettij.

        :param node: Host system node.
        """
        for iface in node.ifaces.values():
            if iface.remove_commands:
                self.logger.debug(f"Cleaning up host interface {iface.name}...")
                if is_suited_host_system():
                    import subprocess

                    for command in iface.remove_commands:
                        remove_result: subprocess.CompletedProcess = subprocess.run(
                            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                        if remove_result.returncode != 0:
                            self.logger.error(remove_result)
                        else:
                            self.logger.debug(remove_result)
                else:
                    print(f"Run the following commands to manually remove rettij interface {iface.name}:")
                    for command in iface.remove_commands:
                        print(" ".join(command))

    # ######### Start Kubernetes management methods ######### #

    def _check_k8s_namespace(self, namespace_id: str) -> None:
        """
        Validate a Kubernetes namespace.

        TODO: Move to KubernetesManager
        For internal use only.

        :param namespace_id: ID of the namespace to be validated.
        :raises NamespaceException: If the namespace is not in phase "Active" and / or faulty.
        """
        try:
            namespace: V1Namespace = self.kubernetes_api.read_namespace(name=namespace_id)

            # Possible namespaces phases:
            # - Active: the namespace is in use
            # - Terminating: the namespace is being deleted, and cannot be used for new objects
            # https://kubernetes.io/docs/tasks/administer-cluster/namespaces/

            if namespace.status.phase == "Terminating":
                raise NamespaceException(namespace_id, NamespaceException.TERMINATING) from None

        except kubernetes.client.rest.ApiException as e:
            if e.status == 404:
                raise NamespaceException(namespace_id, NamespaceException.NOT_FOUND) from None
            else:
                self.logger.error(e)
                raise NamespaceException(namespace_id, NamespaceException.OTHER) from None

    def _create_k8s_namespace(self, namespace_id: str) -> kubernetes.client.V1Namespace:
        """
        Create a Kubernetes namespace.

        Will delete any namespace of the same name first.
        TODO: Move to KubernetesManager
        Method execution is synchronized on the SimulationManager lock.
        For internal use only.

        :param namespace_id: Namespace identifier / name.
        """
        self.logger.debug(f"Creating namespace {namespace_id} ...")
        try:
            self.kubernetes_api.read_namespace(name=namespace_id)
            self.logger.debug(f"Namespace {namespace_id} already exists! Deleting old namespace.")
            self._remove_k8s_namespace(namespace_id, propagation_policy="Foreground")
        except kubernetes.client.rest.ApiException as e:
            if e.status != 404:
                raise e

        ns_meta = kubernetes.client.V1ObjectMeta(name=namespace_id)
        ns_body = kubernetes.client.V1Namespace(metadata=ns_meta)
        ns: kubernetes.client.V1Namespace = self.kubernetes_api.create_namespace(ns_body)
        self.logger.debug(f"Namespace {namespace_id} created!")
        return ns

    def _remove_k8s_namespace(
        self, namespace_id: str, detached: bool = False, propagation_policy: str = "Foreground"
    ) -> None:
        """
        Delete a Kubernetes namespace.

        TODO: Move to KubernetesManager
        Deletion is immediately due to a grace period of 0 seconds.
        Will return once the namespace is fully terminated.
        For internal use only.

        :param namespace_id: Namespace identifier / name.
        :param detached: If `True`, return immediately after triggering namespace removal. If `False`, wait until namespace is fully terminated. Default: `False`.
        :raises kubernetes.client.rest.ApiException: The namespace deletion API request failed with a status other than 404 (namespace doesn't exist).
        """
        try:
            self.logger.debug(f"Deleting namespace {namespace_id} ...")
            self.kubernetes_api.delete_namespace(
                name=namespace_id, grace_period_seconds=0, propagation_policy=propagation_policy
            )
            if detached:
                return
            phase = self.kubernetes_api.read_namespace(name=namespace_id).status.phase
            while phase == "Terminating":
                phase = self.kubernetes_api.read_namespace(name=namespace_id).status.phase
                time.sleep(1)

        except kubernetes.client.rest.ApiException as e:
            if e.status == 404:
                # Continue if the namespace does not exist.
                pass
            elif e.status == 409 and e.reason == "Conflict":
                # Continue if the namespace is already being deleted for some reason.
                pass
            else:
                raise e
        except urllib3.exceptions.MaxRetryError:
            # Continue if the connection to the server is refused, or the request timed out.
            # If rettij encounters an error before the Kubernetes config has been loaded, the request to delete the namespace be refused since the cluster master server is not known.
            pass
        self.logger.debug(f"Namespace {namespace_id} removed!")

    def _deploy_pod_by_node(self, node: Node, namespace_id: str) -> Optional[kubernetes.client.V1Pod]:
        """
        Deploy a Kubernetes executor for a simulation node.

        TODO: Move to KubernetesManager
        For internal use only.

        :param node: Simulation node.
        :param namespace_id: Target Kubernetes namespace.
        :return: Deployed executor object.
        """
        if not isinstance(node.executor, KubernetesPodExecutor):
            raise RuntimeError("_deploy_pod_by_node can only be used on Kubernetes nodes!")
        if not isinstance(node.executor_config, KubernetesPodConfig):
            raise RuntimeError("_deploy_pod_by_node can only be used on Kubernetes nodes!")

        pod: KubernetesPodExecutor = node.executor

        try:
            self._check_k8s_namespace(namespace_id)
        except NamespaceException:
            return None

        try:
            self.kubernetes_api.read_namespaced_pod(name=node.name, namespace=namespace_id)
        except kubernetes.client.rest.ApiException as e:
            if e.status != 404:
                raise e

        while True:
            try:
                self.kubernetes_api.create_namespaced_pod(body=pod.manifest, namespace=namespace_id)
                break
            except kubernetes.client.rest.ApiException as e:
                if e.status == 500:
                    time.sleep(1)
                else:
                    raise e

        while True:
            time.sleep(1)
            v1pod: kubernetes.client.V1Pod = pod.api_pod
            phase: str = v1pod.status.phase
            if phase == "Running":
                break
            elif phase in ["Failed", "Succeeded", "Unknown"]:
                raise RuntimeError(f"Pod {v1pod.metadata.name} in unexpected state {phase}!")
            elif phase == "Pending":
                # Check container_status again, if the pod does not have any containers yet
                if v1pod.status.container_statuses:
                    for container_status in v1pod.status.container_statuses:
                        if container_status.state.waiting is not None:
                            reason: str = container_status.state.waiting.reason
                            if reason == "ImageInspectError":
                                raise RuntimeError(
                                    f"Deployment of Pod '{v1pod.metadata.name}' failed with 'ImageInspectError'. The image might be broken. Please remove the image '{container_status.image}' from node '{v1pod.spec.node_name}' manually, and restart the simulation."
                                )
                            elif reason != "ContainerCreating":
                                raise RuntimeError(
                                    f"Deployment of Pod {v1pod.metadata.name} failed with container status {reason}."
                                )
                # Make sure there are no events leading to an endless pending loop
                for event in self.kubernetes_api.list_namespaced_event(namespace=namespace_id).items:
                    if pod.name in event.metadata.name:
                        if event.reason == "FailedMount" and "MountVolume.SetUp" in event.message:
                            raise RuntimeError(
                                f"Deployment of Pod '{v1pod.metadata.name}' failed with 'FailedMount': '{event.message}'. Pod host IP: {v1pod.status.host_ip}"
                            )

        self.logger.info("Successfully deployed Pod " + node.name)

        return v1pod

    # ######### End Kubernetes management methods ######### #

    # ######### Start step handling functions ######### #

    def add_step(
        self, scheduled_time: int, command: Callable[..., Command], args: Tuple = (), kwargs: Dict = None
    ) -> Command:
        """
        Add a timed step to the simulation.

        :param scheduled_time: Time to execute the step.
        :param command: Command that will be executed (e.g. nodes.n0.ping).
        :param args: Arguments for the command to be executed (tuple, e.g. ("abc", 5) ).
        :param kwargs: Keyword arguments for the command to be executed (dict, e.g. {'a': 1} ).
        :return: A Command child object corresponding to the 'command' parameter.
        """
        if kwargs is None:
            kwargs = {}

        self.logger.debug("Adding step to simulation.")
        if not self.timed_steps.get(scheduled_time, None):
            # Add a new step
            self.timed_steps[scheduled_time] = Step()

        # Add command to the step
        return self.timed_steps[scheduled_time].add_command(command, args, kwargs)

    def step(
        self,
        current_time: int,
        inputs: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
        fail_on_step_error: bool = True,
    ) -> None:
        """
        Pass input data to the simulation and execute the next step in the simulation queue.

        :param current_time: Current time of the simulation.
        :param inputs: (Optional) Dict of inputs for the current step Inputs to be used in this step. Example format: {'n305': {'closed': {'SimPowerSwitch-0.Model_power_switch_0': True}}}
        :param fail_on_step_error: (Optional) Raise an error when a step fails (i.e. command execution with non-zero exit code). Will cancel the simulation.
        """
        self.lock.acquire()
        try:
            if inputs:
                # Write input data to nodes, if present
                for node_id, attrs in inputs.items():
                    self.nodes[node_id].set_data(attrs)

            # Execute the step scheduled for the current_time, if one is present
            if current_time in self.timed_steps.keys():
                self.logger.debug(f"Processing simulation step at {current_time}...")
                step = self.timed_steps[current_time]
                step.execute(current_time, fail_on_step_error)

            self.current_time = current_time

        finally:
            self.lock.release()

    def get_data(self, outputs: Dict[str, List]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Retrieve output data from the simulation.

        :param outputs: Attributes to be retrieved and returned. Format: {'n305': ['closed', 'active']}
        :return: Requested output data. Format: {'n305': {'closed': True, 'active': False}}
        """
        data: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for entity_id, attrs in outputs.items():
            if not isinstance(attrs, List):
                raise ValueError("Output values has to be a list of attribute name strings.")

            node_data: Dict[str, Dict[str, Any]] = self.nodes[entity_id].get_data(attrs)
            data[entity_id] = node_data
            self.logger.debug(f"Output data for node {entity_id}: {node_data}")

        return data

    def has_next_step(self, current_time: int) -> bool:
        """
        Test if there are more steps to execute.

        :return: True if more steps are present, false if not.
        """
        # Make sure the next possible execution current_time is smaller than the largest execution current_time of any step
        try:
            return current_time + 1 <= max(list(self.timed_steps.keys()))
        except ValueError:
            return False

    # ######### End step handling functions ######### #
