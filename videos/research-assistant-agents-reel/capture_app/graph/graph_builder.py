"""Capture-only stand-in for graph.graph_builder.

Replays one research run with the same node names and update shapes the real
LangGraph emits, so the unmodified app.py renders its real UI states without
API keys. Log lines and report text come from the project README/screenshots.
"""

import os
import time

STEP_DELAY = float(os.environ.get("CAPTURE_STEP_DELAY", "4"))
# Written when the writer "saves to memory"; memory/long_term.py lists the session once it exists.
SAVED_FLAG = os.path.join(os.path.dirname(__file__), "..", ".saved_session")

REPORT = """# Future of AI Coding Agents and Multimodal Models

## Executive Summary

The rapid evolution of artificial intelligence (AI) has introduced transformative technologies such as AI coding agents and multimodal models, which promise to revolutionize industries by enhancing productivity and enabling new capabilities. This report synthesizes current research findings to explore the future trajectory of these technologies, their integration into various sectors, and the implications of their development. Despite the potential benefits, there are significant gaps and limitations that need to be addressed to fully realize their potential.

## Key Findings

### Advancements in AI Coding Agents

AI coding agents have made significant strides in automating software development tasks. These agents leverage machine learning algorithms to understand and generate code, reducing the time and effort required for coding. The integration of AI coding agents into development workflows has shown potential in increasing efficiency and reducing human error, thereby accelerating the software development lifecycle.

### Multimodal Models Move Into Production

Multimodal models that combine text, images, audio and code are moving from research demos into production tools, opening new interfaces for search, analysis and creative work.

## Sources

1. arxiv.org — Agentic software engineering survey
2. github.blog — Copilot agent mode
3. openai.com — GPT-4o system card
"""

STEPS = [
    ("planner", {
        "sub_questions": [
            "How capable are today's AI coding agents on real software tasks?",
            "Where are multimodal models already used in production?",
            "What limits reliability and trust in agent-written code?",
            "Which research directions will shape the next two years?",
        ],
        "agent_log": ["[PLANNER] Generated 4 sub-questions | strategy: focused literature review"],
    }),
    ("searcher", {"search_results": [{}] * 18,
                  "agent_log": ["[SEARCHER] Found 18 unique results across 4 queries | retry: 0"]}),
    ("reader", {"extracted_insights": [{}] * 11,
                "agent_log": ["[READER] Extracted insights from 11/18 new sources | avg relevance: 0.73"]}),
    ("critic", {"gaps_found": True,
                "agent_log": ["[CRITIC] Coverage: 0.82 | gaps_found: True | retry_count: 1"]}),
    ("searcher", {"search_results": [{}] * 7,
                  "agent_log": ["[SEARCHER] Found 7 unique results across 2 queries | retry: 1"]}),
    ("reader", {"extracted_insights": [{}] * 16,
                "agent_log": ["[READER] Extracted insights from 5/7 new sources | avg relevance: 0.78"]}),
    ("critic", {"gaps_found": False,
                "agent_log": ["[CRITIC] Coverage: 0.94 | gaps_found: False | retry_count: 1"]}),
    ("writer", {"final_report": REPORT,
                "agent_log": ["[WRITER] Report generated | 1,842 words | saved to memory"]}),
]


class _ReplayGraph:
    def stream(self, state, stream_mode="updates"):
        for node, update in STEPS:
            time.sleep(STEP_DELAY)
            if node == "writer":
                open(SAVED_FLAG, "w").close()
            yield {node: update}


def build_graph():
    return _ReplayGraph()
