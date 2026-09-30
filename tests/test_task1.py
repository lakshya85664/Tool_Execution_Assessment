import pytest

from dispatcher import execute_tool


def echo_tool(args: dict) -> dict:
    return {"echo": args["text"]}


def failing_tool(args: dict) -> dict:
    raise RuntimeError("simulated failure")


def test_dispatcher_executes_allowed_tool():
    result = execute_tool(
        {"echo": echo_tool},
        "echo",
        {"text": "hello"},
    )

    assert result["status"] == "success"
    assert result["tool"] == "echo"
    assert result["output"] == {"echo": "hello"}


def test_dispatcher_rejects_unknown_tool():
    result = execute_tool(
        {"echo": echo_tool},
        "unknown",
        {},
    )

    assert result["status"] == "rejected"
    assert result["error"] == "tool_not_allowed"


def test_dispatcher_captures_tool_failure():
    result = execute_tool(
        {"failing": failing_tool},
        "failing",
        {},
    )

    assert result["status"] == "error"
    assert result["error"] == "RuntimeError"


def test_dispatcher_rejects_non_dictionary_arguments():
    result = execute_tool(
        {"echo": echo_tool},
        "echo",
        "invalid",
    )

    assert result["status"] == "rejected"
    assert result["error"] == "ToolArgumentError"


def test_dispatcher_records_elapsed_time():
    result = execute_tool(
        {"echo": echo_tool},
        "echo",
        {"text": "hello"},
    )

    assert result["status"] == "success"
    assert "elapsed_s" in result
    assert result["elapsed_s"] >= 0