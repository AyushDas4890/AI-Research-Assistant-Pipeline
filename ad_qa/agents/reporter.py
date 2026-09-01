"""Reporter agent.

Aggregates every ad's issues into a final status (FAIL beats WARN beats
PASS), then renders both a Markdown summary report and a flat list of rows
suitable for writing straight to CSV.
"""

from ad_qa.state import AdQAState
from memory.short_term import log_line
from utils.logger import get_logger

log = get_logger("ad_qa.reporter")

_SEVERITY_RANK = {"FAIL": 2, "WARN": 1}


def _overall_status(issues: list) -> str:
    if any(i["severity"] == "FAIL" for i in issues):
        return "FAIL"
    if any(i["severity"] == "WARN" for i in issues):
        return "WARN"
    return "PASS"


def run_reporter(state: AdQAState) -> dict:
    results = state.get("ad_results") or []

    for ad in results:
        ad["status"] = _overall_status(ad["issues"])

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for ad in results:
        counts[ad["status"]] += 1

    lines = [
        "# Ad QA Report",
        "",
        f"**{len(results)} ad(s) reviewed** — "
        f"{counts['PASS']} pass, {counts['WARN']} warn, {counts['FAIL']} fail.",
        "",
    ]

    # Worst-first ordering so failing ads surface at the top.
    ordered = sorted(
        results,
        key=lambda a: (-_SEVERITY_RANK.get(a["status"], 0), a["ad_id"]),
    )

    for ad in ordered:
        badge = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[ad["status"]]
        lines.append(f"## {badge} {ad['ad_id']} — {ad['status']} ({ad['platform']})")
        lines.append(f"- Headline: {ad['headline'] or '_(none)_'}")
        lines.append(f"- Body: {ad['body_copy'] or '_(none)_'}")
        lines.append(f"- Destination: {ad['destination_url'] or '_(none)_'}")
        if not ad["issues"]:
            lines.append("- No issues found.")
        else:
            for issue in sorted(ad["issues"], key=lambda i: -_SEVERITY_RANK.get(i["severity"], 0)):
                lines.append(f"- **[{issue['severity']}]** ({issue['check']}) {issue['message']}")
        lines.append("")

    report_md = "\n".join(lines)

    csv_rows = []
    for ad in ordered:
        csv_rows.append({
            "ad_id": ad["ad_id"],
            "platform": ad["platform"],
            "status": ad["status"],
            "issue_count": len(ad["issues"]),
            "issues": " | ".join(f"[{i['severity']}/{i['check']}] {i['message']}" for i in ad["issues"]),
        })

    entry = log_line(
        "REPORTER",
        f"Report built: {counts['PASS']} pass / {counts['WARN']} warn / {counts['FAIL']} fail.",
    )
    log.info(entry)
    return {"report_md": report_md, "report_csv_rows": csv_rows, "ad_results": results, "agent_log": [entry]}
