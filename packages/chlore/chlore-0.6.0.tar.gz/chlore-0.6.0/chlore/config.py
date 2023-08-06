from typing import Literal, Type, TypeVar

from pydantic import BaseSettings


class LoggingConfig(BaseSettings):
    format: Literal["console", "json"] = "console"


class DatabaseConfig(BaseSettings):
    url: str


T = TypeVar("T", bound=BaseSettings)


def from_env(t: Type[T], with_prefix: str = "") -> T:
    class WithPrefix(t):
        class Config:
            env_prefix = with_prefix

    return WithPrefix()
