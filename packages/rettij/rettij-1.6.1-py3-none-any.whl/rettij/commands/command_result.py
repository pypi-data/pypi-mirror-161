from typing import Dict, Any, Optional

from rettij.topology.exec_result import ExecResult


class CommandResult:
    """
    Storage for the result of a Command.
    """

    def __init__(
        self, exec_result: ExecResult, exit_code: Optional[int] = None, values: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a CommandResult object.

        :param exec_result: ExecResult object of the command.
        :param exit_code: (Optional) Exit code of the command execution. Default: None.
        :param values: (Optional) Custom values parsed from the command execution output. Default: None.
        """
        self.exec_result: ExecResult = exec_result
        if not values:
            values = {}
        self.values: Dict[str, Any] = values
        self.__exit_code: Optional[int] = exit_code

    @property
    def exit_code(self) -> int:
        """
        Retrieve the exit code of the command.

        :return: Command exit code. If the CommandResult has no explicit exit code, the exit code from its 'exec_result' will be used.
        """
        if isinstance(self.__exit_code, int):
            return self.__exit_code
        else:
            return self.exec_result.exit_code

    @property
    def std_out(self) -> str:
        """
        Retrieve the STDOUT content of the command.

        :return: Command STDOUT content.
        """
        return self.exec_result.std_out

    @property
    def std_err(self) -> str:
        """
        Retrieve the STDERR content of the command.

        :return: Command STDERR content.
        """
        return self.exec_result.std_err

    @property
    def api_response(self) -> Dict:
        """
        Retrieve the Kubernetes API response for the command.

        :return: Command API response.
        """
        return self.exec_result.api_response

    def __getitem__(self, item: str) -> Any:
        return self.values[item]

    def __str__(self) -> str:
        return f"Exit code {self.exit_code}: {self.values} | ExecResult: {self.exec_result}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CommandResult):
            return False

        if str(self) == str(other):
            return True
        else:
            return False
