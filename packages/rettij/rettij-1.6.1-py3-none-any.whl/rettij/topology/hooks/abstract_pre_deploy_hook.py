from abc import ABC, abstractmethod

from rettij.topology.network_components.node import Node
from rettij.topology.node_container import NodeContainer


class AbstractPreDeployHook(ABC):
    """
    This abstract class defines the class signature for a 'pre-deploy' hook.

    It allows definition of custom code to be run by the Node before the Nodes are deployed.
    This hook needs to be implemented by a component in order to be used.
    """

    @abstractmethod
    def execute(
        self,
        node: Node,
        nodes: NodeContainer,
    ) -> None:
        """
        Run custom code for Node before all nodes are deployed.

        This is an abstract method definition for a component pre-deploy hook.
        It has to be implemented by each specific component.

        :param node: Node to execute the hook for
        :param nodes: NodeContainer object with all simulation Nodes.
        """
        raise NotImplementedError("This method has to be implemented!")
