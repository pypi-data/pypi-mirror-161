class CopyException(Exception):
    """
    Exception thrown if copying a file wasn't successful.
    """

    def __init__(self, file_name: str, src_name: str, dst_name: str) -> None:
        """
        Throw a new CopyException.

        :param file_name: Name of file.
        :param src_name: Source path.
        :param dst_name: Destination path.
        """
        super().__init__("Failed to copy file '{}' from {} to {}".format(file_name, src_name, dst_name))
