# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_simple_pagination']

package_data = \
{'': ['*']}

install_requires = \
['fastapi<1.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'fastapi-simple-pagination',
    'version': '1.1.1',
    'description': 'Simple and generic pagination dependencies for FastAPI.',
    'long_description': None,
    'author': 'Francisco Del Roio',
    'author_email': 'francipvb@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
