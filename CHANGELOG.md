# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-06-04

### Added
- Five-agent LangGraph pipeline: Planner → Searcher → Reader → Critic → Writer.
- Conditional critic retry loop (max 2) with gap-targeted re-search.
- Dual-layer memory: LangGraph typed state (short-term) + ChromaDB (long-term).
- Tool layer: Tavily web search, BeautifulSoup URL fetcher, vector memory.
- FastAPI backend (`server.py`) streaming live agent progress over SSE.
- Modern single-page web UI (`web/`) — animated pipeline tracker, live console,
  Markdown report, session history.
- CLI runner (`main.py`) and legacy Streamlit UI (`app.py`).
- Graceful error handling across every layer.
