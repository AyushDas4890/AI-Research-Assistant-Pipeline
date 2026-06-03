"""Tool JSON schemas.

These schemas describe the tools available to the agents in a standard
name / description / input_schema format. The pipeline calls the tool functions
directly from the agent code for deterministic control flow, but exposing the
schemas here keeps the tool contracts in one place and makes it trivial to hand
the same definitions to the LLM for native function/tool calling.
"""

SEARCH_WEB_SCHEMA = {
    "name": "search_web",
    "description": (
        "Search the web for a query and return the top results as a list of "
        "{url, title, snippet, score}. Use for finding sources relevant to a "
        "research sub-question."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return.",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}

FETCH_URL_SCHEMA = {
    "name": "fetch_url",
    "description": (
        "Fetch a web page by URL and return its cleaned plain-text content "
        "(scripts, styles, and navigation stripped). Returns an empty string "
        "if the page cannot be retrieved."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The absolute URL to fetch.",
            },
            "max_chars": {
                "type": "integer",
                "description": "Maximum number of characters to return.",
                "default": 4000,
            },
        },
        "required": ["url"],
    },
}

RETRIEVE_MEMORY_SCHEMA = {
    "name": "retrieve_past_research",
    "description": (
        "Retrieve semantically similar past research reports from long-term "
        "vector memory for a given query. Returns a formatted string, or empty "
        "string if nothing relevant is stored."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The research topic to look up.",
            },
            "n_results": {
                "type": "integer",
                "description": "How many past reports to retrieve.",
                "default": 3,
            },
        },
        "required": ["query"],
    },
}

SAVE_MEMORY_SCHEMA = {
    "name": "save_research",
    "description": (
        "Persist a completed research report to long-term vector memory, keyed "
        "by session id and tagged with the originating query and a timestamp."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The research topic."},
            "report": {"type": "string", "description": "The full Markdown report."},
            "session_id": {"type": "string", "description": "Unique run id."},
        },
        "required": ["query", "report", "session_id"],
    },
}

# Convenient bundle for any code that wants to pass all tool schemas at once.
ALL_TOOL_SCHEMAS = [
    SEARCH_WEB_SCHEMA,
    FETCH_URL_SCHEMA,
    RETRIEVE_MEMORY_SCHEMA,
    SAVE_MEMORY_SCHEMA,
]
