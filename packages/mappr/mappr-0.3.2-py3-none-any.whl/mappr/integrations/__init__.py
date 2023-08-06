# All integrations are optional so we need to silently fail on import errors.
try:
    from . import pydantic   # noqa: F401
except ImportError:  # nocov
    pass  # nocov

try:
    from . import sqlalchemy   # noqa: F401
except ImportError:  # nocov
    pass  # nocov
