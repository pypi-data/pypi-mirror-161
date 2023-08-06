import os
import dataclasses
from typing import Dict, List

import jinja2

from simple_openapi_client.config import Config
from simple_openapi_client.openapi import Document
from simple_openapi_client.openapi.path import Operation, Parameter, Response

TYPES = {
    'boolean': 'bool',
    'number': 'float',
    'integer': 'int',
    'string': 'str',
    'array': 'List',
}


def make_client(document: Document, config: Config):
    path = os.path.join(os.path.dirname(__file__), 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=path)
    template_env = jinja2.Environment(loader=template_loader)

    elements = []

    # Main Client
    template_client = template_env.get_template('client.jinja')
    output = template_client.render(
        CLIENT=config.client_name,
        document=dataclasses.asdict(document)
    )
    elements.append(output)

    # Methods
    for route, path in document.paths.items():
        template_method = template_env.get_template('method.jinja')

        # Rename "id" to "id_" because "id" is a builtin function in Python.
        route = route.replace('id', 'id_')

        if path.operations is not None:
            for operation_name, operation in path.operations.items():
                output = template_method.render(
                    FUNCTION_NAME=_make_function_name(route, operation_name),
                    METHOD=operation_name,
                    ROUTE=route,
                    OPERATION=operation,
                    FUNCTION_PARAMETERS=_make_parameters(operation.parameters),
                    PATH_PARAMETERS=_make_path_parameters(operation.parameters),
                    QUERY_PARAMETERS=_make_query_parameters(operation.parameters),
                    HEADERS=_make_headers(operation.parameters),
                    TYPES=TYPES,
                    RESPONSES=_make_responses(operation.responses),
                    REQUEST_BODY=_make_request_body(operation),
                )
                elements.append(output)

    return '\n\n'.join(elements)


def _make_function_name(route: str, method: str) -> str:
    """Makes function name from the route (e.g. /api/potato) and from method (e.g. get, post)"""
    # "/" to "_"
    name = route.replace('/', '_')
    name = f'_{name}' if name[0] != '_' else name

    # "{*}" to "*"
    name = name.replace('{', '').replace('}', '')

    # "-" to "_" and "." to "_"
    name = name.replace('-', '_').replace('.', '_')

    # Removing double "__"
    name = name.replace('__', '_')

    # Removing end "_", if applicable
    name = name[:-1] if name[-1] == '_' else name

    return f'{method}{name}'.lower()


def _make_parameters(parameters: List[Parameter]) -> List:
    if parameters is None:
        return []

    params_in_route = [p for p in parameters if p.in_ == 'path']
    parameters_str = []

    if len(params_in_route) == 0:
        return parameters_str

    for param in params_in_route:
        # Rename "id" to "id_" because "id" is a builtin function in Python.
        param_name = param.name.replace('id', 'id_')
        param_type = TYPES[param.schema['type']]
        param_str = f'{param_name}: {param_type}'

        parameters_str.append(param_str)

    return parameters_str


def _make_headers(parameters: List[Parameter]) -> dict:
    if parameters is None:
        return {}

    return {p.name: {'description': p.description, 'type': TYPES[p.schema['type']]} for p in parameters if p.in_ == 'header'}


def _make_query_parameters(parameters: List[Parameter]) -> dict:
    if parameters is None:
        return {}

    return {p.name: {'description': p.description, 'type': TYPES[p.schema['type']]} for p in parameters if p.in_ == 'query'}


def _make_path_parameters(parameters: List[Parameter]) -> dict:
    if parameters is None:
        return {}

    params = {p.name: p.description for p in parameters if p.in_ == 'path'}

    if 'id' in params:
        params['id_'] = params.pop('id')

    return params


def _make_responses(responses: Dict[str, Response]) -> List:
    responses_str = []

    for status_code, response in responses.items():
        if response.content is None:
            continue

        for _, mediatype in response.content.items():
            if mediatype.schema is None:
                responses_str.append({'description': 'No description'})
            elif 'description' in mediatype.schema:
                responses_str.append({'description': mediatype.schema['description']})
            else:
                responses_str.append({'description': 'No description'})

    return responses_str


def _make_request_body(operation: Operation) -> dict:
    request_body_types = {'content': [], 'data': [], 'json': [], 'files': []}

    if operation.requestBody is not None:
        for content_type, schema in operation.requestBody.content.items():
            request_body_type = {
                'content_type': content_type,
                'description': schema['schema']['description'],
                'properties': {}
            }

            if 'properties' in schema['schema']:
                request_body_type['properties'] = schema['schema']['properties']

            if content_type == 'application/json':
                request_body_types['json'].append(request_body_type)
            elif content_type == 'text/plain':
                request_body_types['data'].append(request_body_type)
            elif 'multipart' in content_type:
                request_body_types['files'].append(request_body_type)
            else:
                request_body_types['content'].append(request_body_type)

    return request_body_types
