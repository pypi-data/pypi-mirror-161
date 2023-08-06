# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omoidasu']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'rich>=12.4.4,<13.0.0']

entry_points = \
{'console_scripts': ['omoidasu = omoidasu.cli:main']}

setup_kwargs = {
    'name': 'omoidasu',
    'version': '0.4.1',
    'description': 'Omoidasu.',
    'long_description': None,
    'author': '0djentd',
    'author_email': None,
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
