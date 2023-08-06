import json
import os
import shlex
import subprocess
import tarfile
import tempfile
from ipaddress import IPv4Address
from pathlib import PurePosixPath, Path
from typing import Dict, Union, List, Any, Tuple, Optional

import kubernetes
import kubernetes.client.rest
import kubernetes.stream
import urllib3
from kubernetes.client import CoreV1Api
from kubernetes.stream.ws_client import STDOUT_CHANNEL
from http.client import HTTPConnection

import yaml
from rettij.commands.command import Command
from rettij.common.file_permissions import FilePermissions
from rettij.common.logging_utilities import Loglevel
from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.executor_not_available_exception import ExecutorNotAvailableException
from rettij.override.kubernetes.stream.ws_client import WSClient
from rettij.topology.exec_result import ExecResult
from rettij.topology.network_components.node import Node
from rettij.topology.node_configurations.kubernetes_pod_config import KubernetesPodConfig
from rettij.topology.node_executors.node_executor import NodeExecutor


class _ForwardedKubernetesHTTPConnection(HTTPConnection):
    """
    Implement a version of the HTTPConnection python class.

    It takes a k8s port forward socket to send HTTP requests from the rettij host system to a node.
    """

    def __init__(self, pf: kubernetes.stream.ws_client.PortForward, port: int):
        """
        Init class.

        :param pf: PortForward with socket from k8s.
        :param port: Port to send data to inside rettij node.
        """
        super().__init__("127.0.0.1", port)
        self.sock = pf.socket(port)

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass


