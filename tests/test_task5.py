from pathlib import Path

from metrics import ExecutionMetrics


def test_metrics_count_total_calls():
    metrics = ExecutionMetrics()

    metrics.record(
        {
            "run_id": "run-1",
            "tool": "echo",
            "status": "success",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.01,
        }
    )

    metrics.record(
        {
            "run_id": "run-2",
            "tool": "slow",
            "status": "timeout",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.05,
        }
    )

    summary = metrics.summary()

    assert summary["total_calls"] == 2


def test_metrics_count_statuses():
    metrics = ExecutionMetrics()

    statuses = [
        "success",
        "success",
        "error",
        "rejected",
        "timeout",
        "blocked",
    ]

    for index, status in enumerate(statuses):
        metrics.record(
            {
                "run_id": f"run-{index}",
                "tool": "test",
                "status": status,
                "attempts": 1,
                "retries": 0,
                "elapsed_s": 0.01,
            }
        )

    summary = metrics.summary()

    assert summary["successes"] == 2
    assert summary["errors"] == 1
    assert summary["rejected"] == 1
    assert summary["timeouts"] == 1
    assert summary["blocked"] == 1


def test_metrics_sum_retries():
    metrics = ExecutionMetrics()

    metrics.record(
        {
            "run_id": "run-1",
            "tool": "flaky",
            "status": "success",
            "attempts": 3,
            "retries": 2,
            "elapsed_s": 0.03,
        }
    )

    metrics.record(
        {
            "run_id": "run-2",
            "tool": "echo",
            "status": "success",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.01,
        }
    )

    assert metrics.summary()["total_retries"] == 2


def test_metrics_calculate_latency():
    metrics = ExecutionMetrics()

    metrics.record(
        {
            "run_id": "run-1",
            "tool": "a",
            "status": "success",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.01,
        }
    )

    metrics.record(
        {
            "run_id": "run-2",
            "tool": "b",
            "status": "success",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.03,
        }
    )

    summary = metrics.summary()

    assert summary["average_latency_s"] == 0.02
    assert summary["max_latency_s"] == 0.03


def test_metrics_save_creates_evidence_file(tmp_path, monkeypatch):
    import metrics

    target = tmp_path / "execution_metrics.json"

    monkeypatch.setattr(
        metrics,
        "METRICS_PATH",
        target,
    )

    recorder = ExecutionMetrics()

    recorder.record(
        {
            "run_id": "run-save",
            "tool": "echo",
            "status": "success",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.01,
        }
    )

    recorder.save()

    assert target.exists()
    assert target.read_text(encoding="utf-8")