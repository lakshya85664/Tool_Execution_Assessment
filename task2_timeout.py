import time

from dispatcher import execute_tool


def fast_tool(args: dict) -> dict:
    return {
        "message": args["message"],
    }


def slow_tool(args: dict) -> dict:
    time.sleep(args["delay_s"])

    return {
        "message": "slow tool completed",
    }


def main() -> None:
    print("=" * 60)
    print("TOPIC 7 — TASK 2: TIMEOUT")
    print("=" * 60)

    registry = {
        "fast": fast_tool,
        "slow": slow_tool,
    }

    print("\nHAPPY PATH")

    result = execute_tool(
        registry,
        "fast",
        {"message": "completed quickly"},
        timeout_s=1.0,
    )

    print(f"status: {result['status']}")
    print(f"tool: {result['tool']}")
    print(f"output: {result['output']}")
    print(f"elapsed_s: {result['elapsed_s']}")

    print("\nTIMEOUT PATH")

    result = execute_tool(
        registry,
        "slow",
        {"delay_s": 0.5},
        timeout_s=0.05,
    )

    print(f"status: {result['status']}")
    print(f"tool: {result['tool']}")
    print(f"timeout_s: {result['timeout_s']}")
    print(f"elapsed_s: {result['elapsed_s']}")


if __name__ == "__main__":
    main()