class KubernetesPodExecutor(NodeExecutor):
    """
    This class implements a NodeExecutor of type 'KubernetesPodExecutor'.

    It represents the a Kubernetes Pod belonging to the simulation network.
    """

    __manifest: Dict[str, Union[str, int, List, Dict]]
    __namespace_id: str
    __deployed: bool
    __api_instance: CoreV1Api

    def __init__(self, name: str) -> None:
        """
        Initialize a Pod object.

        :param name: Name for the Pod.
        """
        super().__init__(name)
        self.__exposed_ports: List[int] = []

    def generate_config(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generate the configuration required to initialize a new Pod executor.

        :param kwargs: Parameters needed to generate the Pod configuration.
            - 'node' (Node) - The simulation Node that this Pod is the executor for.
            - 'namespace_id' (Optional, str) - The ID of the Kubernetes namespace to create the Pod in.

        :returns: Dictionary of configuration settings for the Pod.
            - 'manifest' (Dict) - The Pod manifest.
            - 'namespace_id' (str) - The ID of the Kubernetes namespace to create the Pod in.
        """
        node: Node = kwargs["node"]
        namespace_id = kwargs.get("namespace_id", "")

        if not isinstance(node.executor_config, KubernetesPodConfig):
            raise RuntimeError("KubernetesPodExecutor can only be used with KubernetesPodConfig!")

        pod_config: KubernetesPodConfig = node.executor_config
        pod_spec = pod_config.pod_spec

        # Try to extract executor spec from deployment
        # Case 1: List of deployments (e.g. when generating from docker-compose.yml using Kompose)
        # Case 2: Single deployment (e.g. when generating via kubectl run)

        # Extract first deployment from list of deployments
        try:
            pod_spec = pod_spec["items"][0]
        except KeyError:
            pass  # simply continue if input is not a list

        # Extract executor specification from single deployment
        try:
            pod_spec = pod_spec["spec"]["template"]["spec"]
        except KeyError:
            pass  # simply continue if input is not a deployment

        manifest: Dict[str, Union[str, int, List, Dict]] = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": node.name},
            "spec": pod_spec,
        }

        assert isinstance(manifest["spec"], Dict)
        spec: Dict = manifest["spec"]
        assert isinstance(spec["containers"], List)
        containers: List = spec["containers"]
        for container in containers:
            # Set security context if none is supplied
            container["securityContext"] = pod_spec.get("securityContext", {"privileged": True})
            # Set tty if not supplied
            container["tty"] = pod_spec.get("tty", True)

        if pod_config.execution_host:
            manifest_spec: Any = manifest["spec"]
            manifest_spec["nodeName"] = pod_config.execution_host

        return {"manifest": manifest, "namespace_id": namespace_id}

    def initialize(self, **kwargs: Any) -> None:
        """
        Initialize the Pod to make it usable.

        :param kwargs: Parameters needed to initialize the Pod.
            - 'manifest' (Dict) - The Pod manifest.
            - 'namespace_id' (Optional, str) - The ID of the Kubernetes namespace to create the Pod in.
            Uses "default" if not supplied.
            - 'api_instance' (Optional, CoreV1Api) - A specific Kubernetes API instance.
            Creates a new one if not supplied.
        """
        self.manifest = kwargs["manifest"]
        self.namespace_id = kwargs.get("namespace_id", "default")

        self.is_deployed = False

        self.__api_instance: CoreV1Api = kwargs.get("api_instance", CoreV1Api())

    @property
    def manifest(self) -> Dict[str, Union[str, int, List, Dict]]:
        """
        Return the Pod manifest.

        :return: Pod manifest.
        """
        return self.__manifest

    @manifest.setter
    def manifest(self, manifest: Dict[str, Union[str, int, List, Dict]]) -> None:
        """
        Set the manifest.

        :param manifest: Needed manifest variables.
        """
        if not isinstance(manifest, Dict):
            raise ValueError("Pod manifest must be a dictionary")
        for key, val in manifest.items():
            if not isinstance(key, str):
                raise ValueError("Manifest key type must be str!")
            if not isinstance(val, (str, int, List, Dict)):
                raise ValueError("Manifest value types must be in [str, int, List, Dict]!")
        self.__manifest: Dict[str, Union[str, int, List, Dict]] = manifest

    @property
    def namespace_id(self) -> str:
        """
        Return the Kubernetes namespace id.

        :return: Namespace id.
        """
        return self.__namespace_id

    @namespace_id.setter
    def namespace_id(self, namespace_id: str) -> None:
        """
        Set the namespace id.

        :param namespace_id: Namespace id.
        :raise: ValueError.
        """
        if not isinstance(namespace_id, str):
            raise ValueError("Namespace ID must be string!")
        self.__namespace_id: str = namespace_id

    @property
    def is_deployed(self) -> bool:
        """
        Return the deployment status.

        :return: True if deployed, else false
        """
        return self.__deployed

    @is_deployed.setter
    def is_deployed(self, deployed: bool) -> None:
        """
        Set is deployed.

        :param deployed: Deployed flag.
        :raise: ValueError.
        """
        if not isinstance(deployed, bool):
            raise ValueError("Deployed flag must be boolean value!")
        self.__deployed: bool = deployed

    @property
    def api_pod(self) -> kubernetes.client.V1Pod:
        """
        Return the Pod's attributes in Kubernetes.

        :raise: ExecutorNotAvailableException.
        :raise: kubernetes.client.rest.ApiException
        :return: Return the Pod's attributes.
        """
        try:
            return self.__api_instance.read_namespaced_pod(name=self.name, namespace=self.namespace_id)
        except kubernetes.client.rest.ApiException as e:
            if e.status == 404:
                raise ExecutorNotAvailableException()
            else:
                raise e

    @property
    def logs(self) -> str:
        """
        Return the Pod's logs.

        :raise: ExecutorNotAvailableException.
        :raise: kubernetes.client.rest.ApiException
        :return: Return the Pod's logs.
        """
        try:
            try:
                return str(self.__api_instance.read_namespaced_pod_log(name=self.name, namespace=self.namespace_id))
            except urllib3.exceptions.MaxRetryError:
                return str(CoreV1Api().read_namespaced_pod_log(name=self.name, namespace=self.namespace_id))
        except kubernetes.client.rest.ApiException as e:
            if e.status == 404:
                raise ExecutorNotAvailableException()
            else:
                raise e

    @property
    def ip(self) -> IPv4Address:
        """
        Return the actual Pod IP address within the Kubernetes cluster.

        May change every time the Pod is (re)started.

        :return: Pod IP address.
        """
        return IPv4Address(self.api_pod.status.pod_ip)

    def shell(self, node_name: str) -> int:
        """
        Open an interactive shell on the Node.

        :param node_name: Name of the Node.
        :return: Exit code of the shell.
        """
        namespace = self.namespace_id
        # TODO: Can currently only use environment variables and default kubeconfig path. Add custom path.
        # TODO: Replace by API attached shell.
        proc = subprocess.run(
            shlex.split(f"kubectl exec --stdin --tty --namespace {namespace} {node_name} -- /bin/bash")
        )
        return proc.returncode

    def is_running(self, **kwargs: Any) -> bool:
        """
        Check if the Pod's containers are running.

        :param kwargs: Pod-specific parameters.
            - 'log' (Optional, bool) - If True activate running logs, if False not.

        :return: True if all running, False if not.
        """
        # Possible executor phases:
        # https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
        # - Pending
        # - Running
        # - Succeeded
        # - Failed
        # - Unknown
        #
        # Possible container states:
        # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ContainerState.md
        # - running
        # - terminated
        # - waiting

        log: bool = kwargs.get("log", False)

        # This checks if the number of running containers is same as the total number of containers in this executor
        faulty_containers = [
            container_status
            for container_status in self.api_pod.status.container_statuses
            if not container_status.state.running
        ]
        if len(faulty_containers) > 0:
            if log:
                self.logger.error(f"Pod {self.name} has faulty containers!\n{faulty_containers}\nLogs:\n{self.logs}")
            return False

        return True

    def expose_port_as_k8s_service(self, port: int) -> None:
        """
        Expose a port from a node/container/pod as a so-called Kubernetes service.

        The k8s service has following name: <node-name>-<port-number>

        Can safely be called multiple times for the same port as it keeps track of already exposed ports and will
        simply return if the port already was exposed.

        :param port: Port inside the rettij node to be exposed as a service. The service port will be the same.
                     This will be exposed within the k8s cluster, NOT the rettij host system.
        """
        if port in self.__exposed_ports:  # if port is already exposed, just return
            return
        service_name: str = f"{self.name}-{port}"
        self.logger.debug(
            f"Exposing port '{port}' from node '{self.name}' as service '{service_name}' in k8s cluster..."
        )
        kubernetes_api = kubernetes.client.CoreV1Api()

        # create service for rettij socket so that external processes can connect to the pod via service (by dns)
        service = kubernetes.client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=kubernetes.client.V1ObjectMeta(name=service_name),  # kubernetes service name
            spec=kubernetes.client.V1ServiceSpec(
                # for simplicity, the same port in and outside
                ports=[kubernetes.client.V1ServicePort(port=port, target_port=port)]
            ),
        )
        kubernetes_api.create_namespaced_service(self.namespace_id, service)
        self.__exposed_ports.append(port)
        self.logger.debug(f"Exposed port '{port}' from node '{self.name}' as service '{service_name}' in k8s cluster.")

    def http_post_to_node(self, port: int, msg: str, path: str = "/") -> None:
        """
        Send a HTTP POST request to the rettij node.

        :param port: Port in the node that the HTTP server is listening on.
        :param msg: HTTP POST message body to send.
        :param path: Path to send POST request to. Default: "/"
        """
        self.expose_port_as_k8s_service(port)
        self.logger.debug(f"Sending HTTP POST message from rettij host to node '{self.name}' (port {port}): {msg}")
        try:
            kubernetes_api = kubernetes.client.CoreV1Api()
            pf = kubernetes.stream.portforward(
                kubernetes_api.connect_get_namespaced_pod_portforward, self.name, self.namespace_id, ports=str(port)
            )
            conn = _ForwardedKubernetesHTTPConnection(pf, port)
            conn.request("POST", path, msg)
            resp = conn.getresponse()
            if resp.status != 200:
                self.logger.error(
                    f"HTTP POST failed. Could not send data via forwarded kubernetes port to node. Expected HTTP status '200'. "
                    f"Path: '{path}' | Received: '{resp.status}'"
                )
        except Exception as e:
            self.logger.error(f"Could not send POST request on port '{port}': {e}")

    def http_get_from_node(self, port: int, path: str = "/") -> str:
        """
        Send a HTTP GET request to the rettij node.

        :param port: Port in the node that the HTTP server is listening on.
        :param path: Path to send GET request to. Default: "/"
        """
        self.expose_port_as_k8s_service(port)
        self.logger.debug(f"Sending HTTP GET from rettij host to node '{self.name}' (port {port}) at path '{path}'")
        try:
            kubernetes_api = kubernetes.client.CoreV1Api()
            pf = kubernetes.stream.portforward(
                kubernetes_api.connect_get_namespaced_pod_portforward, self.name, self.namespace_id, ports=str(port)
            )
            conn = _ForwardedKubernetesHTTPConnection(pf, port)
            conn.request("GET", path)
            resp = conn.getresponse()
            if resp.status != 200:
                self.logger.error(
                    f"HTTP GET failed. Error occurred getting data from a forwarded kubernetes port to node. Expected HTTP status '200'. "
                    f"Path: '{path}' | Received: '{resp.status}'"
                )
            response_body = resp.read()  # note: resp.msg only contains the headers, so we need to call resp.read()!
            return response_body.decode("utf-8")
        except Exception as e:
            self.logger.error(f"Could not perform GET request: {e}")
            return ""

    def copy_file_from_node(self, src_file_path: str, dst_dir: str = "") -> Path:
        """
        Copy a file from the Pod to the local machine.

        :param src_file_path: Source path within the container.
        :param dst_dir: (Optional) Destination directory path on the local machine.
        :return: Destination directory path on the local machine.
        """
        # Append a leading slash to the start of src_file_path if not yet present
        src_file_path_posix: PurePosixPath = (
            PurePosixPath("/", src_file_path) if not src_file_path.startswith("/") else PurePosixPath(src_file_path)
        )

        # -c    create a new archive
        # -m    don't extract file modified time
        # -f    use archive file or device ARCHIVE
        exec_command = ["tar", "cmf", "-", src_file_path_posix.relative_to("/").as_posix()]

        with tempfile.TemporaryFile(mode="w+b") as tar_buffer:
            wsclient: WSClient = self._create_k8s_wsclient(
                self.__api_instance.connect_get_namespaced_pod_exec,
                self.name,
                self.namespace_id,
                command=exec_command,
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            # wsclient.update = WSClient.update
            # wsclient: WSClient = WSClient()

            wsclient.hexdump_channels = [STDOUT_CHANNEL]
            out = ""
            while wsclient.is_open():
                wsclient.update(timeout=1)
                if wsclient.peek_stdout():
                    out += wsclient.read_stdout()
                if wsclient.peek_stderr():
                    err: str = wsclient.read_stderr()
                    raise RuntimeError(f"STDERR: {err}")
            wsclient.close()

            # strip '0x' prefixes from combined output, as it contains multiple hex strings
            # each starting with the prefix which breaks conversion
            tar_buffer.write(bytes.fromhex(out.replace("0x", "")))
            tar_buffer.seek(0)

            if dst_dir:
                if not Path(dst_dir).exists():
                    os.makedirs(dst_dir)

            with tarfile.open(fileobj=tar_buffer, mode="r:") as tar:
                for member in tar.getmembers():
                    if member.isdir():
                        continue
                    fname = Path(member.name).name
                    tar.makefile(member, Path(dst_dir, fname))

        return Path(os.getcwd()) / dst_dir

    def copy_file_to_node(
        self, src_file_path: ValidatedFilePath, dst_dir: str = "/", file_permissions: FilePermissions = None
    ) -> Path:
        """
        Copy a file from the local machine to the Pod.

        :param src_file_path: Source path on the local machine.
        :param dst_dir: (Optional) Destination directory path within the container.
        :param file_permissions: (Optional) Target file permissions representation.
        :raise: RuntimeError.
        :return: Path inside target container.
        """
        file_name = Path(src_file_path).name

        # Append a trailing slash to the end of dst_dir if not yet present
        dst_dir_path: Path = Path(dst_dir)

        # Create dir and set permissions
        create_path_result: ExecResult
        if file_permissions:
            create_path_result = self.execute_command(
                [
                    "sh",
                    "-c",
                    f"mkdir -p {dst_dir_path.as_posix()} && "
                    f"chown {file_permissions.owner} {dst_dir_path.as_posix()} && "
                    f"chgrp {file_permissions.group} {dst_dir_path.as_posix()}",
                ],
                log_error_only=True,
            )
        else:
            create_path_result = self.execute_command(["mkdir", "-p", dst_dir_path.as_posix()], log_error_only=True)

        if create_path_result.exit_code != 0:
            raise RuntimeError(str(create_path_result))

        self.logger.debug(f"Copying of {file_name} to {self.name} started:")

        # -x    extract files from an archive
        # -m    don't extract file modified time
        # -f    use archive file or device ARCHIVE
        exec_command = ["tar", "xmf", "-", "-C", "/"]

        wsclient = self._create_k8s_wsclient(
            self.__api_instance.connect_get_namespaced_pod_exec,
            self.name,
            self.namespace_id,
            command=exec_command,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=False,
            _preload_content=False,
        )

        with tempfile.TemporaryFile() as tar_buffer:
            write_complete: bool = False

            with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                tar.add(src_file_path, dst_dir_path.joinpath(file_name).as_posix())

            tar_buffer.seek(0)
            tar_content: Optional[bytes] = tar_buffer.read()

            while wsclient.is_open():
                wsclient.update(timeout=1)
                if wsclient.peek_stdout():
                    self.logger.debug(f"STDOUT: {wsclient.read_stdout()}")
                if wsclient.peek_stderr():
                    err: str = wsclient.read_stderr()
                    self.logger.error(f"STDERR: {err}")
                    raise RuntimeError(err)
                if tar_content:
                    self.logger.debug("Writing archive contents to container...")
                    wsclient.write_stdin(tar_content)
                    tar_content = None  # Clear the content cache, otherwise this will be an endless loop
                else:
                    write_complete = True
                    break
            wsclient.close()
            self.logger.debug("Done.")

            if not write_complete:
                raise RuntimeError(f"Writing file {src_file_path} failed!")

            change_permissions_result: ExecResult
            if file_permissions:
                change_permissions_result = self.execute_command(
                    [
                        "sh",
                        "-c",
                        f"chmod {file_permissions.permissions} {dst_dir_path.joinpath(file_name).as_posix()} && "
                        f"chown {file_permissions.owner} {dst_dir_path.joinpath(file_name).as_posix()} && "
                        f"chgrp {file_permissions.group} {dst_dir_path.joinpath(file_name).as_posix()}",
                    ],
                    log_error_only=True,
                )
            else:
                change_permissions_result = self.execute_command(
                    ["chmod", "774", dst_dir_path.joinpath(file_name).as_posix()], log_error_only=True
                )
            if change_permissions_result.exit_code != 0:
                raise RuntimeError(str(change_permissions_result))

        return dst_dir_path.joinpath(file_name)

    def write_values(self, inputs: Dict[str, Any], file: str = "in.json") -> None:
        """
        Write an attribute value to the Pod.

        Values are exchanged as JSON strings between rettij and the Pod.

        :param inputs: Key-value pairs to be written
        :param file: (Optional) Storage file name on the executor (Default: in.json)
        :raise: ValueError, RuntimeError
        """
        if not isinstance(inputs, dict):
            raise ValueError(f"Expected Dict as input. Got {type(inputs)}. Value: {inputs}")
        if len(inputs.keys()) == 0:
            raise ValueError("Input needs to contain at least one key-value pair!")

        file_path = (self.rettij_dir / file).as_posix()

        new_values: Dict[str, Any] = {}
        new_values.update(self.read_values(file=file))
        new_values.update(inputs)
        try:
            new_values_json: str = json.dumps(new_values)
        except TypeError as e:
            types = {k: type(v) for k, v in inputs.items()}
            raise ValueError(
                f"{e}. Make sure input is a Dict that doesn't contain non-JSON-serializable values. "
                f"Value: {inputs}. Types: {types}"
            )

        write_result: ExecResult = self.execute_command(
            ["/bin/sh", "-c", f"mkdir -p {self.rettij_dir.as_posix()} && echo '{new_values_json}' > {file_path}"],
            log_error_only=True,
        )
        if write_result.exit_code != 0:
            raise RuntimeError(str(write_result))

    def read_values(self, keys: Optional[List[str]] = None, file: str = "out.json") -> Dict[str, Any]:
        """
        Read attributes from the Pod.

        Values are exchanged as JSON strings between rettij and the Pod.

        :param keys: (Optional) Attribute identifiers. If not set, all attributes are returned.
        :param file: (Optional) Storage file name on the executor (Default: out.json)
        :raise: RuntimeError
        :return: Returns a dictionary of the key-value pairs. Will return an empty dictionary if:

            - No attributes were read from the Pod because:
                - The storage file does not exist.
                - The storage file is empty.
            - There were no keys matching the *keys* parameter present in the storage file.

        """
        # Return empty dictionary if no attributes were read from the Pod because the file does not exist.
        file_path = (self.rettij_dir / file).as_posix()
        # "test -f" returns 0 if file_path points to a file, returns 1 if there's no file
        # -> also accept 1 as successful exit_code, so non existent files won't result in printing to ERROR log
        check_file_result: ExecResult = self.execute_command(
            ["test", "-f", file_path], log_error_only=True, success_exit_codes=(0, 1)
        )
        if check_file_result.exit_code == 1:
            self.logger.info(f"No attributes stored on {self.name}!")
            return {}
        elif check_file_result.exit_code > 1:
            raise RuntimeError(str(check_file_result))

        read_result: ExecResult = self.execute_command(["cat", file_path], log_error_only=True)
        if read_result.exit_code != 0:
            raise RuntimeError(str(read_result))

        # Return empty dictionary if no attributes were read from the Pod because the file is empty.
        if not read_result.std_out:
            self.logger.warning(f"No attributes stored on {self.name}!")
            return {}

        current_values: Dict[str, Any] = json.loads(read_result.std_out)

        # If specific keys are to be retrieved, create a new dict only containing these keys
        if keys:
            output: Dict[str, Any] = {}
            for key in keys:
                try:
                    output[key] = current_values[key]
                except KeyError:
                    self.logger.warning(f"Attribute key {key} not found on {self.name}!")
            return output
        else:
            return current_values

    def execute_command(
        self,
        command: Union[str, List[str]],
        detached: bool = False,
        privileged: bool = False,
        log_error_only: bool = False,
        success_exit_codes: Tuple[int, ...] = (0,),
        **kwargs: Any,
    ) -> ExecResult:
        """
        Execute a command inside a Pod container using a Kubernetes stream.

        :param command: Command as string or in exec form
        :param detached: (Optional) If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param privileged: (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        :param log_error_only: (Optional) If True, only log errors unless the overall loglevel is DEBUG. Used to reduce log spamming from internal commands.
        :param success_exit_codes: (Optional) A list of additional exit codes that are evaluated as "success" of the command. Default is "0" as is convention in Unix systems.
        :param kwargs: Pod-specific parameters.
            - 'container_name' (Optional, str) - Name of the container inside the Pod to run the command on. Will default to the main container if not specified.
            - 'tty' (Optional, bool) - Request to allocate a TTY to the session (i.e. add interactivity).

        :raise: ExecutorNotAvailableException
        :return: ExecResult
        """
        container_name: str = kwargs.get("container_name", "")
        tty: bool = kwargs.get("tty", False)

        if isinstance(command, str):
            # convert string shell command to list in exec form
            command = shlex.split(command)

        if not self.is_running():
            raise ExecutorNotAvailableException(self.name)

        if (not log_error_only) or self.logger.level == Loglevel.DEBUG.value:
            self.logger.info(f"Starting command {command} in container {self.name}.")

        kwargs = {
            "command": command,
            "stderr": True,
            "stdin": True,
            "stdout": True,
            "tty": tty,
            "_preload_content": False,
        }
        if container_name != "":
            kwargs["container"] = container_name

        # init web socket client
        wsclient: WSClient = self._create_k8s_wsclient(
            self.__api_instance.connect_get_namespaced_pod_exec, self.name, self.namespace_id, **kwargs
        )

        result: ExecResult = ExecResult()
        if detached:
            for i in range(3):  # Load output 3 times. Somehow the output is sometimes incomplete if we only load once.
                wsclient.update(timeout=1)
            result.set_wsclient(wsclient)
        else:
            while wsclient.is_open():
                wsclient.update(timeout=1)

        result = self.parse_k8s_wsclient(wsclient)
        result.command = command

        # Log result as error if std_err is set or exit_code is not one defined in success_exit_codes
        if result.std_err or result.exit_code not in success_exit_codes:
            self.logger.error(result)
        else:
            self.logger.debug(result)

        return result

    def _create_k8s_wsclient(self, *args: Any, **kwargs: Any) -> WSClient:
        """
        Create a Kubernetes web socket client in a more robust way.

        This is a wrapper for the kubernetes.stream.stream function that retries the websocket creation in case of a handshake status "500 Internal Server Error" response up to 3 times. That is sufficient in many cases to solve some issues. This method is called with the same parameters as kubernetes.stream.stream.

        :param args: Positional parameters passed to the kubernetes.stream.stream function (tuple, e.g. (bounded_api_method_callback, 'callbacks positional argument 1', 'callbacks positional argument 2') ).
        :param kwargs: Keyword parameters passed to the kubernetes.stream.stream function (dict, e.g. {'keyword': 'callbacks keyword argument'} ).
        :raises: kubernetes.client.rest.ApiException
        :return: WSClient
        """
        tries = 3
        while tries > 0:
            try:
                tries -= 1
                wsclient: WSClient = kubernetes.stream.stream(*args, **kwargs)
                return wsclient
            except kubernetes.client.rest.ApiException as e:
                if e.status == 0 and tries > 0:
                    self.logger.error("Retrying to create stream %s", e)
                else:
                    raise

        raise kubernetes.client.rest.ApiException(status=0, reason="Failed to create websocket client")

    def parse_k8s_wsclient(self, wsclient: WSClient) -> ExecResult:
        """
        Parse the outputs from a Kubernetes Web Socket client.

        :param wsclient: Web Socket client to parse outputs from.
        :raises: Exception
        :return: ExecResult
        """
        exec_result = ExecResult()
        try:
            while wsclient.peek_stdout():
                exec_result.append_stdout(wsclient.read_stdout())
            while wsclient.peek_stderr():
                exec_result.append_stderr(wsclient.read_stderr())

            exit_code, api_response = self._parse_k8s_api_channel(wsclient)
            exec_result.exit_code = exit_code
            exec_result.set_api_response(api_response)

        except Exception as e:
            self.logger.critical(e)
            raise e

        return exec_result

    def _parse_k8s_api_channel(self, wsclient: WSClient) -> Tuple[int, Dict]:
        """
        Parse the Kubernetes WSClient API channel.

        This is a workaround to store both the api result dictionary and the exit code. This is necessary because
        using the WSClient.returncode property getter will discard the api result dictionary, leaving us with less
        information.

        :param wsclient: WSClient object to parse the API channel from.
        :return: Tuple of the status code as int and the API channel contents as dict.
        """
        if wsclient.peek_channel(3):
            api_response: Dict = yaml.safe_load(wsclient.read_channel(3))

            status_code: int
            if api_response["status"] == "Success":
                status_code = 0
            else:
                try:
                    status_code = int(api_response["details"]["causes"][0]["message"])
                except ValueError:
                    status_code = int(api_response["code"])

            return status_code, api_response

        else:
            return 0, {}

    def stop_detached(self, command: Command) -> ExecResult:
        """
        Stop an asynchronously started (detached) process.

        :param command: Command object received from the command starting the detached process.
        :raise AttributeError: When the supplied Command does not contain the necessary information for stopping the process.
        """
        if not isinstance(command, Command):
            raise ValueError(f"Parameter 'command' must be of type 'Command', not '{type(command)}'.")

        try:
            wsclient: WSClient = command.result.exec_result.wsclient
            wsclient.write_stdin("\x03")  # Trigger SIGINT / STRG + C to stop the process
            wsclient.update(timeout=3)
            result: ExecResult = self.parse_k8s_wsclient(wsclient)
            wsclient.close()
            self.logger.debug(result)
            return result
        except AttributeError as e:
            self.logger.debug(e)
            return ExecResult()

    def __hash__(self) -> int:
        return hash((self.name, self.manifest))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KubernetesPodExecutor):
            return NotImplemented
        return (self.name, self.manifest) == (other.name, other.manifest)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, KubernetesPodExecutor):
            return NotImplemented
        return not (self == other)
