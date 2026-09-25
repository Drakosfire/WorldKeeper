from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from dungeonmind.application.vnext.materialization import (
    NATIVE_VNEXT_GRAPH_SCHEMA,
    encode_native_graph_payload,
)
from dungeonmind.contracts.semantic_profile import SemanticProfileRef
from dungeonmind.contracts.vnext.domain import (
    DomainContractDescriptor,
    Entity,
    OpenPredicateNamespace,
    SemanticProfileDescriptorV2,
    SemanticProfileDescriptorV3,
    SemanticProfilePredicate,
)
from dungeonmind.contracts.vnext.knowledge import DomainContractRef, PublishKnowledgeRevisionCommand
from dungeonmind.contracts.vnext.source import EvidenceRefV3
from dungeonmind.domain.canonical import canonical_sha256
from dungeonmind.infrastructure.memory.vnext_knowledge import InMemoryKnowledgeRevisionRepository

from worldkeeper.application.commit import (
    PreparedChangeConflict,
    PreparedChangeIntegrityFailure,
    PreparedChangeStale,
    WorldChangeCommitter,
)
from worldkeeper.application.contracts import (
    AssertionMetadata,
    CreateFact,
    CreateObject,
    CreateRelationship,
    DurableObjectRef,
    LiteralFactValue,
    ResultOf,
    ScopeBinding,
    TemporalScope,
    UseExisting,
    Visibility,
    WorldChangeIntent,
)
from worldkeeper.application.preparation import WorldChangePreparer
from worldkeeper.integrations.dungeonmind.vnext_commit import DungeonMindVNextCommitAuthority
from worldkeeper.integrations.dungeonmind.vnext_prepare import (
    DungeonMindVNextPreparationAuthority,
)

NOW = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def descriptors():
    contract = DomainContractDescriptor(
        domain_id="lab.domain",
        domain_revision="1",
        scope_axes=["lab:scope"],
        claim_modes=["lab:fact"],
        admission_policy_id="lab.always",
    )
    profile = SemanticProfileDescriptorV2(
        profile_id="lab.profile",
        profile_revision="1",
        term_namespaces=["lab"],
        predicates=[
            SemanticProfilePredicate(term="lab:title", allowed_value_kinds=["literal"]),
            SemanticProfilePredicate(term="lab:located_at", allowed_value_kinds=["entity_ref"]),
        ],
    )
    return contract, profile


def repository(*, semantic_profile: SemanticProfileDescriptorV2 | None = None):
    repo = InMemoryKnowledgeRevisionRepository()
    contract, profile = descriptors()
    profile = semantic_profile or profile
    payload = encode_native_graph_payload(
        entities={"ent:castle": Entity(entity_id="ent:castle")},
        assertions={},
        aliases={},
        evidence={
            "ev:lab": EvidenceRefV3(
                evidence_ref_id="ev:lab",
                source_artifact_id="art:lab",
                source_revision_id="srcrev:lab",
                evidence_role="support",
                can_open_source=True,
                can_highlight_span=False,
                locator="chapter-1",
            )
        },
    )
    repo.publish_revision(
        PublishKnowledgeRevisionCommand(
            space_id="space:lab",
            operation_ids=["op:genesis"],
            graph_schema=NATIVE_VNEXT_GRAPH_SCHEMA,
            graph_payload=payload,
            domain_contract_ref=DomainContractRef(
                domain_id=contract.domain_id,
                domain_revision=contract.domain_revision,
                descriptor_sha256=canonical_sha256(contract.model_dump(mode="json")),
            ),
            semantic_profile_ref=SemanticProfileRef(
                profile_id=profile.profile_id,
                profile_revision=profile.profile_revision,
                descriptor_sha256=canonical_sha256(profile.model_dump(mode="json")),
            ),
            created_at=NOW,
        )
    )
    return repo


def metadata() -> AssertionMetadata:
    return AssertionMetadata(
        scope=(ScopeBinding("lab:scope", "one"),),
        visibility=Visibility(),
        epistemic_basis="asserted",
        claim_mode="lab:fact",
        standing="established",
        evidence_ref_ids=("ev:lab",),
        temporal_scope=TemporalScope(),
    )


def intent(*, label: str | None = None) -> WorldChangeIntent:
    facts = ()
    if label is not None:
        facts = (CreateFact("fact-1", "lab:title", LiteralFactValue.from_json(label), metadata()),)
    return WorldChangeIntent(
        "space:lab",
        "producer:test",
        (
            UseExisting("ent:castle"),
            CreateObject("npc-7", facts),
            CreateRelationship(
                "rel-4",
                ResultOf("npc-7"),
                "lab:located_at",
                DurableObjectRef("ent:castle"),
                metadata(),
            ),
        ),
    )


def prepare(
    repo,
    change: WorldChangeIntent,
    prepared_id: str,
    at: datetime = NOW,
    *,
    semantic_profile: SemanticProfileDescriptorV2 | None = None,
):
    contract, profile = descriptors()
    profile = semantic_profile or profile
    return WorldChangePreparer(
        authority=DungeonMindVNextPreparationAuthority(repo),
        domain_contract=contract,
        semantic_profile=profile,
        clock=lambda: at,
        prepared_id_factory=lambda: prepared_id,
    ).prepare_change(change)


