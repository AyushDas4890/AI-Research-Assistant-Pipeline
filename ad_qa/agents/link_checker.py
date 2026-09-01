"""Link Checker agent.

Verifies each ad's destination URL actually loads. FAIL on a dead link or
timeout, WARN on an unexpectedly long redirect chain or slow response.
"""

from ad_qa.state import AdQAState
from ad_qa.tools.link_tool import check_url
from memory.short_term import log_line
from utils.logger import get_logger

log = get_logger("ad_qa.link_checker")

SLOW_MS = 3000
MANY_REDIRECTS = 2


def run_link_checker(state: AdQAState) -> dict:
    results = state.get("ad_results") or []
    fail_count = 0

    for ad in results:
        url = ad.get("destination_url", "")
        try:
            check = check_url(url)
        except Exception as exc:  # last-resort safety net, tool already traps errors
            check = {"ok": False, "status_code": None, "final_url": None,
                      "redirect_count": 0, "latency_ms": None, "error": str(exc)}

        ad["checks"]["link"] = check

        if not check["ok"]:
            ad["issues"].append({
                "check": "link", "severity": "FAIL",
                "message": f"Destination URL failed: {check.get('error') or 'unknown error'}",
            })
            fail_count += 1
        else:
            if check.get("redirect_count", 0) > MANY_REDIRECTS:
                ad["issues"].append({
                    "check": "link", "severity": "WARN",
                    "message": f"{check['redirect_count']} redirects before landing "
                                f"on {check['final_url']}",
                })
            if (check.get("latency_ms") or 0) > SLOW_MS:
                ad["issues"].append({
                    "check": "link", "severity": "WARN",
                    "message": f"Landing page took {check['latency_ms']:.0f}ms to respond",
                })

    entry = log_line("LINK_CHECKER", f"Checked {len(results)} URL(s); {fail_count} broken.")
    log.info(entry)
    return {"ad_results": results, "agent_log": [entry]}
