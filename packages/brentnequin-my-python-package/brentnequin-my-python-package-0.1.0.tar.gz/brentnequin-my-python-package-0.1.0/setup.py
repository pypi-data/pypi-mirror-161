# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brentnequin_my_python_package']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'brentnequin-my-python-package',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Brent Nequin',
    'author_email': 'brent.nequin@epsilon.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)
