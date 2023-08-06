import re


class FilePermissions:
    """
    This class stores UNIX file permissions in octet form.
    """

    permission_regex: str = r"^[0-7]{3}$"
    name_regex: str = r"^[a-z][-a-z0-9_]*$"

    def __init__(self, permissions: str, owner: str, group: str) -> None:
        """
        Initialize a FilePermissions object.

        :param permissions: Octal permission string. Example: '755'.
        :param owner: Owner name.
        :param group: Group name.
        """
        self.permissions: str = permissions
        self.owner: str = owner
        self.group: str = group

    @property
    def permissions(self) -> str:
        """
        Retrieve the permissions.

        :return: Octal permission string.
        """
        return self.__permissions

    @permissions.setter
    def permissions(self, permissions: str) -> None:
        """
        Set the permissions.

        Verifies that the octal permission string is valid.

        :param permissions: Octal permission string.
        """
        if re.match(self.permission_regex, permissions):
            self.__permissions = permissions
        else:
            raise ValueError(f"{permissions} are not valid file permissions!")

    @property
    def owner(self) -> str:
        """
        Retrieve the owner.

        :return: Owner name.
        """
        return self.__owner

    @owner.setter
    def owner(self, owner: str) -> None:
        """
        Set the owner.

        Verifies that the owner name is valid.

        :param owner: Owner name.
        """
        if re.match(self.name_regex, owner):
            self.__owner = owner
        else:
            raise ValueError(f"{owner} is not a valid user name!")

    @property
    def group(self) -> str:
        """
        Retrieve the group.

        :return: Group name.
        """
        return self.__group

    @group.setter
    def group(self, group: str) -> None:
        """
        Set the group.

        Verifies that the group name is valid.

        :param group: Group name.
        """
        if re.match(self.name_regex, group):
            self.__group = group
        else:
            raise ValueError(f"{group} is not a valid group name!")
