from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable


class TransientToolError(Exception):
    """Failure that may be retried safely."""


class PermanentToolError(Exception):
    """Failure that should not be retried."""


class AmbiguousWriteError(TransientToolError):
    """
    A write may have been applied even though the caller did not
    receive a definitive result.

    Such operations require idempotency or operation-status checking
    before another attempt.
    """


@dataclass
class RetryPolicy:
    max_retries: int = 2
    backoff_s: float = 0.01
    max_backoff_s: float = 0.05

    def can_retry(self, retry_count: int) -> bool:
        return retry_count < self.max_retries

    def delay_for(self, retry_count: int) -> float:
        delay = self.backoff_s * (2 ** retry_count)
        return min(delay, self.max_backoff_s)


def execute_with_retry(
    tool: Callable[[dict[str, Any]], Any],
    args: dict[str, Any],
    *,
    policy: RetryPolicy | None = None,
    is_write: bool = False,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    """
    Execute a tool with bounded retries.

    Only TransientToolError is retryable.

    Ambiguous writes require an idempotency key before another
    attempt can occur.
    """

    policy = policy or RetryPolicy()

    retry_count = 0
    attempts = 0
    retry_events: list[dict[str, Any]] = []

    while True:
        attempts += 1

        try:
            output = tool(args)

            return {
                "status": "success",
                "output": output,
                "attempts": attempts,
                "retries": retry_count,
                "retry_events": retry_events,
            }

        except AmbiguousWriteError as exc:
            if is_write and not idempotency_key:
                return {
                    "status": "blocked",
                    "error": type(exc).__name__,
                    "message": (
                        "ambiguous write requires an idempotency key "
                        "before retry"
                    ),
                    "attempts": attempts,
                    "retries": retry_count,
                    "retry_events": retry_events,
                }

            if not policy.can_retry(retry_count):
                return {
                    "status": "error",
                    "error": type(exc).__name__,
                    "message": "retry budget exhausted",
                    "attempts": attempts,
                    "retries": retry_count,
                    "retry_events": retry_events,
                }

            delay = policy.delay_for(retry_count)

            retry_events.append(
                {
                    "attempt": attempts,
                    "failure": type(exc).__name__,
                    "classification": "transient",
                    "delay_s": delay,
                }
            )

            retry_count += 1
            time.sleep(delay)

        except TransientToolError as exc:
            if not policy.can_retry(retry_count):
                return {
                    "status": "error",
                    "error": type(exc).__name__,
                    "message": "retry budget exhausted",
                    "attempts": attempts,
                    "retries": retry_count,
                    "retry_events": retry_events,
                }

            delay = policy.delay_for(retry_count)

            retry_events.append(
                {
                    "attempt": attempts,
                    "failure": type(exc).__name__,
                    "classification": "transient",
                    "delay_s": delay,
                }
            )

            retry_count += 1
            time.sleep(delay)

        except PermanentToolError as exc:
            return {
                "status": "error",
                "error": type(exc).__name__,
                "message": "permanent failure is not retryable",
                "attempts": attempts,
                "retries": retry_count,
                "retry_events": retry_events,
            }

        except Exception as exc:
            return {
                "status": "error",
                "error": type(exc).__name__,
                "message": "unclassified failure is not retryable",
                "attempts": attempts,
                "retries": retry_count,
                "retry_events": retry_events,
            }