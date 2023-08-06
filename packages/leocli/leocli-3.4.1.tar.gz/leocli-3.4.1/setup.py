# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leocli']

package_data = \
{'': ['*']}

install_requires = \
['argcomplete>=1.11.1,<2.0.0',
 'argparse>=1.4.0,<2.0.0',
 'beautifulsoup4>=4.9.1,<5.0.0',
 'lxml>=4.5.1,<5.0.0',
 'requests>=2.23.0,<3.0.0',
 'tabulate>=0.8.7,<0.9.0',
 'termcolor>=1.1.0,<2.0.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['leo = leocli.leo:main']}

setup_kwargs = {
    'name': 'leocli',
    'version': '3.4.1',
    'description': 'A console translation script for https://dict.leo.org',
    'long_description': None,
    'author': 'sedrubal',
    'author_email': 'dev@sedrubal.de',
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
