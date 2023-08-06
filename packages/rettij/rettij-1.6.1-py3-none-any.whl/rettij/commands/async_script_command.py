from __future__ import annotations

import tempfile
from pathlib import Path
from time import sleep
from typing import Optional, Dict, List

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.common.uid import UID
from rettij.common.validated_path import ValidatedFilePath
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class AsyncScriptCommand(Command):
    """
    TODO: LEGACY CLASS. DO NOT REMOVE UNTIL ALL FUNCTIONALITY IS REFACTORED OR OBSOLETE.

    Class that defines an asynchronously executed script command.
    """

    def __init__(self, executor: NodeExecutor, command_list: List[str], privileged: bool = False):
        """
        Initialize an AsyncScriptCommand object.

        :param executor: NodeExecutor
        :param command_list: Command
        :param privileged: Privileged
        """
        self.result = CommandResult(ExecResult())
        super().__init__(executor, command_list, privileged)

    # TODO: Integrate with executor.execute
    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute the command using the executor.

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step
        :return: CommandResult.
        """
        script_name: str = f"script-{UID.generate_uid()}.sh"
        tmp_file_path: Path

        result: ExecResult
        with tempfile.TemporaryDirectory(prefix="rettij_AsyncScriptCommand_") as tmp_dir:
            tmp_file_path = Path(tmp_dir, script_name)
            with open(str(tmp_file_path), "w") as f:
                f.writelines(self.command_list)
            self.executor.copy_file_to_node(ValidatedFilePath(str(tmp_file_path)))

        result = self.executor.execute_command(["/bin/sh", f"/{script_name}"], detach=True, tty=True)

        get_pid_cmd = [
            "/usr/bin/pgrep",
            "-f",
            f"/{script_name}",
        ]

        try:
            pid: int = int((self.executor.execute_command(get_pid_cmd)).std_out)
        except ValueError as e:
            pid = 0
            self.logger.debug("{0}: {1}".format(type(e), e))

        self.logger.debug("Command is running with pid {}".format(pid))
        sleep(0.5)
        self.result = CommandResult(ExecResult(), 0, {"pid": pid, "stdout": result.std_out, "stderr": result.std_err})
        return self.result

    def stop(self) -> CommandResult:
        """
        Stop the Command.

        :return: CommandResult
        """
        result: ExecResult
        pid: int = self.result.values.get("pid", -1)

        command_list = ["/bin/kill", "-SIGKILL", str(pid)]
        result = self.executor.execute_command(command_list)

        return CommandResult(result)
