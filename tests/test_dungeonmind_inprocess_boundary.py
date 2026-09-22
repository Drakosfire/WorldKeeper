"""WK-2 conformance proof for the read-only DungeonMind authority seam."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest
from dungeonmind.application.graph_snapshot import (
    GRAPH_SCHEMA_V1,
    VersionedUnionGraphSnapshotReader,
)
from dungeonmind.contracts import SourceArtifact, SourceDomain, SourceRevision
from dungeonmind.contracts.graph import PublishRevisionCommand
from dungeonmind.contracts.review_publication import FinalizedReviewPublicationCommand
from dungeonmind.domain import canonical_sha256
from dungeonmind.domain.revision_ids import compute_revision_id
from dungeonmind.infrastructure.memory import (
    InMemoryFinalizedReviewPublicationRepository,
    InMemorySourceRepository,
    InMemoryWorldGraphRepository,
)

from worldkeeper import (
    AuthorityIntegrityFailure,
    ExactRevisionWitness,
    SourceRevisionWitness,
)
from worldkeeper.integrations.dungeonmind import DungeonMindInProcessAuthority

WORLD_ID = "world:wk2-fixture"
ARTIFACT_ID = "source:wk2-fixture"
REVISION_ID = "source-revision:wk2-fixture"
OTHER_ARTIFACT_ID = "source:wk2-other"
OTHER_REVISION_ID = "source-revision:wk2-other"
PUBLICATION_OPERATION_ID = "reviewop:11111111111111111111111111111111"
NOW = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


@dataclass(frozen=True)
class _PlanRef:
    expected_parent_revision_id: str
    base_graph_payload_sha256: str
    base_graph_schema: str


@dataclass(frozen=True)
class _ReviewRecord:
    world_id: str
    review_id: str
    reviewed_contribution_id: str
    reviewed_contribution_sha256: str
    review_intent_sha256: str
    confirmation_id: str
    operation_id: str
    plan_ref: _PlanRef


@dataclass(frozen=True)
class _ReviewState:
    record: _ReviewRecord


class _ReviewLookup:
    """Fixture setup support for DungeonMind's real publication repository."""

    def __init__(self, state: _ReviewState) -> None:
        self._state = state

    def get(self, world_id: str, review_id: str) -> _ReviewState | None:
        if (
            world_id == self._state.record.world_id
            and review_id == self._state.record.review_id
        ):
            return self._state
        return None


@dataclass(frozen=True)
class _SeededAuthority:
    authority: DungeonMindInProcessAuthority
    graph: InMemoryWorldGraphRepository
    sources: InMemorySourceRepository
    publications: InMemoryFinalizedReviewPublicationRepository
    revision_a_id: str
    publication_revision_id: str


def _payload(*, label: str) -> dict[str, object]:
    return {
        "world_id": WORLD_ID,
        "nodes": [
            {
                "object_id": "object:observatory",
                "kind": "place",
                "label": label,
                "evidence_ref_ids": ["evidence:observatory"],
            },
            {
                "object_id": "object:astronomer",
                "kind": "person",
                "label": "Ilyra Voss",
                "evidence_ref_ids": ["evidence:observatory"],
            },
        ],
        "relationships": [
            {
                "relationship_id": "relationship:works-at",
                "subject_object_id": "object:astronomer",
                "predicate": "works_at",
                "object_object_id": "object:observatory",
                "evidence_ref_ids": ["evidence:observatory"],
            }
        ],
        "evidence_refs": [
            {
                "schema_version": "dm_evidence_ref_v1",
                "evidence_ref_id": "evidence:observatory",
                "source_artifact_id": ARTIFACT_ID,
                "source_revision_id": REVISION_ID,
                "source_domain": "worldbuilding",
                "evidence_role": "support",
            }
        ],
    }


def _publish(
    graph: InMemoryWorldGraphRepository,
    *,
    payload: dict[str, object],
    parent_revision_id: str | None,
    operation_id: str,
    created_at: datetime,
):
    return graph.publish_revision(
        PublishRevisionCommand(
            world_id=WORLD_ID,
            parent_revision_id=parent_revision_id,
            expected_parent_revision_id=parent_revision_id,
            operation_ids=[operation_id],
            graph_schema=GRAPH_SCHEMA_V1,
            graph_payload=payload,
            created_at=created_at,
        )
    )


