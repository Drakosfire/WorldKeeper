"""WK-4 confirmation coordination and verified-result reshaping."""

from __future__ import annotations

from .authority import CommitAuthorityWitness, GovernedCommitAuthority
from .contracts import (
    CommittedAssertionResult,
    CommittedObjectResult,
    PreparedWorldChange,
    VerifiedCommittedChange,
)


class PreparedChangeIntegrityFailure(RuntimeError):
    """The supplied prepared value no longer matches its integrity witness."""


class PreparedChangeStale(RuntimeError):
    """DungeonMind rejected the exact prepared parent as stale."""


class PreparedChangeConflict(RuntimeError):
    """The publication identity is already bound to different meaning."""


class CommitAuthorityIntegrityFailure(RuntimeError):
    """Authority was incoherent before a durable commit was known."""


class CommittedChangeOutcomeUnknown(RuntimeError):
    retry_safe = True

    def __init__(
        self,
        *,
        prepared_change_id: str,
        publication_id: str,
        expected_published_revision_id: str,
    ) -> None:
        super().__init__("committed change outcome is unknown")
        self.prepared_change_id = prepared_change_id
        self.publication_id = publication_id
        self.expected_published_revision_id = expected_published_revision_id


class CommittedChangeVerificationUnavailable(RuntimeError):
    retry_safe = True
    committed = True

    def __init__(
        self, *, prepared_change_id: str, publication_id: str, child_revision_id: str
    ) -> None:
        super().__init__("committed change exact child is temporarily unavailable")
        self.prepared_change_id = prepared_change_id
        self.publication_id = publication_id
        self.child_revision_id = child_revision_id


class CommittedChangeVerificationIntegrityFailure(RuntimeError):
    committed = True

    def __init__(
        self, *, prepared_change_id: str, publication_id: str, child_revision_id: str
    ) -> None:
        super().__init__("committed change exact child failed integrity verification")
        self.prepared_change_id = prepared_change_id
        self.publication_id = publication_id
        self.child_revision_id = child_revision_id


class WorldChangeCommitter:
    def __init__(self, authority: GovernedCommitAuthority) -> None:
        self._authority = authority

    def commit_prepared_change(
        self, prepared: PreparedWorldChange, confirmed_by: str
    ) -> VerifiedCommittedChange:
        if not isinstance(confirmed_by, str) or not confirmed_by.strip():
            raise ValueError("confirmed_by must be nonblank")
        witness = self._authority.commit_and_verify(prepared)
        self._validate_witness(prepared, witness)
        objects = tuple(
            CommittedObjectResult(item.client_op_id, item.durable_id)
            for item in witness.results
            if item.result_kind == "entity"
        )
        assertions = tuple(
            CommittedAssertionResult(
                item.client_op_id,
                item.durable_id,
                _assertion_role(prepared, item.client_op_id),
            )
            for item in witness.results
            if item.result_kind == "assertion"
        )
        return VerifiedCommittedChange(
            prepared_change_id=prepared.prepared_change_id,
            dungeonmind_publication_id=witness.publication_id,
            expected_parent_revision_id=witness.expected_parent_revision_id,
            child_revision_id=witness.child_revision_id,
            child_graph_payload_sha256=witness.child_graph_payload_sha256,
            object_results=objects,
            assertion_results=assertions,
        )

    @staticmethod
    def _validate_witness(prepared: PreparedWorldChange, witness: CommitAuthorityWitness) -> None:
        if (
            witness.space_id != prepared.space_id
            or witness.publication_id != prepared.prepared_change_id
            or witness.expected_parent_revision_id != prepared.expected_parent_revision_id
        ):
            raise CommitAuthorityIntegrityFailure("commit witness identity mismatch")
        from .contracts import CreateObject, CreateRelationship

        expected: dict[str, str] = {}
        for operation in prepared.prepared_operations:
            if isinstance(operation, CreateObject):
                expected[operation.client_op_id] = "entity"
                expected.update((fact.client_op_id, "assertion") for fact in operation.facts)
            elif isinstance(operation, CreateRelationship):
                expected[operation.client_op_id] = "assertion"
        actual = {item.client_op_id: item for item in witness.results}
        if len(actual) != len(witness.results) or set(actual) != set(expected):
            raise CommitAuthorityIntegrityFailure("commit result binding set mismatch")
        if any(
            actual[key].result_kind != kind
            or not actual[key].durable_id.startswith("ent:" if kind == "entity" else "asrt:")
            for key, kind in expected.items()
        ):
            raise CommitAuthorityIntegrityFailure("commit result binding kind mismatch")


def _assertion_role(prepared: PreparedWorldChange, client_op_id: str) -> str:
    from .contracts import CreateObject, CreateRelationship

    for operation in prepared.prepared_operations:
        if isinstance(operation, CreateRelationship) and operation.client_op_id == client_op_id:
            return "relationship"
        if isinstance(operation, CreateObject) and any(
            fact.client_op_id == client_op_id for fact in operation.facts
        ):
            return "fact"
    raise CommitAuthorityIntegrityFailure("unknown assertion result")
