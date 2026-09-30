from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Callable


class ToolExecutionError(Exception):
    """Base exception for tool execution failures."""


class ToolNotAllowedError(ToolExecutionError):
    """Raised when a tool is not present in the allowed registry."""


class ToolArgumentError(ToolExecutionError):
    """Raised when tool arguments are invalid."""


def validate_tool_arguments(args: dict[str, Any]) -> None:
    """Validate the basic tool argument boundary."""

    if not isinstance(args, dict):
        raise ToolArgumentError("tool arguments must be a dictionary")


def execute_tool(
    registry: dict[str, Callable[[dict[str, Any]], Any]],
    name: str,
    args: dict[str, Any],
    timeout_s: float = 2.0,
) -> dict[str, Any]:
    """
    Dispatch one tool call through a bounded execution boundary.

    The dispatcher:
    - rejects unknown tools;
    - validates arguments;
    - executes the tool in a worker;
    - enforces a caller-side timeout;
    - captures failures;
    - records elapsed time.
    """

    if name not in registry:
        return {
            "status": "rejected",
            "tool": name,
            "error": "tool_not_allowed",
        }

    try:
        validate_tool_arguments(args)
    except ToolArgumentError as exc:
        return {
            "status": "rejected",
            "tool": name,
            "error": type(exc).__name__,
            "message": str(exc),
        }

    if timeout_s <= 0:
        return {
            "status": "rejected",
            "tool": name,
            "error": "invalid_timeout",
        }

    started = time.perf_counter()

    executor = ThreadPoolExecutor(max_workers=1)

    try:
        future = executor.submit(registry[name], args)

        try:
            result = future.result(timeout=timeout_s)

        except FutureTimeoutError:
            elapsed = time.perf_counter() - started

            future.cancel()

            return {
                "status": "timeout",
                "tool": name,
                "elapsed_s": round(elapsed, 6),
                "timeout_s": timeout_s,
            }

        except Exception as exc:
            elapsed = time.perf_counter() - started

            return {
                "status": "error",
                "tool": name,
                "error": type(exc).__name__,
                "elapsed_s": round(elapsed, 6),
            }

        elapsed = time.perf_counter() - started

        return {
            "status": "success",
            "tool": name,
            "output": result,
            "elapsed_s": round(elapsed, 6),
        }

    finally:
        # Do not wait for a timed-out worker before returning.
        executor.shutdown(wait=False, cancel_futures=True)