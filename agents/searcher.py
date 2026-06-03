"""Searcher agent.

Runs a Tavily web search for each sub-question and collects raw results,
deduplicated by URL. On a retry loop from the Critic it uses ``gap_notes`` to
run additional targeted searches and *appends* to the existing results rather
than replacing them.
"""

from graph.state import ResearchState
from tools.search_tool import search_web
from memory.short_term import dedupe_by_url, log_line
from utils.logger import get_logger

log = get_logger("searcher")


def run_searcher(state: ResearchState) -> dict:
    """Search the web for every sub-question (plus gap-driven queries on retry)."""
    sub_questions = state.get("sub_questions") or []
    existing = state.get("search_results") or []
    gap_notes = state.get("gap_notes", "") or ""
    retry_count = state.get("retry_count", 0)
    is_retry = retry_count > 0 and bool(gap_notes.strip())

    # Build the list of queries to run this pass.
    queries = list(sub_questions)
    if is_retry:
        # Targeted follow-up searches derived from the critic's gap notes.
        queries = [gap_notes] + [f"{q} {gap_notes}" for q in sub_questions[:2]]

    new_results = []
    try:
        for q in queries:
            for r in search_web(q, max_results=5):
                r = dict(r)
                r["query"] = q
                new_results.append(r)
    except Exception as exc:
        log.error("Searcher failed: %s", exc)
        return {
            "agent_log": [log_line("SEARCHER", f"Failed ({exc}); kept prior results.")],
            "error": f"searcher: {exc}",
        }

    # Merge with any existing results (retry appends, first pass starts fresh).
    merged = dedupe_by_url(existing + new_results)

    entry = log_line(
        "SEARCHER",
        f"Found {len(merged)} unique results across {len(queries)} queries "
        f"| retry: {retry_count}",
    )
    log.info(entry)
    return {"search_results": merged, "agent_log": [entry]}
