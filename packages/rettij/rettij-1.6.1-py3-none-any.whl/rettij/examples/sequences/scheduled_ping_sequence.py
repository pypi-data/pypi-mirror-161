from typing import Dict

from rettij.abstract_scheduled_sequence import AbstractScheduledSequence
from rettij.simulation_manager import SimulationManager
from rettij.topology.network_components.channel import Channel
from rettij.topology.node_container import NodeContainer


class ScheduledSequence(AbstractScheduledSequence):
    """
    This class defines a simple scheduled Sequence running pings between two Nodes.

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
        sm.add_step(
            scheduled_time=10, command=nodes.client0.ping, kwargs={"target": nodes.client1.ifaces.i0.ip, "c": 1}
        )
        sm.add_step(
            scheduled_time=20, command=nodes.client1.ping, kwargs={"target": nodes.client0.ifaces.i0.ip, "c": 1}
        )
