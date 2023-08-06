# Simple OPENAPI Client generator

This project was made to generate a simple client from an openapi
specifications (unlike other client generators, which typically produce
code that is difficult for python beginners to use). It aims to produce a
single file that contains the Client class.

## Notes
This project is in alpha, probably has many bugs and may not work.
Issues/bugfixes/additions are welcome.

## Installation
```shell
$ pip install openapi-client
```

## Usage

This package is usage from a Python script.
Simply load the openapi file (from local file or url) and make the client.

For instance:

```py
from simple_openapi_client import parse_openapi, make_client, Config

config = Config(client_name='Orthanc')
document = parse_openapi(url_or_path='https://api.orthanc-server.com/orthanc-openapi.json')
client_str = make_client(document, config)

with open(f'./{config.package_name}.py', 'w') as file:
    file.write(client_str)
```
