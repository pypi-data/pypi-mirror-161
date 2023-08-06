class TopologyException(Exception):
    """
    Exception thrown if a topology operation went wrong.
    """

    UNDEFINED = 0
    DATA_INVALID = 1
    SCHEMA_INVALID = 2
    SCHEMA_VALIDATION_FAILED = 3
    ADDRESS_VALIDATION_FAILED = 4
    CHANNEL_VALIDATION_FAILED = 5
    NODE_VALIDATION_FAILED = 6
    VERSION_VALIDATION_FAILED = 7
    VALIDATION_ERROR = 8

    causes = {
        UNDEFINED: "Undefined error",
        DATA_INVALID: "Syntax error during parsing of data JSON file",
        SCHEMA_INVALID: "Error during parsing of schema JSON file",
        SCHEMA_VALIDATION_FAILED: "Schema Validation not passed",
        ADDRESS_VALIDATION_FAILED: "Address Validation not passed",
        CHANNEL_VALIDATION_FAILED: "Channel Validation not passed",
        NODE_VALIDATION_FAILED: "Node Validation not passed",
        VALIDATION_ERROR: "Error during validation",
        VERSION_VALIDATION_FAILED: "Version validation not passed.",
    }

    def __init__(self, cause_nbr: int, topology_file_path: str, schema_file_path: str = "", message: str = ""):
        """
        Throw a new TopologyException.

        :param cause_nbr: Per-defined cause number.
        :param topology_file_path: Path the the topology file.
        :param schema_file_path: Path to schema file.
        :param message: Cause message.
        """
        self.cause_nbr: int = cause_nbr
        self.topology_file_path: str = topology_file_path
        self.schema_file_path: str = schema_file_path
        self.message: str = message

    def __str__(self) -> str:

        return "{} | Message: {} | Data file: '{}' | Schema file: '{}'".format(
            self.causes[self.cause_nbr], self.message, self.topology_file_path, self.schema_file_path
        )
