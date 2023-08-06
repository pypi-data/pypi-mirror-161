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
    'version': '0.1.1',
    'description': 'OpenAPI Python client generator that follows the KISS principle.',
    'long_description': "# Simple OPENAPI Client generator\n\nThis project was made to generate a simple client from an openapi\nspecifications (unlike other client generators, which typically produce\ncode that is difficult for python beginners to use). It aims to produce a\nsingle file that contains the Client class.\n\n## Notes\nThis project is in alpha, probably has many bugs and may not work.\nIssues/bugfixes/additions are welcome.\n\n## Installation\n```shell\n$ pip install openapi-client\n```\n\n## Usage\n\nThis package is usage from a Python script.\nSimply load the openapi file (from local file or url) and make the client.\n\nFor instance:\n\n```py\nfrom simple_openapi_client import parse_openapi, make_client, Config\n\nconfig = Config(client_name='Orthanc')\ndocument = parse_openapi(url_or_path='https://api.orthanc-server.com/orthanc-openapi.json')\nclient_str = make_client(document, config)\n\nwith open(f'./{config.package_name}.py', 'w') as file:\n    file.write(client_str)\n```\n",
    'author': 'Gabriel Couture',
    'author_email': 'gacou54@ulaval.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
