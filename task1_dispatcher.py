from dispatcher import execute_tool


def echo_tool(args: dict) -> dict:
    return {
        "echo": args["text"],
    }


def failing_tool(args: dict) -> dict:
    raise RuntimeError("simulated tool failure")


def main() -> None:
    print("=" * 60)
    print("TOPIC 7 — TASK 1: DISPATCHER")
    print("=" * 60)

    registry = {
        "echo": echo_tool,
        "failing": failing_tool,
    }

    print("\nHAPPY PATH")

    result = execute_tool(
        registry,
        "echo",
        {"text": "hello"},
    )

    print(f"status: {result['status']}")
    print(f"tool: {result['tool']}")
    print(f"output: {result['output']}")

    print("\nFAILURE PATH")

    result = execute_tool(
        registry,
        "failing",
        {},
    )

    print(f"status: {result['status']}")
    print(f"tool: {result['tool']}")
    print(f"error: {result['error']}")

    print("\nREJECTED TOOL")

    result = execute_tool(
        registry,
        "unknown_tool",
        {},
    )

    print(f"status: {result['status']}")
    print(f"tool: {result['tool']}")
    print(f"error: {result['error']}")


if __name__ == "__main__":
    main()