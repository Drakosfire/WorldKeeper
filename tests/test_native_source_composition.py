"""Core owns source admission; WK consumes its actual evidence and current head."""

from __future__ import annotations

import hashlib
from copy import deepcopy

import pytest
from dungeonmind.application.vnext.native_source_access import (
    open_admitted_native_text,
    open_native_text_source_access_context,
)
from dungeonmind.application.vnext.native_source_admission import (
    publish_native_text_source_evidence,
)
from dungeonmind.contracts.vnext.common import PublicVisibility
from dungeonmind.contracts.vnext.knowledge import PublishKnowledgeRevisionCommand
from dungeonmind.contracts.vnext.native_source import (
    NativeTextEvidenceSpanRequestV1,
    NativeTextSourceAdmissionV1,
    NativeTextSourceOriginV1,
)
from dungeonmind.infrastructure.memory.vnext_sources import InMemoryNativeSourceEvidenceRepository

import test_wk4_commit_prepared_change as support
from worldkeeper import (
    CreateFact,
    CreateObject,
    LiteralFactValue,
    UseExisting,
    WorldChangeIntent,
)
from worldkeeper.application.commit import PreparedChangeStale
from worldkeeper.application.preparation import InvalidWorldChange
from worldkeeper.integrations.dungeonmind import DungeonMindWorldKeeperRuntime

BODY = "Copper key — beside the door.\n"


def initialized():
    seed = support.repository()
    parent = seed.get_revision("space:lab", seed.get_head("space:lab").head_revision_id)
    payload = deepcopy(parent.graph_payload)
    payload["evidence"] = []
    repo = InMemoryNativeSourceEvidenceRepository()
    repo.publish_revision(
        PublishKnowledgeRevisionCommand(
            space_id="space:lab",
            operation_ids=["op:genesis"],
            graph_schema=parent.revision.graph_schema,
            graph_payload=payload,
            domain_contract_ref=parent.revision.domain_contract_ref,
            semantic_profile_ref=parent.revision.semantic_profile_ref,
            created_at=support.NOW,
        )
    )
    return repo


def runtime(repo, prepared_id="prepared:from-source"):
    contract, profile = support.descriptors()
    return DungeonMindWorldKeeperRuntime(
        repository=repo,
        domain_contract=contract,
        semantic_profile=profile,
        clock=lambda: support.NOW,
        prepared_id_factory=lambda: prepared_id,
    )


def source_request(repo):
    encoded = BODY.encode("utf-8")
    return NativeTextSourceAdmissionV1(
        space_id="space:lab",
        admission_id="admit:workspace",
        expected_parent_revision_id=repo.get_head("space:lab").head_revision_id,
        created_at=support.NOW,
        body_text=BODY,
        expected_body_sha256=hashlib.sha256(encoded).hexdigest(),
        source_classification="lab:authored_text",
        authority="primary",
        visibility=PublicVisibility(),
        origin=NativeTextSourceOriginV1(
            namespace="fixture.workspace", object_id="document:one", revision_id="revision:one"
        ),
        spans=[
            NativeTextEvidenceSpanRequestV1(
                client_ref="opening",
                evidence_role="support",
                start_byte=0,
                end_byte=len(encoded),
                expected_slice_sha256=hashlib.sha256(encoded).hexdigest(),
            )
        ],
    )


def admit(repo, request):
    contract, profile = support.descriptors()
    return publish_native_text_source_evidence(
        repository=repo,
        request=request,
        domain_contract=contract,
        semantic_profile=profile,
    )


def change(evidence_id, fact_id="sourced-fact", subject="ent:castle"):
    from dataclasses import replace

    metadata = replace(support.metadata(), evidence_ref_ids=(evidence_id,))
    return WorldChangeIntent(
        "space:lab",
        "producer:test",
        (
            UseExisting(
                subject,
                (
                    CreateFact(
                        fact_id,
                        "lab:title",
                        LiteralFactValue(BODY.strip()),
                        metadata,
                    ),
                ),
            ),
        ),
    )


def open_source(repo, revision_id, evidence_id):
    contract, _ = support.descriptors()
    context = open_native_text_source_access_context(
        repository=repo,
        space_id="space:lab",
        revision_id=revision_id,
        domain_contract=contract,
    )
    return open_admitted_native_text(context, evidence_id)


