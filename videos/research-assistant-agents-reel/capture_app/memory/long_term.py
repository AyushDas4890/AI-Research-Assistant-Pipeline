"""Capture-only stand-in for memory.long_term (no ChromaDB needed).

Lists the replayed session only after the replay graph's writer step has run,
so the sidebar shows real "saved to memory" behaviour on the next page load.
"""

import os

from graph.graph_builder import REPORT, SAVED_FLAG


def retrieve_past_research(query):
    return ""


def list_sessions():
    if not os.path.exists(SAVED_FLAG):
        return []
    return [{"id": "s1", "query": "Future of AI coding agents and multimodal models",
             "timestamp": "2026-10-05T11:20:00", "report": REPORT}]
