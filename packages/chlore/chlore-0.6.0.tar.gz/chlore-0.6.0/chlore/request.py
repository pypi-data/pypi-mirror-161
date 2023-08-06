from contextlib import contextmanager
from contextvars import ContextVar
import uuid

from fastapi import Request

_REQUEST: ContextVar[Request] = ContextVar("_CURRENT_REQUEST")


def _set_request(request: Request):
    request.state.id = str(uuid.uuid4())
    return _REQUEST.set(request)


def _reset_request(token):
    _REQUEST.reset(token)


def get_request() -> Request:
    """
    Retrieve the current request
    """
    return _REQUEST.get()


@contextmanager
def request_context(request):
    ctx_token = _set_request(request)
    try:
        yield
    finally:
        _reset_request(ctx_token)
