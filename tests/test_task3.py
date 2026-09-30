from retry_policy import (
    AmbiguousWriteError,
    PermanentToolError,
    RetryPolicy,
    TransientToolError,
    execute_with_retry,
)


class FlakyTool:
    def __init__(self, failures_before_success: int):
        self.calls = 0
        self.failures_before_success = failures_before_success

    def __call__(self, args: dict) -> dict:
        self.calls += 1

        if self.calls <= self.failures_before_success:
            raise TransientToolError("temporary failure")

        return {"ok": True}


def test_transient_failure_is_retried():
    tool = FlakyTool(1)

    result = execute_with_retry(
        tool,
        {},
        policy=RetryPolicy(max_retries=2),
    )

    assert result["status"] == "success"
    assert result["attempts"] == 2
    assert result["retries"] == 1


def test_transient_failure_can_succeed_after_two_retries():
    tool = FlakyTool(2)

    result = execute_with_retry(
        tool,
        {},
        policy=RetryPolicy(max_retries=2),
    )

    assert result["status"] == "success"
    assert result["attempts"] == 3
    assert result["retries"] == 2


def test_retry_budget_is_bounded():
    tool = FlakyTool(3)

    result = execute_with_retry(
        tool,
        {},
        policy=RetryPolicy(max_retries=2),
    )

    assert result["status"] == "error"
    assert result["attempts"] == 3
    assert result["retries"] == 2


def test_permanent_failure_is_not_retried():
    calls = 0

    def permanent(args: dict) -> dict:
        nonlocal calls
        calls += 1
        raise PermanentToolError("permanent")

    result = execute_with_retry(
        permanent,
        {},
        policy=RetryPolicy(max_retries=2),
    )

    assert result["status"] == "error"
    assert calls == 1
    assert result["retries"] == 0


def test_ambiguous_write_requires_idempotency():
    def ambiguous(args: dict) -> dict:
        raise AmbiguousWriteError("unknown write outcome")

    result = execute_with_retry(
        ambiguous,
        {},
        policy=RetryPolicy(max_retries=2),
        is_write=True,
        idempotency_key=None,
    )

    assert result["status"] == "blocked"
    assert result["attempts"] == 1
    assert result["retries"] == 0