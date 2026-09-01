"""Destination URL checking tool."""

import time
import httpx

DEFAULT_TIMEOUT = 10.0


def check_url(url: str, *, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Follow a destination URL and report status, redirects, and latency.

    Returns ``{ok, status_code, final_url, redirect_count, latency_ms, error}``.
    Never raises -- network failures are captured in the ``error`` field.
    """
    if not url or not url.strip():
        return {"ok": False, "status_code": None, "final_url": None,
                "redirect_count": 0, "latency_ms": None, "error": "empty URL"}

    start = time.monotonic()
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        ok = 200 <= resp.status_code < 400
        return {
            "ok": ok,
            "status_code": resp.status_code,
            "final_url": str(resp.url),
            "redirect_count": len(resp.history),
            "latency_ms": latency_ms,
            "error": None if ok else f"HTTP {resp.status_code}",
        }
    except httpx.TimeoutException:
        return {"ok": False, "status_code": None, "final_url": None,
                "redirect_count": 0,
                "latency_ms": round((time.monotonic() - start) * 1000, 1),
                "error": f"timed out after {timeout}s"}
    except Exception as exc:
        return {"ok": False, "status_code": None, "final_url": None,
                "redirect_count": 0, "latency_ms": None, "error": str(exc)}
