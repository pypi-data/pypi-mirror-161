from typing import Any, Callable, Optional, Sequence, Set, TypeVar, Union

from logiclayer.module import (
    LOGICLAYER_METHOD_ATTR,
    CallableMayReturnCoroutine,
    MethodType,
    ModuleMethod,
)

C = TypeVar("C", bound=Callable[..., Any])


def healthcheck(func: CallableMayReturnCoroutine[bool]):
    method = ModuleMethod(MethodType.HEALTHCHECK, func=func)
    setattr(func, LOGICLAYER_METHOD_ATTR, method)
    return func


def on_startup(func: Optional[C], *, debug: bool = False):
    def startup_decorator(fn: C) -> C:
        method = ModuleMethod(MethodType.EVENT_STARTUP, debug=debug, func=fn)
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return startup_decorator if func is None else startup_decorator(func)


def on_shutdown(func: Optional[C], *, debug: bool = False):
    def shutdown_decorator(fn: C) -> C:
        method = ModuleMethod(MethodType.EVENT_SHUTDOWN, debug=debug, func=fn)
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return shutdown_decorator if func is None else shutdown_decorator(func)


def route(
    methods: Union[str, Set[str], Sequence[str]],
    path: str,
    *,
    debug: bool = False,
    **kwargs
):
    kwargs["methods"] = set([methods]) if isinstance(methods, str) else set(methods)

    def route_decorator(fn: C) -> C:
        method = ModuleMethod(
            MethodType.ROUTE, debug=debug, func=fn, kwargs=kwargs, path=path
        )
        setattr(fn, LOGICLAYER_METHOD_ATTR, method)
        return fn

    return route_decorator
