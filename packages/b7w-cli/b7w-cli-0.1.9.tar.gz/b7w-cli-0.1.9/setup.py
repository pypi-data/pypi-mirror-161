# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['b7w_cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1,<9.0', 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['b7w = b7w_cli.cli:main']}

setup_kwargs = {
    'name': 'b7w-cli',
    'version': '0.1.9',
    'description': 'Useful cli for photos and other things',
    'long_description': 'b7w-cli\n=======\n\n![License](https://img.shields.io/github/license/b7w/b7w-cli)\n[![Build Status](https://drone.b7w.me/api/badges/b7w/b7w-cli/status.svg)](https://drone.b7w.me/b7w/b7w-cli)\n\nUseful cli for photos and other things\n\n\n## License\nOpen source, MIT license.\n\n\nLook, feel, be happy :-)\n',
    'author': 'B7W',
    'author_email': 'b7w@isudo.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/b7w/b7w-cli',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
