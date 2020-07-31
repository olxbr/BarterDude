from typing import Iterable, Callable, Optional, Any
from traceback import format_tb
from functools import lru_cache
from barterdude.exceptions import ALL_FLOW
from barterdude.hooks import BaseHook
from asyncio import gather


class Runner:
    async def _callback(self,
                        method: Callable[[Any], Optional[Any]],
                        subject: Any,
                        error: Optional[Exception] = None):
        try:
            return await (method(subject, error) if error else method(subject))
        except ALL_FLOW as e:
            raise e
        except Exception as e:
            self._logger.error({
                "subject": f"Error on hook method {method}",
                "exception": repr(e),
                "traceback": format_tb(e.__traceback__),
            })

    @lru_cache(maxsize=None)
    def _prepare_callbacks(self, method_name: str,
                           subject: Any,
                           hooks: Iterable[BaseHook],
                           error: Optional[Exception] = None):
        callbacks = []

        for hook in hooks:
            callbacks.append(
                self._callback(getattr(hook, method_name), subject, error)
            )
        return callbacks

    async def run(callbacks: Iterable[Callable[[Any], Optional[Any]]]):
        await gather(*callbacks)
