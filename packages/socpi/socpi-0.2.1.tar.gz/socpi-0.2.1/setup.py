# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['socpi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'socpi',
    'version': '0.2.1',
    'description': 'A simple socket api framework',
    'long_description': "# socpi\n\nA simple async socket framework for python supporting *tcp* and *unix* sockets.\nAllows you to go beyond *json* by using *pickle*\n\n## How to use it\n\n```python\nfrom socpi import App, Client\n\n\n# create the app with the socket path for unix sockets\napp = App('/run/socpi')\n\n# or use [ip, port] tuple for tcp\n# app = App(('0.0.0.0', 4238))\n\n# Specify your endpoints\n@app.register\ndef echo(msg: str) -> str:\n    return msg.lower()\n\n# then launch your server, change `SERVER` to false to launch a client\nSERVER = True\nif SERVER:\n    asyncio.run(app.run())\n\n# or launch a client:\nasync def main():\n    # no openapi required, everything is generated from the `app`\n    client = Client(app)\n    print(await client.echo('fooo'))\n\nif not SERVER:\n    asyncio.run(main())\n```\n\nThere is a demo of a chat application in the `examples` directory.\n\n## What can it do:\n\n### Generators:\n\nYou can write and call generators and async generators:\n\n```python\n@app.register\ndef foo():\n    print('hello from the other side')\n    yield 'foo'\n```\n\nAnd call them like you would expect:\n\n```python\nasync for i in client.foo():\n    print(i)\n```\n\nEvery generator will be turned into an async one!\n\n### Exceptions:\n\nException handling is completely transparent, just `raise` and `except` them \nas usual.\n\n```python\n@app.register\ndef failer():\n    raise Exception('foo')\n```\n\nHandle them as usual, the objects will not be changed (but missing server and\nbroken connections will add some extra ones):\n\n```python\ntry:\n    await client.failer()\nexcept Exception as e:\n    print(e) # foo\n```\n\n### Serialization:\n\nAnything `pickle`able will work, as such `remote code execution` is not a bug,\nit is a feature. Deploying `socpi` to the wider internet is not recommended.\n\nA `json` only version might be a more secure, less capable option.\n\n",
    'author': 'Grzegorz Koperwas',
    'author_email': 'admin@grzegorzkoperwas.site',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/HakierGrzonzo/socpi',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
