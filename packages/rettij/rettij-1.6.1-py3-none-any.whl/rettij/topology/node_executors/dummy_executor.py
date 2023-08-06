from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, List, Dict, Optional, Union, Tuple

from rettij.commands.command import Command
from rettij.common.file_permissions import FilePermissions
from rettij.common.logging_utilities import LoggingSetup
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class DummyExecutor(NodeExecutor):
    """
    This class implements a NodeExecutor of type 'DummyExecutor'.

    It is just a dummy used by the 'Rettij' class to apply a sequence. Does not actually do anything.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a DummyExecutor object.

        :param name: Name for the DummyExecutor.
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        super().__init__(name)

    def generate_config(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Generate the configuration required to initialize a new DummyExecutor executor.

        The DummyExecutor node executor does not have any configuration parameters. But since the generation has to be done for ALL NodeExecutors, we simple return an empty dictionary.
        """
        return {}

    def initialize(self, **kwargs: Any) -> None:
        """
        Initialize the DummyExecutor to make it usable.

        As the dummy does not have any configuration parameters, there is nothing to initialize.
        """
        pass

    @property
    def logs(self) -> str:
        """
        Return a dummy log.

        :return: Return a dummy log.
        """
        return "Dummy log line 1\nDummy log line 2"

    @property
    def ip(self) -> IPv4Address:
        """
        Return a dummy IP address.

        :return: IPv4Address("0.0.0.0")
        """
        return IPv4Address("0.0.0.0")

    def shell(self, node_name: str) -> int:
        """
        Do nothing because this is a dummy.

        :param node_name:
        :return: 0
        """
        return 0

    def copy_file_from_node(self, src_file_path: str, dst_dir: str = "") -> Path:
        """
        Do nothing because this is a dummy.

        :param src_file_path: Source path within the container
        :param dst_dir: Destination directory path on the local machine
        :return: Empty path
        """
        return Path("")

    def copy_file_to_node(
        self, src_file_path: ValidatedFilePath, dst_dir: str = "/", file_permissions: FilePermissions = None
    ) -> Path:
        """
        Do nothing because this is a dummy.

        :param src_file_path: Source path on the local machine
        :param dst_dir: Destination directory path within the container
        :param file_permissions: Target file permissions representation
        :return: Empty path
        """
        return Path("")

    def read_values(self, keys: Optional[List[str]] = None, file: str = "out.json") -> Dict[str, str]:
        """
        Do nothing because this is a dummy.

        :param keys: (Optional) Attribute identifiers. If not set, all attributes are returned.
        :param file: (Optional) Storage file name on the executor (Default: out.json)
        :return: Empty dictionary
        """
        return {}

    def write_values(self, inputs: Dict[str, Any], file: str = "in.json") -> None:
        """
        Do nothing because this is a dummy.

        :param inputs: Key-value pairs to be written
        :param file: (Optional) Storage file name on the executor (Default: in.json)
        """
        pass

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
        Do nothing because this is a dummy.

        :param command: Command as string or in exec form
        :param detached: (Optional) If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param privileged: (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        :param log_error_only: (Optional) If True, only log errors unless the overall loglevel is DEBUG. Used to reduce log spamming from internal commands.
        :param success_exit_codes: (Optional) A list of additional exit codes that are evaluated as "success" of the command. Default is "0" as is convention in Unix systems.
        :param kwargs: Executor-specific parameters.
        :return: Empty ExecResult object.
        """
        return ExecResult()

    def is_running(self, **kwargs: Any) -> bool:
        """
        Check if the dummy is running.

        Always returns true, as the dummy by definition is always running.

        :return: True if all running, False if not
        """
        return True

    def http_post_to_node(self, port: int, msg: str, path: str = "/") -> None:
        """
        Send a HTTP POST request from the rettij host system to the rettij node.

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
        Do nothing because this is a dummy.

        :param command: Command object received from the command starting the detached process.
        """
        if not isinstance(command, Command):
            raise ValueError(f"Parameter 'command' must be of type 'Command', not '{type(command)}'.")
        return ExecResult()
