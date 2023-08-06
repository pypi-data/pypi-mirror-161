# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_openapi_client', 'simple_openapi_client.openapi']

package_data = \
{'': ['*'], 'simple_openapi_client': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'httpx>=0.23.0,<0.24.0']

setup_kwargs = {
    'name': 'simple-openapi-client',
    'version': '0.1.0',
    'description': 'OpenAPI Python client generator that follows the KISS principle.',
    'long_description': None,
    'author': 'Gabriel Couture',
    'author_email': 'gacou54@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
