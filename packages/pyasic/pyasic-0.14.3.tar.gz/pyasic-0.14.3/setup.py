# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyasic',
 'pyasic.API',
 'pyasic.config',
 'pyasic.data',
 'pyasic.data.error_codes',
 'pyasic.logger',
 'pyasic.miners',
 'pyasic.miners._backends',
 'pyasic.miners._types',
 'pyasic.miners._types.antminer',
 'pyasic.miners._types.antminer.X17',
 'pyasic.miners._types.antminer.X19',
 'pyasic.miners._types.antminer.X9',
 'pyasic.miners._types.avalonminer',
 'pyasic.miners._types.avalonminer.A10X',
 'pyasic.miners._types.avalonminer.A7X',
 'pyasic.miners._types.avalonminer.A8X',
 'pyasic.miners._types.avalonminer.A9X',
 'pyasic.miners._types.whatsminer',
 'pyasic.miners._types.whatsminer.M2X',
 'pyasic.miners._types.whatsminer.M3X',
 'pyasic.miners.antminer',
 'pyasic.miners.antminer.bmminer',
 'pyasic.miners.antminer.bmminer.X17',
 'pyasic.miners.antminer.bmminer.X19',
 'pyasic.miners.antminer.bmminer.X9',
 'pyasic.miners.antminer.bosminer',
 'pyasic.miners.antminer.bosminer.X17',
 'pyasic.miners.antminer.bosminer.X19',
 'pyasic.miners.antminer.bosminer.X9',
 'pyasic.miners.antminer.cgminer',
 'pyasic.miners.antminer.cgminer.X17',
 'pyasic.miners.antminer.cgminer.X19',
 'pyasic.miners.antminer.cgminer.X9',
 'pyasic.miners.antminer.hiveon',
 'pyasic.miners.antminer.hiveon.X9',
 'pyasic.miners.avalonminer',
 'pyasic.miners.avalonminer.cgminer',
 'pyasic.miners.avalonminer.cgminer.A10X',
 'pyasic.miners.avalonminer.cgminer.A7X',
 'pyasic.miners.avalonminer.cgminer.A8X',
 'pyasic.miners.avalonminer.cgminer.A9X',
 'pyasic.miners.whatsminer',
 'pyasic.miners.whatsminer.btminer',
 'pyasic.miners.whatsminer.btminer.M2X',
 'pyasic.miners.whatsminer.btminer.M3X',
 'pyasic.network',
 'pyasic.settings',
 'pyasic.tests',
 'pyasic.tests.network_tests']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.11.0,<3.0.0',
 'httpx>=0.23.0,<0.24.0',
 'passlib>=1.7.4,<2.0.0',
 'pyaml>=21.10.1,<22.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'pyasic',
    'version': '0.14.3',
    'description': 'A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.',
    'long_description': '# pyasic\n*A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.*\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pypi](https://img.shields.io/pypi/v/pyasic.svg)](https://pypi.org/project/pyasic/)\n[![python](https://img.shields.io/pypi/pyversions/pyasic.svg)](https://pypi.org/project/pyasic/)\n[![Read the Docs](https://img.shields.io/readthedocs/pyasic)](https://pyasic.readthedocs.io/en/latest/)\n[![GitHub](https://img.shields.io/github/license/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/blob/master/LICENSE.txt)\n[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/UpstreamData/pyasic)](https://www.codefactor.io/repository/github/upstreamdata/pyasic)\n## Documentation\nDocumentation is located on Read the Docs as [pyasic](https://pyasic.readthedocs.io/en/latest/)\n\n## Usage\n\n### Standard Usage\nYou can install pyasic directly from pip with the command `pip install pyasic`\n\nFor those of you who aren\'t comfortable with code and developer tools, there are windows builds of GUI applications that use this library here -> (https://drive.google.com/drive/folders/1DjR8UOS_g0ehfiJcgmrV0FFoqFvE9akW?usp=sharing)\n\n### Developers\nTo use this repo, first download it, create a virtual environment, enter the virtual environment, and install relevant packages by navigating to this directory and running ```pip install -r requirements.txt``` on Windows or ```pip3 install -r requirements.txt``` on Mac or UNIX if the first command fails.\n\nYou can also use poetry by initializing and running ```poetry install```\n\n### Interfacing with miners programmatically\n\n##### Note: If you are trying to interface with Whatsminers, there is a bug in the way they are interacted with on Windows, so to fix that you need to change the event loop policy using this code: \n```python\n# need to import these 2 libraries, you need asyncio anyway so make sure you have sys imported\nimport sys\nimport asyncio\n\n# if the computer is windows, set the event loop policy to a WindowsSelector policy\nif sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith(\'win\'):\n    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())\n```\n\n##### It is likely a good idea to use this code in your program anyway to be preventative.\n<br>\n\nTo write your own custom programs with this repo, you have many options.\n\nIt is recommended that you explore the files in this repo to familiarize yourself with them, try starting with the miners module and going from there.\n\nThere are 2 main ways to get a miner and it\'s functions via scanning or via the MinerFactory.\n\n#### Scanning for miners\n```python\nimport asyncio\nimport sys\n\nfrom pyasic.network import MinerNetwork\n\n# Fix whatsminer bug\n# if the computer is windows, set the event loop policy to a WindowsSelector policy\nif sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith(\'win\'):\n    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())\n\n\n# define asynchronous function to scan for miners\nasync def scan_and_get_data():\n    # Define network range to be used for scanning\n    # This can take a list of IPs, a constructor string, or an IP and subnet mask\n    # The standard mask is /24, and you can pass any IP address in the subnet\n    net = MinerNetwork("192.168.1.69", mask=24)\n    # Scan the network for miners\n    # This function returns a list of miners of the correct type as a class\n    miners: list = await net.scan_network_for_miners()\n    \n    # We can now get data from any of these miners\n    # To do them all we have to create a list of tasks and gather them\n    tasks = [miner.get_data() for miner in miners]\n    # Gather all tasks asynchronously and run them\n    data = await asyncio.gather(*tasks)\n    \n    # Data is now a list of MinerData, and we can reference any part of that\n    # Print out all data for now\n    for item in data:\n        print(item)\n      \nif __name__ == "__main__":\n    asyncio.run(scan_and_get_data())\n```\n\n</br>\n\n#### Getting a miner if you know the IP\n```python\nimport asyncio\nimport sys\n\nfrom pyasic.miners.miner_factory import MinerFactory\n\n# Fix whatsminer bug\n# if the computer is windows, set the event loop policy to a WindowsSelector policy\nif sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith(\'win\'):\n    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())\n\n\n# define asynchronous function to get miner and data\nasync def get_miner_data(miner_ip: str):\n    # Use MinerFactory to get miner\n    # MinerFactory is a singleton, so we can just get the instance in place\n    miner = await MinerFactory().get_miner(miner_ip)\n    \n    # Get data from the miner\n    data = await miner.get_data()\n    print(data)\n\nif __name__ == "__main__":\n    asyncio.run(get_miner_data("192.168.1.69"))\n```\n\n### Advanced data gathering\n\nIf needed, this library exposes a wrapper for the miner API that can be used for advanced data gathering.\n\n#### List available API commands\n```python\nimport asyncio\nimport sys\n\nfrom pyasic.miners.miner_factory import MinerFactory\n\n# Fix whatsminer bug\n# if the computer is windows, set the event loop policy to a WindowsSelector policy\nif sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith(\'win\'):\n    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())\n\n\nasync def get_api_commands(miner_ip: str):\n    # Get the miner\n    miner = await MinerFactory().get_miner(miner_ip)\n    \n    # List all available commands\n    print(miner.api.get_commands())\n    \n    \nif __name__ == "__main__":\n    asyncio.run(get_api_commands("192.168.1.69"))\n```\n\n#### Use miner API commands to gather data\n\nThe miner API commands will raise an `APIError` if they fail with a bad status code, to bypass this you must send them manually by using `miner.api.send_command(command, ignore_errors=True)`\n\n```python\nimport asyncio\nimport sys\n\nfrom pyasic.miners.miner_factory import MinerFactory\n\n# Fix whatsminer bug\n# if the computer is windows, set the event loop policy to a WindowsSelector policy\nif sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith(\'win\'):\n    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())\n\n\nasync def get_api_commands(miner_ip: str):\n    # Get the miner\n    miner = await MinerFactory().get_miner(miner_ip)\n    \n    # Run the devdetails command\n    # This is equivalent to await miner.api.send_command("devdetails")\n    devdetails: dict = await miner.api.devdetails()\n    print(devdetails)\n    \n    \nif __name__ == "__main__":\n    asyncio.run(get_api_commands("192.168.1.69"))\n```\n',
    'author': 'UpstreamData',
    'author_email': 'brett@upstreamdata.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UpstreamData/pyasic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
