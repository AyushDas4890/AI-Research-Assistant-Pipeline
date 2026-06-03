"""LangGraph StateGraph assembly.

Wires the five agents into a stateful graph:

    planner → searcher → reader → critic ─┬─(gaps & retries left)→ searcher
                                          └─(done)──────────────→ writer → END
"""

from langgraph.graph import StateGraph, END

from graph.state import ResearchState
from graph.edges import route_after_critic
from agents.planner import run_planner
from agents.searcher import run_searcher
from agents.reader import run_reader
from agents.critic import run_critic
from agents.writer import run_writer


def build_graph():
    """Build and compile the research agent graph."""
    graph = StateGraph(ResearchState)

    # Register nodes
    graph.add_node("planner", run_planner)
    graph.add_node("searcher", run_searcher)
    graph.add_node("reader", run_reader)
    graph.add_node("critic", run_critic)
    graph.add_node("writer", run_writer)

    # Linear flow
    graph.set_entry_point("planner")
    graph.add_edge("planner", "searcher")
    graph.add_edge("searcher", "reader")
    graph.add_edge("reader", "critic")

    # Conditional edge: critic → searcher (retry) OR writer (done)
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "searcher": "searcher",
            "writer": "writer",
        },
    )

    graph.add_edge("writer", END)

    return graph.compile()
