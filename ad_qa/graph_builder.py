"""LangGraph StateGraph assembly for the Ad QA pipeline.

Linear pipeline -- unlike the research graph there's no retry loop here, each
check is independent and simply adds its own findings to every ad:

    ingestor -> link_checker -> image_qa -> copy_compliance -> policy_compliance -> reporter -> END
"""

from langgraph.graph import StateGraph, END

from ad_qa.state import AdQAState
from ad_qa.agents.ingestor import run_ingestor
from ad_qa.agents.link_checker import run_link_checker
from ad_qa.agents.image_qa import run_image_qa
from ad_qa.agents.copy_compliance import run_copy_compliance
from ad_qa.agents.policy_compliance import run_policy_compliance
from ad_qa.agents.reporter import run_reporter


def build_ad_qa_graph():
    """Build and compile the ad QA agent graph."""
    graph = StateGraph(AdQAState)

    graph.add_node("ingestor", run_ingestor)
    graph.add_node("link_checker", run_link_checker)
    graph.add_node("image_qa", run_image_qa)
    graph.add_node("copy_compliance", run_copy_compliance)
    graph.add_node("policy_compliance", run_policy_compliance)
    graph.add_node("reporter", run_reporter)

    graph.set_entry_point("ingestor")
    graph.add_edge("ingestor", "link_checker")
    graph.add_edge("link_checker", "image_qa")
    graph.add_edge("image_qa", "copy_compliance")
    graph.add_edge("copy_compliance", "policy_compliance")
    graph.add_edge("policy_compliance", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()
