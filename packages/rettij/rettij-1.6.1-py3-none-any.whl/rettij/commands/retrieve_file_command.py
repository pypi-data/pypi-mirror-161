from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class RetrieveFileCommand(Command):
    """
    Class defining a command to copy a file from a Node.

    Returns when execution has finished.
    """

    def __init__(self, executor: NodeExecutor, file_path_on_node: str, dst_dir: str = "", privileged: bool = False):
        """
        Initialize a RetrieveFileCommand object.

        :param executor: NodeExecutor to execute the Command on.
        :param file_path_on_node: Source path on the executor.
        :param dst_dir: Destination directory path on the local machine.
        :param privileged: (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        """
        self.file_path_on_node: str = file_path_on_node
        self.dst_dir: str = dst_dir

        super().__init__(executor, [], privileged=privileged)

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute the command using the executor.

        :param inputs: Dict of inputs for the current step
        :param current_time: Current time of the simulation.
        :return: CommandResult.
        """
        try:
            local_path: Path = self.executor.copy_file_from_node(self.file_path_on_node, self.dst_dir)
            self.result = CommandResult(ExecResult(), 0, {"path": local_path / self.file_path_on_node})

            if self.result.exit_code != 0:
                self.logger.error(self.result)
            else:
                self.logger.info(
                    f"File copied from '{self.executor.name}:{self.file_path_on_node}' to '{self.result.values.get('path')}'."
                )
        except Exception as e:
            raise e
        return self.result
