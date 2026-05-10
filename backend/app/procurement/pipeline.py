from __future__ import annotations

from sqlalchemy.orm import Session

from app.procurement.agents import analyst_agent, discovery_agent, extraction_agent, scoring_agent, supervisor_agent
from app.procurement.scoring import TrustScoreWeights
from app.procurement.state import ProcurementState


def run_sequential(state: ProcurementState, *, db: Session, weights: TrustScoreWeights | None = None) -> ProcurementState:
    """
    Minimal orchestration without LangGraph (fallback + easy unit testing).
    """

    state = supervisor_agent(state, db=db)
    state = discovery_agent(state, db=db)
    state = extraction_agent(state, db=db)
    state = scoring_agent(state, db=db, weights=weights)
    state = analyst_agent(state, db=db)
    return state


def run_langgraph(state: ProcurementState, *, db: Session, weights: TrustScoreWeights | None = None) -> ProcurementState:
    """
    LangGraph orchestration (sequential graph).

    Note: `langgraph` is an optional dependency; install it to use this runner.
    """

    try:
        from langgraph.graph import END, StateGraph  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("LangGraph is not installed. Add `langgraph` to your environment to use run_langgraph().") from exc

    graph = StateGraph(ProcurementState)

    graph.add_node("supervisor", lambda s: supervisor_agent(s, db=db))
    graph.add_node("discovery", lambda s: discovery_agent(s, db=db))
    graph.add_node("extraction", lambda s: extraction_agent(s, db=db))
    graph.add_node("scoring", lambda s: scoring_agent(s, db=db, weights=weights))
    graph.add_node("analyst", lambda s: analyst_agent(s, db=db))

    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "discovery")
    graph.add_edge("discovery", "extraction")
    graph.add_edge("extraction", "scoring")
    graph.add_edge("scoring", "analyst")
    graph.add_edge("analyst", END)

    app = graph.compile()
    return app.invoke(state)


def run_sequential_from_existing_request(
    state: ProcurementState,
    *,
    db: Session,
    weights: TrustScoreWeights | None = None,
) -> ProcurementState:
    """
    Continue pipeline for an already persisted request.
    """

    state = discovery_agent(state, db=db)
    state = extraction_agent(state, db=db)
    state = scoring_agent(state, db=db, weights=weights)
    state = analyst_agent(state, db=db)
    return state


def run_langgraph_from_existing_request(
    state: ProcurementState,
    *,
    db: Session,
    weights: TrustScoreWeights | None = None,
) -> ProcurementState:
    """
    LangGraph pipeline for an already persisted request.
    """

    try:
        from langgraph.graph import END, StateGraph  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "LangGraph is not installed. Add `langgraph` to your environment to use run_langgraph_from_existing_request()."
        ) from exc

    graph = StateGraph(ProcurementState)
    graph.add_node("discovery", lambda s: discovery_agent(s, db=db))
    graph.add_node("extraction", lambda s: extraction_agent(s, db=db))
    graph.add_node("scoring", lambda s: scoring_agent(s, db=db, weights=weights))
    graph.add_node("analyst", lambda s: analyst_agent(s, db=db))

    graph.set_entry_point("discovery")
    graph.add_edge("discovery", "extraction")
    graph.add_edge("extraction", "scoring")
    graph.add_edge("scoring", "analyst")
    graph.add_edge("analyst", END)

    app = graph.compile()
    return app.invoke(state)
