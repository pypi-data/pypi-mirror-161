# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mayapy_launcher']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['mayapy = mayapy_launcher:main']}

setup_kwargs = {
    'name': 'mayapy-launcher',
    'version': '0.1.0',
    'description': 'Easily launch any version of mayapy',
    'long_description': None,
    'author': 'Loïc Pinsard',
    'author_email': 'muream@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
