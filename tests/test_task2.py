import time

from dispatcher import execute_tool


def fast_tool(args: dict) -> dict:
    return {"message": "fast"}


def slow_tool(args: dict) -> dict:
    time.sleep(args["delay_s"])
    return {"message": "slow"}


def test_fast_tool_completes_before_timeout():
    result = execute_tool(
        {"fast": fast_tool},
        "fast",
        {},
        timeout_s=1.0,
    )

    assert result["status"] == "success"
    assert result["output"] == {"message": "fast"}


def test_slow_tool_times_out():
    result = execute_tool(
        {"slow": slow_tool},
        "slow",
        {"delay_s": 0.5},
        timeout_s=0.05,
    )

    assert result["status"] == "timeout"
    assert result["timeout_s"] == 0.05


def test_timeout_result_contains_elapsed_time():
    result = execute_tool(
        {"slow": slow_tool},
        "slow",
        {"delay_s": 0.5},
        timeout_s=0.05,
    )

    assert result["status"] == "timeout"
    assert result["elapsed_s"] >= 0


def test_invalid_timeout_is_rejected():
    result = execute_tool(
        {"fast": fast_tool},
        "fast",
        {},
        timeout_s=0,
    )

    assert result["status"] == "rejected"
    assert result["error"] == "invalid_timeout"


def test_normal_execution_still_records_elapsed_time():
    result = execute_tool(
        {"fast": fast_tool},
        "fast",
        {},
        timeout_s=1.0,
    )

    assert result["status"] == "success"
    assert "elapsed_s" in result
    assert result["elapsed_s"] >= 0