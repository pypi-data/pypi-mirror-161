import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class DownloadRouterConfigFileCommand(Command):
    """
    Command class to download router configuration.
    """

    def __init__(self, executor: NodeExecutor) -> None:
        """
        Initialize an DownloadRouterConfigFileCommand object.

        :param executor: NodeExecutor that the command will be run with.
        """
        super().__init__(executor, [])

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute all commands to collect router configuration and save in file.

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step
        :return: CommandResult.
        """
        return_dict: Dict[str, Any] = {}
        backup_cmd_result: ExecResult = ExecResult()
        try:

            # Write current config to /etc/frr/frr.conf
            backup_cmd_result = self.executor.execute_command(
                ["bash", "-c", "{ echo write integrated; } | vtysh"], log_error_only=True
            )
            return_dict["backup_cmd_result"] = backup_cmd_result

            # Download /etc/frr/frr.conf
            backup_local_dir: Path = self.executor.copy_file_from_node("/etc/frr/frr.conf")

            # Rename downloaded file to unique name
            new_file_name = str(backup_local_dir / f"frr.conf.{self.executor.name}.{time.strftime('%Y%m%d-%H%M%S')}")
            os.rename(str(backup_local_dir / "frr.conf"), new_file_name)

            return_dict["path"] = new_file_name
            return_code = backup_cmd_result.exit_code

        except Exception as e:
            self.logger.error(e)
            return_dict["error"] = str(e)
            return_code = 1

        self.result = CommandResult(backup_cmd_result, return_code, return_dict)
        return self.result
