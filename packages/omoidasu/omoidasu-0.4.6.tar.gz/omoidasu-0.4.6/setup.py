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
    'version': '0.4.6',
    'description': 'Omoidasu.',
    'long_description': '# omoidasu\n### Description\nCLI flashcards tool.\n\n### Installation\n```\npip install omoidasu\n```\n\n### How to use\n```\nUsage: omoidasu [OPTIONS] COMMAND [ARGS]...\n\n  CLI for Omoidasu.\n\nOptions:\n  --data-dir TEXT                 Data directory.\n  --config-dir TEXT               Config directory.\n  --cache-dir TEXT                Cache directory.\n  --state-dir TEXT                State directory.\n  --log-dir TEXT                  Log directory.\n  --flashcards-dir TEXT           Flashcards directory.\n  --verbose / --no-verbose        Show additional information.\n  --interactive / --no-interactive\n                                  Use interactive features.\n  --debug / --no-debug            Show debug information.\n  --help                          Show this message and exit.\n\nCommands:\n  add     Add cards interactively using text editor.\n  list    Writes all cards to stdout.\n  new     Add card.\n  review  Review all cards.\n```\n\n```\nUsage: omoidasu list [OPTIONS] REGULAR_EXPRESSION\n\n  Writes all cards to stdout.\n\nOptions:\n  --max-cards INTEGER  Max number of cards to list.\n  --help               Show this message and exit.\n```\n\n```\nUsage: omoidasu review [OPTIONS] REGULAR_EXPRESSION\n\n  Review all cards.\n\nOptions:\n  --max-cards INTEGER  Max number of cards to review.\n  --help               Show this message and exit.\n```\n\n```\nUsage: omoidasu add [OPTIONS]\n\n  Add cards interactively using text editor. Save empty file to finish adding\n  cards.\n\nOptions:\n  --editor TEXT\n  --help         Show this message and exit.\n```\n\n```\nUsage: omoidasu new [OPTIONS] [SIDES]...\n\n  Add card.\n\nOptions:\n  --help  Show this message and exit.\n```\n\n',
    'author': '0djentd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/0djentd/omoidasu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
