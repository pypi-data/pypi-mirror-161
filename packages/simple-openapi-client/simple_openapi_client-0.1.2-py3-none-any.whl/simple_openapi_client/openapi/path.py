from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ExternalDocumentation:
    url: str
    description: str = None


@dataclass
class Parameter:
    name: str
    in_: str

    description: str = None
    required: bool = None
    schema: Dict = None

    def __post_init__(self):
        if self.in_ not in ('query', 'header', 'path', 'cookie'):
            raise ValueError(
                f'Invalid "in" value {self.in_} of Parameter({self.name}). '
                f'Should be "query", "header", "path" or "cookie".'
            )


@dataclass
class Header:
    description: str = None
    schema: Dict[str, str] = None


@dataclass
class Example:
    summary: str = None
    description: str = None
    value: Any = None
    externalValue: str = None


@dataclass
class Encoding:
    contentType: str = None
    headers: Dict[str, Header] = None
    style: str = None
    explode: bool = None
    allowReserved: bool = None

    def __post_init__(self):
        if self.headers is not None:
            self.headers = {k: Header(**v) for k, v in self.headers.items()}


@dataclass
class MediaType:
    schema: Dict[str, str] = None
    example: Any = None
    examples: Dict[str, Example] = None
    encoding: Dict[str, Encoding] = None

    def __post_init__(self):
        if self.examples is not None:
            self.examples = {k: Example(**v) for k, v in self.examples.items()}
        if self.encoding is not None:
            self.encoding = {k: Encoding(**v) for k, v in self.encoding.items()}


@dataclass
class Response:
    description: str

    headers: Dict[str, Header] = None
    content: Dict[str, MediaType] = None
    links: Dict = None

    def __post_init__(self):
        if self.headers is not None:
            self.headers = {k: Header(**v) for k, v in self.headers.items()}
        if self.content is not None:
            self.content = {k: MediaType(**v) for k, v in self.content.items()}


@dataclass
class RequestBody:
    content: Dict

    description: str = None
    require: bool = None


@dataclass
class Operation:
    responses: Dict[str, Response]

    tags: List[str] = None
    summary: str = None
    description: str = None
    externalDocs: Any = None
    operationId: str = None

    parameters: List[Parameter] = None
    requestBody: RequestBody = None
    deprecated: bool = None
    security: Dict = None

    def __post_init__(self):
        if self.parameters is not None:
            for param in self.parameters:
                # renaming param name that are also built-in function
                if 'in' in param:
                    param['in_'] = param.pop('in')

            self.parameters = [Parameter(**p) for p in self.parameters]

        if self.requestBody is not None:
            self.requestBody = RequestBody(**self.requestBody)

        self.responses = {k: Response(**v) for k, v in self.responses.items()}


@dataclass
class Path:
    summary: str = None
    description: str = None

    operations: Dict = None

    def __init__(self, **kwargs):
        # self.summary = summary
        # self.description = description

        self.operations = {}

        for operation_name, operation_data in kwargs.items():
            # Cleaning unused data to generate the client
            operation_data.pop('servers', None)
            operation_data.pop('callbacks', None)

            self.operations[operation_name] = Operation(**operation_data)
