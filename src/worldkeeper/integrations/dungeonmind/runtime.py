"""DungeonMind-backed composition root for the accepted WorldKeeper lifecycle."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from dungeonmind.application.vnext.ports import KnowledgeRevisionRepository
from dungeonmind.contracts.vnext.domain import (
    DomainContractDescriptor,
    SemanticProfileDescriptorV2,
)

from .vnext_commit import DungeonMindVNextCommitAuthority
from .vnext_prepare import DungeonMindVNextPreparationAuthority

if TYPE_CHECKING:
    from worldkeeper.application.contracts import (
        PreparedWorldChange,
        VerifiedCommittedChange,
        WorldChangeIntent,
    )


class DungeonMindWorldKeeperRuntime:
    """Compose accepted prepare and commit services over one repository."""

    def __init__(
        self,
        *,
        repository: KnowledgeRevisionRepository,
        domain_contract: DomainContractDescriptor,
        semantic_profile: SemanticProfileDescriptorV2,
        clock: Callable[[], datetime],
        prepared_id_factory: Callable[[], str] | None = None,
    ) -> None:
        from worldkeeper.application.commit import WorldChangeCommitter
        from worldkeeper.application.preparation import WorldChangePreparer

        self._preparer = WorldChangePreparer(
            authority=DungeonMindVNextPreparationAuthority(repository),
            domain_contract=domain_contract,
            semantic_profile=semantic_profile,
            clock=clock,
            prepared_id_factory=prepared_id_factory,
        )
        self._committer = WorldChangeCommitter(DungeonMindVNextCommitAuthority(repository))

    def prepare_change(self, intent: WorldChangeIntent) -> PreparedWorldChange:
        return self._preparer.prepare_change(intent)

    def commit_prepared_change(
        self,
        prepared: PreparedWorldChange,
        confirmed_by: str,
    ) -> VerifiedCommittedChange:
        return self._committer.commit_prepared_change(prepared, confirmed_by)
