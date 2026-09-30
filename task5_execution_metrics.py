from metrics import ExecutionMetrics


def main() -> None:
    print("=" * 60)
    print("TOPIC 7 — TASK 5: EXECUTION METRICS")
    print("=" * 60)

    metrics = ExecutionMetrics()

    print("\nRECORDING EXECUTION RESULTS")

    results = [
        {
            "run_id": "run-metric-001",
            "tool": "echo",
            "status": "success",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.010,
        },
        {
            "run_id": "run-metric-002",
            "tool": "slow",
            "status": "timeout",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.050,
        },
        {
            "run_id": "run-metric-003",
            "tool": "flaky",
            "status": "success",
            "attempts": 2,
            "retries": 1,
            "elapsed_s": 0.025,
        },
        {
            "run_id": "run-metric-004",
            "tool": "unknown",
            "status": "rejected",
            "attempts": 0,
            "retries": 0,
            "elapsed_s": 0.000,
        },
        {
            "run_id": "run-metric-005",
            "tool": "permanent",
            "status": "error",
            "attempts": 1,
            "retries": 0,
            "elapsed_s": 0.015,
        },
    ]

    for result in results:
        metrics.record(result)

        print(
            f"{result['run_id']}: "
            f"status={result['status']}, "
            f"elapsed_s={result['elapsed_s']}"
        )

    summary = metrics.summary()

    print("\nMETRICS SUMMARY")

    print(f"total calls: {summary['total_calls']}")
    print(f"successes: {summary['successes']}")
    print(f"errors: {summary['errors']}")
    print(f"rejected: {summary['rejected']}")
    print(f"timeouts: {summary['timeouts']}")
    print(f"blocked: {summary['blocked']}")
    print(f"total retries: {summary['total_retries']}")
    print(
        f"average latency: "
        f"{summary['average_latency_s']}"
    )
    print(
        f"max latency: "
        f"{summary['max_latency_s']}"
    )
    print(
        f"success rate: "
        f"{summary['success_rate']}"
    )
    print(
        f"error rate: "
        f"{summary['error_rate']}"
    )

    metrics.save()

    print("\nEVIDENCE")

    print("status: metrics saved")
    print("trace: traces/execution_metrics.json")


if __name__ == "__main__":
    main()