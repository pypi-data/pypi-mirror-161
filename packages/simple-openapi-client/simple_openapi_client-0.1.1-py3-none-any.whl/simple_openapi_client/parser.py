import json

import httpx

from .openapi.document import Document


def parse_openapi(url_or_path: str):
    if 'http' in url_or_path:
        response = httpx.get(url_or_path)
        content = response.json()
    else:
        with open(url_or_path) as file:
            content = json.load(file)

    # Cleaning unused data to generate the client
    content.pop('servers', None)
    content.pop('components', None)

    return Document(**content)
