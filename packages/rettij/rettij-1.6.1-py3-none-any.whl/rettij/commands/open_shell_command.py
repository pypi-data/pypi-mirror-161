import sys
from typing import Optional, Dict

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class OpenShellCommand(Command):
    """
    Class defining a Command used to open an interactive shell.
    """

    def __init__(self, executor: NodeExecutor, name: str):
        """
        Initialize an OpenShellCommand object.

        :param executor: NodeExecutor that the command will be run with.
        :param name: Name of the Node.
        """
        self.name: str = name
        super().__init__(executor, [])

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute the OpenShellCommand.

        If a shell cannot be opened, this Command will log a warning, but return with exit code 0 in order to not crash the simulation!

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step.
        :return: CommandResult object.
        """
        # make sure this is an interactive shell
        if sys.__stdin__.isatty():
            print("------")
            shell_exit_code = self.executor.shell(self.name)
            print("------")
            return CommandResult(exec_result=ExecResult(), exit_code=shell_exit_code)
        else:
            self.logger.warning(
                f"This shell doesn't seem to be interactive, so can't open an interactive shell for "
                f"node '{self.name}'."
            )
            return CommandResult(exec_result=ExecResult(), exit_code=0)
