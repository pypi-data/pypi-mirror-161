"""Server TCP protocol implementation."""

# Copyright 2022 LW016 (GPG FINGERPRINT 33CA C1E8 EC4C 0B31 73AE  DD8B 31A5 35D1 2844 39ED)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from time import time
from logging import Logger
from typing import Callable, Dict, Set

from asyncio.events import AbstractEventLoop
from asyncio import Protocol, Transport

from uuid import uuid4


try:
    import ujson as json

except ImportError:
    import json # type: ignore


class TCPServerProtocol(Protocol):
    """Server protocol subclass."""

    def __init__(
            self,
            connections: Dict[str, list],
            connections_limit: int,
            blacklist: Set[str],
            callbacks: Dict[str, Callable],
            logger: Logger
            ) -> None:

        self._connections = connections
        self._connections_limit = connections_limit
        self._blacklist = blacklist

        self._callbacks = callbacks

        self._logger = logger

        self.event_loop: AbstractEventLoop


    def connection_made(self, transport: Transport) -> None: # type: ignore
        client: list = list(transport.get_extra_info("peername"))
        
        client[0] = str(client[0])
        client[1] = str(client[1])


        if client[0] in self._blacklist:
            transport.close()

        elif len(self._connections)+1 > self._connections_limit:
            transport.close()

            self._logger.info("Server | Connection rejected from %s:%s (max capacity)",
                    client[0], client[1])

        else:
            auth: str = uuid4().hex

            self._connections.update({
                client[0] + "-" + client[1]: [transport, time(), auth]})


            data = {
                    'call': 'peer',
                    'instance': None,
                    'host': client[0],
                    'port': client[1],
                    'auth': auth
                    }

            transport.write((json.dumps(data)+"&").encode())


            self._logger.info("Server | Connection from %s:%s",
                    client[0], client[1])


    def data_received(self, data: bytes) -> None:
        data_dec: str
        data_it: str
        data_fmt: dict

        call: str
        instance: str
        address: list
        address_f: tuple
        auth: str


        try:
            data_dec = data.decode()

            
            for data_it in data_dec.split("&"):
                if data_it.strip() == "":
                    continue


                data_fmt = json.loads(data_it)

                call = data_fmt.pop("call")
                instance = data_fmt.pop("instance")

                
                address = data_fmt.pop("address")

                if address[0] is None or address[1] is None:
                    return


                auth = data_fmt.pop("auth")
                auth_key = str(address[0]) + "-" + str(address[1])

                if auth_key in self._connections:
                    if auth != self._connections[auth_key][2]:
                        return

                else:
                    return


                address[1] = int(address[1])
                address_f = tuple(address)


                if call in self._callbacks:
                    self.event_loop.create_task(
                            self._callbacks[call](address_f, instance, data_fmt))

                elif "*" in self._callbacks:
                    self.event_loop.create_task(
                            self._callbacks["*"](address_f, instance, data_fmt))


                self._logger.debug("Server | Data received (%s)",
                        data_it)


        except (json.JSONDecodeError, KeyError, TypeError, UnicodeDecodeError) as error:
            self._logger.error("Server | Error in the data received (%s)",
                    error)
