"""LogicLayer class module.

Contains the main definitions for the LogicLayer class.
"""

import asyncio
import logging
from typing import Any, List

from fastapi import FastAPI, HTTPException
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

from .module import CallableMayReturnCoroutine, LogicLayerModule, _await_for_it

logger = logging.getLogger("logiclayer")


class LogicLayer:
    """Main LogicLayer app handler

    Instances of this class act like ASGI callables."""

    app: FastAPI
    _checklist: List[CallableMayReturnCoroutine[bool]]
    _debug: bool

    def __init__(self, *, debug: bool = False, healthchecks: bool = True):
        self.app = FastAPI()
        self._checklist = []
        self._debug = debug

        if healthchecks:
            self.app.add_api_route("/_health", _new_healthcheck(self._checklist))

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """This method converts the :class:`LogicLayer` instance into an
        ASGI-compatible callable.
        """
        await self.app(scope, receive, send)

    def add_check(self, func: CallableMayReturnCoroutine[bool]):
        """Stores a function to be constantly run as a healthcheck for the app.

        Arguments:
            func :Callable[..., Coroutine[Any, Any, Response]]:
        """
        logger.debug("Check added: %s", func.__name__)
        self._checklist.append(func)

    def add_module(self, prefix: str, module: LogicLayerModule, **kwargs):
        """Setups a module instance in the current LogicLayer instance.

        Arguments:
            prefix :str:
                The prefix path to all routes in the module.
                Must start, and not end, with `/`.
            module :logiclayer.LogicLayerModule:
                An instance of a subclass of :class:`logiclayer.LogicLayerModule`.

        Keyword arguments:
            {any from :func:`FastAPI.include_router` function}
        """
        logger.debug("Module added on path %s: %s", prefix, type(module).__name__)
        self.app.include_router(module.router, prefix=prefix, **kwargs)
        self.add_check(module._llhealthcheck)

    def add_route(self, path: str, func: CallableMayReturnCoroutine[Any], **kwargs):
        """Setups a path function to be used directly in the root app.

        Arguments:
            path :str:
                The full path to the route this function will serve.
            func :Callable[..., Response] | Callable[..., Coroutine[Any, Any, Response]]:
                The function which will serve the content for the route.
        """
        logger.debug("Route added on path %s: %s", path, func.__name__)
        self.app.add_api_route(path, func, **kwargs)

    async def call_startup(self):
        """Forces a call to all handlers registered for the 'startup' event."""
        await self.app.router.startup()

    async def call_shutdown(self):
        """Forces a call to all handlers registered for the 'shutdown' event."""
        await self.app.router.shutdown()


def _new_healthcheck(checklist: List[CallableMayReturnCoroutine[bool]]):
    """Creates a healthcheck route function, which runs all callables in
    `checklist` for diagnostic."""

    async def ll_healthcheck():
        try:
            gen = (_await_for_it(item) for item in checklist)
            await asyncio.gather(*gen)
        except Exception as exc:
            msg = "An element in Healthcheck failed."
            logger.error(msg, exc_info=exc)
            raise HTTPException(500, msg) from None

        return Response("", status_code=204)

    return ll_healthcheck
