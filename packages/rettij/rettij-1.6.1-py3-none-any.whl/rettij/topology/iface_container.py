from unittest.mock import MagicMock

from rettij.topology.network_components.interface import Interface


class IfaceContainer(dict):
    """
    Provide a simple container for Interfaces.

    Enable a way that single items can be accessed as attributes, e.g. node.n1.
    Supports dict-based access by inheriting from dict.
    """

    def __setitem__(self, iface_name: str, iface: Interface) -> None:
        if not isinstance(iface_name, str):
            raise TypeError(f"'iface_name' must be of type 'str', not '{type(iface_name)}'!")
        if not (
            isinstance(iface, Interface) or isinstance(iface, MagicMock)
        ):  # fix for error in unit test using MagicMock
            raise TypeError(f"'iface' must be of type 'Interface', not '{type(iface)}'!")
        super(IfaceContainer, self).__setitem__(iface_name, iface)

    def __getitem__(self, iface_name: str) -> Interface:
        try:
            iface = super(IfaceContainer, self).__getitem__(iface_name)
            if isinstance(iface, Interface) or isinstance(
                iface, MagicMock
            ):  # fix for error in unit test using MagicMock
                return iface
            else:
                raise AttributeError(f"Interface {iface_name} does not exist!")
        except KeyError as e:
            raise AttributeError(f"Interface {e} does not exist!")

    def __setattr__(self, iface_name: str, iface: Interface) -> None:
        self.__setitem__(iface_name, iface)

    def __delattr__(self, iface_name: str) -> None:
        self.__delitem__(iface_name)

    def __getattr__(self, iface_name: str) -> Interface:
        return self.__getitem__(iface_name)

    def __str__(self) -> str:
        iface_list: str = ", ".join(self.keys())
        return f"Available interface names: {iface_list}"

    def __repr__(self) -> str:
        # give the user a nicely formatted string when he simply types "ifaces" in the CLI
        return self.__str__()
