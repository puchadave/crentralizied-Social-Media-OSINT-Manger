"""Compatibility helpers for runtime environments."""

from __future__ import annotations

import inspect
import sys
import typing


def patch_forward_ref_evaluate() -> None:
    """Patch ``typing.ForwardRef._evaluate`` for Python 3.12 / Pydantic 1.x compatibility."""

    if sys.version_info < (3, 12):
        return

    forward_ref = getattr(typing, "ForwardRef", None)
    if forward_ref is None:
        return

    try:
        signature = inspect.signature(forward_ref._evaluate)
    except (AttributeError, TypeError, ValueError):
        return

    parameters = signature.parameters
    recursive_guard_param = parameters.get("recursive_guard")
    if recursive_guard_param is None:
        return

    # Bail out if the runtime already provides a default for ``recursive_guard`` which would make
    # the method compatible with older Pydantic releases.
    if recursive_guard_param.default is not inspect._empty:
        return

    original = forward_ref._evaluate

    def _evaluate(  # type: ignore[override]
        self: typing.ForwardRef,
        globalns: typing.Mapping[str, object] | None,
        localns: typing.Mapping[str, object] | None,
        type_params: typing.Mapping[str, object] | None = None,
        *,
        recursive_guard: typing.Set[int] | None = None,
    ) -> object:
        if recursive_guard is None:
            recursive_guard = set()
        return original(self, globalns, localns, type_params, recursive_guard=recursive_guard)

    forward_ref._evaluate = _evaluate  # type: ignore[assignment]


patch_forward_ref_evaluate()
