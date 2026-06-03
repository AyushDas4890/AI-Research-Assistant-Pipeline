"""Writer agent.

Synthesises all extracted insights (plus any prior research context) into a
final, structured Markdown report, then persists it to long-term memory so
future runs on the same topic can build on it.
"""

from graph.state import ResearchState
from utils.helpers import call_llm_text, truncate
from utils.logger import get_logger
from memory.long_term import save_research
from memory.short_term import summarize_insights, summarize_sources, log_line

log = get_logger("writer")

SYSTEM_PROMPT_TEMPLATE = """You are an expert research writer. Synthesise the following research findings
into a comprehensive, well-structured report on: "{query}".

Use this Markdown structure:
# {query}
## Executive Summary
## Key Findings
### [Finding 1 heading]
### [Finding 2 heading]
...
## Analysis & Implications
## Gaps & Limitations
## Sources

Be thorough. Cite sources inline. The report should be publication-ready."""


def run_writer(state: ResearchState) -> dict:
    """Compile findings into a Markdown report and save it to memory."""
    query = state["query"]
    insights = state.get("extracted_insights") or []
    past_context = state.get("past_context", "") or ""
    gap_notes = state.get("gap_notes", "") or ""
    session_id = state.get("session_id", "")

    system = SYSTEM_PROMPT_TEMPLATE.format(query=query)

    context_block = "## Research Findings\n" + (
        summarize_insights(insights, max_chars=12000) or "(no insights extracted)"
    )
    context_block += "\n\n## Source List\n" + (summarize_sources(insights) or "(none)")
    if gap_notes.strip():
        context_block += f"\n\n## Known Gaps (from critic)\n{gap_notes}"
    if past_context.strip():
        context_block += (
            "\n\n## Prior Research (from earlier sessions — treat as background)\n"
            + truncate(past_context, 3000)
        )

    user = (
        "Write the report now using ONLY the findings below. Cite sources inline "
        "using their titles/URLs.\n\n" + context_block
    )

    try:
        report = call_llm_text(system, user, max_tokens=4096, temperature=0.3)
        if not report.strip():
            raise ValueError("empty report from model")
    except Exception as exc:
        log.error("Writer failed: %s", exc)
        # Graceful fallback: assemble a minimal report from raw insights.
        report = _fallback_report(query, insights)
        word_count = len(report.split())
        save_research(query, report, session_id)
        return {
            "final_report": report,
            "agent_log": [
                log_line("WRITER", f"LLM failed ({exc}); generated fallback report "
                          f"| {word_count} words | saved to memory")
            ],
            "error": f"writer: {exc}",
        }

    # Persist to long-term memory.
    save_research(query, report, session_id)

    word_count = len(report.split())
    entry = log_line(
        "WRITER", f"Report generated | {word_count:,} words | saved to memory"
    )
    log.info(entry)
    return {"final_report": report, "agent_log": [entry]}


def _fallback_report(query: str, insights: list) -> str:
    """Assemble a basic Markdown report when the LLM is unavailable."""
    lines = [f"# {query}", "", "## Key Findings", ""]
    if not insights:
        lines.append("_No insights were extracted for this topic._")
    for ins in insights:
        lines.append(f"### {ins.get('title', 'Untitled')}")
        for p in ins.get("key_points", []):
            lines.append(f"- {p}")
        url = ins.get("source_url", "")
        if url:
            lines.append(f"\nSource: {url}")
        lines.append("")
    lines.append("## Sources")
    lines.append(summarize_sources(insights) or "(none)")
    return "\n".join(lines)
