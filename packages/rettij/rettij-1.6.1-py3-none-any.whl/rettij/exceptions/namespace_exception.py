class NamespaceException(Exception):
    """
    Exception thrown if something went wrong with namespace.
    """

    NOT_FOUND = "NOT_FOUND"
    TERMINATING = "TERMINATING"
    OTHER = "OTHER"

    def __init__(self, namespace_id: str, cause: str) -> None:
        """
        Throw a new NamespaceException.

        :param namespace_id: ID of namespace.
        :param cause: Cause.
        """
        self.namespace_id = namespace_id
        super().__init__(f"{namespace_id}: {cause}")
