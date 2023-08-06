# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylitterbot', 'pylitterbot.robot']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.4.0,<3.0.0', 'aiohttp>=3.8.1,<4.0.0', 'deepdiff>=5.8.1,<6.0.0']

extras_require = \
{':python_version < "3.9"': ['backports.zoneinfo>=0.2.1,<0.3.0']}

setup_kwargs = {
    'name': 'pylitterbot',
    'version': '2022.8.0b1',
    'description': 'Python package for controlling Whisker automatic robots.',
    'long_description': '[![pypi](https://img.shields.io/pypi/v/pylitterbot?style=for-the-badge)](https://pypi.org/project/pylitterbot)\n[![downloads](https://img.shields.io/pypi/dm/pylitterbot?style=for-the-badge)](https://pypi.org/project/pylitterbot)\n[![Buy Me A Coffee/Beer](https://img.shields.io/badge/Buy_Me_A_☕/🍺-F16061?style=for-the-badge&logo=ko-fi&logoColor=white&labelColor=grey)](https://ko-fi.com/natekspencer)\n[![Purchase Litter-Robot](https://img.shields.io/badge/Buy_a_Litter--Robot-Save_$25-lightgrey?style=for-the-badge&labelColor=grey)](https://www.gopjn.com/t/SENKTktMR0lDSEtJTklPQ0hKS05HTQ)\n\n# pylitterbot\n\nPython package for controlling Whisker automatic robots.\n\nThis is an unofficial API for controlling various Whisker automated robots. It currently supports Litter-Robot 3, Litter-Robot 4 and Feeder-Robot.\n\n## Disclaimer\n\nThis API is experimental and was reverse-engineered by monitoring network traffic and decompiling source code from the Whisker app since no public API is currently available at this time. It may cease to work at any time. Use at your own risk.\n\n## Installation\n\nInstall using pip\n\n```bash\npip install pylitterbot\n```\n\nAlternatively, clone the repository and run\n\n```bash\npython setup.py install\n```\n\n## Usage\n\n```python\nimport asyncio\n\nfrom pylitterbot import Account\n\n# Set email and password for initial authentication.\nusername = "Your username"\npassword = "Your password"\n\n\nasync def main():\n    # Create an account.\n    account = Account()\n\n    try:\n        # Connect to the API and load robots.\n        await account.connect(username=username, password=password, load_robots=True)\n\n        # Print robots associated with account.\n        print("Robots:")\n        for robot in account.robots:\n            print(robot)\n    finally:\n        # Disconnect from the API.\n        await account.disconnect()\n\n\nif __name__ == "__main__":\n    asyncio.run(main())\n```\n\nwhich will output something like:\n\n```\nName: Litter-Robot Name, Serial: LR3C012345, id: a0123b4567cd8e\n```\n\nTo start a clean cycle\n\n```python\nawait robot.start_cleaning()\n```\n\nIf no exception occurred, your Litter-Robot should now perform a clean cycle.\n\nCurrently the following methods are available in the Robot class:\n\n- refresh()\n- start_cleaning()\n- reset_settings()\n- set_panel_lockout()\n- set_night_light()\n- set_power_status()\n- set_sleep_mode()\n- set_wait_time()\n- set_name()\n- reset_waste_drawer()\n- get_activity_history()\n- get_insight()\n\n---\n\n## TODO\n\n- Improve support for Litter-Robot 4\n- Improve support for Feeder-Robot\n\n---\n\n## Support Me\n\nI\'m not employed by Whisker and provide this python package as-is.\n\nIf you don\'t already own a Litter-Robot, please consider using [my affiliate link](https://www.gopjn.com/t/SENKTktMR0lDSEtJTklPQ0hKS05HTQ) to purchase your own robot and save $25!\n\nIf you already own a Litter-Robot and/or want to donate to me directly, consider buying me a coffee (or beer) instead by using the link below:\n\n<a href=\'https://ko-fi.com/natekspencer\' target=\'_blank\'><img height=\'35\' style=\'border:0px;height:46px;\' src=\'https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0\' border=\'0\' alt=\'Buy Me a Coffee at ko-fi.com\' />\n',
    'author': 'Nathan Spencer',
    'author_email': 'natekspencer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/natekspencer/pylitterbot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
