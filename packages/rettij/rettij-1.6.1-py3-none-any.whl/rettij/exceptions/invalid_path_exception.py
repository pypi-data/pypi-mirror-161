import os
from pathlib import Path
from typing import Union


class InvalidPathException(Exception):
    """
    Create a new InvalidPathException.

    Please use kind='Directory' when validating a directory path and kind='File' when validating a file path.
    """

    def __init__(self, path: Union[str, Path], kind: str) -> None:
        """
        Throw a new InvalidPathException.

        :param path: Path.
        :param kind: Kind of path.
        """
        self.path: str = str(path)
        self.path_normalized = os.path.normpath(self.path)
        super().__init__(f"There is no {kind} at path '{self.path}'! (normalized: {self.path_normalized})")
