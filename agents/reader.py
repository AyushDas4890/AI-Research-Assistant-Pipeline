"""Reader agent.

Fetches each search-result URL, reads the content, and extracts structured
insights via the LLM. Articles scoring below the relevance threshold (0.4) are
discarded. Already-processed URLs are skipped so retries don't re-read sources.
"""

from graph.state import ResearchState
from tools.fetch_tool import fetch_url
from utils.helpers import call_llm_json, truncate
from utils.logger import get_logger
from memory.short_term import log_line

log = get_logger("reader")

RELEVANCE_THRESHOLD = 0.4

SYSTEM_PROMPT_TEMPLATE = """You are a research analyst. Extract the most important insights from this article
relevant to the research topic: "{query}".

Respond ONLY with a valid JSON object:
{{
  "title": "article title",
  "key_points": ["point 1", "point 2", "point 3"],
  "relevance_score": 0.0-1.0
}}
Skip articles with relevance_score below 0.4.
No markdown, no preamble."""


def run_reader(state: ResearchState) -> dict:
    """Fetch and extract insights from every (new) search result."""
    query = state["query"]
    search_results = state.get("search_results") or []
    existing = state.get("extracted_insights") or []
    already_read = {ins.get("source_url") for ins in existing}

    system = SYSTEM_PROMPT_TEMPLATE.format(query=query)
    insights = list(existing)
    scores = []
    processed = 0

    for result in search_results:
        url = result.get("url")
        if not url or url in already_read:
            continue
        processed += 1

        content = fetch_url(url, max_chars=4000)
        if not content:
            continue  # fetch failed/empty — skip silently

        user = (
            f"Article URL: {url}\n\nArticle content:\n{truncate(content, 4000)}"
        )
        default = {"title": result.get("title", url), "key_points": [], "relevance_score": 0.0}
        try:
            data = call_llm_json(system, user, default=default)
            score = float(data.get("relevance_score", 0.0) or 0.0)
        except Exception as exc:
            log.warning("Reader extraction failed for %s: %s", url, exc)
            continue

        if score < RELEVANCE_THRESHOLD:
            continue

        key_points = data.get("key_points") or []
        key_points = [str(p).strip() for p in key_points if str(p).strip()]
        if not key_points:
            continue

        insights.append(
            {
                "source_url": url,
                "title": str(data.get("title") or result.get("title") or url),
                "key_points": key_points,
                "relevance_score": score,
            }
        )
        already_read.add(url)
        scores.append(score)

    avg = sum(scores) / len(scores) if scores else 0.0
    entry = log_line(
        "READER",
        f"Extracted insights from {len(scores)}/{processed} new sources "
        f"| total insights: {len(insights)} | avg relevance: {avg:.2f}",
    )
    log.info(entry)
    return {"extracted_insights": insights, "agent_log": [entry]}
