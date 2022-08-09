import asyncio
from unittest.mock import Mock
from typing import Dict, Any, Iterable


class AsyncMock(Mock):

    def __call__(self, *args, **kwargs):
        sup = super(AsyncMock, self)

        async def coro():
            return sup.__call__(*args, **kwargs)
        return coro()

    def __await__(self):
        return self().__await__()


class MockWithAssignment(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__data = {}

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __getitem__(self, key):
        return self.__data[key]

    def __delitem__(self, key):
        del self.__data[key]

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def get_calls(self):
        return [
            {'method': method, 'args': args, 'kwargs': kwargs}
            for method, args, kwargs in self.method_calls
        ]


class PartialMockService:
    def __init__(
        self,
        service: Any,
        name: str,
        methods: Dict = None,
        async_methods: Dict = None
    ):
        self._service = service
        self._name = name
        self._methods = methods or {}
        self._async_methods = async_methods or {}

    def __getattr__(self, name):
        if hasattr(self._service, name):
            attr = getattr(self._service, name)
            if hasattr(attr, '__call__'):
                def replace_method(*args, **kwargs):
                    if name in self._methods:
                        return self._methods[name]
                    if name in self._async_methods:
                        future = asyncio.Future()
                        future.set_result(self._async_methods[name])
                        return future
                    return attr(*args, **kwargs)
                return replace_method
            else:
                return attr


class RabbitMQMessageMock(MockWithAssignment):
    def __init__(
        self,
        body: Dict = None,
        headers: Dict = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.body = body
        self.properties = MockWithAssignment()
        self.properties.headers = headers


class BarterdudeMock(MockWithAssignment):
    def __init__(
        self,
        mock_dependencies: Iterable[PartialMockService] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.publish_amqp = AsyncMock()
        if mock_dependencies:
            for dependency in mock_dependencies:
                self[dependency._name] = dependency
