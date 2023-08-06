# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tanmatsu', 'tanmatsu.widgets']

package_data = \
{'': ['*']}

install_requires = \
['parsy>=1.3.0,<2.0.0', 'tri.declarative>=5.0,<6.0', 'wcwidth>=0.2,<0.3']

setup_kwargs = {
    'name': 'tanmatsu',
    'version': '0.0.1',
    'description': 'Declarative Terminal User Interface Library',
    'long_description': None,
    'author': 'snowdrop4',
    'author_email': '82846066+snowdrop4@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<3.12',
}


setup(**setup_kwargs)
