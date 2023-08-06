import asyncio
import shlex
import sys
from typing import Any, Iterable

pyversion = sys.version_info[:2]

if pyversion >= (3, 7):
    from contextlib import asynccontextmanager

    create_task = asyncio.create_task
else:
    from contextlib2 import asynccontextmanager  # type: ignore[no-redef]

    def create_task(coro: Any) -> Any:  # type: ignore[misc]
        loop = asyncio.get_event_loop()
        return loop.create_task(coro)


if pyversion >= (3, 8):
    from importlib.metadata import version
    from typing import Final, Literal, Protocol, TypedDict

    shlex_join = shlex.join  # type: ignore[attr-defined]
else:
    from importlib_metadata import version  # type: ignore[no-redef]
    from typing_extensions import (  # type: ignore[misc]
        Final,
        Literal,
        Protocol,
        TypedDict,
    )

    def shlex_join(split_command: Iterable[str]) -> str:
        return " ".join(shlex.quote(arg) for arg in split_command)


if pyversion >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator

if pyversion >= (3, 10):
    from typing import TypeAlias  # type: ignore[attr-defined]
else:
    from typing_extensions import TypeAlias


__all__ = [
    "AsyncIterator",
    "Final",
    "Literal",
    "Protocol",
    "TypeAlias",
    "TypedDict",
    "asynccontextmanager",
    "create_task",
    "version",
]
