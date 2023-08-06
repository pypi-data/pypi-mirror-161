from enum import Enum, auto
from typing import List, Optional, Dict

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class FRRDaemon(Enum):
    """
    Enumerator class for the different FRR daemons.
    """

    bgpd = (auto(),)
    ospfd = (auto(),)
    ospf6d = (auto(),)
    ripd = (auto(),)
    ripngd = (auto(),)
    isisd = (auto(),)
    pimd = (auto(),)
    ldpd = (auto(),)
    nhrpd = (auto(),)
    eigrpd = (auto(),)
    babeld = (auto(),)
    sharpd = (auto(),)
    pbrd = (auto(),)
    bfdd = (auto(),)
    fabricd = (auto(),)
    vrrpd = (auto(),)


class ExecuteRouterConfigCommand(Command):
    """
    Execute a single command or list of commands using the FRR cli.
    """

    def __init__(self, executor: NodeExecutor, command_list: List[str], daemon: Optional[FRRDaemon] = None):
        """
        Create the command object.

        :param command_list: List of commands.
        :param daemon: (Optional) Enum of FRR daemon.
        """
        self.daemon: Optional[FRRDaemon] = daemon
        super().__init__(executor, command_list)

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute command to config router.

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step
        :return: CommandResult.
        """
        # Result: "conf t", "<cmd_1>", ...
        self.command_list = ["conf t"] + self.command_list

        # Result: "echo conf t", "echo <cmd_1>", ...
        echo_command_list: List[str] = [f"echo {command}" for command in self.command_list]

        # Result: "echo conf t; echo <cmd_1>; ..."
        echo_command_str: str = "; ".join(echo_command_list) + ";"

        # Result: "{ echo conf t; echo <cmd_1>; ... } | vtysh"
        vtysh_command_str: str = "{ " + echo_command_str + " } | vtysh"

        if self.daemon:
            # Result: "{ echo conf t; echo <cmd_1>; ... } | vtysh -d <daemon>"
            vtysh_command_str += f" -d {self.daemon.name}"

        exec_result = self.executor.execute_command(["bash", "-c", vtysh_command_str], log_error_only=True)
        self.result = CommandResult(exec_result, exec_result.exit_code)
        return self.result
