from __future__ import annotations

from copy import deepcopy

import pytest
from dungeonmind.application.vnext.builder import build_parsed_knowledge_revision
from dungeonmind.application.vnext.materialization import decode_native_graph_payload
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
from worldkeeper.integrations.dungeonmind.vnext_prepare import (
    compile_prepared_change_to_dungeonmind,
)


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


class RecoverableLostResponseRepository(RepositoryWrapper):
    def publish_prospective_publication(
        self, command, publication_id, prospective_request_sha256, result_bindings
    ):
        super().publish_prospective_publication(
            command, publication_id, prospective_request_sha256, result_bindings
        )
        raise RuntimeError("response lost after commit")


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


def test_post_commit_response_loss_recovers_exact_result_through_dungeonmind() -> None:
    inner = support.repository()
    prepared = _prepared(inner, "prepared:wk4-recovered")
    result = WorldChangeCommitter(
        DungeonMindVNextCommitAuthority(RecoverableLostResponseRepository(inner))
    ).commit_prepared_change(prepared, "user:keeper")
    assert result.prepared_change_id == prepared.prepared_change_id
    assert result.object_results[0].client_op_id == "npc-7"
    assert result.assertion_results[0].client_op_id == "rel-4"


def _published_verification_fixture(*, with_fact: bool = False):
    repo = support.repository()
    prepared = support.prepare(
        repo,
        support.intent(label="Aldren" if with_fact else None),
        "prepared:wk4-corruption",
    )
    WorldChangeCommitter(DungeonMindVNextCommitAuthority(repo)).commit_prepared_change(
        prepared, "user:keeper"
    )
    aggregate = repo.get_prospective_publication(prepared.space_id, prepared.prepared_change_id)
    assert aggregate is not None
    stored = repo.get_revision(
        prepared.space_id, aggregate.prospective_result.published_revision_id
    )
    assert stored is not None
    child = build_parsed_knowledge_revision(
        revision=stored.revision,
        decoded_content=decode_native_graph_payload(stored.graph_payload),
    )
    return prepared, compile_prepared_change_to_dungeonmind(prepared), aggregate, child, stored


def test_result_binding_absent_from_exact_child_fails_integrity_verification() -> None:
    prepared, plan, aggregate, child, stored = _published_verification_fixture()
    payload = deepcopy(stored.graph_payload)
    bound_entity = next(
        item.durable_id
        for item in aggregate.prospective_result.results
        if item.client_op_id == "npc-7"
    )
    payload["entities"] = [
        item for item in payload["entities"] if item["entity_id"] != bound_entity
    ]
    with pytest.raises(ValueError, match="bound entity absent"):
        DungeonMindVNextCommitAuthority._verify_child(prepared, plan, aggregate, child, payload)


@pytest.mark.parametrize("field", ["subject_entity_id", "value"])
def test_relationship_endpoint_corruption_fails_exact_child_verification(field) -> None:
    prepared, plan, aggregate, child, stored = _published_verification_fixture()
    payload = deepcopy(stored.graph_payload)
    relationship_id = next(
        item.durable_id
        for item in aggregate.prospective_result.results
        if item.client_op_id == "rel-4"
    )
    relationship = next(
        item for item in payload["assertions"] if item["assertion_id"] == relationship_id
    )
    relationship[field] = (
        "ent:castle"
        if field == "subject_entity_id"
        else {"kind": "entity_ref", "entity_id": "ent:wrong"}
    )
    with pytest.raises(ValueError, match="assertion meaning mismatch"):
        DungeonMindVNextCommitAuthority._verify_child(prepared, plan, aggregate, child, payload)


@pytest.mark.parametrize("field", ["predicate", "value", "metadata"])
def test_fact_semantic_corruption_fails_exact_child_verification(field) -> None:
    prepared, plan, aggregate, child, stored = _published_verification_fixture(with_fact=True)
    payload = deepcopy(stored.graph_payload)
    fact_id = next(
        item.durable_id
        for item in aggregate.prospective_result.results
        if item.client_op_id == "fact-1"
    )
    fact = next(item for item in payload["assertions"] if item["assertion_id"] == fact_id)
    if field == "predicate":
        fact[field] = "lab:located_at"
    elif field == "value":
        fact[field] = {"kind": "literal", "value": "changed"}
    else:
        fact[field]["claim_mode"] = "lab:changed"
    with pytest.raises(ValueError, match="assertion meaning mismatch"):
        DungeonMindVNextCommitAuthority._verify_child(prepared, plan, aggregate, child, payload)


def test_receipt_result_and_child_identity_must_agree_explicitly() -> None:
    prepared, plan, aggregate, child, stored = _published_verification_fixture()
    changed_result = aggregate.prospective_result.model_copy(update={"space_id": "space:other"})
    changed = aggregate.model_copy(update={"prospective_result": changed_result})
    with pytest.raises(ValueError, match="published identity drift"):
        DungeonMindVNextCommitAuthority._verify_child(
            prepared, plan, changed, child, stored.graph_payload
        )


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
