"""Tool JSON schemas for the Ad QA pipeline.

Same convention as ``tools/schemas.py`` in the research pipeline: the graph
calls the tool functions directly for deterministic control flow, but the
schemas are kept here so the contracts are documented in one place.
"""

CHECK_URL_SCHEMA = {
    "name": "check_url",
    "description": (
        "Follow an ad's destination URL and report whether it loads, its final "
        "status code, redirect count, and latency."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The destination URL to check."},
            "timeout": {"type": "number", "description": "Request timeout in seconds.", "default": 10},
        },
        "required": ["url"],
    },
}

FETCH_IMAGE_SCHEMA = {
    "name": "fetch_image",
    "description": (
        "Download an ad's image asset and report its format, pixel dimensions, "
        "and file size in bytes."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The image asset URL."},
            "timeout": {"type": "number", "description": "Request timeout in seconds.", "default": 10},
        },
        "required": ["url"],
    },
}

ALL_TOOL_SCHEMAS = [CHECK_URL_SCHEMA, FETCH_IMAGE_SCHEMA]
