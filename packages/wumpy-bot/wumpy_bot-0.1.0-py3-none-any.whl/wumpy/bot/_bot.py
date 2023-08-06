from contextlib import AsyncExitStack
from contextvars import ContextVar, Token
from types import TracebackType
from typing import NoReturn, Optional, Type, TypeVar, cast, overload

import anyio
import anyio.abc
from typing_extensions import Self
from wumpy.cache import Cache
from wumpy.cache.in_memory import InMemoryCache
from wumpy.gateway import Shard
from wumpy.interactions import ErrorContext
from wumpy.interactions._utils import State
from wumpy.models import Intents
from wumpy.rest import APIClient

from ._dispatch import EventDispatcher
from ._utils import RuntimeVar

__all__ = (
    'Bot',
    'get_bot',
)


BotT = TypeVar('BotT', bound='Bot')


# The get_bot() method is defined below the Bot class, because its default
# is the Bot which hasn't been defined at this point.
_running_bot: ContextVar['Bot'] = ContextVar('_running_bot')


class Bot(EventDispatcher):
    """Main representation of a gateway-based Discord bot.

    There are two ways to run the bot. The easiest to use and recommended way
    is to use the `run()` method:

    ```python
    import anyio
    from wumpy.bot import Bot


    bot = Bot('ABC123.XYZ789', intents=65535)


    # Run the bot with no registered events or commands.
    anyio.run(bot.run)
    ```

    Alternatively, you can use the bot as an asynchronous context manager and
    then startup individual parts of the bot as you wish:

    ```python
    import anyio
    from wumpy.bot import Bot


    bot = Bot('ABC123.XYZ789', intents=65535)


    async def main() -> None:
        async with bot:
            await bot.login()

            await bot.connect_cache()
            # This will run the bot and only exit once the gateway has closed.
            await bot.run_gateway()

    anyio.run(main)
    ```
    """

    api: APIClient
    gateway: Shard
    cache: Cache

    state: State

    intents: Intents

    _started: bool
    _stack: AsyncExitStack
    _old_token: Optional[Token]

    __slots__ = (
        'api', 'gateway', 'cache', 'state', 'intents', '_started', '_stack',
        '_old_token',
    )

    def __init__(self, token: str, *, intents: Intents) -> None:
        super().__init__()

        # Unfortunately, the type checker does not understand how we use
        # RuntimeVar and that this will actually what the attribute is typed as
        self.api = RuntimeVar()  # type: ignore
        self.gateway = RuntimeVar()  # type: ignore
        self.cache = RuntimeVar()  # type: ignore

        self.state = State()

        self.intents = intents

        self._token = token

        self._started = False
        self._stack = AsyncExitStack()
        self._old_token = None

    async def __aenter__(self) -> Self:
        if self._started:
            raise RuntimeError('Bot has already been entered.')

        self._started = True
        self._old_token = _running_bot.set(self)

        await self._stack.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> Optional[bool]:
        self._started = False

        # We'd want to complain, because there *should* be a token to reset to,
        # but this is not a good place to do that.
        if self._old_token is not None:
            _running_bot.reset(self._old_token)

        self._old_token = None

        return await self._stack.__aexit__(exc_type, exc_val, traceback)

    async def login(self) -> None:
        if not self._started:
            raise RuntimeError(
                "Cannot login outside of 'run()' or the asynchronous context manager"
            )

        self.api = await self._stack.enter_async_context(
            APIClient(headers={'Authorization': f'Bot {self.token}'})
        )

    async def connect_cache(self) -> None:
        if not self._started:
            raise RuntimeError(
                "Cannot connect the cahce outside of 'run()' or the async context manager"
            )

        self.cache = await self._stack.enter_async_context(
            InMemoryCache(max_messages=2000)
        )

    # This can in fact return, if the WebSocket connection closes or similar.
    # Which is why PyRight complains that it can return None, hence the
    # 'type: ignore' comment. That said, this SHOULD never return in a
    # typical use-case, and NoReturn means that IDEs can help the user by
    # making code after it greyed out or marking it as an error.
    async def run_gateway(self) -> NoReturn:  # type: ignore
        if not self._started:
            raise RuntimeError(
                "Cannot run the gateway outside of 'run()' or the asynchronous context manager"
            )

        link = await self.api.fetch_gateway()
        self.gateway = await self._stack.enter_async_context(
            Shard(link, self._token, int(self.intents))
        )

        async with anyio.create_task_group() as tasks:
            while True:
                try:
                    data = await self.gateway.receive_event()
                except Exception as exc:
                    tasks.start_soon(self.handle_error, ErrorContext(exc, True))
                    continue

                try:
                    handlers = self.get_dispatch_handlers(data['t'])

                    # Called *with* the 't' key in it for the cache to know the
                    # event that was sent from the gateway.
                    cached = await self.cache.update(data, return_old=bool(handlers))
                except Exception as exc:
                    tasks.start_soon(
                        self.handle_error,
                        ErrorContext(exc, True, gateway_data=data)
                    )
                    continue

                tasks.start_soon(self.dispatch, handlers, data['d'], cached)

    async def run(self) -> NoReturn:
        """Run the main bot.

        Compared to other Discord API wrappers this method should be `await`ed
        or called with `anyio.run()`/`asyncio.run()`/`trio.run()` depending on
        event loop.

        You can also override this method to enter asynchronous context
        managers for startup/shutdown purposes. Afterall, this will only be
        called **once** during the lifetime of the bot.

        This method is incompatible with manual setup when using the bot as an
        asynchronous context manager. See the class docstring for more about
        setting up the bot manually.

        Examples:

            ```python
            class MyBot(Bot):
                async def run(self) -> None:
                    async with asyncpg.create_pool(...) as self.pool:
                        return await super().run()
            ```
        """
        if self._started:
            raise RuntimeError("Cannot use 'run()' and 'async with' together")

        async with self:
            await self.login()

            await self.connect_cache()
            await self.run_gateway()


@overload
def get_bot(*, verify: bool = False) -> Bot:
    ...


@overload
def get_bot(subclass: Type[BotT], *, verify: bool = False) -> BotT:
    ...


def get_bot(subclass: Type[BotT] = Bot, *, verify: bool = False) -> BotT:
    """Get the currently running bot.

    This helper-function allows independent parts of the code to access the
    bot without having to pass it around. The benefit of which, is that a lot
    of internal logic can be simplified.

    The `subclass` parameter can be used for the return type, assuming you know
    the type of the bot currently running. **This is not checked for** by
    default, but can be enabled by passing `verify=True`.

    Parameters:
        subclass: The type of the return type for the type checker.
        verify: Whether to do an `isinstance()` check on the gotten instance.

    Raises:
        RuntimeError: There is no currently running bot.
        RuntimeError: If `verify` is True, the `isinstance()` check failed

    Returns:
        The currently running instance.
    """
    try:
        instance = _running_bot.get()
    except LookupError:
        raise RuntimeError('There is no currently running bot') from None

    if verify and not isinstance(instance, subclass):
        raise RuntimeError(f'Currently running bot is not of type {subclass.__name__!r}')

    return cast(BotT, instance)
