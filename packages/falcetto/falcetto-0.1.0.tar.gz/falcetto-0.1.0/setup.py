# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['falcetto']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'falcetto',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'stefaondisponibile',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
