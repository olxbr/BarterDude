import asyncio
from typing import Dict, Any, Iterable, Tuple
from collections import MutableMapping
from aioamqp.properties import Properties


class ObjectWithCallsTracking:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method_calls = []

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        if not hasattr(attr, '__call__') or name == 'get_calls':
            return attr

        if asyncio.iscoroutine(attr) or asyncio.iscoroutinefunction(attr):
            async def async_track_calls(*args, **kwargs):
                self.method_calls.append((
                    name, args, kwargs
                ))
                return await attr(*args, **kwargs)
            return async_track_calls

        def track_calls(*args, **kwargs):
            self.method_calls.append((
                name, args, kwargs
            ))
            return attr(*args, **kwargs)
        return track_calls

    def get_calls(self):
        return [
            {'method': method, 'args': args, 'kwargs': kwargs}
            for method, args, kwargs in self.method_calls
        ]


class RabbitMQMessageMock(ObjectWithCallsTracking):
    def __init__(
        self,
        body: Dict = None,
        headers: Dict = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.body = body
        self.properties = Properties()
        self.properties.headers = headers

    def accept(self, *args, **kwargs):
        pass

    def reject(self, *args, **kwargs):
        pass


class BarterdudeMock(MutableMapping, ObjectWithCallsTracking):
    def __init__(
        self,
        mock_dependencies: Iterable[Tuple[Any, str]] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.__app = {}

        if mock_dependencies:
            for service, name in mock_dependencies:
                self[name] = service

    async def publish_amqp(self, *args, **kwargs):
        pass

    def __getitem__(self, key):
        return self.__app[key]

    def __setitem__(self, key, value):
        self.__app[key] = value

    def __delitem__(self, key):
        del self.__app[key]

    def __len__(self):
        return len(self.__app)

    def __iter__(self):
        return iter(self.__app)
