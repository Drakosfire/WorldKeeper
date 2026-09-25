"""Transport-neutral consumer contract for the accepted World change lifecycle."""

from __future__ import annotations

from typing import Protocol

from .contracts import PreparedWorldChange, VerifiedCommittedChange, WorldChangeIntent


class WorldChangeService(Protocol):
    """Prepare and explicitly commit one immutable World change."""

    def prepare_change(self, intent: WorldChangeIntent) -> PreparedWorldChange: ...

    def commit_prepared_change(
        self,
        prepared: PreparedWorldChange,
        confirmed_by: str,
    ) -> VerifiedCommittedChange: ...
