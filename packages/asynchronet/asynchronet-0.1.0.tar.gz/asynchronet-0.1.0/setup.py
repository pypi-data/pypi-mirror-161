# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asynchronet',
 'asynchronet.vendors',
 'asynchronet.vendors.alcatel',
 'asynchronet.vendors.arista',
 'asynchronet.vendors.aruba',
 'asynchronet.vendors.cisco',
 'asynchronet.vendors.fujitsu',
 'asynchronet.vendors.hp',
 'asynchronet.vendors.huawei',
 'asynchronet.vendors.infotecs',
 'asynchronet.vendors.juniper',
 'asynchronet.vendors.mikrotik',
 'asynchronet.vendors.terminal',
 'asynchronet.vendors.ubiquiti']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.11.0,<3.0.0']

extras_require = \
{':extra == "docs"': ['sphinx-rtd-theme>=1.0.0,<2.0.0', 'Sphinx>=5.1.1,<6.0.0']}

setup_kwargs = {
    'name': 'asynchronet',
    'version': '0.1.0',
    'description': 'Fork of netdev: Asynchronous multi-vendor library for interacting with network devices',
    'long_description': '# Asynchronet (Under Construction)\nInspired by [Netmiko](https://github.com/ktbyers/netmiko), Asynchronet is a multi-vendor library for asynchronously interacting with network devices through the CLI.\n\nAsynchronet is a fork of [Netdev](https://github.com/selfuryon/netdev), which is no longer maintained. This project was forked to continue to expand and enhance the existing capabilities while enabling community contribution.\n\nThe key features are:\n\n- **Asynchronous CLI Interactions**: Thanks to [asyncssh](https://github.com/ronf/asyncssh), which powers asynchronet provides support for multiple SSH connections within a single event loop.\n- **Multi-Vendor Support**: Currently twelve of the most popular networking hardware vendors are supported, with more to be added in the future.\n- **Autodetect Device Type**: By porting [Netmiko\'s](https://github.com/ktbyers/netmiko) battle-tested [SSHDetect](https://ktbyers.github.io/netmiko/docs/netmiko/ssh_autodetect.html) class to work asynchronously with _asyncssh_, asynchronet makes automatic device type detection a breeze.\n- **Simple**: Intuitive classes make it easy to interact with your favorite flavor of device.\n\n## Requirements\nPython 3.10+\n\n## Installation\n\n```console\npip install asynchronet\n```\n\n## Example\n\n```python\nimport asyncio\n\nimport asynchronet\n\nasync def task(param):\n    async with asynchronet.create(**param) as ios:\n        # Send a simple command\n        out = await ios.send_command("show ver")\n        print(out)\n        # Send a full configuration set\n        commands = ["line console 0", "exit"]\n        out = await ios.send_config_set(commands)\n        print(out)\n        # Send a command with a long output\n        out = await ios.send_command("show run")\n        print(out)\n        # Interactive dialog\n        out = await ios.send_command(\n            "conf", pattern=r"\\[terminal\\]\\?", strip_command=False\n        )\n        out += await ios.send_command("term", strip_command=False)\n        out += await ios.send_command("exit", strip_command=False, strip_prompt=False)\n        print(out)\n\n\nasync def run():\n    device_1 = {\n        "username": "user",\n        "password": "pass",\n        "device_type": "cisco_ios",\n        "host": "ip address",\n    }\n    device_2 = {\n        "username": "user",\n        "password": "pass",\n        "device_type": "cisco_ios",\n        "host": "ip address",\n    }\n    devices = [device_1, device_2]\n    tasks = [task(device) for device in devices]\n    await asyncio.wait(tasks)\n\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(run())\n\n```',
    'author': 'Sergey Yakovlev',
    'author_email': 'selfuryon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://netdev.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
