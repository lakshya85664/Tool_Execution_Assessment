from retry_policy import (
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

        return {
            "message": "success after retry",
        }


def permanent_failure(args: dict) -> dict:
    raise PermanentToolError("permanent failure")


def ambiguous_write(args: dict) -> dict:
    raise Exception("placeholder")


def main() -> None:
    print("=" * 60)
    print("TOPIC 7 — TASK 3: RETRY POLICY")
    print("=" * 60)

    policy = RetryPolicy(
        max_retries=2,
        backoff_s=0.01,
        max_backoff_s=0.02,
    )

    print("\nTRANSIENT FAILURE → SUCCESS")

    flaky = FlakyTool(failures_before_success=1)

    result = execute_with_retry(
        flaky,
        {},
        policy=policy,
    )

    print(f"status: {result['status']}")
    print(f"attempts: {result['attempts']}")
    print(f"retries: {result['retries']}")
    print(f"retry events: {result['retry_events']}")

    print("\nPERMANENT FAILURE")

    result = execute_with_retry(
        permanent_failure,
        {},
        policy=policy,
    )

    print(f"status: {result['status']}")
    print(f"error: {result['error']}")
    print(f"attempts: {result['attempts']}")
    print(f"retries: {result['retries']}")

    print("\nAMBIGUOUS WRITE WITHOUT IDEMPOTENCY")

    def ambiguous_write_without_key(args: dict) -> dict:
        from retry_policy import AmbiguousWriteError

        raise AmbiguousWriteError(
            "write result is ambiguous"
        )

    result = execute_with_retry(
        ambiguous_write_without_key,
        {},
        policy=policy,
        is_write=True,
        idempotency_key=None,
    )

    print(f"status: {result['status']}")
    print(f"message: {result['message']}")
    print(f"attempts: {result['attempts']}")


if __name__ == "__main__":
    main()