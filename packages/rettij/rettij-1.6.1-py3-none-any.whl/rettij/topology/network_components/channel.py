from __future__ import annotations

from typing import Optional, Dict

from rettij.common.data_rate import DataRate


class Channel(object):
    """
    This class represents a point-to-point network connection between two network interfaces.
    """

    def __init__(self, name: str, vni: int, data_rate: Optional[str] = None, delay: Optional[str] = None) -> None:
        """
        Initialize a Channel object.

        Refer to /docs/working-with-rettij.md#channels for more information.

        :param name: Unique Channel id
        :param vni: Channel VXLAN Network Identifier (VNI)
        :param data_rate: Channel data rate string
        :param delay: Channel delay string
        """
        self.name: str = name
        self.vni: int = vni

        self.data_rate: Optional[DataRate] = DataRate(data_rate) if data_rate else None
        self.delay: Optional[str] = delay

        self._connected_node_names_and_data_rates: Dict[str, DataRate] = {}

    def on_node_connect(self, node_name: str, data_rate: DataRate) -> None:
        """
        Add a node's name and data rate to the dictionary of connected nodes.

        The connected nodes are used by the NetworkManager for tunnel creation and data rate selection.

        :param node_name: Node name
        :param data_rate: Node data rate
        """
        if len(self._connected_node_names_and_data_rates.keys()) >= 2:
            raise ValueError(
                "Channel {0} is already connected to 2 nodes. Currently, a channel can only be a 1-1 connection.".format(
                    self.name
                )
            )
        else:
            self._connected_node_names_and_data_rates[node_name] = data_rate

    @property
    def connected_node_names_and_data_rates(self) -> Dict[str, DataRate]:
        """
        Return the connected nodes.

        This is done via a property so a node can only be connected via on_node_connect().

        :return: Connected node names and data rates
        """
        return self._connected_node_names_and_data_rates

    @property
    def name(self) -> str:
        """
        Return the channels id.

        :return: Channel id
        """
        return self._channel_id

    @name.setter
    def name(self, channel_id: str) -> None:
        """
        Set the channel id.

        TODO: Add validity check

        :param channel_id: Channel id
        """
        self._channel_id: str = channel_id

    @property
    def vni(self) -> int:
        """
        Return the VXLAN Network Identifier (VNI) of the channel.

        :return: VXLAN Network Identifier (VNI)
        """
        return self._vni

    @vni.setter
    def vni(self, vni: int) -> None:
        """
        Set the VXLAN Network Identifier (VNI) of the channel.

        Verifies that the VNI is within the valid value range of 0 to 16777215.

        :param vni: VXLAN Network Identifier (VNI)
        """
        if not isinstance(vni, int):
            raise ValueError(f"VNI has to be integer, but is {type(vni)}.")
        if vni > 16777215:
            raise ValueError("Too many channels! Maximum VNI of 16777215 exceeded.")
        elif vni < 0:
            raise ValueError("VNI has to be between 0 and 16777215")
        self._vni = vni

    @property
    def delay(self) -> Optional[str]:
        """
        Return the channel delay.

        :return: Channel delay (e.g. "200ms" or "2s")
        """
        return self._delay

    @delay.setter
    def delay(self, delay: Optional[str]) -> None:
        """
        Set the channel delay.

        Refer to /docs/working-with-rettij.md#channels for more information.
        TODO: Add validity check

        :param delay: Channel delay
        """
        self._delay: Optional[str] = delay

    def __str__(self) -> str:
        return "Channel: {}".format(self.name)
