# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sayd']

package_data = \
{'': ['*']}

install_requires = \
['pyOpenSSL>=22.0.0', 'typer>=0.4.1']

entry_points = \
{'console_scripts': ['sayd = sayd.__main__:execute']}

setup_kwargs = {
    'name': 'sayd',
    'version': '1.1.2',
    'description': 'A performant asynchronous communication protocol in pure Python.',
    'long_description': 'Sayd\n====\n*A performant asynchronous communication protocol in pure Python.*\n\nThis library was developed with simplicity, security and performance in mind, with modern practices of Python development, currently in a test state.\n\n`Documentation Reference <https://sayd.readthedocs.io>`_\n\n\nInstall\n-------\nWorks on Python 3.7.4+, is highly recommended to have installed `ujson <https://github.com/ultrajson/ultrajson>`_ and `uvloop <https://github.com/MagicStack/uvloop>`_ for a performance boost.\n\n.. code-block:: bash\n\n    pip install sayd\n\n\nOptional\n^^^^^^^^^^\n.. code-block:: bash\n\n    pip install ujson uvloop\n\n\nDevelopment\n-----------\nYou need to have installed `poetry <https://github.com/python-poetry/poetry>`_ for dependencies management.\n\n.. code-block:: bash\n\n    pip install poetry\n    git clone https://github.com/lw016/sayd\n    cd sayd\n    poetry install -E dev\n\n\nRun tests\n^^^^^^^^^^\n.. code-block:: bash\n\n    poetry run tox -e tests\n\nBuild docs\n^^^^^^^^^^\n.. code-block:: bash\n\n    poetry run tox -e docs\n\n\nFeatures\n--------\n- Client and server implementations\n- Reliable TCP persistent connection\n- Auto reconnection\n- Multiple asynchronous connections *(server)*\n- Blacklist of clients *(server)*\n- TLS encryption\n- Data transmitted as dictionaries *(json)*\n- Broadcast *(server)*\n- Remote function callbacks\n- Built-in CLI utility to generate self-signed certificates\n\n\nRoadmap\n-------\n- Add option to use Unix socket\n- Implement TLS certificate authentication\n- Add file transference support\n- Support to optionally return a result right after call a remote function\n\n\nCLI\n---\nThe built-in CLI utility (*sayd*) can be used to generate self-signed certificates to encrypt the connection.\n\n.. code-block:: bash\n\n    sayd --help\n\n\nUsage\n-----\nServer\n^^^^^^\n.. code-block:: python\n\n    import logging\n    import asyncio\n\n    from sayd import SaydServer\n\n\n    logging.basicConfig(\n            format="[%(name)s][%(levelname)s] %(asctime)s - %(message)s",\n            datefmt="%Y/%m/%d %H:%M:%S"\n            )\n\n    logger = logging.getLogger("SERVER")\n    logger.setLevel(logging.INFO)\n\n\n    server = SaydServer(logger=logger)\n\n\n    @server.callback("message")\n    async def msg(address: tuple, instance: str, data: dict) -> None:\n        print(data)\n\n\n    async def main() -> None:\n        await server.start()\n        \n        while True:\n            await server.call("message", {"content": "Hello from server!"})\n            await asyncio.sleep(1)\n        \n        await server.stop()\n\n\n    if __name__ == "__main__":\n        asyncio.run(main())\n\nClient\n^^^^^^\n.. code-block:: python\n\n    import logging\n    import asyncio\n\n    from sayd import SaydClient\n\n\n    logging.basicConfig(\n            format="[%(name)s][%(levelname)s] %(asctime)s - %(message)s",\n            datefmt="%Y/%m/%d %H:%M:%S"\n            )\n\n    logger = logging.getLogger("CLIENT")\n    logger.setLevel(logging.INFO)\n\n\n    client = SaydClient(logger=logger)\n\n\n    @client.callback("message")\n    async def msg(instance: str, data: dict) -> None:\n        print(data)\n\n\n    async def main() -> None:\n        await client.start()\n\n        while True:\n            await client.call("message", {"content": "Hello from client!"})\n            await asyncio.sleep(1)\n\n        await client.stop()\n\n\n    if __name__ == "__main__":\n        asyncio.run(main())\n',
    'author': 'LW016',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lw016/sayd',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.4,<4.0.0',
}


setup(**setup_kwargs)
