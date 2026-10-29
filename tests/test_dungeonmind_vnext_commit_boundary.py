from __future__ import annotations

from copy import deepcopy

import pytest
from dungeonmind.application.vnext.builder import build_parsed_knowledge_revision
from dungeonmind.application.vnext.materialization import decode_native_graph_payload
from dungeonmind.contracts.vnext.prospective import ProspectiveResultBinding
from dungeonmind.domain.errors import PersistenceIntegrityError, PersistenceUnavailableError

import test_wk4_commit_prepared_change as support
from worldkeeper.application.authority import CommitAuthorityWitness, CommitResultBinding
from worldkeeper.application.commit import (
    CommitAuthorityIntegrityFailure,
    CommittedChangeOutcomeUnknown,
    CommittedChangeVerificationIntegrityFailure,
    CommittedChangeVerificationUnavailable,
    PreparedChangeConflict,
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


class MissingOnlyOnWorldKeeperReadRepository(RepositoryWrapper):
    """Allow DungeonMind's two verification reads, then hide WK's exact child."""

    def __init__(self, inner) -> None:
        super().__init__(inner)
        self.post_commit_child_reads = 0

    def get_revision(self, space_id, revision_id):
        if self.committed:
            self.post_commit_child_reads += 1
            if self.post_commit_child_reads == 3:
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


def test_worldkeeper_independent_missing_child_read_is_integrity_failure() -> None:
    inner = support.repository()
    prepared = _prepared(inner, "prepared:wk4-wk-read-missing")
    repository = MissingOnlyOnWorldKeeperReadRepository(inner)

    with pytest.raises(CommittedChangeVerificationIntegrityFailure) as caught:
        WorldChangeCommitter(DungeonMindVNextCommitAuthority(repository)).commit_prepared_change(
            prepared, "user:keeper"
        )

    assert repository.post_commit_child_reads == 3
    assert caught.value.committed is True
    assert caught.value.child_revision_id


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


def _name_intent(label):
    from worldkeeper import CreateFact, CreateObject, LiteralFactValue, WorldChangeIntent

    return WorldChangeIntent(
        "space:lab",
        "producer:regression",
        (
            CreateObject(
                "named-person",
                (
                    CreateFact(
                        "name", "lab:title", LiteralFactValue.from_json(label), support.metadata()
                    ),
                ),
            ),
        ),
    )


@pytest.mark.parametrize("changed_label", ["Changed", "Original"])
def test_descendant_changed_intent_is_conflict_without_implicating_original_child(changed_label):
    repo = support.repository()
    service = support.committer(repo)
    original = support.prepare(repo, _name_intent("Original"), "prepared:stable-key")
    first = service.commit_prepared_change(original, "operator-delegated-test")
    descendant = support.prepare(repo, _name_intent("Descendant"), "prepared:independent-child")
    service.commit_prepared_change(descendant, "operator-delegated-test")
    events, head = repo.head_events("space:lab"), repo.get_head("space:lab")
    assert service.commit_prepared_change(original, "operator-delegated-test") == first
    changed = support.prepare(repo, _name_intent(changed_label), "prepared:stable-key")
    try:
        with pytest.raises(PreparedChangeConflict):
            service.commit_prepared_change(changed, "operator-delegated-test")
    finally:
        assert repo.head_events("space:lab") == events
        assert repo.get_head("space:lab") == head
        assert service.commit_prepared_change(original, "operator-delegated-test") == first


def test_same_parent_changed_meaning_remains_an_idempotency_conflict():
    repo = support.repository()
    original = support.prepare(repo, _name_intent("Original"), "prepared:stable-parent")
    changed = support.prepare(repo, _name_intent("Changed"), "prepared:stable-parent")
    service = support.committer(repo)
    first = service.commit_prepared_change(original, "operator-test")
    events, head = repo.head_events("space:lab"), repo.get_head("space:lab")
    with pytest.raises(PreparedChangeConflict):
        service.commit_prepared_change(changed, "operator-test")
    assert repo.head_events("space:lab") == events
    assert repo.get_head("space:lab") == head
    assert service.commit_prepared_change(original, "operator-test") == first


class FailureClassificationRepository(RepositoryWrapper):
    """Publish through real Core once, then fault only the failure inspection."""

    def __init__(self, inner, fault):
        super().__init__(inner)
        self.fault = fault

    def publish_prospective_publication(
        self, command, publication_id, prospective_request_sha256, result_bindings
    ):
        super().publish_prospective_publication(
            command, publication_id, prospective_request_sha256, result_bindings
        )
        raise PersistenceIntegrityError("injected post-publication verification failure")

    def get_prospective_publication(self, space_id, publication_id):
        aggregate = super().get_prospective_publication(space_id, publication_id)
        if self.fault == "missing":
            return None
        if self.fault == "unavailable":
            raise PersistenceUnavailableError("aggregate unavailable")
        if self.fault == "request_digest":
            return aggregate.model_copy(
                update={
                    "prospective_result": aggregate.prospective_result.model_copy(
                        update={"prospective_request_sha256": "0" * 64}
                    )
                }
            )
        if self.fault == "result_identity":
            return aggregate.model_copy(
                update={
                    "prospective_result": aggregate.prospective_result.model_copy(
                        update={"space_id": "space:other"}
                    )
                }
            )
        if self.fault in ("command_sha", "child_id", "payload_sha", "bindings"):
            field = {
                "command_sha": "command_sha256",
                "child_id": "published_revision_id",
                "payload_sha": "graph_payload_sha256",
            }.get(self.fault)
            receipt = aggregate.publication_receipt
            result = aggregate.prospective_result
            if field:
                receipt = receipt.model_copy(
                    update={field: "rev:missing" if self.fault == "child_id" else "0" * 64}
                )
            if self.fault == "child_id":
                result = result.model_copy(update={"published_revision_id": "rev:missing"})
            if self.fault == "bindings":
                result = result.model_copy(update={"results": []})
            return aggregate.model_copy(
                update={"publication_receipt": receipt, "prospective_result": result}
            )
        if self.fault in ("parent", "receipt_mismatch"):
            return aggregate.model_copy(
                update={
                    "publication_receipt": aggregate.publication_receipt.model_copy(
                        update={"expected_parent_revision_id": "rev:other"}
                    )
                }
            )
        return aggregate

    def get_publication_receipt(self, space_id, publication_id):
        receipt = super().get_publication_receipt(space_id, publication_id)
        if self.fault == "receipt_unavailable":
            raise PersistenceUnavailableError("receipt unavailable")
        if receipt and self.fault in ("command_sha", "child_id", "payload_sha"):
            field = {
                "command_sha": "command_sha256",
                "child_id": "published_revision_id",
                "payload_sha": "graph_payload_sha256",
            }[self.fault]
            return receipt.model_copy(
                update={field: "rev:missing" if self.fault == "child_id" else "0" * 64}
            )
        if receipt and self.fault == "parent":
            return receipt.model_copy(update={"expected_parent_revision_id": "rev:other"})
        return receipt


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "unavailable",
        "request_digest",
        "result_identity",
        "parent",
        "receipt_mismatch",
        "receipt_unavailable",
        "command_sha",
        "child_id",
        "payload_sha",
        "bindings",
    ],
)
def test_unverified_aggregate_does_not_establish_that_submitted_intent_committed(fault):
    inner = support.repository()
    prepared = _prepared(inner, f"prepared:wk-exact-{fault}")
    with pytest.raises(CommitAuthorityIntegrityFailure) as caught:
        WorldChangeCommitter(
            DungeonMindVNextCommitAuthority(FailureClassificationRepository(inner, fault))
        ).commit_prepared_change(prepared, "operator-test")
    assert not getattr(caught.value, "committed", False)
    # Fault injection changed no durable authority: actual Core can still replay
    # and verify the exact original publication without allocating another child.
    events, head = inner.head_events("space:lab"), inner.get_head("space:lab")
    first = support.committer(inner).commit_prepared_change(prepared, "operator-test")
    assert first.child_revision_id == head.head_revision_id
    assert inner.head_events("space:lab") == events
    assert inner.get_head("space:lab") == head


def test_exact_request_match_preserves_known_committed_integrity_failure():
    inner = support.repository()
    prepared = _prepared(inner, "prepared:wk-exact-known")
    with pytest.raises(CommittedChangeVerificationIntegrityFailure) as caught:
        WorldChangeCommitter(
            DungeonMindVNextCommitAuthority(FailureClassificationRepository(inner, "none"))
        ).commit_prepared_change(prepared, "operator-test")
    assert caught.value.committed is True
    assert caught.value.child_revision_id == inner.get_head("space:lab").head_revision_id
