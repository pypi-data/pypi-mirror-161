import subprocess
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
from typing import Any, List, Dict, Optional, Union, Tuple

from kubernetes.client import V1Node, CoreV1Api

from rettij.commands.command import Command
from rettij.common.file_permissions import FilePermissions
from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class Host(NodeExecutor):
    """
    This class implements a NodeExecutor of type 'Host'.

    It represents the local machine that the Kubernetes master node is run on.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a Host executor.

        :param name: Name for the Host.
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        self._logs: str = ""

        super().__init__(name)

    def generate_config(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generate the configuration required to initialize a new Host executor.

        Currently, the Host node executor does not have any supported configuration parameters. But since the generation has to be done for ALL NodeExecutors, we simple return an empty dictionary.
        """
        return {}

    def initialize(self, **kwargs: Any) -> None:
        """
        Initialize the Host to make it usable.

        As the host currently does not have any supported configuration parameters, there is nothing to initialize.
        """
        pass

    @property
    def logs(self) -> str:
        """
        Return the log of the host session.

        :return: The log of the host session.
        """
        return self._logs

    @property
    def ip(self) -> IPv4Address:
        """
        Return the host IP address within the Kubernetes cluster.

        :return: Host IP address
        """
        master_node: V1Node = CoreV1Api().list_node().items[0]
        pod_cidr: str = master_node.spec.pod_cidr
        if not pod_cidr:
            raise RuntimeError(
                "No Pod IP CIDR range defined in cluster. This is likely due to usage of Docker for Windows WSL2, which we do not support host system integration for (yet)."
            )
        master_ip: IPv4Address = next(IPv4Network(pod_cidr).hosts())

        return master_ip

    def shell(self, node_name: str) -> int:
        """
        Open a subprocess with an interactive shell on a given node.

        The user will be dropped into an interactive shell-session - this is mostly meant for usage in the CLI.

        :param node_name: Name of the node to open a shell on.
        :return: Return code of the shell.
        """
        proc = subprocess.run("/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if proc.stdout:
            self._logs += proc.stdout.decode()
        if proc.stderr:
            self._logs += proc.stderr.decode()

        return proc.returncode

    def copy_file_from_node(self, src_file_path: str, dst_dir: str = "") -> Path:
        """
        [NOT IMPLEMENTED] Copy a file from the host to the local machine.

        Not implemented, as the host IS the local machine.

        :param src_file_path: Source path within the container
        :param dst_dir: Destination directory path on the local machine
        :return: Destination directory path on the local machine
        """
        raise NotImplementedError()

    def copy_file_to_node(
        self, src_file_path: ValidatedFilePath, dst_dir: str = "/", file_permissions: FilePermissions = None
    ) -> Path:
        """
        [NOT IMPLEMENTED] Copy a file from the local machine to the host.

        Not implemented, as the host IS the local machine.

        :param src_file_path: Source path on the local machine
        :param dst_dir: Destination directory path within the container
        :param file_permissions: Target file permissions representation
        :raise: NotImplementedError
        :return: Path inside target container
        """
        raise NotImplementedError()

    def read_values(self, keys: Optional[List[str]] = None, file: str = "out.json") -> Dict[str, Any]:
        """
        [NOT IMPLEMENTED YET] Read attributes from the host.

        Values are exchanged as JSON strings between rettij and the Pod.

        :param keys: (Optional) Attribute identifiers. If not set, all attributes are returned.
        :param file: (Optional) Storage file name on the executor. Default: `out.json`.
        :raise: NotImplementedError
        :return: Returns a dictionary of the key-value pairs. Will return an empty dictionary if:

            * No attributes were read from the Pod because:

                * The storage file does not exist.

                * The storage file is empty.

            * There were no keys matching the *keys* parameter present in the storage file.

        """
        raise NotImplementedError()

    def write_values(self, inputs: Dict[str, Any], file: str = "in.json") -> None:
        """
        [NOT IMPLEMENTED YET] Write attributes to the host.

        Values are exchanged as JSON strings between rettij and the host.

        :param inputs: Key-value pairs to be written
        :param file: (Optional) Storage file name on the executor. Default: `in.json`.
        :raise: ValueError, RuntimeError
        """
        raise NotImplementedError()

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
        Execute a command on the host using a bash subprocess.

        :param command: Command as string or in exec form
        :param detached: [NOT IMPLEMENTED YET] (Optional) If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param privileged: [NOT IMPLEMENTED YET] (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        :param log_error_only: (Optional) If True, only log errors unless the overall loglevel is DEBUG. Used to reduce log spamming from internal commands.
        :param success_exit_codes: (Optional) A list of additional exit codes that are evaluated as "success" of the command. Default is "0" as is convention in Unix systems.
        :return: ExecResult
        """
        process_result: subprocess.CompletedProcess = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        exec_result: ExecResult = ExecResult()
        exec_result.exit_code = process_result.returncode
        exec_result.append_stdout(process_result.stdout.decode())
        exec_result.append_stderr(process_result.stderr.decode())
        exec_result.command = command
        return exec_result

    def is_running(self, **kwargs: Any) -> bool:
        """
        Check if the host is running.

        Always returns true, as the host by definition is always running.

        :return: True if all running, False if not
        """
        return True

    def http_post_to_node(self, port: int, msg: str, path: str = "/") -> None:
        """
        Send a HTTP POST request to the rettij node.

        :param port: Port in the node that the HTTP server is listening on.
        :param msg: HTTP POST message body to send.
        :param path: Path to send POST request to. Default: "/"
        """
        raise NotImplementedError()

    def http_get_from_node(self, port: int, path: str = "/") -> str:
        """
        Send a HTTP GET request to the rettij node.

        :param port: Port in the node that the HTTP server is listening on.
        :param path: Path to send GET request to. Default: "/"
        """
        raise NotImplementedError()

    def stop_detached(self, command: Command) -> ExecResult:
        """
        [NOT IMPLEMENTED YET] Stop an asynchronously started (detached) process.

        :param command: Command object received from the command starting the detached process.
        :raise RuntimeError: When the supplied CommandResult does not contain the necessary information for stopping the process.
        """
        if not isinstance(command, Command):
            raise ValueError(f"Parameter 'command' must be of type 'Command', not '{type(command)}'.")
        raise NotImplementedError()
