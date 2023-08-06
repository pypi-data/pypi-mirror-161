from __future__ import annotations

from typing import Optional, Dict, Callable

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class StopCommand(Command):
    """
    Class defining a Command used to stop other asynchronously started commands.
    """

    def __init__(self, executor: NodeExecutor, stop_method: Callable[[Command], ExecResult], command: Command) -> None:
        """
        Stop an asynchronously started command.

        :param stop_method: The method used for stopping the command
        """
        super().__init__(executor, ["This command has no command String."])
        self.stop_method: Callable[[Command], ExecResult] = stop_method
        self.command: Command = command

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute the command using the executor.

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step
        :return: CommandResult.
        """
        result: ExecResult = self.stop_method(self.command)
        self.result = CommandResult(result)
        return self.result
