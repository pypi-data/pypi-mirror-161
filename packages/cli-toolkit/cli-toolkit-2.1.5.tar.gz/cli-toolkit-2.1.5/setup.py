# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cli_toolkit', 'cli_toolkit.tests']

package_data = \
{'': ['*']}

install_requires = \
['pylint<2.14', 'sys-toolkit>=2.1,<3.0']

entry_points = \
{'pytest11': ['cli_toolkit_fixtures = cli_toolkit.fixtures']}

setup_kwargs = {
    'name': 'cli-toolkit',
    'version': '2.1.5',
    'description': 'Classes to implement CLI commands in python',
    'long_description': None,
    'author': 'Ilkka Tuohela',
    'author_email': 'hile@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
