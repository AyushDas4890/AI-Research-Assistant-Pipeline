"""Image QA agent.

Downloads each ad's image asset and checks it against the destination
platform's spec: allowed format, file size ceiling, and (for platforms that
mandate exact sizes) valid pixel dimensions or minimum resolution.
"""

from ad_qa.config import PLATFORM_SPECS, DEFAULT_PLATFORM
from ad_qa.state import AdQAState
from ad_qa.tools.image_tool import fetch_image
from memory.short_term import log_line
from utils.logger import get_logger

log = get_logger("ad_qa.image_qa")


def run_image_qa(state: AdQAState) -> dict:
    results = state.get("ad_results") or []
    fail_count = 0

    for ad in results:
        url = ad.get("image_url", "")
        spec = PLATFORM_SPECS.get(ad.get("platform"), PLATFORM_SPECS[DEFAULT_PLATFORM])

        if not url:
            ad["checks"]["image"] = {"ok": False, "error": "no image_url provided"}
            ad["issues"].append({
                "check": "image", "severity": "WARN",
                "message": "No image asset supplied to QA.",
            })
            continue

        try:
            check = fetch_image(url)
        except Exception as exc:
            check = {"ok": False, "format": None, "width": None, "height": None,
                      "size_bytes": 0, "content_type": None, "error": str(exc)}

        ad["checks"]["image"] = check

        if not check["ok"]:
            ad["issues"].append({
                "check": "image", "severity": "FAIL",
                "message": f"Image asset failed to load: {check.get('error') or 'unknown error'}",
            })
            fail_count += 1
            continue

        # Format
        allowed_formats = spec.get("allowed_formats", [])
        if allowed_formats and check.get("format") not in allowed_formats:
            ad["issues"].append({
                "check": "image", "severity": "FAIL",
                "message": f"Format '{check.get('format')}' not in allowed formats "
                            f"{allowed_formats} for {spec['label']}.",
            })
            fail_count += 1

        # File size
        size_bytes = check.get("size_bytes") or 0
        if "max_file_size_kb" in spec and size_bytes > spec["max_file_size_kb"] * 1024:
            ad["issues"].append({
                "check": "image", "severity": "FAIL",
                "message": f"Image is {size_bytes / 1024:.0f}KB, over the "
                            f"{spec['max_file_size_kb']}KB limit for {spec['label']}.",
            })
            fail_count += 1
        elif "max_file_size_mb" in spec and size_bytes > spec["max_file_size_mb"] * 1024 * 1024:
            ad["issues"].append({
                "check": "image", "severity": "FAIL",
                "message": f"Image is {size_bytes / (1024 * 1024):.1f}MB, over the "
                            f"{spec['max_file_size_mb']}MB limit for {spec['label']}.",
            })
            fail_count += 1

        # Dimensions
        w, h = check.get("width"), check.get("height")
        if w and h:
            if "valid_sizes_px" in spec and (w, h) not in spec["valid_sizes_px"]:
                ad["issues"].append({
                    "check": "image", "severity": "WARN",
                    "message": f"{w}x{h} isn't one of {spec['label']}'s standard sizes "
                                f"{spec['valid_sizes_px']}.",
                })
            if "min_resolution_px" in spec:
                min_w, min_h = spec["min_resolution_px"]
                if w < min_w or h < min_h:
                    ad["issues"].append({
                        "check": "image", "severity": "FAIL",
                        "message": f"{w}x{h} is below the {min_w}x{min_h} minimum "
                                    f"for {spec['label']}.",
                    })
                    fail_count += 1
        elif check.get("error"):
            ad["issues"].append({
                "check": "image", "severity": "WARN",
                "message": f"Could not verify dimensions: {check['error']}",
            })

    entry = log_line("IMAGE_QA", f"Checked {len(results)} image asset(s); {fail_count} failures.")
    log.info(entry)
    return {"ad_results": results, "agent_log": [entry]}
