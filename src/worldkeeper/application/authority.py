"""Narrow, read-only governed-authority seam for the WK-2 boundary proof."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .contracts import PreparedWorldChange


class AuthorityIntegrityFailure(RuntimeError):
    """DungeonMind returned durable authority that cannot be trusted as-is."""


class AuthorityUnavailable(RuntimeError):
    """DungeonMind authority could not be reached for a read."""


@dataclass(frozen=True)
class WorldHeadWitness:
    """The one exact current head observed for a World."""

    world_id: str
    head_revision_id: str


@dataclass(frozen=True)
class ExactRevisionWitness:
    """A selected, immutable World revision without its raw graph payload."""

    world_id: str
    revision_id: str
    parent_revision_id: str | None
    graph_schema: str
    graph_payload_sha256: str
    object_ids: tuple[str, ...]
    relationship_ids: tuple[str, ...]
    evidence_ref_ids: tuple[str, ...]


@dataclass(frozen=True)
class SourceRevisionWitness:
    """A source revision proven to belong to the requested source artifact."""

    source_artifact_id: str
    source_revision_id: str
    content_sha256: str
    locator: str | None


@dataclass(frozen=True)
class FinalizedPublicationWitness:
    """Terminal DungeonMind publication correspondence, exposed read-only."""

    world_id: str
    publication_operation_id: str
    expected_parent_revision_id: str
    published_revision_id: str
    status: str


class GovernedWorldAuthority(Protocol):
    """World Keeper's read-only view of governed DungeonMind authority."""

    def read_head(self, world_id: str) -> WorldHeadWitness | None: ...

    def read_exact_revision(
        self, world_id: str, revision_id: str
    ) -> ExactRevisionWitness | None: ...

    def read_source_revision(
        self,
        source_artifact_id: str,
        source_revision_id: str,
    ) -> SourceRevisionWitness | None: ...

    def read_finalized_publication(
        self,
        world_id: str,
        publication_operation_id: str,
    ) -> FinalizedPublicationWitness | None: ...


@dataclass(frozen=True)
class PreparationAuthorityRef:
    """Pinned descriptor identity carried by one native vNext parent."""

    authority_id: str
    revision: str
    descriptor_sha256: str


@dataclass(frozen=True)
class PreparationEvidenceWitness:
    """Exact evidence identity visible in the selected native parent."""

    evidence_ref_id: str
    source_artifact_id: str
    source_revision_id: str | None
    evidence_role: str
    locator: str | None
    uri: str | None
    source_locator: str | None
    line_ref: str | None
    source_span_ref_id: str | None


@dataclass(frozen=True)
class PreparationAuthorityWitness:
    """Narrow immutable native-vNext authority required by WK-3 prepare."""

    space_id: str
    head_revision_id: str
    graph_payload_sha256: str
    domain_contract_ref: PreparationAuthorityRef
    semantic_profile_ref: PreparationAuthorityRef
    durable_entity_ids: tuple[str, ...]
    evidence_witnesses: tuple[PreparationEvidenceWitness, ...]


class GovernedPreparationAuthority(Protocol):
    """Read-only current native-vNext authority used by prepare."""

    def read_current_space(self, space_id: str) -> PreparationAuthorityWitness | None: ...


@dataclass(frozen=True, slots=True)
class CommitResultBinding:
    client_op_id: str
    result_kind: str
    durable_id: str


@dataclass(frozen=True, slots=True)
class CommitAuthorityWitness:
    space_id: str
    publication_id: str
    expected_parent_revision_id: str
    child_revision_id: str
    child_graph_payload_sha256: str
    results: tuple[CommitResultBinding, ...]


class GovernedCommitAuthority(Protocol):
    """Narrow publication and exact-child verification seam for WK-4."""

    def commit_and_verify(self, prepared: PreparedWorldChange) -> CommitAuthorityWitness: ...
