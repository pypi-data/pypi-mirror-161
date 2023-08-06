from typing import Dict, Optional, List, Union

from rettij.override.kubernetes.stream.ws_client import WSClient


class ExecResult:
    """
    This class contains the result of running a command via an Executor.
    """

    def __init__(self) -> None:
        """
        Initialize an ExecResult object.
        """
        self.__exit_code: int = 0
        self.__std_out: str = ""
        self.__std_err: str = ""
        self.__api_response: Dict = {}
        self.__wsclient: Optional[WSClient] = None
        self.__command: Union[str, List[str]] = ""

    @property
    def exit_code(self) -> int:
        """
        Retrieve the exit code.

        :return: Exit code.
        """
        return self.__exit_code

    @exit_code.setter
    def exit_code(self, code: int) -> None:
        """
        Set the exit code.

        :param code: Exit code.
        """
        self.__exit_code = code

    @property
    def std_out(self) -> str:
        """
        Retrieve the contents of STDOUT.

        :return: Contents of STDOUT as string.
        """
        return self.__std_out

    def append_stdout(self, std_out: str) -> None:
        """
        Add contents of STDOUT.

        :param std_out: Contents of STDOUT as string.
        """
        self.__std_out += std_out

    @property
    def std_err(self) -> str:
        """
        Retrieve the contents of STDERR.

        :return: Contents of STDERR as string.
        """
        return self.__std_err

    def append_stderr(self, std_err: str) -> None:
        """
        Add contents of STDERR.

        :param std_err: Contents of STDERR as string.
        """
        self.__std_err += std_err

    @property
    def api_response(self) -> Dict:
        """
        Retrieve the Kubernetes API response.

        :return: Kubernetes API response as Dict.
        """
        return self.__api_response

    def set_api_response(self, api_response_dict: Dict) -> None:
        """
        Set the Kubernetes API response.

        :param api_response_dict: Kubernetes API response as Dict.
        """
        self.__api_response = api_response_dict

    @property
    def wsclient(self) -> WSClient:
        """
        Retrieve the Kubernetes API websocket client.

        :return: Kubernetes API websocket client object.
        """
        if self.__wsclient:
            return self.__wsclient
        else:
            raise AttributeError("This exec result has no WSClient.")

    def set_wsclient(self, wsclient: WSClient) -> None:
        """
        Set the Kubernetes API websocket client.

        :param wsclient: Kubernetes API websocket client object.
        """
        self.__wsclient = wsclient

    @property
    def command(self) -> Union[str, List[str]]:
        """
        Retrieve the command that was executed.

        :return: Command as string.
        """
        return self.__command

    @command.setter
    def command(self, command: Union[str, List[str]]) -> None:
        """
        Set the command that was executed.
        """
        self.__command = command

    def __str__(self) -> str:
        return (
            f"\n# ---- Start ExecResult ---- # \n"
            f"Exit code: {self.exit_code} \n"
            f"Command: \n"
            f"{self.command}\n"
            f"stdout: \n"
            f"{self.std_out}"
            f"stderr: \n"
            f"{self.std_err}"
            f"apierr: \n"
            f"{self.api_response}\n"
            f"# ---- End ExecResult ---- # \n"
        )

    def __repr__(self) -> str:
        return self.__str__()
