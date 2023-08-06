"""Client implementation."""

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

import ssl

from time import time
from logging import Logger, getLogger
from typing import Callable, Optional, Union, Dict

from asyncio import get_event_loop, sleep
from asyncio.events import AbstractEventLoop
from asyncio.transports import Transport
from asyncio.tasks import Task

from ._client_tcp_protocol import TCPClientProtocol


try:
    import ujson as json

except ImportError:
    import json # type: ignore

try:
    from uvloop import install as tune

except ImportError:
    pass


class SaydClient:
    """Client class.
    
    :param host: Server hostname, defaults to localhost.
    :type host: str
    :param port: Server port, defaults to `7050`.
    :type port: int
    :param local_host: Local address to bind the client, defaults to `None`.
    :type local_host: str
    :param local_port: Local port to bind the client, defaults to `None`.
    :type local_port: Optional[Union[int, str]]
    :param timeout: Time in seconds to disconnect from the server if is not responding,\
            defaults to `4`.
    :type timeout: int
    :param ping: Frequency in seconds to ping the server, defaults to `2`.
    :type ping: int
    :param loop: Asynchronous event loop to use, defaults to `None`.
    :type loop: Optional[AbstractEventLoop]
    :param reconnect: If disconnected from the server try to reconnect, defaults to `True`.
    :type reconnect: bool
    :param reconnect_timeout: Frequency in seconds to try to reconnect if disconnected,\
            defaults to `4`.
    :type reconnect_timeout: int
    :param logger: Logger to use, defaults to `None`.
    :type logger: Optional[Logger]
    :param cert: Path to the TLS certificate, defaults to `None`.
    :type cert: Optional[str]
    """

    def __init__(
            self,
            host: str = "localhost",
            port: int = 7050,
            local_host: Optional[str] = None,
            local_port: Optional[Union[int, str]] = None,
            timeout: int = 4,
            ping: int = 2,
            loop: Optional[AbstractEventLoop] = None,
            reconnect: bool = True,
            reconnect_timeout: int = 5,
            logger: Optional[Logger] = None,
            cert: Optional[str] = None
            ) -> None:

        self._host = host
        self._port = port
        self._dlocal_host = local_host
        self._dlocal_port = local_port

        self._connection_timeout = timeout
        self._ping_timeout = ping

        self._event_loop = loop
        self._reconnect = reconnect
        self._reconnect_timeout = reconnect_timeout


        if logger is not None:
            self._logger = logger

        else:
            self._logger = getLogger()

        
        self._ssl_context: Union[ssl.SSLContext, bool, None]

        if cert is not None:
            self._ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cert)

        else:
            self._ssl_context = None

        
        self._local_host: Union[str, None] = None
        self._local_port: Optional[int] = 0
        self._auth: Union[str, None] = None

        self._reconnect_state: bool = False
        
        self._ping_task: Task

        self._connection: list = []

        self._callbacks: Dict[str, Callable] = {
                "ping": self._ping,
                "peer": self._peer
                }


        self._client: Transport
        
        self._protocol: TCPClientProtocol = TCPClientProtocol(
                self._connection,
                self._callbacks,
                self._logger)


        try:
            tune()

        except NameError:
            pass


    @property
    def connected(self) -> bool:
        """Return the connection status.

        :return: `True` if connected, else `False`.
        :rtype: bool
        """

        return not self._client.is_closing()

    
    def callback(self, name: str) -> Callable:
        """Decorator to bind functions to be called when a request is received.

        :param name: Name to bind the function.
        :type name: str
        """

        assert name != "ping", "Name 'ping' is used internally."
        assert name != "peer", "Name 'peer' is used internally."

        def decorator(function: Callable) -> Callable:
            self._callbacks.update({name: function})
            
            def wrapper(instance: Union[str, None], data: dict) -> Callable:
                return function(instance, data)

            return wrapper

        return decorator

    
    def add_callback(self, name: str, function: Callable) -> None:
        """Method to bind functions to be called when a request is received.

        :param name: Name to bind the function.
        :type name: str
        :param function: Function to bind.
        :type function: Callable
        """

        assert name != "ping", "Name 'ping' is used internally."
        assert name != "peer", "Name 'peer' is used internally."

        self._callbacks.update({name: function})


    async def call(
            self,
            name: str,
            data: Optional[dict] = None,
            instance: Optional[str] = None
            ) -> None:

        """Call a function in the server.

        :param name: Name of the function.
        :type name: str
        :param data: Data to send.
        :type data: dict
        :param instance: Instance to pass to remote function.
        :type instance: Optional[str]
        """
        
        if data is not None:
            assert "call" not in data, "Key 'call' is used internally."
            assert "instance" not in data, "Key 'instance' is used internally."
            assert "address" not in data, "Key 'address' is used internally."
            assert "auth" not in data, "Key 'auth' is used internally."


        address: list = [self._local_host, self._local_port]
        
        datap = data.copy() if data is not None else {}
        datap.update({
            "auth": self._auth,
            "address": address,
            "call": name,
            "instance": instance})
        
        dataf = json.dumps(datap).encode() + b"&"
        
        
        try:
            if not self._client.is_closing():
                self._client.write(dataf)

        except (RuntimeError, KeyError) as error:
            self._logger.error("Client | Call error (%s)", error)


    async def start(self) -> None:
        """Start the client."""

        if self._event_loop is None:
            self._event_loop = get_event_loop()

        self._protocol.event_loop = self._event_loop


        if self._ssl_context is not None:
            ssl_data = {
                    "ssl": self._ssl_context,
                    "ssl_handshake_timeout": self._connection_timeout*2
                    }

        else:
            ssl_data = {}


        self._local_host, self._local_port = None, 0
        self._auth = None

                
        if self._dlocal_host is None or self._dlocal_port is None:
            self._client, _ = await self._event_loop.create_connection( # type: ignore
                    lambda: self._protocol,
                    host=self._host,
                    port=self._port,
                    **ssl_data)

        else:
            self._client, _ = await self._event_loop.create_connection( # type: ignore
                    lambda: self._protocol,
                    host=self._host,
                    port=self._port,
                    local_addr=(self._dlocal_host, self._dlocal_port),
                    **ssl_data)


        while self._local_host is None or self._local_port == 0 or self._auth is None:
            if not self.connected:
                break

            await sleep(0.3)
        
        
        if not self._reconnect_state:
            self._ping_task = self._event_loop.create_task(self._ping_server())

            self._reconnect_state = True

        
    async def stop(self) -> None:
        """Stop the client."""

        self._ping_task.cancel()
        self._reconnect_state = False

        self._connection.clear()

        self._client.close()

    
    async def _ping_server(self) -> None:
        """Continuously check the connection status of the server."""

        timeout: int

        host: str = self._connection[0]
        port: int = self._connection[1]


        if self._connection_timeout <= 1:
            timeout = 2

        else:
            timeout = self._connection_timeout


        while 1:
            current_time = time()

            
            try:
                if (current_time - self._connection[3]) >= timeout:
                    if not self._connection[2].is_closing():
                        self._connection[2].close()


                    self._logger.info("Client | Disconnected from %s:%s",
                            host, port)
                    

                    self._connection.clear()

                    
                    while self._reconnect and len(self._connection) == 0:
                        self._logger.info("Client | Trying to reconnect to %s:%s",
                                host, port)
                        
                        try:
                            await self.start()

                        except ConnectionError:
                            await sleep(self._reconnect_timeout)

                        else:
                            break


                elif not self._connection[2].is_closing():
                    await self.call(name="ping")

            except IndexError as error:
                self._logger.error("Client | Ping send error (%s)",
                        error)


            await sleep(self._ping_timeout)
    
    
    async def _ping(self, instance: None, data: dict) -> None: # pylint: disable=unused-argument
        """Called when a ping is received from the server."""

        try:
            self._connection[3] = time()
            
        except IndexError as error:
            self._logger.error("Client | Ping receive error (%s)",
                    error)
   

    async def _peer(self, instance: None, data: dict) -> None: # pylint: disable=unused-argument
        """Called when the peer name is received from the server."""

        try:
            self._local_host, self._local_port = data["host"], data["port"]
            self._auth = data["auth"]
            
        except KeyError as error:
            self._logger.error("Client | Peer receive error (%s)",
                    error)
