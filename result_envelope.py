from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ResultStatus = Literal[
    "success",
    "rejected",
    "timeout",
    "error",
    "blocked",
]


class ToolResultEnvelope(BaseModel):
    """
    Standard result contract for tool execution.
    """

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    tool: str = Field(min_length=1)

    status: ResultStatus

    output: Any | None = None

    error: str | None = None
    message: str | None = None

    attempts: int = Field(default=1, ge=0)
    retries: int = Field(default=0, ge=0)

    elapsed_s: float = Field(default=0.0, ge=0.0)

    @classmethod
    def success(
        cls,
        *,
        run_id: str,
        tool: str,
        output: Any,
        attempts: int = 1,
        retries: int = 0,
        elapsed_s: float = 0.0,
    ) -> "ToolResultEnvelope":
        return cls(
            run_id=run_id,
            tool=tool,
            status="success",
            output=output,
            attempts=attempts,
            retries=retries,
            elapsed_s=elapsed_s,
        )

    @classmethod
    def failure(
        cls,
        *,
        run_id: str,
        tool: str,
        status: ResultStatus,
        error: str,
        message: str | None = None,
        attempts: int = 1,
        retries: int = 0,
        elapsed_s: float = 0.0,
    ) -> "ToolResultEnvelope":
        return cls(
            run_id=run_id,
            tool=tool,
            status=status,
            error=error,
            message=message,
            attempts=attempts,
            retries=retries,
            elapsed_s=elapsed_s,
        )