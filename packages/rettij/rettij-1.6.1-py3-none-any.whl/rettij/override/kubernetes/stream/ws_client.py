# ORIGINAL (kubernetes.stream.ws_client)
# Copyright 2018 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# MODIFICATION (this module)
# Copyright 2021 Forschungsgruppe Rechnernetze und Informationssicherheit
# (FRI), Hochschule Bremen & other rettij authors
#
# Licensed under The MIT License (MIT)
#
# Changes made:
# - Updated the functionality of WSClient.update() to allow proper parsing of binary output

import select
from typing import List

import six
from websocket import ABNF

from kubernetes.stream.ws_client import STDOUT_CHANNEL, STDERR_CHANNEL
from kubernetes.stream.ws_client import WSClient as K8S_WSClient


class WSClient(K8S_WSClient):
    """
    Override of the original `kubernetes.stream.ws_client.WSClient` class containing a fix for binary output handling.

    Using this class, binary output can be handled by setting adding the `kubernetes.stream.ws_client.STDOUT_CHANNEL`
    to the `hexdump_channels` list before running the `update()` method. This way the received output for that channel
    will be converted into a hexadecimal string with the common `0x` prefix.
    """

    hexdump_channels: List[int] = []

    def update(self, timeout: int = 0) -> None:
        """Update channel buffers with at most one complete frame of input."""
        if not self.is_open():
            return
        if not self.sock.connected:
            self._connected = False
            return
        r, _, _ = select.select((self.sock.sock,), (), (), timeout)
        if r:
            op_code, frame = self.sock.recv_data_frame(True)
            if op_code == ABNF.OPCODE_CLOSE:
                self._connected = False
                return
            elif op_code == ABNF.OPCODE_BINARY or op_code == ABNF.OPCODE_TEXT:
                data = frame.data
                if six.PY3:
                    data = data.decode("utf-8", "replace")
                if len(data) > 1:
                    channel = ord(data[0])
                    data = data[1:]
                    if data:
                        if channel in self.hexdump_channels:
                            # retrieve raw data from stream as hex
                            data = "0x" + frame.data[1:].hex()
                        if channel in [STDOUT_CHANNEL, STDERR_CHANNEL]:
                            # keeping all messages in the order they received
                            # for non-blocking call.
                            self._all.write(data)
                        if channel not in self._channels:
                            self._channels[channel] = data
                        else:
                            self._channels[channel] += data
