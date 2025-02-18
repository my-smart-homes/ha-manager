from contextvars import ContextVar
from typing import Optional

# Declaring ContextVar variables with Optional[str] type hints to allow None values
tenant_context: ContextVar[Optional[str]] = ContextVar(
    "tenant_context", default=None)
