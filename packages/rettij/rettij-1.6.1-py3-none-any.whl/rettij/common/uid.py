from threading import Lock
from typing import List


class UID:
    """
    Class to supply runtime-unique identifiers. Can supply a maximum of 1048575 (16^5) UIDs. Thread safe.
    """

    max_len: int = pow(16, 5)
    uid_list: List[str] = [f"{0:04x}"]
    lock = Lock()

    @staticmethod
    def generate_uid() -> str:
        """
        Generate a runtime-unique identifier of 6 hexadecimal symbols.

        :return: Unique identifier
        """
        UID.lock.acquire()
        if len(UID.uid_list) == UID.max_len:
            raise RuntimeError(f"Maximum number of UIDs reached ({UID.max_len}). How did you even achieve this?")

        uid = f"{int(UID.uid_list[-1], 16) + 1:04x}"
        UID.uid_list.append(uid)

        UID.lock.release()
        return uid


if __name__ == "__main__":

    for i in range(UID.max_len - 1):
        if i % 10000 == 0:
            print(f"---{i:,}/{UID.max_len - 1:,}---")
        UID.generate_uid()

    print(UID.uid_list[-1])
