Sayd
====
*A performant asynchronous communication protocol in pure Python.*

This library was developed with simplicity, security and performance in mind, with modern practices of Python development, currently in a test state.

`Documentation Reference <https://sayd.readthedocs.io>`_


Install
-------
Works on Python 3.7.4+, is highly recommended to have installed `ujson <https://github.com/ultrajson/ultrajson>`_ and `uvloop <https://github.com/MagicStack/uvloop>`_ for a performance boost.

.. code-block:: bash

    pip install sayd


Optional
^^^^^^^^^^
.. code-block:: bash

    pip install ujson uvloop


Development
-----------
You need to have installed `poetry <https://github.com/python-poetry/poetry>`_ for dependencies management.

.. code-block:: bash

    pip install poetry
    git clone https://github.com/lw016/sayd
    cd sayd
    poetry install -E dev


Run tests
^^^^^^^^^^
.. code-block:: bash

    poetry run tox -e tests

Build docs
^^^^^^^^^^
.. code-block:: bash

    poetry run tox -e docs


Features
--------
- Client and server implementations
- Reliable TCP persistent connection
- Auto reconnection
- Multiple asynchronous connections *(server)*
- Blacklist of clients *(server)*
- TLS encryption
- Data transmitted as dictionaries *(json)*
- Broadcast *(server)*
- Remote function callbacks
- Built-in CLI utility to generate self-signed certificates


Roadmap
-------
- Add option to use Unix socket
- Implement TLS certificate authentication
- Add file transference support
- Support to optionally return a result right after call a remote function


CLI
---
The built-in CLI utility (*sayd*) can be used to generate self-signed certificates to encrypt the connection.

.. code-block:: bash

    sayd --help


Usage
-----
Server
^^^^^^
.. code-block:: python

    import logging
    import asyncio

    from sayd import SaydServer


    logging.basicConfig(
            format="[%(name)s][%(levelname)s] %(asctime)s - %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S"
            )

    logger = logging.getLogger("SERVER")
    logger.setLevel(logging.INFO)


    server = SaydServer(logger=logger)


    @server.callback("message")
    async def msg(address: tuple, instance: str, data: dict) -> None:
        print(data)


    async def main() -> None:
        await server.start()
        
        while True:
            await server.call("message", {"content": "Hello from server!"})
            await asyncio.sleep(1)
        
        await server.stop()


    if __name__ == "__main__":
        asyncio.run(main())

Client
^^^^^^
.. code-block:: python

    import logging
    import asyncio

    from sayd import SaydClient


    logging.basicConfig(
            format="[%(name)s][%(levelname)s] %(asctime)s - %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S"
            )

    logger = logging.getLogger("CLIENT")
    logger.setLevel(logging.INFO)


    client = SaydClient(logger=logger)


    @client.callback("message")
    async def msg(instance: str, data: dict) -> None:
        print(data)


    async def main() -> None:
        await client.start()

        while True:
            await client.call("message", {"content": "Hello from client!"})
            await asyncio.sleep(1)

        await client.stop()


    if __name__ == "__main__":
        asyncio.run(main())
