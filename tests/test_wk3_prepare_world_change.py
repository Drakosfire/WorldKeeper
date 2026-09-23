from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime

import pytest
from dungeonmind.contracts.vnext.common import (
    EpistemicBasis,
    KnowledgeStanding,
    PublicVisibility,
    TimelessTemporalScope,
)
from dungeonmind.contracts.vnext.common import (
    ScopeBinding as DungeonMindScopeBinding,
)
from dungeonmind.contracts.vnext.domain import (
    AssertionMetadata as DungeonMindAssertionMetadata,
)
from dungeonmind.contracts.vnext.domain import (
    DomainContractDescriptor,
    SemanticProfileDescriptorV2,
    SemanticProfilePredicate,
)
from dungeonmind.contracts.vnext.prospective import (
    DurableEntityRef,
    ProspectiveCreateAssertion,
    ProspectiveCreateEntity,
    ProspectiveEntityRef,
    ProspectiveEntityRefValue,
)
from dungeonmind.domain.canonical import canonical_sha256

from worldkeeper.application.authority import (
    PreparationAuthorityRef,
    PreparationAuthorityWitness,
    PreparationEvidenceWitness,
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
from worldkeeper.application.preparation import InvalidWorldChange, WorldChangePreparer
from worldkeeper.integrations.dungeonmind.vnext_prepare import (
    compile_prepared_change_to_dungeonmind,
)

NOW = datetime(2026, 9, 23, 12, 0, tzinfo=UTC)


def descriptors():
    contract = DomainContractDescriptor(
        domain_id="lab.domain",
        domain_revision="1",
        scope_axes=["lab:scope"],
        visibility_labels=["lab:hidden"],
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


def authority_witness() -> PreparationAuthorityWitness:
    contract, profile = descriptors()
    return PreparationAuthorityWitness(
        space_id="space:lab",
        head_revision_id="rev:parent",
        graph_payload_sha256="a" * 64,
        domain_contract_ref=PreparationAuthorityRef(
            authority_id=contract.domain_id,
            revision=contract.domain_revision,
            descriptor_sha256=canonical_sha256(contract.model_dump(mode="json")),
        ),
        semantic_profile_ref=PreparationAuthorityRef(
            authority_id=profile.profile_id,
            revision=profile.profile_revision,
            descriptor_sha256=canonical_sha256(profile.model_dump(mode="json")),
        ),
        durable_entity_ids=("ent:castle",),
        evidence_witnesses=(
            PreparationEvidenceWitness(
                evidence_ref_id="ev:lab",
                source_artifact_id="art:lab",
                source_revision_id="srcrev:lab",
                evidence_role="support",
                locator="chapter-1",
                uri=None,
                source_locator=None,
                line_ref=None,
                source_span_ref_id=None,
            ),
        ),
    )


class FakeAuthority:
    def __init__(self, witness: PreparationAuthorityWitness | None = None) -> None:
        self.witness = witness or authority_witness()
        self.reads = 0
        self.mutations = 0

    def read_current_space(self, space_id: str):
        self.reads += 1
        return self.witness

    def publish(self, *_args, **_kwargs):
        self.mutations += 1
        raise AssertionError("prepare attempted mutation")


def metadata(evidence_ref_ids: tuple[str, ...] = ("ev:lab",)) -> AssertionMetadata:
    return AssertionMetadata(
        scope=(ScopeBinding(axis="lab:scope", value="one"),),
        visibility=Visibility(),
        epistemic_basis="asserted",
        claim_mode="lab:fact",
        standing="established",
        evidence_ref_ids=evidence_ref_ids,
        temporal_scope=TemporalScope(),
    )


def canonical_intent() -> WorldChangeIntent:
    return WorldChangeIntent(
        space_id="space:lab",
        producer="producer:worldkeeper-test",
        operations=(
            CreateObject(client_op_id="npc-7"),
            CreateRelationship(
                client_op_id="rel-4",
                source=ResultOf("npc-7"),
                predicate="lab:located_at",
                target=DurableObjectRef("ent:castle"),
                metadata=metadata(),
            ),
        ),
    )


def preparer(
    *,
    authority: FakeAuthority | None = None,
    prepared_id: str = "prepared:wk3-test",
    contract: DomainContractDescriptor | None = None,
    profile: SemanticProfileDescriptorV2 | None = None,
) -> tuple[WorldChangePreparer, FakeAuthority]:
    real_contract, real_profile = descriptors()
    fake = authority or FakeAuthority()
    return (
        WorldChangePreparer(
            authority=fake,
            domain_contract=contract or real_contract,
            semantic_profile=profile or real_profile,
            prepared_id_factory=lambda: prepared_id,
            clock=lambda: NOW,
        ),
        fake,
    )


def test_canonical_prepare_compiles_exact_v5_4_witness_without_mutation() -> None:
    service, authority = preparer()
    prepared = service.prepare_change(canonical_intent())
    plan = compile_prepared_change_to_dungeonmind(prepared)

    assert prepared.prepared_change_id == "prepared:wk3-test"
    assert prepared.dungeonmind_publication_id == prepared.prepared_change_id
    assert prepared.expected_parent_revision_id == "rev:parent"
    assert prepared.parent_graph_payload_sha256 == "a" * 64
    assert prepared.prospective_handles[0].client_op_id == "npc-7"
    assert prepared.evidence_witnesses[0].evidence_ref_id == "ev:lab"
    assert len(prepared.compiled_plan_digest) == 64
    assert authority.reads == 1
    assert authority.mutations == 0

    entity, relationship = plan.prospective_contribution.items
    assert isinstance(entity, ProspectiveCreateEntity)
    assert entity.client_op_id == "npc-7"
    assert entity.item_id != entity.client_op_id
    assert isinstance(relationship, ProspectiveCreateAssertion)
    assert relationship.client_op_id == "rel-4"
    assert relationship.item_id != relationship.client_op_id
    assert relationship.subject == ProspectiveEntityRef(client_op_id="npc-7")
    assert relationship.value == ProspectiveEntityRefValue(
        entity=DurableEntityRef(entity_id="ent:castle")
    )
    assert plan.publication_id == prepared.prepared_change_id
    assert plan.publication.operation_ids == (prepared.prepared_change_id,)
    assert plan.publication.expected_parent_revision_id == "rev:parent"
    assert plan.prospective_contribution.status == "finalized"
    assert plan.prospective_contribution.source_refs == ["art:lab"]
    assert all(item.disposition == "accepted" for item in plan.dispositions)

    serialized = plan.prospective_contribution.model_dump_json()
    assert "result_of" in serialized
    assert "ent:castle" in serialized
    assert "ent:" not in serialized.replace("ent:castle", "")
    assert "asrt:" not in serialized


def test_object_fact_and_use_existing_compile_losslessly() -> None:
    intent = WorldChangeIntent(
        space_id="space:lab",
        producer="producer:test",
        operations=(
            UseExisting("ent:castle"),
            CreateObject(
                client_op_id="npc-7",
                facts=(
                    CreateFact(
                        client_op_id="fact-1",
                        predicate="lab:title",
                        value=LiteralFactValue.from_json({"text": ["A", "B"]}),
                        metadata=metadata(),
                    ),
                ),
            ),
        ),
    )
    service, _authority = preparer()
    prepared = service.prepare_change(intent)
    plan = compile_prepared_change_to_dungeonmind(prepared)

    assert len(plan.prospective_contribution.items) == 2
    fact = plan.prospective_contribution.items[1]
    assert isinstance(fact, ProspectiveCreateAssertion)
    assert fact.subject == ProspectiveEntityRef(client_op_id="npc-7")
    assert fact.value.model_dump(mode="json") == {
        "kind": "literal",
        "value": {"text": ["A", "B"]},
    }
    assert all(item.client_op_id != item.item_id for item in plan.prospective_contribution.items)


@pytest.mark.parametrize(
    ("intent", "reason"),
    [
        (WorldChangeIntent("", "producer:test", canonical_intent().operations), "blank_space_id"),
        (WorldChangeIntent("space:lab", "producer:test", ()), "empty_operation_list"),
        (
            WorldChangeIntent(
                "space:lab",
                "producer:test",
                (
                    CreateObject("dup"),
                    CreateRelationship(
                        "dup",
                        ResultOf("dup"),
                        "lab:located_at",
                        DurableObjectRef("ent:castle"),
                        metadata(),
                    ),
                ),
            ),
            "duplicate_client_op_id",
        ),
        (
            WorldChangeIntent(
                "space:lab",
                "producer:test",
                (
                    CreateRelationship(
                        "rel",
                        ResultOf("missing"),
                        "lab:located_at",
                        DurableObjectRef("ent:castle"),
                        metadata(),
                    ),
                ),
            ),
            "result_of_missing_create_object",
        ),
        (
            WorldChangeIntent(
                "space:lab",
                "producer:test",
                (
                    CreateRelationship(
                        "rel",
                        DurableObjectRef("ent:missing"),
                        "lab:located_at",
                        DurableObjectRef("ent:castle"),
                        metadata(),
                    ),
                ),
            ),
            "durable_endpoint_absent",
        ),
        (
            WorldChangeIntent(
                "space:lab",
                "producer:test",
                (
                    CreateObject(
                        "npc",
                        (
                            CreateFact(
                                "fact", "lab:title", LiteralFactValue.from_json("X"), metadata()
                            ),
                        ),
                    ),
                    CreateRelationship(
                        "rel",
                        ResultOf("fact"),
                        "lab:located_at",
                        DurableObjectRef("ent:castle"),
                        metadata(),
                    ),
                ),
            ),
            "result_of_assertion",
        ),
        (
            WorldChangeIntent(
                "space:lab",
                "producer:test",
                (
                    CreateObject(
                        "npc",
                        (
                            CreateFact(
                                "fact",
                                "lab:title",
                                LiteralFactValue.from_json("X"),
                                metadata(("ev:missing",)),
                            ),
                        ),
                    ),
                ),
            ),
            "evidence_ref_absent",
        ),
    ],
)
def test_prepare_fails_closed_on_invalid_structure(intent, reason) -> None:
    service, _authority = preparer()
    with pytest.raises(InvalidWorldChange) as caught:
        service.prepare_change(intent)
    assert caught.value.reason == reason


def test_descriptor_mismatches_fail_closed() -> None:
    contract, profile = descriptors()
    bad_contract = contract.model_copy(update={"domain_revision": "2"})
    service, _authority = preparer(contract=bad_contract)
    with pytest.raises(InvalidWorldChange, match="domain_contract_mismatch"):
        service.prepare_change(canonical_intent())

    bad_profile = profile.model_copy(update={"profile_revision": "2"})
    service, _authority = preparer(profile=bad_profile)
    with pytest.raises(InvalidWorldChange, match="semantic_profile_mismatch"):
        service.prepare_change(canonical_intent())


def test_missing_head_and_use_existing_only_fail_closed() -> None:
    service, _authority = preparer(authority=FakeAuthority(witness=None))
    # Explicitly overwrite the default witness for this test.
    service._authority.witness = None  # type: ignore[attr-defined]
    with pytest.raises(InvalidWorldChange, match="missing_current_head"):
        service.prepare_change(canonical_intent())

    service, _authority = preparer()
    with pytest.raises(InvalidWorldChange, match="no_contribution_items"):
        service.prepare_change(
            WorldChangeIntent("space:lab", "producer:test", (UseExisting("ent:castle"),))
        )


def test_prepared_result_is_immutable_isolated_and_repeatable() -> None:
    source_value = {"nested": ["original"]}
    fact = CreateFact(
        client_op_id="fact-1",
        predicate="lab:title",
        value=LiteralFactValue.from_json(source_value),
        metadata=metadata(),
    )
    source_value["nested"].append("mutated")
    intent = WorldChangeIntent("space:lab", "producer:test", (CreateObject("npc-7", (fact,)),))
    service, _authority = preparer()
    prepared = service.prepare_change(intent)
    first = compile_prepared_change_to_dungeonmind(prepared)
    second = compile_prepared_change_to_dungeonmind(prepared)

    assert first == second
    assert first.prospective_contribution.items[1].value.model_dump(mode="json") == {
        "kind": "literal",
        "value": {"nested": ["original"]},
    }
    with pytest.raises(FrozenInstanceError):
        prepared.space_id = "space:other"  # type: ignore[misc]


def test_authority_mutation_changes_digest_and_reprepare_gets_new_identity() -> None:
    ids = iter(("prepared:one", "prepared:two"))
    contract, profile = descriptors()
    fake = FakeAuthority()
    service = WorldChangePreparer(
        authority=fake,
        domain_contract=contract,
        semantic_profile=profile,
        prepared_id_factory=lambda: next(ids),
        clock=lambda: NOW,
    )
    first = service.prepare_change(canonical_intent())
    fake.witness = replace(
        fake.witness,
        head_revision_id="rev:new-parent",
        graph_payload_sha256="b" * 64,
    )
    second = service.prepare_change(canonical_intent())

    assert first.prepared_change_id != second.prepared_change_id
    assert first.dungeonmind_publication_id == first.prepared_change_id
    assert second.dungeonmind_publication_id == second.prepared_change_id
    assert first.expected_parent_revision_id != second.expected_parent_revision_id
    assert first.compiled_plan_digest != second.compiled_plan_digest


def test_metadata_conversion_matches_dungeonmind_contract() -> None:
    prepared = preparer()[0].prepare_change(canonical_intent())
    relationship = compile_prepared_change_to_dungeonmind(prepared).prospective_contribution.items[
        1
    ]
    assert isinstance(relationship, ProspectiveCreateAssertion)
    assert relationship.metadata == DungeonMindAssertionMetadata(
        scope=[DungeonMindScopeBinding(axis="lab:scope", value="one")],
        visibility=PublicVisibility(),
        epistemic_basis=EpistemicBasis.ASSERTED,
        claim_mode="lab:fact",
        standing=KnowledgeStanding.ESTABLISHED,
        evidence_ref_ids=["ev:lab"],
        temporal_scope=TimelessTemporalScope(),
    )
