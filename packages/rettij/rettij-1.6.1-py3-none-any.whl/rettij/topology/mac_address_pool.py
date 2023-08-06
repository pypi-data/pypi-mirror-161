import random
from typing import List


class MacAddressPool:
    """
    This class tracks all MAC addresses in the simulation network.

    It can also create a unique new MAC address.
    """

    macs_in_use: List[str] = []

    @classmethod
    def add_used_mac(cls, mac: str) -> None:
        """
        Add a MAC address to the global list of addresses in use.

        :param mac: MAC address string.
        """
        cls.macs_in_use.append(mac)

    @classmethod
    def generate_unique_mac(cls) -> str:
        """
        Return a random mac address that is unique in the topology.

        Uses the 02:00:00 prefix which is not used by any real vendor.
        The first two bytes (0x02) make it a so called locally administered unicast address.
        """
        while True:
            # {:02x} formats an integer as a two digit hexadecimal, pads leading zero if hex <= F
            # : = Apply the following formatting to the value
            # 0 = Pad with leading zeros
            # 2 = Total number of digits
            # x = Format as hexadecimal
            mac_gen: str = "02:00:00:{:02x}:{:02x}:{:02x}".format(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            if mac_gen not in cls.macs_in_use:
                # add to used macs to prevent generating the same mac twice
                cls.add_used_mac(mac_gen)
                break
        return mac_gen
