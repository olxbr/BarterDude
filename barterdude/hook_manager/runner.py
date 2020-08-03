from typing import Tuple, Callable, Optional, Any
from traceback import format_tb
from barterdude.exceptions import ALL_FLOW
from barterdude.hooks import BaseHook
from asyncio import gather


class Runner:
    async def __callback(self,
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

    def _prepare_callbacks(self, method_name: str,
                           subject: Any,
                           hooks: Tuple[BaseHook],
                           error: Optional[Exception] = None):
        callbacks = []
        for hook in hooks:
            callbacks.append(
                self.__callback(getattr(hook, method_name), subject, error)
            )
        return callbacks

    async def _run(self, callbacks: Tuple[Callable[[Any], Optional[Any]]]):
        await gather(*callbacks)
