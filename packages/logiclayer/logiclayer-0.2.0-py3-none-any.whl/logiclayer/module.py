import asyncio
import dataclasses
import inspect
from enum import Enum
from functools import partial, wraps
from typing import Any, Awaitable, Callable, Coroutine, Dict, Tuple, TypeVar, Union

from fastapi import APIRouter

LOGICLAYER_METHOD_ATTR = "_llmethod"

T = TypeVar("T")
CallableMayReturnAwaitable = Union[Callable[..., T], Callable[..., Awaitable[T]]]
CallableMayReturnCoroutine = Union[
    Callable[..., T],
    Callable[..., Coroutine[Any, Any, T]],
]


class MethodType(Enum):
    HEALTHCHECK = 1
    ROUTE = 2
    EVENT_STARTUP = 3
    EVENT_SHUTDOWN = 4


@dataclasses.dataclass
class ModuleMethod:
    kind: MethodType
    func: CallableMayReturnCoroutine[Any]
    debug: bool = False
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)
    path: str = ""


class ModuleMeta(type):
    """Base LogicLayer Module Metaclass."""

    def __new__(
        cls, clsname: str, supercls: Tuple[type, ...], attrdict: Dict[str, Any]
    ):
        attrdict["_llchecklist"] = tuple()
        attrdict["_llmethods"] = tuple(
            getattr(item, LOGICLAYER_METHOD_ATTR)
            for item in attrdict.values()
            if hasattr(item, LOGICLAYER_METHOD_ATTR)
        )
        return super(ModuleMeta, cls).__new__(cls, clsname, supercls, attrdict)


class LogicLayerModule(metaclass=ModuleMeta):
    """Base class for LogicLayer Modules.

    Modules must inherit from this class to be used in LogicLayer.
    Routes can be set using the provided decorators on any instance method.
    """

    _llchecklist: Tuple[ModuleMethod, ...]
    _llmethods: Tuple[ModuleMethod, ...]

    def __init__(self, **kwargs):
        router = APIRouter(**kwargs)

        for item in self._llmethods:
            if item.kind == MethodType.HEALTHCHECK:
                continue
            func = _bind_if_needed(item.func, self)
            if item.kind == MethodType.ROUTE:
                router.add_api_route(item.path, func, **item.kwargs)
            elif item.kind == MethodType.EVENT_STARTUP:
                router.add_event_handler("startup", func)
            elif item.kind == MethodType.EVENT_SHUTDOWN:
                router.add_event_handler("shutdown", func)

        self.router = router
        self._llchecklist = tuple(
            item for item in self._llmethods if item.kind == MethodType.HEALTHCHECK
        )

    async def _llhealthcheck(self) -> bool:
        checklist = self._llchecklist
        try:
            gen = (_await_for_it(item.func) for item in checklist)
            result = await asyncio.gather(*gen)
            return all(item is True for item in result)
        except Exception as exc:
            return False


async def _await_for_it(check: CallableMayReturnAwaitable[Any]) -> Any:
    """Wraps a function, which might be synchronous or asynchronous, into an
    asynchronous function, which returns the value wrapped in a coroutine.
    """
    result = check()
    if inspect.isawaitable(result):
        result = await result
    return result


def _bind_if_needed(func, self):
    """Creates a binding of the `func` method to the `self` object as the first
    positional parameter, only if this positional parameter is called 'self'."""
    sig = inspect.signature(func)
    if "self" in sig.parameters:
        return (
            async_partial(func, self)
            if inspect.iscoroutinefunction(func)
            else partial(func, self)
        )
    return func


def async_partial(func, self):
    """Async-enabled monkeypatch for the partial function."""

    @wraps(partial(func, self))
    async def wrapper(*args, **kwargs):
        return await func(self, *args, **kwargs)

    return wrapper
