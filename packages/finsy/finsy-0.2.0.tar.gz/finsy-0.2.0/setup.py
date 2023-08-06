# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['finsy',
 'finsy.proto',
 'finsy.proto.gnmi1',
 'finsy.proto.google.rpc',
 'finsy.proto.google.rpc.context',
 'finsy.proto.p4',
 'finsy.proto.p4.config',
 'finsy.proto.p4.config.v1',
 'finsy.proto.p4.v1',
 'finsy.test']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.47.0,<2.0.0',
 'macaddress>=1.2.0,<2.0.0',
 'parsy>=1.4.0,<2.0.0',
 'protobuf>=4.21.3,<5.0.0',
 'pyee>=9.0.4,<10.0.0',
 'pylev>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'finsy',
    'version': '0.2.0',
    'description': 'Async P4Runtime/gNMI Framework',
    'long_description': '# 🐟 Finsy P4Runtime Framework\n\n[![ci](https://github.com/byllyfish/finsy/actions/workflows/ci.yml/badge.svg)](https://github.com/byllyfish/finsy/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/byllyfish/finsy/branch/main/graph/badge.svg?token=8RPYWRXNGS)](https://codecov.io/gh/byllyfish/finsy)\n\nFinsy is a P4Runtime controller framework written in Python using asyncio.\n\n```python\nimport asyncio\nimport finsy as fy\n\nasync def main():\n    async with fy.Switch("sw1", "127.0.0.1:50001") as sw1:\n        print(sw1.p4info)\n\nasyncio.run(main())\n```\n\n## Multiple Switches\n\nWith Finsy, you can write a P4Runtime controller that manages multiple switches.\n\nEach switch is managed by an async `ready_handler` function. Your `ready_handler` function can read or \nupdate various P4Runtime entities in the switch. It can also create tasks to listen for \npackets or digests.\n\n```python\nasync def ready_handler(sw: fy.Switch):\n    await sw.delete_all()\n    await sw.insert(fy.P4MulticastGroupEntry(1, replicas=[1, 2, 3, 255]))\n\n    async for packet in sw.packet_iterator():\n        print(packet)\n```\n\nUse the `SwitchOptions` class to specify each switch\'s settings, including the p4info/p4blob and ready_handler. Use the `Controller` class to drive multiple switch connections. Each switch will call back\ninto your ready_handler function after the P4Runtime connection is established.\n\n```python\nfrom pathlib import Path\n\noptions = fy.SwitchOptions(\n    p4info=Path("example.p4info.txt"),\n    p4blob=Path("example.json"),\n    ready_handler=ready_handler,\n)\ncontroller = fy.Controller([\n    fy.Switch("sw1", "127.0.0.1:50001", options),\n    fy.Switch("sw2", "127.0.0.1:50002", options),\n    fy.Switch("sw3", "127.0.0.1:50003", options),\n])\n\nasyncio.run(controller.run())\n```\n\nFor more examples, see the examples directory.\n',
    'author': 'Bill Fisher',
    'author_email': 'william.w.fisher@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/byllyfish/finsy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
