"""Image asset fetching and lightweight format/dimension inspection.

Deliberately avoids adding an image-processing dependency (e.g. Pillow):
dimensions for the common ad creative formats (PNG, JPEG, GIF, WebP) are
parsed directly from the file header bytes with the standard library.
"""

import struct
import httpx

DEFAULT_TIMEOUT = 10.0


def _png_size(data: bytes):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def _gif_size(data: bytes):
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        return None
    width, height = struct.unpack("<HH", data[6:10])
    return width, height


def _jpeg_size(data: bytes):
    if data[:2] != b"\xff\xd8":
        return None
    i, n = 2, len(data)
    while i + 9 < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD9:
            i += 2
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg_len
    return None


def _webp_size(data: bytes):
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8 ":
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L":
        b0, b1, b2, b3 = data[21:25]
        width = 1 + (((b1 & 0x3F) << 8) | b0)
        height = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | (b1 >> 6))
        return width, height
    return None


def detect_dimensions(data: bytes):
    """Best-effort ``(width, height)`` from raw image bytes, or ``None``."""
    for fn in (_png_size, _jpeg_size, _gif_size, _webp_size):
        try:
            result = fn(data)
        except Exception:
            result = None
        if result:
            return result
    return None


def detect_format(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:2] == b"\xff\xd8":
        return "jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return "unknown"


def fetch_image(url: str, *, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Download an image asset and report format, dimensions, and size.

    Returns ``{ok, format, width, height, size_bytes, content_type, error}``.
    Never raises.
    """
    if not url or not url.strip():
        return {"ok": False, "format": None, "width": None, "height": None,
                "size_bytes": 0, "content_type": None, "error": "empty URL"}
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
        if resp.status_code >= 400:
            return {"ok": False, "format": None, "width": None, "height": None,
                     "size_bytes": 0, "content_type": resp.headers.get("content-type"),
                     "error": f"HTTP {resp.status_code}"}
        data = resp.content
        fmt = detect_format(data)
        dims = detect_dimensions(data)
        width, height = dims if dims else (None, None)
        return {
            "ok": True, "format": fmt, "width": width, "height": height,
            "size_bytes": len(data),
            "content_type": resp.headers.get("content-type"),
            "error": None if dims else "could not parse dimensions (unsupported/corrupt format)",
        }
    except Exception as exc:
        return {"ok": False, "format": None, "width": None, "height": None,
                "size_bytes": 0, "content_type": None, "error": str(exc)}
