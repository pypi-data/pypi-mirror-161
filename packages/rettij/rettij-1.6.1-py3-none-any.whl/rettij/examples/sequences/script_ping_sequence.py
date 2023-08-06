from typing import Dict

from rettij.abstract_script_sequence import AbstractScriptSequence
from rettij.simulation_manager import SimulationManager
from rettij.topology.network_components.channel import Channel
from rettij.topology.node_container import NodeContainer


class ScriptSequence(AbstractScriptSequence):
    """
    This class defines a simple scripted Sequence running pings between two Nodes.

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
        Define the sequential / script simulation sequence to be run.

        Add commands like you would in the rettij CLI:

        .. code-block:: python

            nodes.n1.ping(nodes.n2.ifaces.i0.ip)

        All parameters are automatically supplied upon execution by rettij.

        :param sm: SimulationManager controlling the simulation.
        :param node: NodeContainer object with all simulation Nodes (alternative to 'nodes', same object referenced).
        :param nodes: NodeContainer object with all simulation Nodes (alternative to 'node', same object referenced).
        :param channel: Map of all simulation Channels (alternative to 'channels', same object referenced).
        :param channels: Map of all simulation Channels (alternative to 'channel', same object referenced).
        """
        nodes.client0.ping(target=nodes.client1.ifaces.i0.ip.compressed, c=1)
        nodes.client1.ping(target=nodes.client0.ifaces.i0.ip.compressed, c=1)
