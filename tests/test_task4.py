import pytest
from pydantic import ValidationError

from result_envelope import ToolResultEnvelope


def test_success_envelope():
    result = ToolResultEnvelope.success(
        run_id="run-001",
        tool="echo",
        output={"message": "hello"},
    )

    assert result.status == "success"
    assert result.output == {"message": "hello"}
    assert result.error is None


def test_timeout_envelope():
    result = ToolResultEnvelope.failure(
        run_id="run-002",
        tool="slow",
        status="timeout",
        error="TimeoutError",
    )

    assert result.status == "timeout"
    assert result.error == "TimeoutError"


def test_rejection_envelope():
    result = ToolResultEnvelope.failure(
        run_id="run-003",
        tool="unknown",
        status="rejected",
        error="tool_not_allowed",
    )

    assert result.status == "rejected"
    assert result.error == "tool_not_allowed"


def test_negative_attempts_are_rejected():
    with pytest.raises(ValidationError):
        ToolResultEnvelope(
            run_id="run-004",
            tool="echo",
            status="success",
            attempts=-1,
        )


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        ToolResultEnvelope(
            run_id="run-005",
            tool="echo",
            status="success",
            unexpected="value",
        )