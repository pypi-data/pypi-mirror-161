class NotFoundException(Exception):
    """
    Exception thrown if object not found.
    """

    def __init__(self, query_obj: object, wanted_object: object) -> None:
        """
        Throw a new NotFoundException.

        :param query_obj: Current object.
        :param wanted_object: Expected object.
        """
        wanted_type = type(wanted_object)

        super().__init__("Could not find object of type {0} for query {1}.".format(wanted_type, str(query_obj)))
