from ipaddress import IPv4Address
from typing import List

from rettij.commands.run_command import RunCommand
from rettij.topology.node_executors.node_executor import NodeExecutor


class NmapCommand(RunCommand):
    """
    Class defining a command for running an NMAP tcp scan.

    Returns when execution has finished.
    """

    def __init__(self, executor: NodeExecutor, target: IPv4Address, tcp_ports: List[int] = None):
        """
        Run an NMAP tcp scan by supplying a target IP and optional ports.

        :param target: Target IP.
        :param tcp_ports: (Optional) Target ports.
        """
        if tcp_ports:
            ports_joined = ",".join(str(port) for port in tcp_ports)
            ports_param = ["-p", f"T:{ports_joined}"]
        else:
            ports_param = [""]

        super().__init__(executor, ["nmap", "-sT", *ports_param, target.compressed])
