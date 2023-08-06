"""
This module overrides the `kubernetes.stream.ws_client.WSClient` class to fix binary output handling.

Once a new version of the client without this issue is released, this module will be obsolete.
Respective issues:
- https://gitlab.com/frihsb/rettij/-/issues/83
- https://github.com/kubernetes-client/python/issues/1471
"""
from .ws_client import WSClient, K8S_WSClient

# Since we retrieve WSClient objects from various methods from the `kubernetes` module, we need to replace the
# parts of the original WSClient as early as possible. Since this is run upon module import, the replacement
# takes place before the first `kubernetes` method is called.
K8S_WSClient.hexdump_channels = WSClient.hexdump_channels
K8S_WSClient.update = WSClient.update
