"""SSL context for urllib on macOS Python (cert bundle)."""

from __future__ import annotations

import ssl

try:
    import certifi
except ImportError:  # pragma: no cover
    certifi = None  # type: ignore[assignment]


def ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()
