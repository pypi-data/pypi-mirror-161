"""
This module contains a helper class that allows storage and comparison of a 'tc' compatible data rate.

See https://man7.org/linux/man-pages/man8/tc.8.html.

Classes:
    - DataRateUnit - An enumerator for 'tc' compatible data rate units.
    - DataRate - Stores a 'tc' compatible data rate and implements methods for comparing data rates.
"""
from enum import Enum
from typing import List, Any


class DataRateUnit(Enum):
    """
    This class implements an enumerator for 'tc' compatible data rate units.

    The enumeration values are based on the SI and IEC units in relation to 1 bit.
    """

    BIT = 1
    KBIT = 1000
    MBIT = 1000 * 1000
    GBIT = 1000 * 1000 * 1000

    KIBIT = 1024
    MIBIT = 1024 * 1024
    GIBIT = 1024 * 1024 * 1024

    BPS = 8
    KBPS = 8 * 1000
    MBPS = 8 * 1000 * 1000
    GBPS = 8 * 1000 * 1000 * 1000

    KIBPS = 8 * 1024
    MIBPS = 8 * 1024 * 1024
    GIBPS = 8 * 1024 * 1024 * 1024

    @classmethod
    def values(cls) -> List[int]:
        """
        Return a list of all enumeration values.

        :return: List of all enumeration values (i.e. [1, 1000, 1000000, 1000000000, 1024, 1048576, 1073741824, 8, 8000, 8000000, 8000000000, 8192, 8388608, 8589934592])
        """
        return [e.value for e in cls]

    @classmethod
    def members(cls) -> List[str]:
        """
        Return a list of all enumeration members.

        :return: List of all enumeration members (i.e. ['BIT', 'KBIT', 'MBIT', 'GBIT', 'KIBIT', 'MIBIT', 'GIBIT', 'BPS', 'KBPS', 'MBPS', 'GBPS', 'KIBPS', 'MIBPS', 'GIBPS'])
        """
        return list(DataRateUnit.__members__)


class DataRate:
    """
    This class stores a 'tc' compatible data rate.

    It also implements methods for comparing data rates.
    """

    def __init__(self, data_rate_str: str):
        """
        Initialize a DataRate object by splitting the input string into a value and a unit.

        :param data_rate_str: Input data rate string (e.g. "10.3mpbs")
        """
        if not isinstance(data_rate_str, str):
            raise ValueError("Parameter 'data_rate_str' must be of type 'str'")

        # split number and unit (e.g. "10.3mpbs" -> "10.3" and "mbps")
        i, c = 0, ""
        for i, c in enumerate(data_rate_str):
            if not (c.isdigit() or c == "."):
                break
        rate: float = float(data_rate_str[:i])
        unit: DataRateUnit = DataRateUnit[data_rate_str[i:].strip().upper()]

        if rate > 0:
            self.rate: float = rate
            self.unit: DataRateUnit = unit
            self.rate_in_bit_per_sec: float = float(rate * unit.value)
        else:
            raise ValueError("Data rate must be > 0")

    def __str__(self) -> str:
        return f"{self.rate}{self.unit.name.lower()}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DataRate):
            return self.rate_in_bit_per_sec == other.rate_in_bit_per_sec
        else:
            return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, DataRate):
            return self.rate_in_bit_per_sec < other.rate_in_bit_per_sec
        else:
            return False

    def __le__(self, other: Any) -> bool:
        if isinstance(other, DataRate):
            return self.rate_in_bit_per_sec <= other.rate_in_bit_per_sec
        else:
            return False

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, DataRate):
            return self.rate_in_bit_per_sec >= other.rate_in_bit_per_sec
        else:
            return False

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, DataRate):
            return self.rate_in_bit_per_sec > other.rate_in_bit_per_sec
        else:
            return False
