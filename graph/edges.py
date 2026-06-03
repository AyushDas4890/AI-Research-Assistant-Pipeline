"""Conditional routing logic for the agent graph."""

from graph.state import ResearchState

MAX_RETRIES = 2


def route_after_critic(state: ResearchState) -> str:
    """Decide where to go after the Critic runs.

    Route back to ``searcher`` if the critic found gaps and we still have
    retries remaining; otherwise proceed to ``writer``.
    """
    if state.get("gaps_found") and state.get("retry_count", 0) < MAX_RETRIES:
        return "searcher"
    return "writer"
