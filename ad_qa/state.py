"""Shared state for the Ad QA pipeline.

Mirrors ``graph/state.py``'s approach: one typed dict threaded through every
node. Each agent reads ``ads`` (and the ``ad_results`` produced so far) and
returns an updated ``ad_results`` list with its own check appended per ad.
"""

from typing import TypedDict, List, Optional, Annotated
import operator


class AdQAState(TypedDict):
    # ----- Input -----
    ads: List[dict]                     # Raw ad records loaded from CSV/JSON
    session_id: str

    # ----- Per-ad findings -----
    # One entry per ad:
    #   {
    #     "ad_id": str, "platform": str, "headline": str, "body_copy": str,
    #     "cta": str, "destination_url": str, "image_url": str,
    #     "checks": {"link": {...}, "image": {...}, "copy": {...}, "policy": {...}},
    #     "issues": [{"check": str, "severity": "FAIL"|"WARN", "message": str}],
    #     "status": "PASS"|"WARN"|"FAIL",
    #   }
    ad_results: List[dict]

    # ----- Reporter output -----
    report_md: str
    report_csv_rows: List[dict]

    # ----- Metadata -----
    # Append-only log of agent steps (same ``operator.add`` pattern as the
    # research pipeline: every node appends instead of overwriting).
    agent_log: Annotated[List[str], operator.add]
    error: Optional[str]
