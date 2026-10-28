from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest
from dungeonmind.contracts.vnext.domain import SemanticProfilePredicate
from dungeonmind.contracts.vnext.knowledge import PublishKnowledgeRevisionCommand
from dungeonmind.infrastructure.memory.vnext_knowledge import InMemoryKnowledgeRevisionRepository

import test_dungeonmind_vnext_commit_boundary as boundary
import test_wk4_commit_prepared_change as support
from worldkeeper import (
    CreateFact,
    CreateObject,
    LiteralFactValue,
    ScopeBinding,
    TermRefFactValue,
    UseExisting,
    WorldChangeIntent,
)
from worldkeeper.application.commit import (
    CommitAuthorityIntegrityFailure,
    PreparedChangeIntegrityFailure,
    PreparedChangeStale,
    WorldChangeCommitter,
)
from worldkeeper.application.preparation import InvalidWorldChange
from worldkeeper.integrations.dungeonmind import DungeonMindWorldKeeperRuntime
from worldkeeper.integrations.dungeonmind.vnext_commit import DungeonMindVNextCommitAuthority


def runtime(repo, prepared_id="prepared:existing", *, profile=None):
    contract, default_profile = support.descriptors()
    return DungeonMindWorldKeeperRuntime(
        repository=repo,
        domain_contract=contract,
        semantic_profile=profile or default_profile,
        clock=lambda: support.NOW,
        prepared_id_factory=lambda: prepared_id,
    )


def fact(op_id="existing-fact", *, metadata=None):
    return CreateFact(
        op_id,
        "lab:title",
        LiteralFactValue.from_json("New sourced title"),
        metadata or support.metadata(),
    )


def intent(*facts, subject="ent:castle"):
    return WorldChangeIntent("space:lab", "producer:test", (UseExisting(subject, facts),))


@pytest.mark.parametrize("kind", ["literal", "term_ref"])
def test_public_runtime_adds_fact_without_replacing_selected_entity(kind):
    _, profile = support.descriptors()
    profile = profile.model_copy(
        update={
            "predicates": [
                *profile.predicates,
                SemanticProfilePredicate(term="lab:rank", allowed_value_kinds=["term_ref"]),
            ]
        }
    )
    repo = support.repository(semantic_profile=profile)
    service = runtime(repo, profile=profile)
    new_fact = fact()
    if kind == "term_ref":
        new_fact = replace(new_fact, predicate="lab:rank", value=TermRefFactValue("lab:captain"))
    head = repo.get_head("space:lab")
    events = repo.head_events("space:lab")
    prepared = service.prepare_change(intent(new_fact))
    assert repo.get_head("space:lab") == head
    assert repo.head_events("space:lab") == events
    assert prepared.prospective_handles == ()
    assert [w.evidence_ref_id for w in prepared.evidence_witnesses] == ["ev:lab"]

    result = service.commit_prepared_change(prepared, confirmed_by="user:test")
    child = repo.get_revision("space:lab", result.child_revision_id)
    assert [entity["entity_id"] for entity in child.graph_payload["entities"]] == ["ent:castle"]
    (assertion,) = child.graph_payload["assertions"]
    assert assertion["subject_entity_id"] == "ent:castle"
    assert assertion["predicate"] == new_fact.predicate
    assert assertion["value"] == (
        {"kind": "term_ref", "term": "lab:captain"}
        if kind == "term_ref"
        else {"kind": "literal", "value": "New sourced title"}
    )
    assert assertion["metadata"]["evidence_ref_ids"] == ["ev:lab"]
    assert result.object_results == ()
    (binding,) = result.assertion_results
    assert binding.client_op_id == "existing-fact"
    assert binding.durable_assertion_id == assertion["assertion_id"]
    assert binding.semantic_role == "fact"
    assert result.verification.exact_child_read_back
    assert service.commit_prepared_change(prepared, confirmed_by="user:test") == result


def test_empty_selection_still_has_no_contribution():
    repo = support.repository()
    with pytest.raises(InvalidWorldChange, match="no_contribution_items"):
        runtime(repo).prepare_change(intent())
    # An empty selection in a contributing intent remains valid and result-free.
    change = WorldChangeIntent(
        "space:lab", "producer:test", (UseExisting("ent:castle"), CreateObject("new"))
    )
    result = runtime(repo).commit_prepared_change(
        runtime(repo).prepare_change(change), confirmed_by="user:test"
    )
    assert [r.client_op_id for r in result.object_results] == ["new"]


@pytest.mark.parametrize(
    ("subject", "reason"),
    [
        ("", "blank_durable_object_id"),
        ("ent:missing", "durable_endpoint_absent"),
        ("ent:other-world", "durable_endpoint_absent"),
        ("asrt:wrong-kind", "durable_endpoint_absent"),
    ],
)
def test_invalid_selected_subject_refuses_without_mutation(subject, reason):
    repo = support.repository()
    head = repo.get_head("space:lab")
    with pytest.raises(InvalidWorldChange, match=reason):
        runtime(repo).prepare_change(intent(fact(), subject=subject))
    assert repo.get_head("space:lab") == head
    assert len(repo.head_events("space:lab")) == 1


def test_missing_evidence_and_duplicate_operation_ids_refuse():
    repo = support.repository()
    service = runtime(repo)
    with pytest.raises(InvalidWorldChange, match="evidence_ref_absent"):
        service.prepare_change(
            intent(fact(metadata=replace(support.metadata(), evidence_ref_ids=("ev:absent",))))
        )
    with pytest.raises(InvalidWorldChange, match="duplicate_client_op_id"):
        service.prepare_change(intent(fact(), fact()))
    change = WorldChangeIntent(
        "space:lab",
        "producer:test",
        (CreateObject("existing-fact"), UseExisting("ent:castle", (fact(),))),
    )
    with pytest.raises(InvalidWorldChange, match="duplicate_client_op_id"):
        service.prepare_change(change)
    assert len(repo.head_events("space:lab")) == 1


