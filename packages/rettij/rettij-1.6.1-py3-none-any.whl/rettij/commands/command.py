from __future__ import annotations

import shlex
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union

from rettij.commands.command_result import CommandResult
from rettij.common.logging_utilities import LoggingSetup
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class Command(ABC):
    """
    Abstract class that defines a command.
    """

    result: CommandResult

    def __init__(
        self, executor: NodeExecutor, command: Union[str, List[str]], detached: bool = False, privileged: bool = False
    ):
        """
        Create a command object that is used to execute something in NodeExecutor.

        :param executor: NodeExecutor to execute the Command on.
        :param command: Command as string or in exec form
        :param detached: (Optional) If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param privileged: (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        """
        if isinstance(command, str):
            # convert string shell command to list in exec form
            command = shlex.split(command)

        self.executor: NodeExecutor = executor
        self.command_list: List[str] = command
        self.detached: bool = detached
        self.privileged: bool = privileged
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)
        self.result = CommandResult(
            exec_result=ExecResult(), exit_code=-2, values={"std_out": "Command has not been executed yet!"}
        )  # Replaced by an actual result once the Command is executed

    @abstractmethod
    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Stub for command execution logic.

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step
        :return: CommandResult.
        """
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.__dict__.get('command_list')} -> {self.result}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Command):
            return False

        if self.executor == other.executor and self.command_list == other.command_list and self.result == other.result:
            return True
        else:
            return False
