"""URL fetch tool — downloads a page and returns cleaned plain text."""

import httpx
from bs4 import BeautifulSoup

from utils.logger import get_logger

log = get_logger("fetch_tool")


def fetch_url(url: str, max_chars: int = 4000) -> str:
    """Fetch a URL and return cleaned plain-text content.

    Returns an empty string on any failure (never raises), so the Reader agent
    can simply skip unreadable sources.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Research Bot)"}
        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:max_chars]
    except Exception as exc:
        log.warning("fetch_url failed for %s: %s", url, exc)
        return ""
