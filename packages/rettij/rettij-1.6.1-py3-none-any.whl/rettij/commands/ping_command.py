from __future__ import annotations

import re
from ipaddress import IPv4Address
from re import Match
from typing import Any, Dict, Optional, List

from rettij.commands.command import Command
from rettij.commands.command_result import CommandResult
from rettij.topology.exec_result import ExecResult
from rettij.topology.node_executors.node_executor import NodeExecutor


class PingCommand(Command):
    """
    Class defining a command for running a ping.

    Returns when execution has finished.
    """

    def __init__(
        self,
        executor: NodeExecutor,
        target: IPv4Address,
        detached: bool = False,
        privileged: bool = False,
        **kwargs: Any,
    ):
        """
        Run a ping by supplying a target IP and an optional package count.

        :param target: Target IP.
        :param detached: (Optional) If 'True', run the command asynchronously / in the background, meaning execution will not wait for the command to finish. Otherwise, the execution will be blocked until the command execution is finished. Default: 'False'.
        :param privileged: (Optional) If True, the supplied command_list will be executed in 'privileged mode', allowing root access. USE WITH CAUTION.
        :param kwargs: Optional parameters for the linux 'ping' command
          - 'a' - use audible ping
          - 'A' - use adaptive ping
          - 'B' - sticky source address
          - 'c' - stop after <count> replies
          - 'D' - print timestamps
          - 'd' - use SO_DEBUG socket option
          - 'f' - flood ping
          - 'h' - print help and exit
          - 'I' - either interface name or address
          - 'i' - seconds between sending each packet
          - 'L' - suppress loopback of multicast packets
          - 'l' - send <preload> number of packages while waiting replies
          - 'm' - tag the packets going out
          - 'M' - define mtu discovery, can be one of <do|dont|want>
          - 'n' - no dns name resolution
          - 'O' - report outstanding replies
          - 'p' - contents of padding byte
          - 'q' - quiet output
          - 'Q' - use quality of service <tclass> bits
          - 's' - use <size> as number of data bytes to be sent
          - 'S' - use <size> as SO_SNDBUF socket option value
          - 't' - define time to live
          - 'U' - print user-to-user latency
          - 'v' - verbose output
          - 'V' - print version and exit
          - 'w' - reply wait <deadline> in seconds
          - 'W' - time to wait for response in seconds
        """
        args: List[str] = []
        for arg, val in kwargs.items():
            args.append(f"-{arg}")
            if not isinstance(val, bool):  # dont append a value for flags
                args.append(val)

        command_list = ["ping", *args, target.compressed]
        super().__init__(executor, command_list, detached=detached, privileged=privileged)

    def execute(self, current_time: int = 0, inputs: Optional[Dict] = None) -> CommandResult:
        """
        Execute the command using the executor.

        :param current_time: Current time of the simulation.
        :param inputs: Dict of inputs for the current step
        :return: CommandResult.
        """
        ping_result: ExecResult = self.executor.execute_command(
            self.command_list, detached=self.detached, privileged=self.privileged
        )

        value_dict: Dict[str, Any] = {}
        if not self.detached:  # Only run in foreground mode, as detached mode has no output to parse yet.
            output: str = ping_result.std_out

            transmitted_regex_str: str = r"(\d+) packets transmitted"
            transmitted_match: Optional[Match] = re.search(transmitted_regex_str, output)
            if isinstance(transmitted_match, Match):
                transmitted: int = int(transmitted_match.groups()[0])
            else:
                raise ValueError(f"Regular expression '{transmitted_regex_str}' not found in output!")

            received_regex_str: str = r"(\d+) received"
            received_match: Optional[Match] = re.search(received_regex_str, output)
            if isinstance(received_match, Match):
                received: int = int(received_match.groups()[0])
            else:
                raise ValueError(f"Regular expression '{received_regex_str}' not found in output!")

            loss_regex_str: str = r"(\d+)% packet loss"
            loss_match: Optional[Match] = re.search(loss_regex_str, output)
            if isinstance(loss_match, Match):
                loss: int = int(loss_match.groups()[0])
            else:
                raise ValueError(f"Regular expression '{loss_regex_str}' not found in output!")

            self.logger.info(
                f"Result for {self.command_list} on {self.executor.name}: Packets transmitted: {str(transmitted)}, received: {str(received)}, loss: {str(loss)}"
            )

            average: float
            if loss != 100:
                average_regex_str: str = r"[\w/]+ = [\d.]+/(\d+\.\d+)"
                average_match: Optional[Match] = re.search(average_regex_str, output)
                if isinstance(average_match, Match):
                    average = float(average_match.groups()[0])
                else:
                    raise ValueError(f"Regular expression '{average_regex_str}' not found in output!")
            else:
                average = -1.0

            value_dict = {
                "output": output,
                "transmitted": transmitted,
                "received": received,
                "loss": loss,
                "average": average,
            }

        self.result = CommandResult(ping_result, values=value_dict)
        return self.result
