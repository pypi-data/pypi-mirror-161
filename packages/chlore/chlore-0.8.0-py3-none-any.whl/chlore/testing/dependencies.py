from contextlib import contextmanager
from typing import Callable


@contextmanager
def override_dependency(app, dependency: Callable, replacement: Callable):
    """
    Override a given dependency in a FastAPI app by replacing it with another function
    """
    previous = app.dependency_overrides.get(dependency)
    app.dependency_overrides[dependency] = replacement
    try:
        yield
    finally:
        if previous is not None:
            app.dependency_overrides[dependency] = previous
        else:
            app.dependency_overrides.pop(dependency)
