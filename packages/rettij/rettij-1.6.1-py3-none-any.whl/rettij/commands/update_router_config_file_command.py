from typing import Optional, Dict

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.commands.download_router_config_file_command import DownloadRouterConfigFileCommand
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class UpdateRouterConfigFileCommand(Command):
    """
    Command class to update router config file.
    """

    def __init__(self, executor: NodeExecutor, config_file_path: ValidatedFilePath) -> None:
        """
        Create a command object that is used to update router config file.

        :param config_file_path: path to config file.
        """
        self.config_file_path: ValidatedFilePath = config_file_path
        super().__init__(executor, [])

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Update the router config via a config file.

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step.
        :return: CommandResult.
        """
        return_dict = {}
        update_cmd_result: ExecResult = ExecResult()
        try:

            # Create backup of current configuration
            backup_cmd_result = DownloadRouterConfigFileCommand(self.executor).execute()
            backup_file_path = backup_cmd_result.values.get("path", "")
            return_dict["backup_local_dir"] = backup_file_path

            with open(self.config_file_path, "r") as config_file:
                config = config_file.read().splitlines()

            update_cmd = ["vtysh", "-c", "conf t"]
            for item in config:
                update_cmd.append("-c")
                update_cmd.append(item)

            update_cmd_result = self.executor.execute_command(update_cmd, log_error_only=True)
            return_dict["update_cmd_result"] = update_cmd_result

            # Return code is 0, otherwise highest error code
            return_code = max(backup_cmd_result.exit_code, update_cmd_result.exit_code)

        except Exception as e:
            self.logger.error(e)
            return_dict["error"] = str(e)
            return_code = 1

        self.result = CommandResult(update_cmd_result, return_code, return_dict)
        return self.result
