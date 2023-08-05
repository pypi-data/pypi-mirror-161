# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['asgikit', 'asgikit.errors', 'asgikit.multipart']

package_data = \
{'': ['*']}

modules = \
['py']
setup_kwargs = {
    'name': 'asgikit',
    'version': '0.2.2',
    'description': 'Toolkit for building ASGI applications and libraries',
    'long_description': '# Asgikit - ASGI Toolkit\n\nAsgikit is a toolkit for building asgi applications and frameworks.\n\nIt is intended to be a minimal library and provide the building blocks for other libraries.\n\nThe [examples directory](./examples) contain usage examples of several use cases\n\n## Features:\n\n- Request\n  - Headers\n  - Cookies\n  - Body (bytes, str, json, stream)\n  - Form\n    - url encoded\n- Response\n  - Plain text\n  - Json\n  - Streaming\n  - File\n- Websockets\n\n## Example request and response\n\n```python\nfrom asgikit.requests import HttpRequest\nfrom asgikit.responses import JsonResponse\n\nasync def main(scope, receive, send):\n    request = HttpRequest(scope, receive, send)\n\n    # request headers\n    headers = request.headers\n\n    body_stream = bytearray()\n    # read body as stream\n    async for chunk in request.stream():\n      body_stream += chunk\n  \n    # read body as bytes\n    body_bytes = await request.body()\n\n    # read body as text\n    body_text = await request.text()\n  \n    # read body as json\n    body_json = await request.json()\n\n    # read body as form\n    body_form = await request.form()\n\n    # send json response\n    data = {"lang": "Python", "async": True, "web_platform": "asgi"}\n    response = JsonResponse(data)\n    await response(request)\n```\n\n## Example websocket\n\n```python\nfrom asgikit.websockets import WebSocket\nfrom asgikit.errors.websocket import WebSocketDisconnectError\n\nasync def app(scope, receive, send):\n    websocket = WebSocket(scope, receive, send)\n    await websocket.accept()\n\n    while True:\n        try:\n            message = await websocket.receive()\n            await websocket.send_text(message)\n        except WebSocketDisconnectError:\n            print("Client disconnect")\n            break\n```\n',
    'author': 'Livio Ribeiro',
    'author_email': 'livioribeiro@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/livioribeiro/asgikit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