def committer(repo) -> WorldChangeCommitter:
    return WorldChangeCommitter(DungeonMindVNextCommitAuthority(repo))


def test_canonical_commit_verifies_exact_child_and_replays_same_mapping() -> None:
    repo = repository()
    prepared = prepare(repo, intent(), "prepared:wk4-canonical")
    service = committer(repo)

    first = service.commit_prepared_change(prepared, "user:keeper")
    events = repo.head_events("space:lab")
    second = service.commit_prepared_change(prepared, "user:keeper")

    assert second == first
    assert len(repo.head_events("space:lab")) == len(events)
    assert first.verification.exact_child_read_back is True
    assert first.object_results[0].client_op_id == "npc-7"
    assert first.object_results[0].durable_object_id.startswith("ent:")
    assert first.assertion_results[0].client_op_id == "rel-4"
    assert first.assertion_results[0].durable_assertion_id.startswith("asrt:")
    assert first.assertion_results[0].semantic_role == "relationship"
    child = repo.get_revision("space:lab", first.child_revision_id)
    assert child is not None
    assertion = next(
        item
        for item in child.graph_payload["assertions"]
        if item["assertion_id"] == first.assertion_results[0].durable_assertion_id
    )
    assert assertion["subject_entity_id"] == first.object_results[0].durable_object_id
    assert assertion["value"] == {"kind": "entity_ref", "entity_id": "ent:castle"}


def test_v3_custom_relationship_commits_exact_predicate_and_child() -> None:
    _, old_profile = descriptors()
    profile = SemanticProfileDescriptorV3(
        profile_id=old_profile.profile_id,
        profile_revision="2",
        term_namespaces=["lab", "lab.custom"],
        predicates=old_profile.predicates,
        open_predicate_namespaces=[
            OpenPredicateNamespace(namespace="lab.custom", allowed_value_kinds=["entity_ref"])
        ],
    )
    repo = repository(semantic_profile=profile)
    change = intent()
    relationship = change.operations[-1]
    change = replace(
        change,
        operations=(
            *change.operations[:-1],
            replace(relationship, predicate="lab.custom:works_at"),
        ),
    )
    prepared = prepare(repo, change, "prepared:wk4-v3", semantic_profile=profile)
    result = committer(repo).commit_prepared_change(prepared, "user:keeper")

    child = repo.get_revision("space:lab", result.child_revision_id)
    assert child is not None
    assertion = next(
        item
        for item in child.graph_payload["assertions"]
        if item["assertion_id"] == result.assertion_results[0].durable_assertion_id
    )
    assert result.verification.exact_child_read_back is True
    assert assertion["predicate"] == "lab.custom:works_at"
    assert assertion["subject_entity_id"] == result.object_results[0].durable_object_id


def test_fact_role_and_use_existing_has_no_result() -> None:
    repo = repository()
    result = committer(repo).commit_prepared_change(
        prepare(repo, intent(label="Aldren"), "prepared:wk4-fact"), "user:keeper"
    )

    assert [item.client_op_id for item in result.object_results] == ["npc-7"]
    assert [(item.client_op_id, item.semantic_role) for item in result.assertion_results] == [
        ("fact-1", "fact"),
        ("rel-4", "relationship"),
    ]
    assert all(item.client_op_id != "ent:castle" for item in result.object_results)


def test_blank_confirmation_and_tamper_fail_before_publication() -> None:
    repo = repository()
    prepared = prepare(repo, intent(), "prepared:wk4-guard")
    before = repo.head_events("space:lab")
    with pytest.raises(ValueError, match="confirmed_by"):
        committer(repo).commit_prepared_change(prepared, " ")
    with pytest.raises(PreparedChangeIntegrityFailure):
        committer(repo).commit_prepared_change(
            replace(prepared, parent_graph_payload_sha256="b" * 64), "user:keeper"
        )
    assert repo.head_events("space:lab") == before


def test_stale_parent_and_same_publication_changed_request_remain_distinct() -> None:
    repo = repository()
    stale = prepare(repo, intent(), "prepared:wk4-stale")
    first = prepare(repo, intent(), "prepared:wk4-conflict")
    changed = prepare(repo, intent(label="changed"), "prepared:wk4-conflict")
    committer(repo).commit_prepared_change(first, "user:keeper")

    with pytest.raises(PreparedChangeStale):
        committer(repo).commit_prepared_change(stale, "user:keeper")
    with pytest.raises(PreparedChangeConflict):
        committer(repo).commit_prepared_change(changed, "user:keeper")


def test_replay_after_descendant_verifies_historical_child_without_head_rewind() -> None:
    repo = repository()
    first_prepared = prepare(repo, intent(), "prepared:wk4-first")
    first = committer(repo).commit_prepared_change(first_prepared, "user:keeper")
    descendant_prepared = prepare(
        repo,
        WorldChangeIntent("space:lab", "producer:test", (CreateObject("npc-8"),)),
        "prepared:wk4-descendant",
        NOW + timedelta(seconds=1),
    )
    descendant = committer(repo).commit_prepared_change(descendant_prepared, "user:keeper")
    head_before = repo.get_head("space:lab")

    replay = committer(repo).commit_prepared_change(first_prepared, "user:keeper")

    assert replay == first
    assert repo.get_head("space:lab") == head_before
    assert replay.child_revision_id != descendant.child_revision_id
