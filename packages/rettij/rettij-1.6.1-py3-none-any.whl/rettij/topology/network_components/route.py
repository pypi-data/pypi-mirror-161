from __future__ import annotations

from ipaddress import IPv4Network, IPv4Address
from typing import Optional

from rettij.common.logging_utilities import LoggingSetup


class Route:
    """
    This class stores a IPv4 network route.
    """

    def __init__(
        self,
        network: IPv4Network,
        gateway: IPv4Address,
        metric: Optional[int] = None,
    ):
        """
        Initialize a Route object.

        :param network: Destination network for the route.
        :param gateway: Gateway / next hop on the route.
        :param metric: (Optional) Metric for the route.
        """
        self.logger = LoggingSetup.submodule_logging(self.__class__.__name__)

        self.metric: Optional[int] = metric
        self.gateway: IPv4Address = IPv4Address(gateway)
        self.network: IPv4Network = IPv4Network(network)
