"""Copy Compliance agent.

Two layers: a fast deterministic pass (banned/risky terms, per-platform
character limits) that never depends on model availability, followed by an
LLM pass that judges tone, unsubstantiated claims, and missing disclaimers --
the things a keyword list can't catch.
"""

from ad_qa.config import BANNED_OR_RISKY_TERMS, COPY_LIMITS, DEFAULT_PLATFORM
from ad_qa.state import AdQAState
from memory.short_term import log_line
from utils.helpers import call_llm_json, truncate
from utils.logger import get_logger

log = get_logger("ad_qa.copy_compliance")

SYSTEM_PROMPT = """You are an ad-copy compliance reviewer. Given an ad's headline, body
copy, and call-to-action, flag anything a platform reviewer or legal team would push back
on: unsubstantiated superlatives or claims ("best", "guaranteed", "clinically proven"
without support), missing disclaimers for testimonials/earnings/health/finance claims,
misleading urgency, or copy that implies functionality/personal attributes it shouldn't.
Do not flag normal marketing enthusiasm -- only concrete, defensible issues.

Respond ONLY with a valid JSON object matching this schema:
{
  "issues": [{"severity": "FAIL" | "WARN", "message": "specific, actionable finding"}]
}
An empty "issues" list means the copy looks fine. No markdown, no preamble."""


def _deterministic_checks(ad: dict) -> list:
    issues = []
    headline = ad.get("headline", "")
    body = ad.get("body_copy", "")
    combined = f"{headline} {body}".lower()
    platform = ad.get("platform", DEFAULT_PLATFORM)

    for term in BANNED_OR_RISKY_TERMS:
        if term in combined:
            issues.append({
                "check": "copy", "severity": "WARN",
                "message": f"Contains risky/regulated term \"{term}\" -- verify it's substantiated.",
            })

    limits = COPY_LIMITS.get(platform, COPY_LIMITS[DEFAULT_PLATFORM])
    if headline and len(headline) > limits["headline"]:
        issues.append({
            "check": "copy", "severity": "FAIL",
            "message": f"Headline is {len(headline)} chars, over the {limits['headline']}-char "
                        f"limit for this platform.",
        })
    if body and len(body) > limits["body_copy"]:
        issues.append({
            "check": "copy", "severity": "FAIL",
            "message": f"Body copy is {len(body)} chars, over the {limits['body_copy']}-char "
                        f"limit for this platform.",
        })
    return issues


def run_copy_compliance(state: AdQAState) -> dict:
    results = state.get("ad_results") or []
    fail_count = 0

    for ad in results:
        det_issues = _deterministic_checks(ad)

        user = (
            f'Headline: "{ad.get("headline", "")}"\n'
            f'Body copy: "{ad.get("body_copy", "")}"\n'
            f'CTA: "{ad.get("cta", "")}"'
        )
        default = {"issues": []}
        try:
            data = call_llm_json(SYSTEM_PROMPT, truncate(user, 2000), default=default)
            llm_issues = data.get("issues") or []
        except Exception as exc:
            log.error("Copy compliance LLM check failed for %s: %s", ad.get("ad_id"), exc)
            llm_issues = []

        all_issues = det_issues + [
            {"check": "copy", "severity": i.get("severity", "WARN"), "message": i.get("message", "")}
            for i in llm_issues if i.get("message")
        ]

        ad["checks"]["copy"] = {"ok": not any(i["severity"] == "FAIL" for i in all_issues),
                                  "issue_count": len(all_issues)}
        ad["issues"].extend(all_issues)
        if any(i["severity"] == "FAIL" for i in all_issues):
            fail_count += 1

    entry = log_line("COPY_COMPLIANCE", f"Reviewed {len(results)} ad(s); {fail_count} with FAIL-level copy issues.")
    log.info(entry)
    return {"ad_results": results, "agent_log": [entry]}
