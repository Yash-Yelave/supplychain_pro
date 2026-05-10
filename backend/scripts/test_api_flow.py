from __future__ import annotations

import argparse
import time
from datetime import date, timedelta

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate procurement API lifecycle end-to-end.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--material", default="cement")
    parser.add_argument("--quantity", type=float, default=120.0)
    parser.add_argument("--unit", default="bag")
    parser.add_argument("--deadline-days", type=int, default=7)
    parser.add_argument("--timeout-s", type=int, default=120)
    parser.add_argument("--poll-interval-s", type=float, default=2.0)
    args = parser.parse_args()

    payload = {
        "material_type": args.material,
        "quantity": args.quantity,
        "unit": args.unit,
        "deadline": (date.today() + timedelta(days=args.deadline_days)).isoformat(),
    }
    create = requests.post(f"{args.base_url}/procurement/request", json=payload, timeout=20)
    create.raise_for_status()
    request_id = create.json()["request_id"]
    print("request_id:", request_id)

    started = time.time()
    last = None
    while time.time() - started < args.timeout_s:
        status_resp = requests.get(f"{args.base_url}/procurement/{request_id}/status", timeout=20)
        status_resp.raise_for_status()
        last = status_resp.json()
        print(
            "status:",
            last["pipeline_status"],
            "| agent:",
            last["current_agent"],
            "| quotations:",
            last["quotation_count"],
            "| trust_scores:",
            last["trust_score_count"],
        )
        if last["pipeline_status"] in ("complete", "failed"):
            break
        time.sleep(args.poll_interval_s)

    if not last or last["pipeline_status"] != "complete":
        raise RuntimeError(f"Pipeline did not complete successfully: {last}")

    results = requests.get(f"{args.base_url}/procurement/{request_id}/results", timeout=20)
    results.raise_for_status()
    body = results.json()
    print("ranked_suppliers:", len(body["ranked_suppliers"]))
    print("trust_scores:", len(body["trust_scores"]))
    print("extracted_quotations:", len(body["extracted_quotations"]))
    print("has_summary:", bool(body["analyst_summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
