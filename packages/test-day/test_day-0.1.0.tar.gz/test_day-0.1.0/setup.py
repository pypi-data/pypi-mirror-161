# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['test_day']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0', 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'test-day',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Stefan Hagemann',
    'author_email': 'StefanHagemann@gmx.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
