from __future__ import annotations

from typing import Optional, Dict

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.topology.exec_result import ExecResult


class RunCommand(Command):
    """
    Class defining a Command used to start a shell command.
    """

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute the command using the executor.

        :param inputs: Dict of inputs for the current step
        :param current_time: Current time of the simulation.
        :return: CommandResult.
        """
        result: ExecResult = self.executor.execute_command(
            self.command_list, detached=self.detached, privileged=self.privileged
        )

        self.result = CommandResult(result)
        return self.result
