from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.common.file_permissions import FilePermissions
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class PutFileCommand(Command):
    """
    Class defining a command to copy a file to a Node.
    """

    def __init__(
        self,
        executor: NodeExecutor,
        src_file_path: ValidatedFilePath,
        dst_dir: str = "",
        file_permissions: Optional[FilePermissions] = None,
        privileged: bool = False,
    ):
        """
        Initialize a PutFileCommand object.

        :param executor: NodeExecutor to execute the Command on.
        :param src_file_path: Source path on the local machine.
        :param dst_dir: Destination directory path on the executor.
        :param file_permissions: Target file permissions representation.
        :param privileged: (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        """
        self.src_file_path: ValidatedFilePath = src_file_path
        self.dst_dir: str = dst_dir
        self.file_permissions: Optional[FilePermissions] = file_permissions

        super().__init__(executor, [], privileged=privileged)

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute the command using the executor.

        :param inputs: Dict of inputs for the current step
        :param current_time: Current time of the simulation.
        :return: CommandResult object.
        """
        try:
            remote_path: Path = self.executor.copy_file_to_node(self.src_file_path, self.dst_dir, self.file_permissions)
            self.result = CommandResult(ExecResult(), 0, {"path": self.dst_dir / remote_path})

            if self.result.exit_code != 0:
                self.logger.error(self.result)
            else:
                self.logger.info(
                    f"File copied from '{self.src_file_path}' to '{self.executor.name}:{self.result.values.get('path')}'."
                )

        except Exception as e:
            raise e
        return self.result
