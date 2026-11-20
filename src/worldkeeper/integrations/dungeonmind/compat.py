"""Explicit historical DungeonMind World Graph read compatibility.

The original adapter and its direct module remain unchanged. Native consumers
should import the runtime/preparation/commit surfaces from the integration root.
"""

from .in_process import DungeonMindInProcessAuthority

__all__ = ["DungeonMindInProcessAuthority"]
