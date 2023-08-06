# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['correct_hours']

package_data = \
{'': ['*']}

install_requires = \
['openpyxl>=3.0.10,<4.0.0']

setup_kwargs = {
    'name': 'correct-hours',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Jose Orozco',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
