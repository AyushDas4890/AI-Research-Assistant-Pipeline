"""Ingestor agent.

Validates and normalizes the raw ad records, assigning a stable ``ad_id`` to
any row missing one and seeding the per-ad results skeleton every downstream
agent appends findings to.
"""

from ad_qa.config import DEFAULT_PLATFORM
from ad_qa.state import AdQAState
from memory.short_term import log_line
from utils.logger import get_logger

log = get_logger("ad_qa.ingestor")


def run_ingestor(state: AdQAState) -> dict:
    ads = state.get("ads") or []
    results = []
    for i, ad in enumerate(ads):
        ad_id = str(ad.get("ad_id") or f"ad_{i + 1}").strip()
        results.append({
            "ad_id": ad_id,
            "platform": (ad.get("platform") or DEFAULT_PLATFORM).strip().lower(),
            "headline": (ad.get("headline") or "").strip(),
            "body_copy": (ad.get("body_copy") or "").strip(),
            "cta": (ad.get("cta") or "").strip(),
            "destination_url": (ad.get("destination_url") or "").strip(),
            "image_url": (ad.get("image_url") or "").strip(),
            "checks": {},
            "issues": [],
            "status": "PASS",
        })

    entry = log_line("INGESTOR", f"Loaded {len(results)} ad(s) for QA.")
    log.info(entry)
    return {"ad_results": results, "agent_log": [entry]}
