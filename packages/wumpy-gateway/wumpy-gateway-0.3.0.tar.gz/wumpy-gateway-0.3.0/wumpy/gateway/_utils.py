import time
from contextlib import asynccontextmanager
from functools import partial
from types import TracebackType
from typing import (
    Any, AsyncContextManager, AsyncGenerator, Awaitable, Callable, Optional,
    Type
)

import anyio
from discord_gateway import Opcode
from typing_extensions import Protocol, Self

__all__ = (
    'GatewayLimiter',
    'DefaultGatewayLimiter',
)


async def _done_callback(
    func: Callable[[], Awaitable[Any]],
    callback: Callable[[], Any]
) -> None:
    await func()

    # It is a deliberate design decision to not use a try/finally block here,
    # we only want to call the callback if func() was successful.
    callback()


async def race(*functions: Callable[[], Awaitable[Any]]) -> None:
    """Race several coroutine functions against each other.

    This function will return when the first of the functions complete, by
    cancelling all other functions. This means that only functions that can
    properly handle cancellation should be used with this function.

    Parameters:
        functions: The functions to race against each other.
    """
    if not functions:
        raise ValueError("race() missing at least 1 required positional argument")

    async with anyio.create_task_group() as tg:
        for func in functions:
            tg.start_soon(partial(_done_callback, func, tg.cancel_scope.cancel))


class GatewayLimiter(Protocol):
    """Interface for a gateway ratelimiter.

    This protocol is almost the same as the following:

    ```python
    AsynContextManager[Callable[
        [int], AsyncContextManager[object]
    ]]
    ```

    The difference is the fact that the async context manager must also be
    callable (and therefore it should return `self`).
    """
    async def __aenter__(self) -> object:
        ...

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> Optional[bool]:
        ...

    def __call__(self, __opcode: Opcode) -> AsyncContextManager[object]:
        ...


class DefaultGatewayLimiter:
    _lock: anyio.Lock
    _reset: Optional[float]
    _value: int

    RATE = 120 - 3  # We leave a margin of 3 heartbeats per minute
    PER = 60

    __slots__ = ('_lock', '_reset', '_value')

    def __init__(self) -> None:
        self._reset = None
        self._value = self.RATE

        # self._lock is set in __aenter__()

    @asynccontextmanager
    async def __call__(self, opcode: Opcode) -> AsyncGenerator[None, None]:
        # Heartbeats are not ratelimited and we have left a margin for them.
        if opcode is not Opcode.HEARTBEAT:
            async with self._lock:
                if self._reset is None or self._reset < time.perf_counter():
                    self._reset = time.perf_counter() + self.PER
                    self._value = self.RATE - 1

                elif self._value <= 0:
                    await anyio.sleep(self._reset - time.perf_counter())
                    self._reset = time.perf_counter() + self.PER
                    self._value = self.RATE - 1
                else:
                    self._value -= 1

        # Yield once we have released the lock, it is only held for the
        # case that we're sleeping, because if one tasks sleep then all
        # following tasks will also need to sleep.
        yield

    async def __aenter__(self) -> Self:
        self._lock = anyio.Lock()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        pass
