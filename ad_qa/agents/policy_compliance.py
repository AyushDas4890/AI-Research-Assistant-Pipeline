"""Platform Policy Compliance agent.

LLM-based review of the full ad (copy + destination + platform) against the
kinds of things Google/Meta/LinkedIn ad-policy reviewers reject for: prohibited
or restricted content categories, misleading claims about the product itself,
missing required disclosures, and destination/content mismatch (the landing
page not matching what the ad promises).
"""

from ad_qa.config import PLATFORM_SPECS, DEFAULT_PLATFORM
from ad_qa.state import AdQAState
from memory.short_term import log_line
from utils.helpers import call_llm_json, truncate
from utils.logger import get_logger

log = get_logger("ad_qa.policy_compliance")

SYSTEM_PROMPT = """You are an ad platform policy reviewer (the kind of review Google Ads
or Meta runs before an ad goes live). Given an ad's platform, headline, body copy, CTA,
and destination URL, flag anything likely to get the ad rejected or suspended: prohibited
content (weapons, drugs, counterfeit goods, adult content, etc.), restricted content run
without the required certification language (gambling, alcohol, healthcare, financial
services, political), personalized-attribute targeting language ("as a single mom...",
"if you have diabetes..."), or a clear mismatch between what the ad promises and what a
destination URL like this would plausibly show. Do not flag ordinary, compliant ads --
only concrete policy risks a reviewer would act on.

Respond ONLY with a valid JSON object matching this schema:
{
  "issues": [{"severity": "FAIL" | "WARN", "message": "specific, actionable finding"}]
}
An empty "issues" list means no policy risk found. No markdown, no preamble."""


def run_policy_compliance(state: AdQAState) -> dict:
    results = state.get("ad_results") or []
    fail_count = 0

    for ad in results:
        platform = ad.get("platform", DEFAULT_PLATFORM)
        label = PLATFORM_SPECS.get(platform, PLATFORM_SPECS[DEFAULT_PLATFORM])["label"]

        user = (
            f'Platform: {label}\n'
            f'Headline: "{ad.get("headline", "")}"\n'
            f'Body copy: "{ad.get("body_copy", "")}"\n'
            f'CTA: "{ad.get("cta", "")}"\n'
            f'Destination URL: {ad.get("destination_url", "")}'
        )
        default = {"issues": []}
        try:
            data = call_llm_json(SYSTEM_PROMPT, truncate(user, 2000), default=default)
            llm_issues = data.get("issues") or []
        except Exception as exc:
            log.error("Policy compliance LLM check failed for %s: %s", ad.get("ad_id"), exc)
            llm_issues = []

        issues = [
            {"check": "policy", "severity": i.get("severity", "WARN"), "message": i.get("message", "")}
            for i in llm_issues if i.get("message")
        ]

        ad["checks"]["policy"] = {"ok": not any(i["severity"] == "FAIL" for i in issues),
                                    "issue_count": len(issues)}
        ad["issues"].extend(issues)
        if any(i["severity"] == "FAIL" for i in issues):
            fail_count += 1

    entry = log_line("POLICY_COMPLIANCE", f"Reviewed {len(results)} ad(s); {fail_count} with policy-risk findings.")
    log.info(entry)
    return {"ad_results": results, "agent_log": [entry]}
