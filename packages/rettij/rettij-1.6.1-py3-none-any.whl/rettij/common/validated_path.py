import os
from pathlib import Path
from typing import Any

from rettij.exceptions.invalid_path_exception import InvalidPathException


class ValidatedPath(str):
    """
    Base class for ValidatedFilePath and ValidatedDirPath.

    Implements str() and repr() methods.
    """

    path: str = ""

    def __str__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return self.path


class ValidatedFilePath(ValidatedPath):
    """
    This class stores a validated file path.

    Validation happens during initialization by checking if the supplied path actually points to a file.
    Once initialized, the contained file path does not need to be checked before using anymore.
    """

    def __init__(self, path: Any) -> None:
        """
        Initialize a ValidatedFilePath object.

        :param path: Path to the file.
        :raises: InvalidPathException: If a path is invalid or does not point to a file.
        """
        str_path: str = str(path)
        normalized_path = os.path.normpath(str_path)
        if os.path.isfile(normalized_path):
            self.path: str = normalized_path
        else:
            raise InvalidPathException(normalized_path, kind="File")

        super().__init__()

    # TODO: Replace by reworked constructor
    @staticmethod
    def join_paths(path: Any, *paths: Any) -> Any:
        """
        Join multiple path parts into a single, validated file path.

        :param path: Original path.
        :param paths: Additional path parts.
        :return: ValidatedFilePath object.
        """
        return ValidatedFilePath(Path(path, *paths))


class ValidatedDirPath(ValidatedPath):
    """
    This class stores a validated directory path.

    Validation happens during initialization by checking if the supplied path actually points to a directory.
    Once initialized, the contained directory path does not need to be checked before using anymore.
    """

    def __init__(self, path: Any) -> None:
        """
        Initialize a ValidatedDirPath object.

        :param path: Path to the directory.
        :raises: InvalidPathException: If a path is invalid or does not point to a directory.
        """
        str_path: str = str(path)
        normalized_path: str = os.path.normpath(str_path)
        if os.path.isdir(normalized_path):
            self.path: str = normalized_path
        else:
            raise InvalidPathException(path, kind="Directory")

        super().__init__()

    # TODO: Replace by reworked constructor
    @staticmethod
    def join_paths(path: Any, *paths: Any) -> Any:
        """
        Join multiple path parts into a single, validated directory path.

        :param path: Original path.
        :param paths: Additional path parts.
        :return: ValidatedFilePath object.
        """
        return ValidatedDirPath(Path(path, *paths))
