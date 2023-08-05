# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dolistparser', 'dolistparser.parsers']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'dolistparser',
    'version': '0.2.0',
    'description': 'Parse to-dos from the comment',
    'long_description': None,
    'author': 'yunjae',
    'author_email': 'yunjae.oh.nl@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
