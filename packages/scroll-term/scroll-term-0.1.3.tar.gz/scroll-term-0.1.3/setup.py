# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scroll_term']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['scroll = scroll_term.cli:main']}

setup_kwargs = {
    'name': 'scroll-term',
    'version': '0.1.3',
    'description': 'scroll stdout!',
    'long_description': None,
    'author': 'redraw',
    'author_email': 'redraw@sdf.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/redraw/scroll',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
