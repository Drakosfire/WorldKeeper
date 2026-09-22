"""Read-only in-process adapter over DungeonMind's governed authority."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from dungeonmind.application.graph_snapshot import GraphSnapshotReader
from dungeonmind.application.repositories import (
    FinalizedReviewPublicationRepository,
    SourceRepository,
    WorldGraphRepository,
)
from dungeonmind.domain.errors import (
    DungeonMindError,
    PersistenceIntegrityError,
    PersistenceUnavailableError,
)

from worldkeeper.application.authority import (
    AuthorityIntegrityFailure,
    AuthorityUnavailable,
    ExactRevisionWitness,
    FinalizedPublicationWitness,
    SourceRevisionWitness,
    WorldHeadWitness,
)

_WitnessValue = TypeVar("_WitnessValue")


class DungeonMindInProcessAuthority:
    """Adapt DungeonMind reads into narrow World Keeper-owned witnesses.

    This WK-2 adapter deliberately has no publication, source-write, or
    lifecycle-orchestration methods. DungeonMind remains the durable authority.
    """

    def __init__(
        self,
        *,
        world_graph_repository: WorldGraphRepository,
        source_repository: SourceRepository,
        finalized_publication_repository: FinalizedReviewPublicationRepository,
        graph_snapshot_reader: GraphSnapshotReader,
    ) -> None:
        self._world_graph_repository = world_graph_repository
        self._source_repository = source_repository
        self._finalized_publication_repository = finalized_publication_repository
        self._graph_snapshot_reader = graph_snapshot_reader

    def read_head(self, world_id: str) -> WorldHeadWitness | None:
        head = self._read(lambda: self._world_graph_repository.get_head(world_id))
        if head is None:
            return None
        if head.world_id != world_id:
            self._integrity("DungeonMind head does not match the requested World")
        return WorldHeadWitness(world_id=head.world_id, head_revision_id=head.head_revision_id)

    def read_exact_revision(
        self, world_id: str, revision_id: str
    ) -> ExactRevisionWitness | None:
        stored = self._read(
            lambda: self._world_graph_repository.get_revision(world_id, revision_id)
        )
        if stored is None:
            return None
        revision = stored.revision
        if revision.world_id != world_id or revision.revision_id != revision_id:
            self._integrity("DungeonMind revision does not match the requested identity")
        if revision.status != "published":
            self._integrity("DungeonMind exact revision is not published")
        snapshot = self._read(
            lambda: self._graph_snapshot_reader.parse(
                graph_schema=revision.graph_schema,
                graph_payload=stored.graph_payload,
            )
        )
        if snapshot.world_id != world_id or snapshot.graph_schema != revision.graph_schema:
            self._integrity("DungeonMind parsed snapshot disagrees with its revision envelope")
        return ExactRevisionWitness(
            world_id=revision.world_id,
            revision_id=revision.revision_id,
            parent_revision_id=revision.parent_revision_id,
            graph_schema=revision.graph_schema,
            graph_payload_sha256=revision.graph_payload_sha256,
            object_ids=tuple(sorted(snapshot.objects)),
            relationship_ids=tuple(sorted(snapshot.relationships)),
            evidence_ref_ids=tuple(sorted(snapshot.evidence)),
        )

    def read_source_revision(
        self,
        source_artifact_id: str,
        source_revision_id: str,
    ) -> SourceRevisionWitness | None:
        artifact = self._read(lambda: self._source_repository.get_artifact(source_artifact_id))
        revision = self._read(lambda: self._source_repository.get_revision(source_revision_id))
        if artifact is None or revision is None:
            return None
        if artifact.source_artifact_id != source_artifact_id:
            self._integrity("DungeonMind source artifact does not match the requested identity")
        if revision.source_revision_id != source_revision_id:
            self._integrity("DungeonMind source revision does not match the requested identity")
        if revision.source_artifact_id != artifact.source_artifact_id:
            self._integrity("DungeonMind source revision belongs to another artifact")
        return SourceRevisionWitness(
            source_artifact_id=artifact.source_artifact_id,
            source_revision_id=revision.source_revision_id,
            content_sha256=revision.content_sha256,
            locator=revision.locator,
        )

    def read_finalized_publication(
        self,
        world_id: str,
        publication_operation_id: str,
    ) -> FinalizedPublicationWitness | None:
        publication = self._read(
            lambda: self._finalized_publication_repository.get(
                world_id, publication_operation_id
            )
        )
        if publication is None:
            return None
        if (
            publication.world_id != world_id
            or publication.operation_id != publication_operation_id
            or publication.status != "published"
        ):
            self._integrity("DungeonMind publication does not match the requested identity")
        return FinalizedPublicationWitness(
            world_id=publication.world_id,
            publication_operation_id=publication.operation_id,
            expected_parent_revision_id=publication.expected_parent_revision_id,
            published_revision_id=publication.published_revision_id,
            status=publication.status,
        )

    @staticmethod
    def _integrity(message: str) -> None:
        raise AuthorityIntegrityFailure(message)

    @staticmethod
    def _read(callback: Callable[[], _WitnessValue]) -> _WitnessValue:
        try:
            return callback()
        except PersistenceUnavailableError as exc:
            raise AuthorityUnavailable("DungeonMind authority is unavailable") from exc
        except PersistenceIntegrityError as exc:
            raise AuthorityIntegrityFailure(
                "DungeonMind authority failed integrity validation"
            ) from exc
        except DungeonMindError as exc:
            raise AuthorityIntegrityFailure("DungeonMind authority read failed closed") from exc
