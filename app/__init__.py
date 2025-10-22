"""Realtime Social Media Marketing OSINT Manager."""

# Ensure runtime compatibility patches are applied before the application and models load.
from . import compat  # noqa: F401  (imported for side effects)
from .main import app, create_application

__all__ = ["app", "create_application"]