def _seed() -> _SeededAuthority:
    graph = InMemoryWorldGraphRepository()
    sources = InMemorySourceRepository()
    sources.put_artifact(
        SourceArtifact(
            source_artifact_id=ARTIFACT_ID,
            source_domain=SourceDomain.WORLDBUILDING,
            world_id=WORLD_ID,
            created_at=NOW,
        )
    )
    sources.put_revision(
        SourceRevision(
            source_revision_id=REVISION_ID,
            source_artifact_id=ARTIFACT_ID,
            content_sha256="a" * 64,
            locator="object://wk2/observatory.md",
            created_at=NOW,
        )
    )
    sources.put_artifact(
        SourceArtifact(
            source_artifact_id=OTHER_ARTIFACT_ID,
            source_domain=SourceDomain.WORLDBUILDING,
            world_id=WORLD_ID,
            created_at=NOW,
        )
    )
    sources.put_revision(
        SourceRevision(
            source_revision_id=OTHER_REVISION_ID,
            source_artifact_id=OTHER_ARTIFACT_ID,
            content_sha256="b" * 64,
            locator="object://wk2/other.md",
            created_at=NOW,
        )
    )

    parent = _publish(
        graph,
        payload=_payload(label="Old Observatory"),
        parent_revision_id=None,
        operation_id="fixture:revision-a",
        created_at=NOW,
    )
    publication_payload = _payload(label="The Astral Observatory")
    publication_payload_sha256 = canonical_sha256(publication_payload)
    expected_publication_revision_id = compute_revision_id(
        world_id=WORLD_ID,
        parent_revision_id=parent.revision_id,
        operation_ids=[PUBLICATION_OPERATION_ID],
        graph_schema=GRAPH_SCHEMA_V1,
        graph_payload_sha256=publication_payload_sha256,
    )
    review_state = _ReviewState(
        record=_ReviewRecord(
            world_id=WORLD_ID,
            review_id="review:11111111111111111111111111111111",
            reviewed_contribution_id="contrib:11111111111111111111111111111111",
            reviewed_contribution_sha256="c" * 64,
            review_intent_sha256="d" * 64,
            confirmation_id="confirm:11111111111111111111111111111111",
            operation_id=PUBLICATION_OPERATION_ID,
            plan_ref=_PlanRef(
                expected_parent_revision_id=parent.revision_id,
                base_graph_payload_sha256=parent.graph_payload_sha256,
                base_graph_schema=GRAPH_SCHEMA_V1,
            ),
        )
    )
    publications = InMemoryFinalizedReviewPublicationRepository(_ReviewLookup(review_state), graph)
    publication = publications.publish(
        FinalizedReviewPublicationCommand(
            world_id=WORLD_ID,
            review_id=review_state.record.review_id,
            reviewed_contribution_id=review_state.record.reviewed_contribution_id,
            reviewed_contribution_sha256=review_state.record.reviewed_contribution_sha256,
            review_intent_sha256=review_state.record.review_intent_sha256,
            confirmation_id=review_state.record.confirmation_id,
            operation_id=PUBLICATION_OPERATION_ID,
            expected_parent_revision_id=parent.revision_id,
            parent_graph_payload_sha256=parent.graph_payload_sha256,
            expected_published_revision_id=expected_publication_revision_id,
            graph_schema=GRAPH_SCHEMA_V1,
            graph_payload=publication_payload,
            graph_payload_sha256=publication_payload_sha256,
            requested_published_at=NOW + timedelta(minutes=1),
        )
    )
    authority = DungeonMindInProcessAuthority(
        world_graph_repository=graph,
        source_repository=sources,
        finalized_publication_repository=publications,
        graph_snapshot_reader=VersionedUnionGraphSnapshotReader(),
    )
    return _SeededAuthority(
        authority=authority,
        graph=graph,
        sources=sources,
        publications=publications,
        revision_a_id=parent.revision_id,
        publication_revision_id=publication.published_revision_id,
    )


def test_head_and_exact_revision_are_worldkeeper_owned_witnesses() -> None:
    seeded = _seed()

    head = seeded.authority.read_head(WORLD_ID)
    exact = seeded.authority.read_exact_revision(WORLD_ID, seeded.publication_revision_id)

    assert head is not None
    assert head.head_revision_id == seeded.publication_revision_id
    assert isinstance(exact, ExactRevisionWitness)
    assert exact is not None
    assert exact.revision_id == seeded.publication_revision_id
    assert exact.object_ids == ("object:astronomer", "object:observatory")
    assert exact.relationship_ids == ("relationship:works-at",)
    assert exact.evidence_ref_ids == ("evidence:observatory",)
    assert type(exact).__module__.startswith("worldkeeper.")
    assert seeded.authority.read_head("world:missing") is None


def test_exact_revision_stays_pinned_after_head_advances() -> None:
    seeded = _seed()
    revision_a = seeded.authority.read_exact_revision(WORLD_ID, seeded.publication_revision_id)
    assert revision_a is not None

    revision_b = _publish(
        seeded.graph,
        payload=_payload(label="The Rebuilt Observatory"),
        parent_revision_id=seeded.publication_revision_id,
        operation_id="fixture:revision-b",
        created_at=NOW + timedelta(minutes=2),
    )

    assert (
        seeded.authority.read_exact_revision(WORLD_ID, seeded.publication_revision_id)
        == revision_a
    )
    assert seeded.authority.read_head(WORLD_ID).head_revision_id == revision_b.revision_id  # type: ignore[union-attr]
    assert seeded.authority.read_exact_revision(WORLD_ID, "rev:missing") is None


