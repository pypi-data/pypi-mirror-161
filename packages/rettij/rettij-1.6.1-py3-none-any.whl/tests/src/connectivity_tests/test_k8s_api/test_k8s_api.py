import unittest

import kubernetes
import kubernetes.client.rest

from tests.src.utils.load_k8s_config import load_k8s_config


@unittest.skipIf(not load_k8s_config(), "No Kubernetes configuration found, skipping test.")
class TestK8sApi(unittest.TestCase):
    """
    This TestCase is used to verify that the Kubernetes API is available before running integration tests.
    """

    v1: kubernetes.client.CoreV1Api

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the TestCase class variables.
        """
        cls.v1 = kubernetes.client.CoreV1Api()

    def test_k8s_api_successful_request(self) -> None:
        """
        Verify that a valid api request does succeed.
        """
        self.v1.get_api_resources()

    def test_k8s_api_unsuccessful_request(self) -> None:
        """
        Verify that an invalid request or a request for a nonexistent resource does not succeed.
        """
        with self.assertRaises(kubernetes.client.rest.ApiException):
            self.v1.read_namespace(name="This-namespace-does-not-exist")
