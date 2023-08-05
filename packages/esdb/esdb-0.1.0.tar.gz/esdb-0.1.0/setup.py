# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esdb',
 'esdb.client',
 'esdb.client.streams',
 'esdb.client.subscriptions',
 'esdb.generated']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'esdb',
    'version': '0.1.0',
    'description': 'gRPC client for EventStore DB',
    'long_description': '# esdb-py\n\nEventStoreDB Python gRPC client\n> NOTE: This project is still work in progress\n\n**Implemented parts**\n- [x] secure connection\n- [x] basic auth\n- [ ] other connection options\n  - [ ] multi-node gossip\n  - [ ] keepalive\n- [x] async client\n- [ ] streams\n  - [x] append\n  - [x] batch append\n  - [x] delete\n  - [x] read\n  - [x] tombstone\n  - [ ] filtering\n  - [ ] exception handling\n- [ ] subscriptions\n- [ ] users\n- [ ] tbd\n\n\n# Setting things up\n1. Install [poetry](https://python-poetry.org/docs/#installation)\n2. Create virtualenv (i.e. using pyenv):\n```sh\npyenv install 3.10.5\npyenv virtualenv 3.10.5 esdb-py\npyenv local esdb-py\n```\n3. Install deps with `poetry install`\n4. Start eventstore in docker: `make run-esdb`\n5. Run the tests: `pytest tests`\n\nUsage:\n\n```py\nimport datetime\nimport uuid\n\nfrom esdb.client.client import ESClient\n\n# For insecure connection without basic auth:\n# client = ESClient("localhost:2113", tls=False)\nwith open("certs/ca/ca.crt", "rb") as fh:\n  root_cert = fh.read()\n\nclient = ESClient("localhost:2111", root_certificates=root_cert, username="admin", password="changeit")\n\nstream = f"test-{str(uuid.uuid4())}"\n\nfor i in range(10):\n  append_result = client.streams.append(\n    stream=stream,\n    event_type="test_event",\n    data={"i": i, "ts": datetime.datetime.utcnow().isoformat()},\n  )\n\nprint("Forwards!")\nfor result in client.streams.read(stream=stream, count=10):\n  print(result.data)\n\nprint("Backwards!")\nfor result in client.streams.read(stream=stream, count=10, backwards=True):\n  print(result.data)\n\nprint("Forwards start from middle!")\nfor result in client.streams.read(stream=stream, count=10, revision=5):\n  print(result.data)\n\nprint("Backwards start from middle!")\nfor result in client.streams.read(stream=stream, count=10, backwards=True, revision=5):\n  print(result.data)\n```\n\nAsync example:\n\n```py\nimport asyncio\n\nfrom esdb.client.client import AsyncESClient\n\n\nasync def append():\n  client = AsyncESClient("localhost:2113")\n  result = await client.streams.append("stream", "type", {"x": 1})\n  assert result.commit_position > 0\n  async for event in client.streams.read("stream", count=10):\n    print(event)\n\n\nasyncio.run(append())\n```\n\nSubscriptions:\n```py\nfrom esdb.client.client import ESClient\n\nclient = ESClient("localhost:2113", tls=False)\nstream = "stream-name"\ngroup = "group-name"\n\n# emit some events to the same stream\nfor _ in range(10):\n    client.streams.append(stream, "foobar", b"data")\n\n# create a subscription\nclient.subscriptions.create_stream_subscription(stream=stream, group_name=group)\n\n# Read from subscription\n# This will block and wait for messages\nsubscription = client.subscriptions.subscribe_to_stream(stream, group)\nfor event in subscription:\n    # ... do work with the event ...\n    # ack the event\n    subscription.ack([event])\n```',
    'author': 'Andrii Kohut',
    'author_email': 'kogut.andriy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andriykohut/esdb-py',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
