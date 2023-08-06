from abc import ABC, abstractmethod
from typing import Any

from rettij.topology.network_components.node import Node


class AbstractConnectHook(ABC):
    """
    This abstract class defines the class signature for a 'connect' hook.

    It allows definition of custom code to connect one Node to another.
    This hook needs to be implemented by a component in order to be used.
    """

    @abstractmethod
    def execute(self, source_node: Node, target_node: Node, **kwargs: Any) -> None:
        """
        Run custom code to connect one Node to another.

        This is an abstract method definition for a component connect hook.
        It has to be implemented by each specific component.

        :param source_node: Base node
        :param target_node: Node to connect the base Node to
        :param kwargs: Custom parameters. Contents depend on the specific implementation.
        """
        raise NotImplementedError("This method has to be implemented!")
