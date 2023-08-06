"""Client TCP protocol implementation."""

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
from typing import Callable, Dict

from asyncio.events import AbstractEventLoop
from asyncio import Protocol, Transport


try:
    import ujson as json

except ImportError:
    import json # type: ignore


class TCPClientProtocol(Protocol):
    """Client protocol subclass."""

    def __init__(
            self,
            connection: list,
            callbacks: Dict[str, Callable],
            logger: Logger
            ) -> None:

        self._connection = connection

        self._callbacks = callbacks

        self._logger = logger

        self.event_loop: AbstractEventLoop


    def connection_made(self, transport: Transport) -> None: # type: ignore
        client: list = list(transport.get_extra_info("peername"))
        
        client[0] = str(client[0])
        client[1] = str(client[1])

        self._connection += [client[0], client[1], transport, round(time())]

        self._logger.info("Client | Connected to %s:%s",
                client[0], client[1])


    def data_received(self, data: bytes) -> None:
        data_dec: str
        data_it: str
        data_fmt: dict

        call: str
        instance: str


        try:
            data_dec = data.decode()

            
            for data_it in data_dec.split("&"):
                if data_it.strip() == "":
                    continue


                data_fmt = json.loads(data_it)
                
                call = data_fmt.pop("call")
                instance = data_fmt.pop("instance")


                if call in self._callbacks:
                    self.event_loop.create_task(
                            self._callbacks[call](instance, data_fmt))

                elif "*" in self._callbacks:
                    self.event_loop.create_task(
                            self._callbacks["*"](instance, data_fmt))


                self._logger.debug("Client | Data received (%s)",
                        data_it)


        except (json.JSONDecodeError, KeyError, TypeError, UnicodeDecodeError) as error:
            self._logger.error("Client | Error in the data received (%s)",
                    error)
