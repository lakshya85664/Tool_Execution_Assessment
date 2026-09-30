from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any


METRICS_PATH = Path("traces/execution_metrics.json")


class ExecutionMetrics:
    """
    Collects deterministic execution measurements.

    Metrics are derived from completed result envelopes rather than
    from assumptions about the underlying tool implementation.
    """

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def record(self, result: dict[str, Any]) -> None:
        self.records.append(
            {
                "run_id": result.get("run_id"),
                "tool": result.get("tool"),
                "status": result.get("status"),
                "attempts": result.get("attempts", 0),
                "retries": result.get("retries", 0),
                "elapsed_s": result.get("elapsed_s", 0.0),
            }
        )

    def summary(self) -> dict[str, Any]:
        total = len(self.records)

        successes = sum(
            record["status"] == "success"
            for record in self.records
        )

        errors = sum(
            record["status"] == "error"
            for record in self.records
        )

        rejected = sum(
            record["status"] == "rejected"
            for record in self.records
        )

        timeouts = sum(
            record["status"] == "timeout"
            for record in self.records
        )

        blocked = sum(
            record["status"] == "blocked"
            for record in self.records
        )

        retries = sum(
            record["retries"]
            for record in self.records
        )

        latencies = [
            record["elapsed_s"]
            for record in self.records
        ]

        average_latency = (
            mean(latencies)
            if latencies
            else 0.0
        )

        max_latency = (
            max(latencies)
            if latencies
            else 0.0
        )

        success_rate = (
            successes / total
            if total
            else 0.0
        )

        error_rate = (
            errors / total
            if total
            else 0.0
        )

        return {
            "total_calls": total,
            "successes": successes,
            "errors": errors,
            "rejected": rejected,
            "timeouts": timeouts,
            "blocked": blocked,
            "total_retries": retries,
            "average_latency_s": round(
                average_latency,
                6,
            ),
            "max_latency_s": round(
                max_latency,
                6,
            ),
            "success_rate": round(
                success_rate,
                4,
            ),
            "error_rate": round(
                error_rate,
                4,
            ),
        }

    def save(self) -> None:
        METRICS_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "records": self.records,
            "summary": self.summary(),
        }

        METRICS_PATH.write_text(
            json.dumps(
                payload,
                indent=2,
            ),
            encoding="utf-8",
        )