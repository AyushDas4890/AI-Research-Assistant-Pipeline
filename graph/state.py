"""Shared graph state.

``ResearchState`` is the single typed object that LangGraph threads through
every node in the agent graph. Each agent reads the keys it needs and writes
back the keys it produces. This file has no dependencies on any other project
module, so it is built first — everything imports from here.
"""

from typing import TypedDict, List, Optional, Annotated
import operator


class ResearchState(TypedDict):
    # ----- Input -----
    query: str                          # Original user research topic
    session_id: str                     # Unique ID per research run

    # ----- Planner output -----
    sub_questions: List[str]            # Focused sub-questions to research
    search_strategy: str                # Brief strategy note from planner

    # ----- Searcher output -----
    # Raw results: [{url, title, snippet, score, query}]
    search_results: List[dict]

    # ----- Reader output -----
    # [{source_url, title, key_points: List[str], relevance_score}]
    extracted_insights: List[dict]

    # ----- Critic output -----
    gaps_found: bool                    # Whether critic found coverage gaps
    gap_notes: str                      # What's missing
    retry_count: int                    # How many times we've looped back

    # ----- Writer output -----
    final_report: str                   # Markdown report string

    # ----- Memory -----
    past_context: str                   # Retrieved from ChromaDB for this topic

    # ----- Metadata -----
    # Append-only log of agent steps. The ``operator.add`` reducer means every
    # node *appends* its entries instead of overwriting the list.
    agent_log: Annotated[List[str], operator.add]
    error: Optional[str]                # Error message if any agent fails
