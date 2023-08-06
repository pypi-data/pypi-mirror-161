from abc import ABC, abstractmethod
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, List, Dict, Optional, Union, Tuple

from rettij.common.file_permissions import FilePermissions
from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.exec_result import ExecResult


class NodeExecutor(ABC):
    """
    Interface class for a Node's Executor. Implemented by backend-specific executors like Pod or VM.

    The NodeExecutor is an interface meant to make the Node independent of any actual execution backend like Kubernetes,
    VMs or physical machines. It contains abstract method definitions for all Node execution and status functionalities.
    These abstract methods are then implemented by backend-specific child classes.
    """

    rettij_dir: Path = Path("/rettij/")

    def __init__(self, name: str) -> None:
        """
        Initialize a NodeExecutor or subclass object.

        :param name: Name for the object (usually derived from the Node name).
        """
        self.name: str = name
        self.logger = LoggingSetup.submodule_logging(f"{self.__class__.__name__}:{name}")

    @abstractmethod
    def generate_config(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generate the configuration needed to initialize the executor.

        :param kwargs: Executor-specific parameters needed to generate the configuration.
        :returns: Dictionary of executor-specific configuration settings.
        """
        raise NotImplementedError()

    @abstractmethod
    def initialize(self, **kwargs: Any) -> None:
        """
        Initialize the executor to make it usable.

        :param kwargs: Executor-specific parameters needed to initialize the executor.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def logs(self) -> str:
        """
        Return the executor's logs.

        :raise: ExecutorNotAvailableException.
        :return: Return the executor's logs.
        """

    @property
    @abstractmethod
    def ip(self) -> IPv4Address:
        """
        Return the external IP address of the executor.

        :return: external IP address
        """
        raise NotImplementedError()

    @abstractmethod
    def shell(self, node_name: str) -> int:
        """
        Open an interactive shell on a given node.

        The user will be dropped into an interactive shell-session - this is mostly meant for usage in the CLI.

        :param node_name: Name of the node to open a shell on.
        :return: Return code of the shell.
        """
        raise NotImplementedError()

    @abstractmethod
    def write_values(self, inputs: Dict[str, Any], file: str = "in.json") -> None:
        """
        Write attributes to the executor.

        Values are exchanged as JSON strings between rettij and the executor.
        The resulting json file will be stored in the `/rettij` directory.

        :param inputs: Key-value pairs to be written
        :param file: (Optional) Storage file name on the executor. Default: `in.json`.
        :raise: ValueError, RuntimeError
        """
        raise NotImplementedError()

    @abstractmethod
    def read_values(self, keys: Optional[List[str]] = None, file: str = "out.json") -> Dict[str, Any]:
        """
        Read attributes from the executor.

        Values are exchanged as JSON strings between rettij and the executor.
        The json file will be read from the `/rettij` directory.

        :param keys: (Optional) Attribute identifiers. If not set, all attributes are returned.
        :param file: (Optional) Storage file name on the executor. Default: `out.json`.
        :raise: RuntimeError
        :return: Returns a dictionary of the key-value pairs. Will return an empty dictionary if:

            * No attributes were read from the Pod because:

                * The storage file does not exist.

                * The storage file is empty.

            * There were no keys matching the *keys* parameter present in the storage file.

        """
        raise NotImplementedError()

    @abstractmethod
    def copy_file_from_node(self, src_file_path: str, dst_dir: str = "") -> Path:
        """
        Copy a file from the executor to the local machine.

        :param src_file_path: Source path on the executor
        :param dst_dir: Destination directory path on the local machine
        :return: Destination directory path on the local machine
        """
        raise NotImplementedError()

    @abstractmethod
    def copy_file_to_node(
        self, src_file_path: ValidatedFilePath, dst_dir: str = "/", file_permissions: FilePermissions = None
    ) -> Path:
        """
        Copy a file from the local machine to the executor.

        :param src_file_path: Source path on the local machine
        :param dst_dir: Destination directory path on the executor
        :param file_permissions: Target file permissions representation
        :return: Final file path on the executor
        """
        raise NotImplementedError()

    @abstractmethod
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
        Execute a command inside the executor.

        :param command: Command as string or in exec form
        :param detached: (Optional) If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param privileged: (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        :param log_error_only: (Optional) If True, only log errors unless the overall loglevel is DEBUG. Used to reduce log spamming from internal commands.
        :param success_exit_codes: (Optional) A list of additional exit codes that are evaluated as "success" of the command. Default is "0" as is convention in Unix systems.
        :param kwargs: Executor-specific parameters.
        :return: ExecResult
        """
        raise NotImplementedError()

    @abstractmethod
    def is_running(self, **kwargs: Any) -> bool:
        """
        Check if the executor is running properly.

        :return:
            - True - Executor is running properly
            - False - Executor is not running or is faulty.
        """
        raise NotImplementedError()

    @abstractmethod
    def http_post_to_node(self, port: int, msg: str, path: str = "/") -> None:
        """
        Send a HTTP POST request to the rettij node.

        :param port: Port in the node that the HTTP server is listening on.
        :param msg: HTTP POST message body to send.
        :param path: Path to send POST request to. Default: "/"
        """
        raise NotImplementedError()

    @abstractmethod
    def http_get_from_node(self, port: int, path: str = "/") -> str:
        """
        Send a HTTP GET request to the rettij node.

        :param port: Port in the node that the HTTP server is listening on.
        :param path: Path to send GET request to. Default: "/"
        """
        raise NotImplementedError()

    @abstractmethod
    def stop_detached(self, command: Any) -> ExecResult:
        """
        Stop an asynchronously started (detached) process.

        :param command: Command object received from the command starting the detached process. Must be subclass of 'Command', which cannot be hinted here due to circular imports.
        :raise RuntimeError: When the supplied CommandResult does not contain the necessary information for stopping the process.
        """
        raise NotImplementedError()
