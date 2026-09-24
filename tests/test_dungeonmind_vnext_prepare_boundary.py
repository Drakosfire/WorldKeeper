from __future__ import annotations

from datetime import UTC, datetime

import pytest
from dungeonmind.application.vnext.materialization import (
    NATIVE_VNEXT_GRAPH_SCHEMA,
    encode_native_graph_payload,
)
from dungeonmind.contracts.semantic_profile import SemanticProfileRef
from dungeonmind.contracts.vnext.domain import (
    DomainContractDescriptor,
    Entity,
    SemanticProfileDescriptorV2,
)
from dungeonmind.contracts.vnext.knowledge import (
    DomainContractRef,
    KnowledgeHead,
    PublishKnowledgeRevisionCommand,
)
from dungeonmind.contracts.vnext.source import EvidenceRefV3
from dungeonmind.domain.canonical import canonical_sha256
from dungeonmind.domain.errors import PersistenceUnavailableError
from dungeonmind.infrastructure.memory.vnext_knowledge import (
    InMemoryKnowledgeRevisionRepository,
)

from worldkeeper.application.authority import (
    AuthorityIntegrityFailure,
    AuthorityUnavailable,
)
from worldkeeper.integrations.dungeonmind.vnext_prepare import (
    DungeonMindVNextPreparationAuthority,
)

NOW = datetime(2026, 9, 23, 12, 0, tzinfo=UTC)


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
    )
    return contract, profile


def repository():
    repo = InMemoryKnowledgeRevisionRepository()
    contract, profile = descriptors()
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
    command = PublishKnowledgeRevisionCommand(
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
    repo.publish_revision(command)
    return repo


def test_adapter_reads_exact_native_authority_without_mutation() -> None:
    repo = repository()
    head_before = repo.get_head("space:lab")
    events_before = repo.head_events("space:lab")
    adapter = DungeonMindVNextPreparationAuthority(repo)

    witness = adapter.read_current_space("space:lab")

    assert witness is not None
    assert witness.space_id == "space:lab"
    assert witness.head_revision_id == head_before.head_revision_id  # type: ignore[union-attr]
    assert witness.graph_payload_sha256
    assert witness.durable_entity_ids == ("ent:castle",)
    assert witness.domain_contract_ref.authority_id == "lab.domain"
    assert witness.semantic_profile_ref.authority_id == "lab.profile"
    assert witness.evidence_witnesses[0].evidence_ref_id == "ev:lab"
    assert witness.evidence_witnesses[0].source_artifact_id == "art:lab"
    assert repo.get_head("space:lab") == head_before
    assert repo.head_events("space:lab") == events_before
    assert repo.get_publication_receipt("space:lab", "prepared:wk3") is None
    assert repo.get_prospective_publication("space:lab", "prepared:wk3") is None


def test_adapter_returns_none_for_missing_space() -> None:
    adapter = DungeonMindVNextPreparationAuthority(repository())
    assert adapter.read_current_space("space:missing") is None


class UnavailableRepository:
    def get_head(self, space_id: str):
        raise PersistenceUnavailableError("offline")

    def get_revision(self, space_id: str, revision_id: str):
        raise AssertionError("must not read a revision without a head")


def test_adapter_maps_persistence_unavailable() -> None:
    adapter = DungeonMindVNextPreparationAuthority(UnavailableRepository())
    with pytest.raises(AuthorityUnavailable):
        adapter.read_current_space("space:lab")


class MismatchedHeadRepository:
    def get_head(self, space_id: str):
        return KnowledgeHead(
            space_id="space:other",
            head_revision_id="rev:wrong",
            updated_at=NOW,
        )

    def get_revision(self, space_id: str, revision_id: str):
        raise AssertionError("must fail before revision read")


def test_adapter_fails_closed_on_integrity_mismatch() -> None:
    adapter = DungeonMindVNextPreparationAuthority(MismatchedHeadRepository())
    with pytest.raises(AuthorityIntegrityFailure):
        adapter.read_current_space("space:lab")
