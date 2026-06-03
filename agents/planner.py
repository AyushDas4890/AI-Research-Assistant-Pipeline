"""Planner agent.

Decomposes the raw user query into 3-5 focused sub-questions and a short search
strategy. If long-term memory holds prior research on a similar topic, that
context is injected into the prompt so the plan builds on what's already known.
"""

from graph.state import ResearchState
from utils.helpers import call_llm_json, truncate
from utils.logger import get_logger
from memory.short_term import log_line

log = get_logger("planner")

SYSTEM_PROMPT = """You are a research planner. Your job is to decompose a research topic into
3-5 focused sub-questions that, when answered together, will provide comprehensive
coverage of the topic. Also provide a one-sentence search strategy.

You must respond ONLY with a valid JSON object matching this schema:
{
  "sub_questions": ["question 1", "question 2", ...],
  "search_strategy": "brief strategy string"
}
No markdown, no preamble, no explanation outside the JSON."""


def run_planner(state: ResearchState) -> dict:
    """Generate sub-questions and a search strategy for the query."""
    query = state["query"]
    past_context = state.get("past_context", "") or ""

    user = f'Research topic: "{query}"'
    if past_context.strip():
        user += (
            "\n\nRelevant prior research from past sessions (use it to avoid "
            "re-treading old ground and to sharpen the new sub-questions):\n"
            + truncate(past_context, 3000)
        )

    default = {
        "sub_questions": [query],
        "search_strategy": "Broad single-query search (planner fallback).",
    }

    try:
        data = call_llm_json(SYSTEM_PROMPT, user, default=default)
        sub_questions = data.get("sub_questions") or default["sub_questions"]
        # Defensive: ensure it's a list of non-empty strings.
        sub_questions = [str(q).strip() for q in sub_questions if str(q).strip()]
        if not sub_questions:
            sub_questions = default["sub_questions"]
        strategy = str(data.get("search_strategy") or default["search_strategy"])
    except Exception as exc:
        log.error("Planner failed: %s", exc)
        return {
            "sub_questions": default["sub_questions"],
            "search_strategy": default["search_strategy"],
            "agent_log": [log_line("PLANNER", f"Failed ({exc}); used fallback plan.")],
            "error": f"planner: {exc}",
        }

    entry = log_line(
        "PLANNER",
        f"Generated {len(sub_questions)} sub-questions | strategy: {strategy}",
    )
    log.info(entry)
    return {
        "sub_questions": sub_questions,
        "search_strategy": strategy,
        "agent_log": [entry],
    }
