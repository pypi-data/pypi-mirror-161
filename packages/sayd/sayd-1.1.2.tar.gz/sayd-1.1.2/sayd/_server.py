"""Server implementation."""

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
from typing import Callable, Optional, Union, Dict, List, Set

from asyncio import get_event_loop, sleep
from asyncio.events import AbstractEventLoop, AbstractServer
from asyncio.tasks import Task

from ._server_tcp_protocol import TCPServerProtocol


try:
    import ujson as json

except ImportError:
    import json # type: ignore

try:
    from uvloop import install as tune

except ImportError:
    pass


class SaydServer:
    """Server class.

    :param host: A list of addresses or a address to bind the server, defaults to `None`.
    :type host: Optional[Union[str, list]]
    :param port: Port to use, defaults to `7050`.
    :type port: int
    :param queue: Limit of clients waiting to connect, defaults to `1024`.
    :type queue: int
    :param limit: Limit of connected clients, defaults to `4096`.
    :type limit: int
    :param timeout: Time in seconds to disconnect a client that is not responding,\
            defaults to `4`.
    :type timeout: int
    :param ping: Frequency in seconds to ping the clients, defaults to `2`.
    :type ping: int
    :param loop: Asynchronous event loop to use, defaults to `None`.
    :type loop: Optional[AbstractEventLoop]
    :param logger: Logger to use, defaults to `None`.
    :type logger: Optional[Logger]
    :param cert: Path to the TLS certificate, defaults to `None`.
    :type cert: Optional[str]
    :param cert_key: Path to the TLS certificate key, defaults to `None`.
    :type cert_key: Optional[str]
    """

    def __init__(
            self,
            host: Optional[Union[str, list]] = None,
            port: int = 7050,
            queue: int = 1024,
            limit: int = 4096,
            timeout: int = 4,
            ping: int = 2,
            loop: Optional[AbstractEventLoop] = None,
            logger: Optional[Logger] = None,
            cert: Optional[str] = None,
            cert_key: Optional[str] = None
            ) -> None:

        self._host = host
        self._port = port

        self._queue_limit = queue
        self._connections_limit = limit
        self._connection_timeout = timeout
        self._ping_timeout = ping

        self._event_loop = loop


        if logger is not None:
            self._logger = logger

        else:
            self._logger = getLogger()


        self._ssl_context: Union[ssl.SSLContext, bool, None]

        if cert is not None and cert_key is not None:
            self._ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self._ssl_context.load_cert_chain(cert, cert_key)

        else:
            self._ssl_context = None
        

        self._ping_task: Task
        
        self._connections: Dict[str, list] = {}
        self._blacklist: Set[str] = set()

        self._callbacks: Dict[str, Callable] = {
                "ping": self._ping
                }


        self._server: AbstractServer
        
        self._protocol: TCPServerProtocol = TCPServerProtocol(
                self._connections,
                self._connections_limit,
                self._blacklist,
                self._callbacks,
                self._logger
                )


        try:
            tune()

        except NameError:
            pass


    @property
    def clients(self) -> Set[tuple]:
        """Return the connected clients.

        :return: A set containing the connections.
        :rtype: Set[tuple]
        """

        clients_con = self._connections.keys()
        con: set = set()
        

        if len(clients_con) == 0:
            return con

        
        for _ in clients_con:
            con.add((_.split("-")[0],
                int(_.split("-")[1])
                ))

        
        return con

    
    def callback(self, name: str) -> Callable:
        """Decorator to bind functions to be called when a request is received.

        :param name: Name to bind the function.
        :type name: str
        """

        assert name != "ping", "Name 'ping' is used internally."

        def decorator(function: Callable) -> Callable:
            self._callbacks.update({name: function})
            
            def wrapper(address: tuple, instance: Union[str, None], data: dict) -> Callable: # pylint: disable=unused-argument
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

        self._callbacks.update({name: function})


    def blacklist(self, host: str) -> None:
        """Method to add a host to the blacklist.

        :param host: Host to block.
        :type host: str
        """

        self._blacklist.add(host)
        
        for connection in list(self._connections.keys()):
            if connection.split("-")[0] == host:
                if not self._connections[connection][0].is_closing():
                    self._connections[connection][0].close()

        self._logger.info("Server | Host %s added to the blacklist", host)


    def unblacklist(self, host: str) -> None:
        """Method to remove a host from the blacklist.

        :param host: Host to unblock.
        :type host: str
        """
        
        if host in self._blacklist:
            self._blacklist.remove(host)

        self._logger.info("Server | Host %s removed from the blacklist", host)


    async def call(
            self,
            name: str,
            data: Optional[dict] = None,
            instance: Optional[str] = None,
            address: Optional[tuple] = None
            ) -> None:
        """Call a function in a remote client or in all clients (broadcast) if address
        is not specified.

        :param name: Name of the function.
        :type name: str
        :param data: Data to send.
        :type data: dict
        :param instance: Instance to pass to remote function.
        :type instance: Optional[str]
        :param address: Client address.
        :type address: Optional[tuple]
        """
        
        if data is not None:
            assert "call" not in data, "Key 'call' is used internally."
            assert "instance" not in data, "Key 'instance' is used internally."

        
        datap = data.copy() if data is not None else {}
        datap.update({
            "call": name,
            "instance": instance
            })

        
        dataf = json.dumps(datap).encode() + b"&"

        
        try:
            if address is not None:
                address_f: str = address[0] + "-" + str(address[1])

                if not self._connections[address_f][0].is_closing():
                    self._connections[address_f][0].write(dataf)
                
            else:
                for connection in list(self._connections.keys()):
                    if not self._connections[connection][0].is_closing():
                        self._connections[connection][0].write(dataf)

        except (RuntimeError, KeyError) as error:
            self._logger.error("Server | Call error (%s)", error)

    
    async def start(self) -> None:
        """Start the server."""

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
        
        
        self._server = await self._event_loop.create_server( # type: ignore
                lambda: self._protocol,
                host=self._host,
                port=self._port,
                backlog=self._queue_limit,
                start_serving=True,
                **ssl_data)


        self._ping_task = self._event_loop.create_task(self._ping_clients())


    async def stop(self) -> None:
        """Stop the server."""

        self._ping_task.cancel()


        for connection in list(self._connections.keys()):
            if not self._connections[connection][0].is_closing():
                self._connections[connection][0].close()

                del self._connections[connection]
                

        self._server.close()

    
    async def _ping_clients(self) -> None:
        """Continuously check the connection status of the clients."""

        timeout: int

        con_keys: List[str] = []


        if self._connection_timeout <= 1:
            timeout = 2

        else:
            timeout = self._connection_timeout


        while 1:
            current_time = time()


            for connection in list(self._connections.keys()):
                try:
                    if (current_time - self._connections[connection][1]) >= timeout:
                        if not self._connections[connection][0].is_closing():
                            self._connections[connection][0].close()

                        con_keys.append(connection)
                        
                        instf = connection.split("-")

                        self._logger.info("Server | Disconnection from %s:%s",
                                instf[0], instf[1])

                    elif not self._connections[connection][0].is_closing():
                        await self.call(
                                name="ping",
                                address=tuple(connection.split("-"))
                                )

                except KeyError as error:
                    self._logger.error("Server | Ping send error (%s)",
                            error)


            for _ in con_keys:
                try:
                    del self._connections[_]

                except KeyError:
                    pass

            con_keys.clear()


            await sleep(self._ping_timeout)

    
    async def _ping(self, address: tuple, instance: None, data: dict) -> None: # pylint: disable=unused-argument
        """Called when a ping is received from a client."""

        try:
            address_f: str = address[0] + "-" + str(address[1])

            self._connections[address_f][1] = time()

        except KeyError as error:
            self._logger.error("Server | Ping receive error (%s)",
                    error)
