class HostNotAvailableException(Exception):
    """
    Exception thrown if host is not available.
    """

    def __init__(self, host: str, reason: str) -> None:
        """
        Throw a new HostNotAvailableException.

        :param host: Target hostname.
        :param reason: Reason message.
        """
        super().__init__(f"Connection to host {host} failed. Reason: '{reason}'")
