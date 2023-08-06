def is_suited_host_system() -> bool:
    """
    Determine if the executing system is suited for rettij network integration.

    :return: True if suited, false if not
    """
    import socket
    import shutil
    import os
    from kubernetes.client import CoreV1Api, V1NodeAddress

    # hostname equals kubernetes master node hostname
    api = CoreV1Api()
    addresses: list = api.list_node().items[0].status.addresses
    if not V1NodeAddress(socket.gethostname(), "Hostname") in addresses:
        return False

    # host is not Windows
    if not os.name != "nt":
        return False

    # iproute2 is available
    if not shutil.which("ip"):
        return False

    # user has root permissions
    if not os.geteuid() == 0:  # type: ignore
        return False

    return True
