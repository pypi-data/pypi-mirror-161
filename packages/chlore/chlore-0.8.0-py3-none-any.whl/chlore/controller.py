import inspect
from typing import ClassVar, Type, get_origin, get_type_hints

from fastapi import APIRouter, Depends
import structlog

from .logging import request_logger


def _patch_class(cls: Type):
    """
    Patch a class P defined as:
    ```
    class P:
        x: int = Depends(y)
    ```
    To turn it into a class defined like:
    ```
    class P:
        def __init__(self, *, x: int = Depends(y)):
            self.x = x
    ```
    """

    def to_new_param(name: str, type_hint) -> inspect.Parameter:
        return inspect.Parameter(
            name=name,
            kind=inspect.Parameter.KEYWORD_ONLY,  # use kwargs in order to access them by name later
            annotation=type_hint,
            default=getattr(cls, name, Ellipsis),
        )

    def new_init(self, *_, **kwargs):
        for p in new_param_names:
            setattr(self, p, kwargs.get(p))

    original_signature = inspect.signature(cls.__init__)
    new_params = [to_new_param(n, h) for n, h in get_type_hints(cls).items() if get_origin(h) is not ClassVar]
    cls.__signature__ = original_signature.replace(parameters=new_params)
    new_param_names = [p.name for p in new_params]
    cls.__init__ = new_init


def _patch_endpoint(cls: Type, endpoint):
    """
    Patch a FastAPI endpoint defined as a method of a given class:
    ```
    @app.get("/{item}")
    def index(self, item: int):
        pass
    ```
    To turn it into a method defined like:
    ```
    @app.get("/{item}")
    def index(self = Depends(cls), *, item: int):
        pass
    ```
    """
    original_signature = inspect.signature(endpoint)
    original_params = iter(original_signature.parameters.values())
    self_param = next(original_params).replace(default=Depends(cls))
    kwargs = [p.replace(kind=inspect.Parameter.KEYWORD_ONLY) for p in original_params]
    endpoint.__signature__ = original_signature.replace(parameters=[self_param] + kwargs)


class Controller:
    """
    Base class allowing to write FastAPI endpoints as methods and specify class-level dependencies

    Example:
    ```
    class MyClass(Controller, router=router):
        some_dependency: str = Depends(get_some_dependency)

        @router.get("/index")
        def index(self):
            return "OK " + self.some_dependency
    ```
    """

    def __init_subclass__(cls, router: APIRouter = None, **kwargs):
        if router is not None:
            _patch_class(cls)

            methods = {v for _, v in inspect.getmembers(cls, inspect.isfunction)}
            for route in router.routes:
                if route.endpoint not in methods:
                    continue
                _patch_endpoint(cls, route.endpoint)


class LoggerMixin:
    """
    A controller mixin to add a dependency over the current request logger
    """

    logger: structlog.stdlib.BoundLogger = Depends(request_logger)
