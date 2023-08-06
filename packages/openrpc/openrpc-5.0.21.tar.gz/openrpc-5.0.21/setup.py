# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openrpc']

package_data = \
{'': ['*']}

install_requires = \
['case-switcher>=1.2.13,<2.0.0',
 'jsonrpc2-objects>=2.0.0,<3.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'openrpc',
    'version': '5.0.21',
    'description': 'OpenRPC provides classes to rapidly develop an OpenRPC server.',
    'long_description': '<div align=center>\n  <h1>OpenRPC</h1>\n  <h3>OpenRPC provides classes to rapidly develop an\n  <a href="https://open-rpc.org">OpenRPC</a> server.</h3>\n  <img src="https://img.shields.io/badge/License-MIT-blue.svg"\n   height="20"\n   alt="License: MIT">\n  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"\n   height="20"\n   alt="Code style: black">\n  <img src="https://img.shields.io/pypi/v/openrpc.svg"\n   height="20"\n   alt="PyPI version">\n  <img src="https://img.shields.io/badge/coverage-100%25-success"\n   height="20"\n   alt="Code Coverage">\n  <a href="https://www.codefactor.io/repository/github/matthew-burkard/openrpc">\n    <img src="https://www.codefactor.io/repository/github/matthew-burkard/openrpc/badge" \n     alt="CodeFactor" /></a>\n  <a href="https://gitlab.com/mburkard/openrpc/-/blob/main/CONTRIBUTING.md">\n    <img src="https://img.shields.io/static/v1.svg?label=Contributions&message=Welcome&color=2267a0"\n     height="20"\n     alt="Contributions Welcome">\n  </a>\n</div>\n\n## Installation\n\nOpenRPC is on PyPI and can be installed with:\n\n```shell\npip install openrpc\n```\n\n```shell\npoetry add openrpc\n```\n\n## Usage\n\nThis library provides an `RPCServer` class that can be used to quickly create an OpenRPC\nServer.\n\n```python\nfrom openrpc.server import RPCServer\n\nrpc = RPCServer(title="Demo Server", version="1.0.0")\n```\n\n### Register a function as an RPC Method\n\nTo register a method with the RPCServer add the `@rpc.method` decorator to a function.\n\n```python\n@rpc.method\ndef add(a: int, b: int) -> int:\n    return a + b\n```\n\n### Process JSON RPC Request\n\nOpenRPC is transport agnostic. To use it, pass JSON RPC requests as strings or byte\nstrings to the `process_request` or `process_request_async` method.\n\nThe `process_request` will return a JSON RPC response as a string.\n\n```python\nreq = """\n{\n  "id": 1,\n  "method": "add",\n  "params": {"a": 2, "b": 2},\n  "jsonrpc": "2.0"\n}\n"""\nawait rpc.process_request_async(req)\n# returns -> \'{"id": 1, "result": 4, "jsonrpc": "2.0"}\'\n```\n\n### Pydantic Support\n\nFor data classes to work properly use Pydantic. RPCServer will use Pydantic for JSON\nserialization/deserialization when calling methods and when generating schemas\nwith `rpc.discover`.\n\n### RPC Discover\n\nThe `rpc.discover` method is automatically generated. It relies heavily on type hints.\n\n## Example Using Sanic\n\nA quick example using `OpenRPC` exposing the methods\nusing [Sanic](https://sanic.dev/en/).\n\n```python\nfrom sanic import HTTPResponse, Request, Sanic, text\n\nfrom openrpc.server import RPCServer\n\napp = Sanic("DemoServer")\nrpc = RPCServer(title="DemoServer", version="1.0.0")\n\n\n@rpc.method\ndef add(a: int, b: int) -> int:\n    return a + b\n\n\n@app.post("/api/v1/")\ndef process_rpc(request: Request) -> HTTPResponse:\n    return text(rpc.process_request(request.body))\n\n\nif __name__ == "__main__":\n    app.run()\n```\n\nExample In\n\n```json\n[\n  {\n    "id": 1,\n    "method": "add",\n    "params": {\n      "a": 1,\n      "b": 3\n    },\n    "jsonrpc": "2.0"\n  },\n  {\n    "id": 2,\n    "method": "add",\n    "params": [\n      11,\n      "thirteen"\n    ],\n    "jsonrpc": "2.0"\n  }\n]\n```\n\nExample Result Out\n\n```json\n[\n  {\n    "id": 1,\n    "result": 4,\n    "jsonrpc": "2.0"\n  },\n  {\n    "id": 2,\n    "error": {\n      "code": -32603,\n      "message": "Internal error",\n      "data": "Failed to deserialize request param [thirteen] to type [<class \'int\'>]"\n    },\n    "jsonrpc": "2.0"\n  }\n]\n```\n',
    'author': 'Matthew Burkard',
    'author_email': 'matthewjburkard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mburkard/openrpc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
