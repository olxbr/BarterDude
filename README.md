# BarterDude
[![Build Status](https://travis-ci.com/olxbr/BarterDude.svg?branch=master)](https://travis-ci.com/olxbr/BarterDude)
[![Coverage Status](https://coveralls.io/repos/github/olxbr/BarterDude/badge.svg?branch=master)](https://coveralls.io/github/olxbr/BarterDude?branch=master)

Message exchange engine to build pipelines using brokers like RabbitMQ. This project is build on top of the great [async-worker](https://github.com/b2wdigital/async-worker).

![barter](https://github.com/olxbr/BarterDude/blob/master/barterdude.jpg)

## Install

Using Python 3.6+

```sh
pip install barterdude
```

## Usage

Build your consumer with this complete example:

```python
import logging
from barterdude import BarterDude
from barterdude.monitor import Monitor
from barterdude.hooks.healthcheck import Healthcheck
from barterdude.hooks.logging import Logging
from barterdude.hooks.metrics.prometheus import Prometheus
from barterdude.message import Message
from barterdude.conf import getLogger

# from my_project import MyHook # (you can build your own hooks)


# configure RabbitMQ
barterdude = BarterDude(
    hostname="localhost",
    username="guest",
    password="guest",
    prefetch=256,
)

# Prometheus labels for automatic metrics
labels = dict(
    app_name="my_app",
    team_name="my_team"
)
healthcheck = Healthcheck(barterdude) # automatic and customizable healthcheck
prometheus = Prometheus(labels) # automatic and customizable Prometheus integration

self.logger = getLogger("my_app", logging.DEBUG) # automatic json log with barterdude namespace
# BARTERDUDE_DEFAULT_APP_NAME is an env var to control your project namespace
# BARTERDUDE_DEFAULT_LOG_LEVEL is an env var to control loglevel by number 0, 10, 20, etc...

monitor = Monitor(
    healthcheck,
    prometheus,
    # MyHook(barterdude, "/path"), # (will make localhost:8080/path url)
    Logging() # automatic and customizable logging
)

my_metric = prometheus.metrics.counter(name="fail", description="fail again")  # It's the same as https://github.com/prometheus/client_python


@barterdude.consume_amqp(
    ["queue1", "queue2"],
    monitor,
    coroutines = 10,  # number of coroutines spawned to consume messages (1 per message)
    bulk_flush_interval = 60.0,  #  max waiting time for messages to start process n_coroutines
    requeue_on_fail = True  # should retry or not the message
)
async def your_consumer(msg: Message): # you receive only one message and we parallelize processing for you
    await barterdude.publish_amqp(
        exchange="my_exchange",
        data=msg.body
    )
    if msg.body == "fail":
    
        my_metric.inc() # you can use prometheus metrics
        healthcheck.force_fail() # you can use your hooks inside consumer too
        msg.reject(requeue=False) # You can force to reject a message, exactly equal https://b2wdigital.github.io/async-worker/src/asyncworker/asyncworker.rabbitmq.html#asyncworker.rabbitmq.message.RabbitMQMessage

    if msg.body == "exception":
        raise Exception() # this will reject the message and requeue

    # if everything is fine, than message automatically is accepted


barterdude.run() # you will start consume and start a server on http://localhost:8080
# Change host and port with ASYNCWORKER_HTTP_HOST and ASYNCWORKER_HTTP_PORT env vars

```

### Build your own Hook

#### Base Hook (Simple One)

These hooks are called when message retreive, have success and fail.

```python
from barterdude.hooks import BaseHook
from asyncworker.rabbitmq.message import RabbitMQMessage

class MyCounterHook(BaseHook):
    _consume = _fail = _success = 0

    async def on_success(self, message: RabbitMQMessage):
        self._success += 1

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        self._fail += 1

    async def before_consume(self, message: RabbitMQMessage):
        self._consume += 1

```

#### Http Hook (Open Route)

These hooks can do everything simple hook does, but responding to a route.

```python
from aiohttp import web
from barterdude.hooks import HttpHook
from asyncworker.rabbitmq.message import RabbitMQMessage

class MyCounterHttpHook(HttpHook):
    _consume = _fail = _success = 0

    async def __call__(self, req: web.Request):
        return web.json_response(dict(
            consumed=self._consume,
            success=self._success,
            fail=self._fail
        ))

    async def on_success(self, message: RabbitMQMessage):
        self._success += 1

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        self._fail += 1

    async def before_consume(self, message: RabbitMQMessage):
        self._consume += 1


```

### Data Sharing

Following the approach found in [async-worker](https://b2wdigital.github.io/async-worker/userguide/asyncworker-app/storage.html) and in [aiohttp](https://docs.aiohttp.org/en/stable/web_advanced.html#data-sharing-aka-no-singletons-please),
`BarterDude` discourages the use of global variables, aka singletons.

To share data states globally in an application, `BarterDude` behaves like a `dict`.
As an example, one can save a global-like variable in a  `BarterDude` instance:

```python
from barterdude import BarterDude

barterdude = BarterDude()
baterdude["my_variable"] = data
```

and get it back in a consumer

```python
async def consumer_access_storage(msg):
    data = baterdude["my_variable"]
```

### Schema Validation

Consumed messages can be validated by json schema:

```python
@barterdude.consume_amqp(
    ["queue1", "queue2"],
    monitor,
    validation_schema={
            "$schema": "http://json-schema.org/draft-04/schema#",
            "$id": "http://example.com/example.json",
            "type": "object",
            "title": "Message Schema",
            "description": "The root schema comprises the entire JSON document.",
            "additionalProperties": True,
            "required": [
                "key"
            ],
            "properties": {
                "key": {
                    "$id": "#/properties/key",
                    "type": "string",
                    "title": "The Key Schema",
                    "description": "An explanation about message.",
                    "default": ""
                }
            }
        },
    requeue_on_validation_fail=False # invalid messages are removed without requeue
)
```

You can still validate messages before produce them or when you want:

```python
from barterdude.message import MessageValidation

validator = MessageValidation(json_schema)
validator.validate(message)
```

### Data Protection

Barterdude takes in account GDPR data protection and by default doesn't log message body, but you can deactivate with environment variable `BARTERDUDE_LOG_REDACTED=0`

Now messages body will be logged by Logging hook.

This configuration just controls BarterDude's default Logging Hook and doesn't have effect on user custom user log. If you want to control your log with this configuration use:

```python
from baterdude.conf import BARTERDUDE_LOG_REDACTED
```

### Testing

To test async consumers we recommend `asynctest` lib

```python
from asynctest import TestCase


class TestMain(TestCase):
    def test_should_pass(self):
        self.assertTrue(True)
```

We hope you enjoy! :wink:

## Contribute

For development and contributing, please follow [Contributing Guide](https://github.com/olxbr/BarterDude/blob/master/CONTRIBUTING.md) and **ALWAYS** respect the [Code of Conduct](https://github.com/olxbr/BarterDude/blob/master/CODE_OF_CONDUCT.md)
