import os
from pathlib import Path

import kubernetes

from rettij.common.validated_path import ValidatedFilePath
from rettij.exceptions.invalid_path_exception import InvalidPathException


def load_k8s_config() -> bool:
    """
    Load the Kubernetes API connection configuration.

    Used only for integration tests.
    Checks '~/.kube/config' and environment variables.
    :return: True if config was loaded correctly, False if not.
    """
    try:
        kubernetes.config.load_kube_config(ValidatedFilePath.join_paths(str(Path.home()), ".kube", "config"))
        return True
    except InvalidPathException:

        try:
            configuration = kubernetes.client.Configuration()

            configuration.api_key["authorization"] = os.environ["KUBE_TOKEN"]
            configuration.api_key_prefix["authorization"] = "Bearer"
            configuration.host = os.environ["KUBE_URL"]
            configuration.ssl_ca_cert = os.environ["KUBE_CA_PEM"]

            kubernetes.client.Configuration.set_default(configuration)
            return True

        except Exception:
            return False
