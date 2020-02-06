[![Build Status](https://travis-ci.com/olxbr/BarterDude.svg?branch=master)](https://travis-ci.com/olxbr/BarterDude)

# BarterDude
Message exchange engine to build pipelines using brokers like RabbitMQ

## Install

Using Python 3.6+

```sh
make install
```

or

```sh
make setup
```

for development

## Test

```sh
make test
```

## Usage

```python
    barterdude = BarterDude([connection, ...])

    healthcheck = Healthcheck(baterdude, ...)
    metrics = Prometheus(baterdude, ...)
    monitor = Monitor(healthcheck, metrics)

    @barterdude.route(["queue"], ...)
    @barterdude.forward(["exchange"], ...)
    @barterdude.observe(monitor)
    def my_callback(msg):
        pass
```

## Contribute

For development and contributing, please follow [Contributing Guide](https://github.com/olxbr/BarterDude/blob/master/CONTRIBUTING.md) and **ALWAYS** respect the [Code of Conduct](https://github.com/olxbr/BarterDude/blob/master/CODE_OF_CONDUCT.md)