"""Raftly deterministic project engine.

Standard library only. Every script in ``scripts/`` is a thin CLI over this
package so behaviour stays testable and consistent.
"""

FORGE_VERSION = "0.1.0"
SCHEMA_VERSION = 1

__all__ = ["FORGE_VERSION", "SCHEMA_VERSION"]
