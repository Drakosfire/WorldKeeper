from __future__ import annotations

import pytest
from dungeonmind.contracts.vnext.prospective import ProspectiveResultBinding
from dungeonmind.domain.errors import PersistenceUnavailableError

import test_wk4_commit_prepared_change as support
from worldkeeper.application.authority import CommitAuthorityWitness, CommitResultBinding
from worldkeeper.application.commit import (
    CommitAuthorityIntegrityFailure,
    CommittedChangeOutcomeUnknown,
    CommittedChangeVerificationIntegrityFailure,
    CommittedChangeVerificationUnavailable,
    WorldChangeCommitter,
)
from worldkeeper.integrations.dungeonmind.vnext_commit import DungeonMindVNextCommitAuthority


class RepositoryWrapper:
    def __init__(self, inner) -> None:
        self.inner = inner
        self.committed = False

    def get_head(self, space_id):
        return self.inner.get_head(space_id)

    def get_revision(self, space_id, revision_id):
        return self.inner.get_revision(space_id, revision_id)

    def publish_revision(self, command):
        return self.inner.publish_revision(command)

    def publish_publication(self, command, publication_id):
        return self.inner.publish_publication(command, publication_id)

    def get_publication_receipt(self, space_id, publication_id):
        return self.inner.get_publication_receipt(space_id, publication_id)

    def publish_prospective_publication(
        self, command, publication_id, prospective_request_sha256, result_bindings
    ):
        result = self.inner.publish_prospective_publication(
            command, publication_id, prospective_request_sha256, result_bindings
        )
        self.committed = True
        return result

    def get_prospective_publication(self, space_id, publication_id):
        return self.inner.get_prospective_publication(space_id, publication_id)

    def head_events(self, space_id):
        return self.inner.head_events(space_id)


class UnavailableChildRepository(RepositoryWrapper):
    def get_revision(self, space_id, revision_id):
        if self.committed:
            raise PersistenceUnavailableError("child temporarily unavailable")
        return super().get_revision(space_id, revision_id)


class MissingChildRepository(RepositoryWrapper):
    def get_revision(self, space_id, revision_id):
        if self.committed:
            return None
        return super().get_revision(space_id, revision_id)


class ChangedBindingRepository(RepositoryWrapper):
    def publish_prospective_publication(
        self, command, publication_id, prospective_request_sha256, result_bindings
    ):
        result = super().publish_prospective_publication(
            command, publication_id, prospective_request_sha256, result_bindings
        )
        changed = result.prospective_result.model_copy(
            update={
                "results": [
                    ProspectiveResultBinding(
                        client_op_id="extra", result_kind="entity", durable_id="ent:extra"
                    )
                ]
            }
        )
        return result.model_copy(update={"prospective_result": changed})


class LostResponseAndRecoveryRepository(RepositoryWrapper):
    def publish_prospective_publication(
        self, command, publication_id, prospective_request_sha256, result_bindings
    ):
        super().publish_prospective_publication(
            command, publication_id, prospective_request_sha256, result_bindings
        )
        raise RuntimeError("response lost")

    def get_prospective_publication(self, space_id, publication_id):
        raise RuntimeError("recovery unavailable")


def _prepared(repo, prepared_id: str):
    return support.prepare(repo, support.intent(), prepared_id)


def test_known_commit_with_unavailable_child_is_not_outcome_unknown() -> None:
    inner = support.repository()
    prepared = _prepared(inner, "prepared:wk4-unavailable")
    with pytest.raises(CommittedChangeVerificationUnavailable) as caught:
        WorldChangeCommitter(
            DungeonMindVNextCommitAuthority(UnavailableChildRepository(inner))
        ).commit_prepared_change(prepared, "user:keeper")
    assert caught.value.committed is True
    assert caught.value.retry_safe is True
    assert inner.get_prospective_publication("space:lab", prepared.prepared_change_id) is not None


@pytest.mark.parametrize("wrapper", [MissingChildRepository, ChangedBindingRepository])
def test_known_commit_corruption_is_integrity_failure(wrapper) -> None:
    inner = support.repository()
    prepared = _prepared(inner, f"prepared:wk4-{wrapper.__name__}")
    with pytest.raises(CommittedChangeVerificationIntegrityFailure) as caught:
        WorldChangeCommitter(
            DungeonMindVNextCommitAuthority(wrapper(inner))
        ).commit_prepared_change(prepared, "user:keeper")
    assert caught.value.committed is True


def test_genuine_outcome_unknown_maps_retry_safe_identity() -> None:
    inner = support.repository()
    prepared = _prepared(inner, "prepared:wk4-unknown")
    with pytest.raises(CommittedChangeOutcomeUnknown) as caught:
        WorldChangeCommitter(
            DungeonMindVNextCommitAuthority(LostResponseAndRecoveryRepository(inner))
        ).commit_prepared_change(prepared, "user:keeper")
    assert caught.value.retry_safe is True
    assert caught.value.prepared_change_id == prepared.prepared_change_id
    assert caught.value.publication_id == prepared.prepared_change_id


class WitnessAuthority:
    def __init__(self, witness: CommitAuthorityWitness) -> None:
        self.witness = witness

    def commit_and_verify(self, prepared):
        return self.witness


@pytest.mark.parametrize(
    "results",
    [
        (),
        (
            CommitResultBinding("npc-7", "assertion", "asrt:wrong-kind"),
            CommitResultBinding("rel-4", "assertion", "asrt:relationship"),
        ),
        (
            CommitResultBinding("npc-7", "entity", "ent:object"),
            CommitResultBinding("rel-4", "assertion", "asrt:relationship"),
            CommitResultBinding("extra", "entity", "ent:extra"),
        ),
    ],
)
def test_application_rejects_missing_wrong_kind_and_extra_bindings(results) -> None:
    repo = support.repository()
    prepared = _prepared(repo, "prepared:wk4-witness")
    witness = CommitAuthorityWitness(
        space_id=prepared.space_id,
        publication_id=prepared.prepared_change_id,
        expected_parent_revision_id=prepared.expected_parent_revision_id,
        child_revision_id="rev:child",
        child_graph_payload_sha256="a" * 64,
        results=results,
    )
    with pytest.raises(CommitAuthorityIntegrityFailure):
        WorldChangeCommitter(WitnessAuthority(witness)).commit_prepared_change(
            prepared, "user:keeper"
        )
