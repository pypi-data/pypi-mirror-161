# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nionctl', 'nionctl.lib']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['nionctl = nionctl.main:main_app']}

setup_kwargs = {
    'name': 'nionctl',
    'version': '0.2.4.1',
    'description': '',
    'long_description': '\n# `nionctl`\n\nAn abbreviation of common linux command-line utilities into one ctl\n\n\n## Installation\n\nInstall `nionctl` with pip:\n\n```bash\npip install nionctl\n```\nThe PyPi page is availible [here.](https://pypi.org/project/nionctl/)\n\n\n## Current commands (WIP):\n\n- Basic WiFi controlling (uses `nmcli`)\n- Basic Bluetooth controlling (uses `bluetoothctl`)\n- `git clone` from url to default directory\n- Basic archiving utilities (supports `.zip`, `.tar`, `.tar.gz`, `.tar.bz2`)\n- Simple image editing (converting, rotating, resizing, negating etc)\n\nFull docs are available [at COMMANDS.md](COMMANDS.md)\n\n\n## Contributing\n\nAny kinds of contributions are very welcome!\nCurrently the main goals are to bring more utilities and make the ctl cross-platform. Any tests on other linux distros are also welcome!\n\n',
    'author': '8Dion8',
    'author_email': 'shvartserinfo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
