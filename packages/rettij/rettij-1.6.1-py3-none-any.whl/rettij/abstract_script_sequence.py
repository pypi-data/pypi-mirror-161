from abc import ABC, abstractmethod
from typing import Dict

from rettij.simulation_manager import SimulationManager
from rettij.topology.network_components.channel import Channel
from rettij.topology.node_container import NodeContainer


class AbstractScriptSequence(ABC):
    """
    This abstract class defines the signature for a simulation sequence which is run sequentially like a shell script, i.e. without (external) scheduling of timed steps.
    """

    @abstractmethod
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
        raise NotImplementedError("This method has to be implemented!")
