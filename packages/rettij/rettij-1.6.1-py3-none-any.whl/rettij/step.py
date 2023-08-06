from __future__ import annotations

from typing import Tuple, Callable, List, Dict

from rettij.commands.command import Command


class Step:
    """
    This class holds a simulation step, consisting of one or more Commands.
    """

    def __init__(self) -> None:
        """
        Initialize a new step object.
        """
        self.commands: List[Command] = []

    def add_command(self, command: Callable[..., Command], args: Tuple = (), kwargs: Dict = None) -> Command:
        """
        Add an additional command to an existing step.

        :param command: Command that will be executed (e.g. nodes.n0.ping).
        :param args: Parameters for the command to be executed (tuple, e.g. ("abc", 5) ).
        :param kwargs: Keyword parameters for the command to be executed (dict, e.g. {'a': 1} ).
        """
        if kwargs is None:
            kwargs = {}

        command_object: Command = command(*args, **kwargs, exec_now=False)
        self.commands.append(command_object)
        return command_object

    def execute(self, current_time: int, fail_on_step_error: bool = True) -> None:
        """
        Execute all Interactions for this step.

        :param current_time: Current time of the simulation.
        :param fail_on_step_error: Raise an error when a command execution has an exit code other than 0. Will cancel the simulation.
        """
        for command in self.commands:
            command.execute()

            if command.result.exit_code != 0 and fail_on_step_error:
                raise RuntimeError(f"Step: {current_time} | {str(command)}")

    def __str__(self) -> str:
        return f"Step: {' | '.join(str(command) for command in self.commands)}"

    def __repr__(self) -> str:
        return self.__str__()