def test_changed_prepared_fact_and_stale_parent_refuse():
    repo = support.repository()
    service = runtime(repo)
    prepared = service.prepare_change(intent(fact()))
    stale = runtime(repo, "prepared:stale").prepare_change(intent(fact("later")))
    changed = replace(
        prepared,
        prepared_operations=(
            UseExisting("ent:castle", (replace(fact(), value=LiteralFactValue("Tampered")),)),
        ),
    )
    with pytest.raises(PreparedChangeIntegrityFailure):
        service.commit_prepared_change(changed, confirmed_by="user:test")
    assert len(repo.head_events("space:lab")) == 1
    service.commit_prepared_change(prepared, confirmed_by="user:test")
    with pytest.raises(PreparedChangeStale):
        service.commit_prepared_change(stale, confirmed_by="user:test")
    assert len(repo.head_events("space:lab")) == 2


@pytest.mark.parametrize("wrong_kind", [False, True])
def test_fact_result_binding_cannot_be_omitted_or_relabelled_as_entity(wrong_kind):
    repo = support.repository()
    prepared = runtime(repo).prepare_change(intent(fact()))
    witness = DungeonMindVNextCommitAuthority(repo).commit_and_verify(prepared)
    results = ()
    if wrong_kind:
        results = (replace(witness.results[0], result_kind="entity", durable_id="ent:castle"),)
    bad = replace(witness, results=results)
    with pytest.raises(CommitAuthorityIntegrityFailure, match="binding"):
        WorldChangeCommitter(boundary.WitnessAuthority(bad)).commit_prepared_change(
            prepared, "user:test"
        )


def test_scoped_facts_are_separate_assertions_not_conjoined_support():
    seed = support.repository()
    parent = seed.get_revision("space:lab", seed.get_head("space:lab").head_revision_id)
    payload = deepcopy(parent.graph_payload)
    payload["evidence"].append(
        {
            **payload["evidence"][0],
            "evidence_ref_id": "ev:c2",
            "source_artifact_id": "art:c2",
            "source_revision_id": "srcrev:c2",
        }
    )
    repo = InMemoryKnowledgeRevisionRepository()
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
    facts = tuple(
        fact(
            "fact:" + campaign,
            metadata=replace(
                support.metadata(),
                scope=(ScopeBinding("lab:scope", campaign),),
                evidence_ref_ids=(evidence,),
            ),
        )
        for campaign, evidence in (("c1", "ev:lab"), ("c2", "ev:c2"))
    )
    service = runtime(repo)
    result = service.commit_prepared_change(
        service.prepare_change(intent(*facts)), confirmed_by="user:test"
    )
    child = repo.get_revision("space:lab", result.child_revision_id)
    assert len(child.graph_payload["entities"]) == 1
    assert sorted(a["metadata"]["evidence_ref_ids"] for a in child.graph_payload["assertions"]) == [
        ["ev:c2"],
        ["ev:lab"],
    ]
    assert sorted((a["metadata"]["scope"] for a in child.graph_payload["assertions"]), key=str) == [
        [{"axis": "lab:scope", "value": "c1"}],
        [{"axis": "lab:scope", "value": "c2"}],
    ]


def test_lost_response_recovery_and_replay_after_descendant_preserve_same_assertion():
    repo = support.repository()
    prepared = runtime(repo).prepare_change(intent(fact()))
    service = WorldChangeCommitter(
        DungeonMindVNextCommitAuthority(boundary.RecoverableLostResponseRepository(repo))
    )
    recovered = service.commit_prepared_change(prepared, "user:test")
    descendant_service = runtime(repo, "prepared:descendant")
    descendant = descendant_service.commit_prepared_change(
        descendant_service.prepare_change(intent(fact("descendant-fact"))),
        confirmed_by="user:test",
    )
    head = repo.get_head("space:lab")
    events = repo.head_events("space:lab")
    replay = runtime(repo).commit_prepared_change(prepared, confirmed_by="user:test")
    assert replay == recovered
    assert replay.child_revision_id != descendant.child_revision_id
    assert repo.get_head("space:lab") == head
    assert repo.head_events("space:lab") == events
    latest = repo.get_revision("space:lab", head.head_revision_id)
    assert len(latest.graph_payload["entities"]) == 1
    assert len(latest.graph_payload["assertions"]) == 2


def test_wrong_world_and_profile_refuse_before_semantic_mutation():
    repo = support.repository()
    service = runtime(repo)
    with pytest.raises(InvalidWorldChange, match="missing_current_head"):
        service.prepare_change(replace(intent(fact()), space_id="space:other-world"))
    _, profile = support.descriptors()
    with pytest.raises(InvalidWorldChange, match="semantic_profile_mismatch"):
        runtime(
            repo, profile=profile.model_copy(update={"profile_revision": "wrong"})
        ).prepare_change(intent(fact()))
    assert len(repo.head_events("space:lab")) == 1


@pytest.mark.parametrize(
    "bad_fact",
    [
        replace(fact(), predicate=""),
        fact(metadata=replace(support.metadata(), standing="")),
        fact(metadata=replace(support.metadata(), evidence_ref_ids=("ev:lab", "ev:lab"))),
    ],
)
def test_invalid_fact_metadata_refuses_before_semantic_mutation(bad_fact):
    repo = support.repository()
    with pytest.raises(InvalidWorldChange):
        runtime(repo).prepare_change(intent(bad_fact))
    assert len(repo.head_events("space:lab")) == 1
