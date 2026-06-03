"""FastAPI backend for the AI Research Assistant.

Exposes the LangGraph agent pipeline over HTTP and streams each agent's
progress to the browser in real time using Server-Sent Events (SSE).

Run with:
    uvicorn server:app --reload
    # then open http://localhost:8000
"""

import json
import time
import uuid
import queue
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from graph.graph_builder import build_graph
from memory.long_term import retrieve_past_research, list_sessions
from utils.logger import get_logger

load_dotenv()
log = get_logger("server")

BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="AI Research Assistant", version="1.0.0")

# Human-friendly labels for each pipeline node.
AGENT_META = {
    "planner":  {"label": "Planner",  "desc": "Decomposing the topic"},
    "searcher": {"label": "Searcher", "desc": "Searching the web"},
    "reader":   {"label": "Reader",   "desc": "Extracting insights"},
    "critic":   {"label": "Critic",   "desc": "Checking coverage"},
    "writer":   {"label": "Writer",   "desc": "Writing the report"},
}


def _fresh_state(query: str) -> dict:
    return {
        "query": query,
        "session_id": str(uuid.uuid4()),
        "sub_questions": [],
        "search_strategy": "",
        "search_results": [],
        "extracted_insights": [],
        "gaps_found": False,
        "gap_notes": "",
        "retry_count": 0,
        "final_report": "",
        "past_context": retrieve_past_research(query),
        "agent_log": [],
        "error": None,
    }


def _sse(event: str, data: dict) -> str:
    """Format a single Server-Sent Event frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _summarize_update(node: str, update: dict) -> dict:
    """Pull the UI-relevant bits out of a node's state update."""
    out = {"node": node, **AGENT_META.get(node, {"label": node, "desc": ""})}
    if node == "planner":
        out["sub_questions"] = update.get("sub_questions", []) or []
        out["strategy"] = update.get("search_strategy", "")
    elif node == "searcher":
        out["results"] = len(update.get("search_results", []) or [])
    elif node == "reader":
        out["insights"] = len(update.get("extracted_insights", []) or [])
    elif node == "critic":
        out["gaps_found"] = bool(update.get("gaps_found"))
        out["retry_count"] = update.get("retry_count", 0)
    elif node == "writer":
        out["words"] = len((update.get("final_report", "") or "").split())
    out["log"] = update.get("agent_log", []) or []
    return out


def _event_stream(query: str):
    """Generator that runs the graph and yields SSE frames as agents finish."""
    start = time.time()
    try:
        graph = build_graph()
        state = _fresh_state(query)
    except Exception as exc:
        yield _sse("error", {"message": f"Failed to initialise pipeline: {exc}"})
        return

    yield _sse("start", {
        "query": query,
        "has_memory": bool(state.get("past_context")),
        "agents": [{"node": k, **v} for k, v in AGENT_META.items()],
    })

    final_report = ""
    full_log: list[str] = []

    try:
        for step in graph.stream(state, stream_mode="updates"):
            for node, update in step.items():
                summary = _summarize_update(node, update)
                full_log.extend(summary.get("log", []))
                if node == "writer":
                    final_report = update.get("final_report", "") or final_report
                yield _sse("agent", summary)
    except Exception as exc:
        log.error("Stream failed: %s", exc)
        yield _sse("error", {"message": str(exc)})
        return

    elapsed = round(time.time() - start, 1)
    yield _sse("done", {
        "report": final_report,
        "log": full_log,
        "elapsed": elapsed,
    })


@app.get("/api/research/stream")
def research_stream(query: str):
    """SSE endpoint: streams live agent progress for a research query."""
    if not query or not query.strip():
        return JSONResponse({"error": "query is required"}, status_code=400)
    return StreamingResponse(
        _event_stream(query.strip()),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/sessions")
def sessions():
    """Return past research sessions (newest first) for the history panel."""
    data = list_sessions()
    # Trim the heavy report body out of the list payload.
    return [
        {"id": s["id"], "query": s["query"], "timestamp": s["timestamp"]}
        for s in data
    ]


@app.get("/api/report/{session_id}")
def report(session_id: str):
    """Return the full saved report for one session."""
    for s in list_sessions():
        if s["id"] == session_id:
            return {"id": s["id"], "query": s["query"],
                    "timestamp": s["timestamp"], "report": s["report"]}
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


# Serve CSS/JS assets.
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
