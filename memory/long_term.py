"""Long-term memory facade.

Thin re-export layer over :mod:`tools.memory_tool` so the rest of the codebase
imports memory operations from a stable ``memory.long_term`` namespace. Keeping
the ChromaDB mechanics in ``tools`` and the semantic API here means callers
(agents, main, app) never touch the vector store directly.
"""

from tools.memory_tool import (
    retrieve_past_research,
    save_research,
    list_sessions,
)

__all__ = ["retrieve_past_research", "save_research", "list_sessions"]
