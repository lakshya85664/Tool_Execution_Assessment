from result_envelope import ToolResultEnvelope


def main() -> None:
    print("=" * 60)
    print("TOPIC 7 — TASK 4: RESULT ENVELOPE")
    print("=" * 60)

    print("\nSUCCESS ENVELOPE")

    success = ToolResultEnvelope.success(
        run_id="run-001",
        tool="echo",
        output={"message": "hello"},
        attempts=1,
        retries=0,
        elapsed_s=0.001,
    )

    print(success.model_dump_json(indent=2))

    print("\nTIMEOUT ENVELOPE")

    timeout = ToolResultEnvelope.failure(
        run_id="run-002",
        tool="slow",
        status="timeout",
        error="TimeoutError",
        message="tool execution exceeded timeout",
        attempts=1,
        retries=0,
        elapsed_s=0.051,
    )

    print(timeout.model_dump_json(indent=2))

    print("\nREJECTION ENVELOPE")

    rejected = ToolResultEnvelope.failure(
        run_id="run-003",
        tool="unknown",
        status="rejected",
        error="tool_not_allowed",
        message="tool is not registered",
        attempts=0,
        retries=0,
    )

    print(rejected.model_dump_json(indent=2))


if __name__ == "__main__":
    main()