"""Streamlit UI for the AI Research Assistant.

Run with:
    streamlit run app.py

Shows the agent graph executing in real time (live agent log + per-agent
intermediate outputs), renders the final Markdown report, and lists past
research sessions pulled from ChromaDB.
"""

import time
import uuid

import streamlit as st
from dotenv import load_dotenv

from graph.graph_builder import build_graph
from memory.long_term import retrieve_past_research, list_sessions

load_dotenv()

GRAPH_DIAGRAM = """```
User Query
    │
    ▼
 [Planner]  → sub-questions + strategy
    │
    ▼
 [Searcher] → web search (Tavily)
    │
    ▼
 [Reader]   → fetch + extract insights
    │
    ▼
 [Critic]   → gaps? ──(retry ≤2)──► Searcher
    │ (satisfied)
    ▼
 [Writer]   → final report → memory
    │
    ▼
   END
```"""

AGENT_LABELS = {
    "planner": "🧭 Planner — decomposing the topic",
    "searcher": "🔎 Searcher — searching the web",
    "reader": "📖 Reader — extracting insights",
    "critic": "🧪 Critic — checking coverage",
    "writer": "✍️ Writer — synthesising the report",
}


def fresh_state(query: str) -> dict:
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


# --------------------------------------------------------------------------- #
# Page config
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="AI Research Assistant", page_icon="🔬", layout="wide")
st.title("🔬 AI Research Assistant")
st.caption("Multi-Agent Pipeline · LangGraph + OpenAI + Tool Calling + Memory")

# Session-state defaults
if "report" not in st.session_state:
    st.session_state.report = None
if "agent_log" not in st.session_state:
    st.session_state.agent_log = []
if "run_time" not in st.session_state:
    st.session_state.run_time = None

# --------------------------------------------------------------------------- #
# Sidebar: architecture + history
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.subheader("Agent Graph")
    st.markdown(GRAPH_DIAGRAM)

    st.divider()
    st.subheader("Past Sessions")
    sessions = list_sessions()
    if not sessions:
        st.caption("No past research yet. Run a topic to build memory.")
    else:
        for s in sessions:
            label = s["query"] or "(untitled)"
            ts = (s.get("timestamp") or "")[:19].replace("T", " ")
            if st.button(f"📄 {label}", key=f"sess_{s['id']}", help=ts):
                st.session_state.report = s["report"]
                st.session_state.agent_log = ["[MEMORY] Loaded saved report."]
                st.session_state.run_time = None

# --------------------------------------------------------------------------- #
# Main: input
# --------------------------------------------------------------------------- #
query = st.text_input(
    "Research topic", placeholder="e.g. The impact of LLM agents on software engineering"
)
run = st.button("🚀 Run Research", type="primary", disabled=not query.strip())

if run and query.strip():
    st.session_state.report = None
    st.session_state.agent_log = []
    start = time.time()

    graph = build_graph()
    state = fresh_state(query.strip())

    if state.get("past_context"):
        st.info("🧠 Prior research found in memory — it will inform this run.")

    log_box = st.empty()
    collected_log: list[str] = []

    with st.status("Running agent pipeline…", expanded=True) as status:
        try:
            for step in graph.stream(state, stream_mode="updates"):
                # Each step is {node_name: partial_state_update}
                for node, update in step.items():
                    status.update(label=AGENT_LABELS.get(node, node))

                    # Append this node's log lines.
                    for line in update.get("agent_log", []) or []:
                        collected_log.append(line)
                    log_box.code("\n".join(collected_log) or "…", language="text")

                    # Per-agent intermediate outputs.
                    if node == "planner":
                        sqs = update.get("sub_questions", [])
                        if sqs:
                            st.markdown("**Planner — sub-questions:**")
                            st.markdown("\n".join(f"- {q}" for q in sqs))
                    elif node == "searcher":
                        n = len(update.get("search_results", []) or [])
                        st.markdown(f"**Searcher —** {n} unique results collected.")
                    elif node == "reader":
                        n = len(update.get("extracted_insights", []) or [])
                        st.markdown(f"**Reader —** {n} insights extracted.")
                    elif node == "critic":
                        gaps = update.get("gaps_found")
                        verdict = "gaps found → re-searching" if gaps else "coverage OK"
                        st.markdown(f"**Critic —** verdict: {verdict}")
                    elif node == "writer":
                        st.session_state.report = update.get("final_report", "")

            status.update(label="✅ Research complete", state="complete")
        except Exception as exc:
            status.update(label="❌ Pipeline failed", state="error")
            st.error(f"Pipeline error: {exc}")

    st.session_state.agent_log = collected_log
    st.session_state.run_time = time.time() - start

# --------------------------------------------------------------------------- #
# Results
# --------------------------------------------------------------------------- #
if st.session_state.agent_log:
    with st.expander("Agent log", expanded=False):
        st.code("\n".join(st.session_state.agent_log), language="text")

if st.session_state.run_time is not None:
    st.caption(f"⏱️ Total run time: {st.session_state.run_time:.1f}s")

if st.session_state.report:
    st.divider()
    st.markdown(st.session_state.report)
    st.download_button(
        "⬇️ Download report (.md)",
        data=st.session_state.report,
        file_name="research_report.md",
        mime="text/markdown",
    )
