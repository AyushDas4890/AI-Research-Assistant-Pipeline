"""Short-term memory helpers.

Short-term memory *is* the LangGraph ``ResearchState`` carried between nodes —
LangGraph handles the passing automatically. These helpers just keep the
in-graph state manipulation tidy and consistent: appending log lines, building
compact summaries of intermediate results for prompts, and deduplicating
search results by URL.
"""

from typing import List, Dict


def log_line(tag: str, message: str) -> str:
    """Format a single structured agent-log entry, e.g. ``[PLANNER] ...``."""
    return f"[{tag.upper()}] {message}"


def dedupe_by_url(results: List[Dict]) -> List[Dict]:
    """Remove duplicate search results, keeping the first occurrence per URL."""
    seen = set()
    unique = []
    for r in results:
        url = r.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        unique.append(r)
    return unique


def summarize_insights(insights: List[Dict], max_chars: int = 6000) -> str:
    """Build a compact text summary of extracted insights for prompts."""
    lines = []
    for ins in insights:
        title = ins.get("title", "Untitled")
        score = ins.get("relevance_score", 0.0)
        url = ins.get("source_url", "")
        points = ins.get("key_points", []) or []
        lines.append(f"### {title} (relevance {score:.2f})\n{url}")
        for p in points:
            lines.append(f"- {p}")
        lines.append("")
    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n…[truncated]"
    return text


def summarize_sources(insights: List[Dict]) -> str:
    """Build a deduplicated Markdown source list from insights."""
    seen = set()
    lines = []
    for ins in insights:
        url = ins.get("source_url", "")
        title = ins.get("title", url)
        if not url or url in seen:
            continue
        seen.add(url)
        lines.append(f"- [{title}]({url})")
    return "\n".join(lines)