def test_source_revision_requires_exact_artifact_membership() -> None:
    seeded = _seed()

    witness = seeded.authority.read_source_revision(ARTIFACT_ID, REVISION_ID)

    assert isinstance(witness, SourceRevisionWitness)
    assert witness is not None
    assert witness.content_sha256 == "a" * 64
    assert witness.locator == "object://wk2/observatory.md"
    assert type(witness).__module__.startswith("worldkeeper.")
    assert seeded.authority.read_source_revision("source:missing", REVISION_ID) is None
    assert seeded.authority.read_source_revision(ARTIFACT_ID, "source-revision:missing") is None
    with pytest.raises(AuthorityIntegrityFailure, match="belongs to another artifact"):
        seeded.authority.read_source_revision(ARTIFACT_ID, OTHER_REVISION_ID)


def test_finalized_publication_witness_is_exact_and_repeatable() -> None:
    seeded = _seed()

    first = seeded.authority.read_finalized_publication(WORLD_ID, PUBLICATION_OPERATION_ID)
    second = seeded.authority.read_finalized_publication(WORLD_ID, PUBLICATION_OPERATION_ID)

    assert first == second
    assert first is not None
    assert first.expected_parent_revision_id == seeded.revision_a_id
    assert first.published_revision_id == seeded.publication_revision_id
    assert first.status == "published"
    assert type(first).__module__.startswith("worldkeeper.")
    assert seeded.authority.read_finalized_publication(WORLD_ID, "reviewop:missing") is None


class _ReadOnlyWorldGraph:
    def __init__(self, inner: InMemoryWorldGraphRepository) -> None:
        self.inner = inner
        self.mutation_calls: list[str] = []

    def get_head(self, world_id: str):
        return self.inner.get_head(world_id)

    def get_revision(self, world_id: str, revision_id: str):
        return self.inner.get_revision(world_id, revision_id)

    def publish_revision(self, command):
        del command
        self.mutation_calls.append("publish_revision")
        raise AssertionError("WK-2 adapter must not publish")

    def rollback_head(self, world_id: str, target_revision_id: str, *, updated_at: datetime):
        del world_id, target_revision_id, updated_at
        self.mutation_calls.append("rollback_head")
        raise AssertionError("WK-2 adapter must not roll back")


class _ReadOnlySources:
    def __init__(self, inner: InMemorySourceRepository) -> None:
        self.inner = inner
        self.mutation_calls: list[str] = []

    def get_artifact(self, source_artifact_id: str):
        return self.inner.get_artifact(source_artifact_id)

    def get_revision(self, source_revision_id: str):
        return self.inner.get_revision(source_revision_id)

    def put_artifact(self, artifact):
        del artifact
        self.mutation_calls.append("put_artifact")
        raise AssertionError("WK-2 adapter must not write source artifacts")

    def put_revision(self, revision):
        del revision
        self.mutation_calls.append("put_revision")
        raise AssertionError("WK-2 adapter must not write source revisions")


class _ReadOnlyPublications:
    def __init__(self, inner: InMemoryFinalizedReviewPublicationRepository) -> None:
        self.inner = inner
        self.mutation_calls: list[str] = []

    def get(self, world_id: str, operation_id: str):
        return self.inner.get(world_id, operation_id)

    def publish(self, command):
        del command
        self.mutation_calls.append("publish")
        raise AssertionError("WK-2 adapter must not publish finalized reviews")


def test_runtime_adapter_only_uses_read_operations() -> None:
    seeded = _seed()
    graph = _ReadOnlyWorldGraph(seeded.graph)
    sources = _ReadOnlySources(seeded.sources)
    publications = _ReadOnlyPublications(seeded.publications)
    authority = DungeonMindInProcessAuthority(
        world_graph_repository=graph,
        source_repository=sources,
        finalized_publication_repository=publications,
        graph_snapshot_reader=VersionedUnionGraphSnapshotReader(),
    )

    assert authority.read_head(WORLD_ID) is not None
    assert authority.read_exact_revision(WORLD_ID, seeded.publication_revision_id) is not None
    assert authority.read_source_revision(ARTIFACT_ID, REVISION_ID) is not None
    assert authority.read_finalized_publication(WORLD_ID, PUBLICATION_OPERATION_ID) is not None
    assert graph.mutation_calls == []
    assert sources.mutation_calls == []
    assert publications.mutation_calls == []
