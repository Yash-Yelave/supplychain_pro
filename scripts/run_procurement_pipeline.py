from __future__ import annotations

import argparse
from datetime import date, timedelta

from sqlalchemy import func, select

from app.db.context import session_scope
from app.models.procurement_request import ProcurementRequest
from app.models.quotation import Quotation
from app.models.report import Report
from app.models.trust_score import TrustScore
from app.procurement.pipeline import run_langgraph, run_sequential
from app.procurement.state import ProcurementRequestInput, ProcurementState


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the end-to-end multi-agent procurement pipeline.")
    parser.add_argument("--material", default="cement")
    parser.add_argument("--quantity", type=float, default=100)
    parser.add_argument("--unit", default="bag")
    parser.add_argument("--deadline-days", type=int, default=7)
    parser.add_argument("--langgraph", action="store_true", help="Use LangGraph orchestration (requires langgraph installed).")
    args = parser.parse_args()

    state = ProcurementState(
        request=ProcurementRequestInput(
            material_type=args.material.strip().lower(),
            quantity=float(args.quantity),
            unit=args.unit.strip(),
            deadline=date.today() + timedelta(days=int(args.deadline_days)),
        )
    )

    with session_scope() as db:
        if args.langgraph:
            state = run_langgraph(state, db=db)
        else:
            state = run_sequential(state, db=db)

        if state.request_id is None:
            raise RuntimeError("Pipeline finished without request_id")

        req = db.get(ProcurementRequest, state.request_id)
        q_count = db.scalar(select(func.count()).select_from(Quotation).where(Quotation.request_id == state.request_id))
        ts_count = db.scalar(select(func.count()).select_from(TrustScore).where(TrustScore.request_id == state.request_id))
        report = db.scalar(select(Report).where(Report.request_id == state.request_id))

        print("\n=== PIPELINE STATE ===")
        print("request_id:", state.request_id)
        print("status:", state.status)
        print("suppliers:", len(state.suppliers))
        print("quotations:", len(state.extracted_quotations))
        print("trust_scores:", len(state.trust_scores))
        print("report_id:", report.id if report else None)

        print("\n=== TRANSITION LOG ===")
        for entry in state.logs:
            print(f"{entry.ts_utc.isoformat()} | {entry.agent:<10} | {entry.event} | {entry.detail}")

        print("\n=== DB VERIFY ===")
        print("request_status:", req.status if req else None)
        print("quotation_rows:", q_count)
        print("trust_score_rows:", ts_count)
        print("report_row:", bool(report))

        if report:
            print("\n=== REPORT SUMMARY ===")
            print(report.summary_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
