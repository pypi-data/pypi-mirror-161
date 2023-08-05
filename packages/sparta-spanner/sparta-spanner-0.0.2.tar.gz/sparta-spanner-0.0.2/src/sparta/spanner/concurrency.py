import functools
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

_T = TypeVar("_T")


async def run_as_non_blocking(func: Callable[[...], _T], *args, **kwargs) -> _T:
    try:
        from starlette.concurrency import run_in_threadpool

        return await run_in_threadpool(func, *args, **kwargs)
    except ModuleNotFoundError as error:
        with ThreadPoolExecutor(max_workers=1) as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor, functools.partial(func, *args, **kwargs)
            )
