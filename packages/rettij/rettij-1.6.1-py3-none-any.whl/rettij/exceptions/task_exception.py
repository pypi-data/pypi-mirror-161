class TaskException(Exception):
    """
    Exception thrown if task failed.
    """

    def __init__(self, task: str, msg: str) -> None:
        """
        Throw a new TaskException.

        :param task: Name of task.
        :param msg: Task fail message.
        """
        super().__init__("Task '{}' failed with message '{}'".format(task, msg))
