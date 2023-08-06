# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esdb',
 'esdb.client',
 'esdb.client.streams',
 'esdb.client.subscriptions',
 'esdb.client.subscriptions.aio',
 'esdb.generated']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.47.0,<2.0.0', 'protobuf<4.0']

setup_kwargs = {
    'name': 'esdb',
    'version': '0.1.7',
    'description': 'gRPC client for EventStore DB',
    'long_description': '# esdb-py\n\n[![PyPI version](https://badge.fury.io/py/esdb.svg)](https://pypi.org/project/esdb/)\n\nEventStoreDB Python gRPC client\n> NOTE: This project is still work in progress\n\n**Implemented parts**\n- [x] secure connection\n- [x] basic auth\n- [x] async client\n- [x] streams\n  - [x] append\n  - [x] batch append\n  - [x] delete\n  - [x] read\n  - [x] tombstone\n  - [x] filtering\n- [x] persistent subscriptions\n    - [x] create\n    - [x] read\n    - [ ] update\n    - [ ] delete\n    - [ ] list\n    - [ ] info\n    - [ ] reply parked events \n- [ ] CRUD for projections\n- [ ] users\n- [ ] other connection options\n  - [ ] multi-node gossip\n\n# Installation\nUsing pip:\n```sh\npip install esdb\n```\nUsing poetry:\n```sh\npoetry add esdb\n```\n\n# Development\n1. Install [poetry](https://python-poetry.org/docs/#installation)\n2. Create virtualenv (i.e. using pyenv):\n```sh\npyenv install 3.10.5\npyenv virtualenv 3.10.5 esdb-py\npyenv local esdb-py\n```\n3. Install deps with `poetry install`\n4. Start eventstore in docker: `make run-esdb`\n5. Run the tests: `pytest tests`\n\nUsage:\n\n```py\nimport datetime\nimport uuid\n\nfrom esdb.client import ESClient\n\n# For insecure connection without basic auth:\n# client = ESClient("localhost:2113", tls=False)\nwith open("certs/ca/ca.crt", "rb") as fh:\n  root_cert = fh.read()\n\nclient = ESClient(\n    "localhost:2111",\n    root_certificates=root_cert,\n    username="admin",\n    password="changeit",\n    keepalive_time_ms=5000,\n    keepalive_timeout_ms=10000,\n)\n\nstream = f"test-{str(uuid.uuid4())}"\n\nwith client.connect() as conn:\n    for i in range(10):\n        append_result = conn.streams.append(\n            stream=stream,\n            event_type="test_event",\n            data={"i": i, "ts": datetime.datetime.utcnow().isoformat()},\n        )\n\n    print("Forwards!")\n    for result in conn.streams.read(stream=stream, count=10):\n        print(result.data)\n\n    print("Backwards!")\n    for result in conn.streams.read(stream=stream, count=10, backwards=True):\n        print(result.data)\n\n    print("Forwards start from middle!")\n    for result in conn.streams.read(stream=stream, count=10, revision=5):\n        print(result.data)\n\n    print("Backwards start from middle!")\n    for result in conn.streams.read(stream=stream, count=10, backwards=True, revision=5):\n        print(result.data)\n```\n\nAsync example:\n\n```py\nimport asyncio\n\nfrom esdb.client import AsyncESClient\n\n\nasync def append():\n    client = AsyncESClient("localhost:2113", tls=False)\n    async with client.connect() as conn:\n        result = await conn.streams.append("stream", "type", {"x": 1})\n        assert result.commit_position > 0\n        async for event in conn.streams.read("stream", count=10):\n            print(event)\n\n\nasyncio.run(append())\n```\n\nSubscriptions:\n```py\nfrom esdb.client import ESClient\nfrom esdb.client.subscriptions import SubscriptionSettings, NackAction\n\nclient = ESClient("localhost:2113", tls=False)\nstream = "stream-name"\ngroup = "group-name"\n\nwith client.connect() as conn:\n    # emit some events to the same stream\n    for _ in range(10):\n        conn.streams.append(stream, "foobar", b"data")\n\n    # create a subscription\n    conn.subscriptions.create_stream_subscription(\n        stream=stream,\n        group_name=group,\n        settings=SubscriptionSettings(\n            read_batch_size=5,\n            live_buffer_size=10,\n            history_buffer_size=10,\n            checkpoint=SubscriptionSettings.DurationType(\n                type=SubscriptionSettings.DurationType.Type.MS,\n                value=10000,\n            ),\n        ),\n    )\n\n    # Read from subscription\n    # This will block and wait for messages\n    subscription = conn.subscriptions.subscribe_to_stream(stream, group, buffer_size=10)\n    for event in subscription:\n        try:\n            # ... do work with the event ...\n            # ack the event\n            subscription.ack([event])\n        except Exception as err:\n            subscription.nack([event], NackAction.RETRY, reason=str(err))\n          \n        \n```\n\nAsync subscriptions\n```python\nfrom esdb.client import AsyncESClient\nfrom esdb.client.subscriptions import SubscriptionSettings\n\nclient = AsyncESClient("localhost:2113", tls=False)\n\nstream = "stream-foo"\ngroup = "group-bar"\n\nasync with client.connect() as conn:\n    # emit some events to the same stream\n    for i in range(50):\n        await conn.streams.append(stream, "foobar", {"i": i})\n\n    # create a subscription\n    await conn.subscriptions.create_stream_subscription(\n        stream=stream,\n        group_name=group,\n        settings=SubscriptionSettings(\n            max_subscriber_count=50,\n            read_batch_size=5,\n            live_buffer_size=10,\n            history_buffer_size=10,\n            consumer_strategy=SubscriptionSettings.ConsumerStrategy.ROUND_ROBIN,\n            checkpoint=SubscriptionSettings.DurationType(\n                type=SubscriptionSettings.DurationType.Type.MS,\n                value=10000,\n            ),\n        ),\n    )\n\nasync with client.connect() as conn:\n    subscription = conn.subscriptions.subscribe_to_stream(stream=stream, group_name=group, buffer_size=5)\n    async for event in subscription:\n        await subscription.ack([event])\n```',
    'author': 'Andrii Kohut',
    'author_email': 'kogut.andriy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andriykohut/esdb-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
