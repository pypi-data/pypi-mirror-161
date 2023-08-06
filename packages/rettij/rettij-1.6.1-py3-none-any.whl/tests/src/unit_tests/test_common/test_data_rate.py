import unittest
from typing import Dict

from rettij.common.data_rate import DataRate, DataRateUnit


class TestDataRate(unittest.TestCase):
    """
    This TestCase contains tests regarding the DataRate class.
    """

    def test_init(self) -> None:
        """
        Verify that a DataRate object can be initialized and that error handling works as expected.

        Tested values:
        - 100<unit>, 10.0<unit> for all possible units
        - 0<unit> and -1<unit> for all possible units (ValueError)
        - Rate without unit (ValueError)
        - Rate with bogus unit (ValueError)
        - Wrong parameter type (ValueError)
        """
        failed_values_with_exception_msgs: Dict[str, str] = {}

        # Test values 100<unit>, 10.0<unit>, 0<unit> and -1<unit> for all possible units
        for data_rate_unit in DataRateUnit.members():

            valid_data_rate_value_int = f"100{data_rate_unit}"
            try:
                DataRate(valid_data_rate_value_int)
            except Exception as e:
                failed_values_with_exception_msgs[valid_data_rate_value_int] = str(e)

            valid_data_rate_value_float = f"10.0{data_rate_unit}"
            try:
                DataRate(valid_data_rate_value_float)
            except Exception as e:
                failed_values_with_exception_msgs[valid_data_rate_value_float] = str(e)

            invalid_data_rate_value_zero = f"0{data_rate_unit}"
            try:
                DataRate(invalid_data_rate_value_zero)
                failed_values_with_exception_msgs[
                    invalid_data_rate_value_zero
                ] = f"Value '{invalid_data_rate_value_zero}' should raise exception, but didn't"
            except Exception:
                pass

            invalid_data_rate_value_neg = f"-1{data_rate_unit}"
            try:
                DataRate(invalid_data_rate_value_neg)
                failed_values_with_exception_msgs[
                    invalid_data_rate_value_neg
                ] = f"Value '{invalid_data_rate_value_neg}' should raise exception, but didn't"
            except Exception:
                pass

        # Test rate without unit
        try:
            val_1 = "100"
            DataRate(val_1)
            failed_values_with_exception_msgs[val_1] = f"Value '{val_1}' should raise exception, but didn't"
        except Exception:
            pass

        # Test rate with bogus unit
        try:
            val_2 = "100ABC"
            DataRate(val_2)
            failed_values_with_exception_msgs[val_2] = f"Value '{val_2}' should raise exception, but didn't"
        except Exception:
            pass

        # Test init with wrong parameter type
        try:
            val_3 = 100
            # noinspection PyTypeChecker
            DataRate(val_3)  # type: ignore
            failed_values_with_exception_msgs[str(val_3)] = f"Value '{val_3}' (int) should raise exception, but didn't"
        except Exception:
            pass

        if len(failed_values_with_exception_msgs.keys()) > 0:
            self.fail(msg=" | ".join([f"{val}: {msg}" for val, msg in failed_values_with_exception_msgs.items()]))

    def test_comparison(self) -> None:
        """
        Verify that all data rate comparison operations works as expected.
        """
        self.assertTrue(DataRate("1000bps") == DataRate("1kbps"))

        self.assertTrue(DataRate("1bps") < DataRate("1kbps"))
        self.assertTrue(DataRate("1bps") <= DataRate("1kbps"))
        self.assertTrue(DataRate("1kbps") > DataRate("1bps"))
        self.assertTrue(DataRate("1kbps") >= DataRate("1bps"))
