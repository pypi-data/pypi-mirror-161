from ipaddress import IPv4Address
from typing import Dict

from rettij.abstract_scheduled_sequence import AbstractScheduledSequence
from rettij.simulation_manager import SimulationManager
from rettij.topology.network_components.channel import Channel
from rettij.topology.node_container import NodeContainer


class ScheduledSequence(AbstractScheduledSequence):
    """
    This class defines a scheduled Sequence running tcpdump and a ping between Nodes.

    It is meant to be used together with the simple-switch_topology.yml topology.
    """

    def define(
        self,
        sm: SimulationManager,
        node: NodeContainer,
        nodes: NodeContainer,
        channel: Dict[str, Channel],
        channels: Dict[str, Channel],
    ) -> None:
        """
        Define the timed steps simulation sequence to be run.

        Add timed steps like this:

        .. code-block:: python

            sm.add_step(
                scheduled_time=1,
                command = nodes.client0.ping,
                args = (nodes.client1.ifaces.i0.ip,),
                kwargs = {'c': 10}
            )

        All parameters are automatically supplied upon execution by rettij.

        :param sm: SimulationManager controlling the simulation.
        :param node: NodeContainer object with all simulation Nodes (alternative to 'nodes', same object referenced).
        :param nodes: NodeContainer object with all simulation Nodes (alternative to 'node', same object referenced).
        :param channel: Map of all simulation Channels (alternative to 'channels', same object referenced).
        :param channels: Map of all simulation Channels (alternative to 'channel', same object referenced).
        """
        ############################################################################################################
        # START YOUR CODE
        ############################################################################################################

        # Start tcpdump on simple-switch node
        pcap_file_name = "demo.pcap"
        tcpdump_cmd = sm.add_step(
            scheduled_time=0,
            command=nodes.switch0.run,
            kwargs={
                "shell_cmd": ["tcpdump", "-i", "vxlan-bridge", "-e", "-s", "0", "-w", pcap_file_name],
                "detached": True,
            },
        )

        client1_ip: IPv4Address = nodes.client1.ifaces.i0.ip
        sm.add_step(scheduled_time=1, command=nodes.client0.ping, kwargs={"target": client1_ip, "c": 10})

        # Stop tcpdump on simple-switch node
        sm.add_step(scheduled_time=2, command=nodes.switch0.stop_detached, args=(tcpdump_cmd,))

        # Download the PCAP file
        sm.add_step(scheduled_time=3, command=nodes.switch0.copy_file_from_node, args=(pcap_file_name,))

        ############################################################################################################
        # END YOUR CODE
        ############################################################################################################
