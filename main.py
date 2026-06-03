"""CLI entry point for the AI Research Assistant pipeline.

Usage:
    python main.py
    # then type a research topic when prompted
"""

import uuid

from dotenv import load_dotenv

from graph.graph_builder import build_graph
from memory.long_term import retrieve_past_research
from utils.logger import get_logger

load_dotenv()
log = get_logger("main")


def initial_state(query: str) -> dict:
    """Construct a fresh ResearchState dict for a run."""
    session_id = str(uuid.uuid4())
    return {
        "query": query,
        "session_id": session_id,
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


def run_research(query: str) -> dict:
    """Run the full agent graph for a query and return the final state.

    The entire invocation is wrapped so a failure in any agent surfaces as an
    error field rather than an unhandled crash.
    """
    graph = build_graph()
    state = initial_state(query)

    try:
        result = graph.invoke(state)
    except Exception as exc:  # last-resort safety net
        log.error("Graph invocation failed: %s", exc)
        state["error"] = str(exc)
        state["final_report"] = (
            f"# {query}\n\n_Research could not be completed due to an error: {exc}_"
        )
        return state

    return result


if __name__ == "__main__":
    query = input("Enter research topic: ").strip()
    if not query:
        print("No topic entered. Exiting.")
        raise SystemExit(0)

    result = run_research(query)

    print("\n" + "=" * 60)
    print(result.get("final_report", "(no report produced)"))
    print("=" * 60)

    if result.get("past_context"):
        print("\n[memory] Prior research was found and used for this run.")

    print("\nAgent log:\n" + "\n".join(result.get("agent_log", [])))

    if result.get("error"):
        print(f"\n[!] Completed with error: {result['error']}")