def test_native_source_then_wk_publication_uses_actual_head_and_exact_returned_bindings():
    repo = initialized()
    old_head = repo.get_head("space:lab")
    old = repo.get_revision("space:lab", old_head.head_revision_id)
    request = source_request(repo)
    receipt = admit(repo, request)
    source_child = repo.get_revision("space:lab", receipt.published_revision_id)
    for name in ("entities", "assertions", "aliases"):
        assert source_child.graph_payload[name] == old.graph_payload[name]
    (binding,) = receipt.bindings
    assert receipt.origin == request.origin
    assert binding.client_ref == "opening"
    assert receipt.source_artifact_id != request.origin.object_id

    service = runtime(repo)
    prepared = service.prepare_change(change(binding.evidence_ref_id))
    actual_head = repo.get_head("space:lab")
    assert prepared.expected_parent_revision_id == actual_head.head_revision_id
    (witness,) = prepared.evidence_witnesses
    assert witness.source_artifact_id == receipt.source_artifact_id
    assert witness.source_revision_id == receipt.source_revision_id
    assert witness.source_span_ref_id == binding.span_id
    result = service.commit_prepared_change(prepared, confirmed_by="user:test")
    child = repo.get_revision("space:lab", result.child_revision_id)
    assert child.graph_payload["entities"] == old.graph_payload["entities"]
    (assertion,) = child.graph_payload["assertions"]
    assert assertion["subject_entity_id"] == "ent:castle"
    assert assertion["metadata"]["evidence_ref_ids"] == [binding.evidence_ref_id]
    assert result.object_results == ()
    assert result.assertion_results[0].durable_assertion_id == assertion["assertion_id"]
    assert result.verification.exact_child_read_back
    access = open_source(repo, result.child_revision_id, binding.evidence_ref_id)
    assert access.status == "available"
    assert access.body_text == BODY
    assert access.body_sha256 == request.expected_body_sha256
    assert (access.span_start_byte, access.span_end_byte) == (0, len(BODY.encode("utf-8")))


def test_missing_evidence_refuses_before_admission_and_old_prepared_parent_refuses_after_it():
    repo = initialized()
    service = runtime(repo)
    before = repo.get_head("space:lab")
    with pytest.raises(InvalidWorldChange, match="evidence_ref_absent"):
        service.prepare_change(change("not-an-admitted-evidence-id"))
    assert repo.get_head("space:lab") == before
    stale = service.prepare_change(
        WorldChangeIntent(
            "space:lab",
            "producer:test",
            (CreateObject("never-published"),),
        )
    )
    request = source_request(repo)
    receipt = admit(repo, request)
    with pytest.raises(PreparedChangeStale):
        service.commit_prepared_change(stale, confirmed_by="user:test")
    assert repo.get_head("space:lab").head_revision_id == receipt.published_revision_id
    child = repo.get_revision("space:lab", receipt.published_revision_id)
    assert len(child.graph_payload["entities"]) == 1
    assert child.graph_payload["assertions"] == []
    assert (
        open_source(
            repo, receipt.published_revision_id, receipt.bindings[0].evidence_ref_id
        ).body_text
        == BODY
    )


def test_semantic_refusal_preserves_the_separately_committed_source():
    repo = initialized()
    request = source_request(repo)
    receipt = admit(repo, request)
    evidence_id = receipt.bindings[0].evidence_ref_id
    with pytest.raises(InvalidWorldChange, match="durable_endpoint_absent"):
        runtime(repo).prepare_change(change(evidence_id, subject="ent:missing"))
    assert repo.get_head("space:lab").head_revision_id == receipt.published_revision_id
    assert repo.get_native_source_admission_receipt("space:lab", request.admission_id) == receipt
    assert open_source(repo, receipt.published_revision_id, evidence_id).body_text == BODY


def test_source_and_semantic_replay_after_descendant_preserve_actual_current_head():
    repo = initialized()
    request = source_request(repo)
    receipt = admit(repo, request)
    evidence_id = receipt.bindings[0].evidence_ref_id
    service = runtime(repo)
    prepared = service.prepare_change(change(evidence_id))
    first = service.commit_prepared_change(prepared, confirmed_by="user:test")
    descendant_service = runtime(repo, "prepared:descendant")
    descendant = descendant_service.commit_prepared_change(
        descendant_service.prepare_change(change(evidence_id, "descendant-fact")),
        confirmed_by="user:test",
    )
    head = repo.get_head("space:lab")
    events = repo.head_events("space:lab")
    epoch = repo.open_native_source_view("space:lab").epoch
    assert admit(repo, request) == receipt
    assert service.commit_prepared_change(prepared, confirmed_by="user:test") == first
    assert repo.get_head("space:lab") == head
    assert repo.head_events("space:lab") == events
    assert repo.open_native_source_view("space:lab").epoch == epoch
    assert descendant.child_revision_id != receipt.published_revision_id
    latest = repo.get_revision("space:lab", head.head_revision_id)
    assert len(latest.graph_payload["entities"]) == 1
    assert len(latest.graph_payload["assertions"]) == 2
    # Preparing after replay captures the actual descendant, not the old source child.
    fresh = runtime(repo, "prepared:fresh").prepare_change(change(evidence_id, "fresh-fact"))
    assert fresh.expected_parent_revision_id == head.head_revision_id
    assert fresh.expected_parent_revision_id != receipt.published_revision_id
    assert open_source(repo, head.head_revision_id, evidence_id).body_text == BODY
