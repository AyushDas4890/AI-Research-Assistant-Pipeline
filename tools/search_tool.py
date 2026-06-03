"""Web search tool — wraps the Tavily Search API."""

import os

from tavily import TavilyClient

from utils.logger import get_logger

log = get_logger("search_tool")


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Tavily.

    Returns a list of ``{url, title, snippet, score}`` dicts. Never raises —
    on any failure it logs a warning and returns an empty list so the Searcher
    agent can degrade gracefully.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        log.warning("TAVILY_API_KEY not set; returning no results.")
        return []

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_raw_content=False,
        )
    except Exception as exc:
        log.error("Tavily search failed for %r: %s", query, exc)
        return []

    return [
        {
            "url": r.get("url", ""),
            "title": r.get("title", ""),
            "snippet": r.get("content", ""),
            "score": r.get("score", 0.0),
        }
        for r in response.get("results", [])
    ]
