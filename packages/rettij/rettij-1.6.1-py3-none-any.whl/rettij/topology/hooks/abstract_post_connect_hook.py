from abc import ABC, abstractmethod

from rettij.topology.network_components.node import Node


class AbstractPostConnectHook(ABC):
    """
    This abstract class defines the class signature for a 'post-connect' hook.

    It allows definition of custom code to be run by the Node after `connect` hook is executed.
    This hook needs to be implemented by a component in order to be used.
    """

    @abstractmethod
    def execute(
        self,
        node: Node,
    ) -> None:
        """
        Run custom code for Node after `connect` hook is executed.

        This is an abstract method definition for a component post-connect hook.
        It has to be implemented by each specific component.

        :param node: Node to execute the hook for
        """
        raise NotImplementedError("This method has to be implemented!")
