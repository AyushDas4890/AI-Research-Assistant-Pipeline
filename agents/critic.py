"""Critic agent.

Reviews the extracted insights against the original sub-questions and decides
whether significant coverage gaps remain. To prevent infinite loops, once
``retry_count`` has reached 2 the critic forces ``gaps_found = False``.
"""

from graph.state import ResearchState
from utils.helpers import call_llm_json
from utils.logger import get_logger
from memory.short_term import summarize_insights, log_line

log = get_logger("critic")

MAX_RETRIES = 2

SYSTEM_PROMPT_TEMPLATE = """You are a critical research reviewer. Review the following research insights
for the topic: "{query}".

Sub-questions that needed answering:
{sub_questions}

Extracted insights so far:
{extracted_insights_summary}

Decide: are there significant gaps? Are any sub-questions left unanswered?

Respond ONLY with valid JSON:
{{
  "gaps_found": true or false,
  "gap_notes": "description of what is missing, or empty string if none",
  "coverage_score": 0.0-1.0
}}"""


def run_critic(state: ResearchState) -> dict:
    """Assess coverage and decide whether to loop back to the Searcher."""
    query = state["query"]
    sub_questions = state.get("sub_questions") or []
    insights = state.get("extracted_insights") or []
    retry_count = state.get("retry_count", 0)

    sub_q_text = "\n".join(f"- {q}" for q in sub_questions) or "- (none)"
    summary = summarize_insights(insights) or "(no insights extracted)"
    system = SYSTEM_PROMPT_TEMPLATE.format(
        query=query,
        sub_questions=sub_q_text,
        extracted_insights_summary=summary,
    )

    default = {"gaps_found": False, "gap_notes": "", "coverage_score": 0.0}
    try:
        data = call_llm_json(system, "Provide your review now.", default=default)
        gaps_found = bool(data.get("gaps_found", False))
        gap_notes = str(data.get("gap_notes") or "")
        coverage = float(data.get("coverage_score", 0.0) or 0.0)
    except Exception as exc:
        log.error("Critic failed: %s", exc)
        gaps_found, gap_notes, coverage = False, "", 0.0

    # We are about to consume a retry if we loop, so the new count reflects this
    # pass. Force-stop once we've already retried MAX_RETRIES times.
    new_retry_count = retry_count + 1
    if retry_count >= MAX_RETRIES:
        gaps_found = False

    entry = log_line(
        "CRITIC",
        f"Coverage: {coverage:.2f} | gaps_found: {gaps_found} "
        f"| retry_count: {new_retry_count}",
    )
    log.info(entry)
    return {
        "gaps_found": gaps_found,
        "gap_notes": gap_notes,
        "retry_count": new_retry_count,
        "agent_log": [entry],
    }
