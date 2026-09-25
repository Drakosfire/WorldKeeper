"""Read-only DungeonMind vNext authority adapter and pure WK-3 compiler."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Protocol, TypeVar

from dungeonmind.application.vnext.builder import build_parsed_knowledge_revision
from dungeonmind.application.vnext.materialization import (
    GovernedPublicationIdentity,
    decode_native_graph_payload,
)
from dungeonmind.application.vnext.records import StoredKnowledgeRevision
from dungeonmind.contracts.vnext.common import (
    DomainMetadataEntry,
    DomainTemporalScope,
    EpistemicBasis,
    KnowledgeStanding,
    LabelsAllVisibility,
    LabelsAnyVisibility,
    PublicVisibility,
    TimelessTemporalScope,
    UnknownTemporalScope,
    UtcIntervalTemporalScope,
    VisibilityRequirement,
)
from dungeonmind.contracts.vnext.common import (
    ScopeBinding as DungeonMindScopeBinding,
)
from dungeonmind.contracts.vnext.common import (
    TemporalScope as DungeonMindTemporalScope,
)
from dungeonmind.contracts.vnext.contribution import ContributionDisposition
from dungeonmind.contracts.vnext.domain import (
    AssertionMetadata as DungeonMindAssertionMetadata,
)
from dungeonmind.contracts.vnext.domain import (
    DomainContractDescriptor,
    LiteralValue,
    SemanticProfileDescriptorV2,
    TermRefValue,
    parse_semantic_profile_descriptor,
)
from dungeonmind.contracts.vnext.knowledge import KnowledgeHead
from dungeonmind.contracts.vnext.prospective import (
    DurableEntityRef,
    EntityOperand,
    ProspectiveContributionItem,
    ProspectiveCreateAssertion,
    ProspectiveCreateEntity,
    ProspectiveEntityRef,
    ProspectiveEntityRefValue,
    ProspectiveKnowledgeContribution,
)
from dungeonmind.domain.canonical import canonical_sha256
from dungeonmind.domain.errors import (
    DungeonMindError,
    PersistenceIntegrityError,
    PersistenceUnavailableError,
)

from worldkeeper.application.authority import (
    AuthorityIntegrityFailure,
    AuthorityUnavailable,
    PreparationAuthorityRef,
    PreparationAuthorityWitness,
    PreparationEvidenceWitness,
)
from worldkeeper.application.contracts import (
    AssertionMetadata,
    AuthorityRef,
    CreateObject,
    CreateRelationship,
    DurableObjectRef,
    LiteralFactValue,
    PreparedWorldChange,
    ResultOf,
    TemporalScope,
    TermRefFactValue,
    Visibility,
    thaw_json,
)

_ReadValue = TypeVar("_ReadValue")


class NativeKnowledgeReader(Protocol):
    """Read-only subset of DungeonMind's native knowledge repository."""

    def get_head(self, space_id: str) -> KnowledgeHead | None: ...

    def get_revision(self, space_id: str, revision_id: str) -> StoredKnowledgeRevision | None: ...


class DungeonMindVNextPreparationAuthority:
    """Adapt exact native-vNext authority into immutable WorldKeeper witnesses."""

    def __init__(self, repository: NativeKnowledgeReader) -> None:
        self._repository = repository

    def read_current_space(self, space_id: str) -> PreparationAuthorityWitness | None:
        head = self._read(lambda: self._repository.get_head(space_id))
        if head is None:
            return None
        if head.space_id != space_id:
            self._integrity("DungeonMind head does not match the requested space")
        stored = self._read(lambda: self._repository.get_revision(space_id, head.head_revision_id))
        if stored is None:
            self._integrity("DungeonMind current head revision is missing")
        assert stored is not None
        revision = stored.revision
        if revision.space_id != space_id or revision.revision_id != head.head_revision_id:
            self._integrity("DungeonMind revision does not match its current head")
        if stored.graph_payload_sha256 != revision.graph_payload_sha256:
            self._integrity("DungeonMind stored payload digest disagrees with its envelope")
        parsed = self._read(
            lambda: build_parsed_knowledge_revision(
                revision=revision,
                decoded_content=decode_native_graph_payload(stored.graph_payload),
            )
        )
        if (
            parsed.space_id != space_id
            or parsed.revision_id != head.head_revision_id
            or parsed.graph_payload_sha256 != revision.graph_payload_sha256
        ):
            self._integrity("DungeonMind parsed authority disagrees with its envelope")
        domain_ref = parsed.domain_contract_ref
        profile_ref = parsed.semantic_profile_ref
        return PreparationAuthorityWitness(
            space_id=space_id,
            head_revision_id=parsed.revision_id,
            graph_payload_sha256=parsed.graph_payload_sha256,
            domain_contract_ref=PreparationAuthorityRef(
                authority_id=domain_ref.domain_id,
                revision=domain_ref.domain_revision,
                descriptor_sha256=domain_ref.descriptor_sha256,
            ),
            semantic_profile_ref=PreparationAuthorityRef(
                authority_id=profile_ref.profile_id,
                revision=profile_ref.profile_revision,
                descriptor_sha256=profile_ref.descriptor_sha256,
            ),
            durable_entity_ids=tuple(sorted(parsed.entities_by_id)),
            evidence_witnesses=tuple(
                PreparationEvidenceWitness(
                    evidence_ref_id=evidence.evidence_ref_id,
                    source_artifact_id=evidence.source_artifact_id,
                    source_revision_id=evidence.source_revision_id,
                    evidence_role=evidence.evidence_role,
                    locator=evidence.locator,
                    uri=evidence.uri,
                    source_locator=evidence.source_locator,
                    line_ref=evidence.line_ref,
                    source_span_ref_id=evidence.source_span_ref_id,
                )
                for evidence in sorted(
                    parsed.evidence_by_id.values(), key=lambda item: item.evidence_ref_id
                )
            ),
        )

    @staticmethod
    def _integrity(message: str) -> None:
        raise AuthorityIntegrityFailure(message)

    @staticmethod
    def _read(callback: Callable[[], _ReadValue]) -> _ReadValue:
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


@dataclass(frozen=True, slots=True)
class DungeonMindPreparedProspectivePlan:
    """Fresh compile output for a single immutable prepared change."""

    prospective_contribution: ProspectiveKnowledgeContribution
    dispositions: tuple[ContributionDisposition, ...]
    publication: GovernedPublicationIdentity
    domain_contract: DomainContractDescriptor
    semantic_profile: SemanticProfileDescriptorV2
    publication_id: str
    parent_graph_payload_sha256: str
    domain_contract_ref: AuthorityRef
    semantic_profile_ref: AuthorityRef


def _stable_id(prepared_id: str, role: str, client_op_id: str) -> str:
    digest = hashlib.sha256(
        f"worldkeeper-wk3\0{prepared_id}\0{role}\0{client_op_id}".encode()
    ).hexdigest()
    return f"wk:{role}:{digest}"


def _visibility(value: Visibility) -> VisibilityRequirement:
    if value.kind == "public" and not value.labels:
        return PublicVisibility()
    if value.kind == "labels_any":
        return LabelsAnyVisibility(labels=list(value.labels))
    if value.kind == "labels_all":
        return LabelsAllVisibility(labels=list(value.labels))
    raise ValueError("invalid visibility")


def _temporal(value: TemporalScope) -> DungeonMindTemporalScope:
    if value.kind == "timeless":
        return TimelessTemporalScope()
    if value.kind == "unknown":
        return UnknownTemporalScope()
    if value.kind == "utc_interval":
        return UtcIntervalTemporalScope(
            valid_from=value.valid_from,
            valid_until=value.valid_until,
        )
    if value.kind == "domain_ref" and value.schema_term and value.payload is not None:
        return DomainTemporalScope(
            schema=value.schema_term,
            payload=thaw_json(value.payload),
        )
    raise ValueError("invalid temporal scope")


def _metadata(value: AssertionMetadata) -> DungeonMindAssertionMetadata:
    return DungeonMindAssertionMetadata(
        scope=[DungeonMindScopeBinding(axis=item.axis, value=item.value) for item in value.scope],
        visibility=_visibility(value.visibility),
        epistemic_basis=EpistemicBasis(value.epistemic_basis),
        claim_mode=value.claim_mode,
        standing=KnowledgeStanding(value.standing),
        evidence_ref_ids=list(value.evidence_ref_ids),
        temporal_scope=_temporal(value.temporal_scope),
        domain_metadata=[
            DomainMetadataEntry(
                schema=item.schema_term,
                payload=thaw_json(item.payload),
            )
            for item in value.domain_metadata
        ],
    )


def _entity_operand(value: DurableObjectRef | ResultOf) -> EntityOperand:
    if isinstance(value, ResultOf):
        return ProspectiveEntityRef(client_op_id=value.client_op_id)
    return DurableEntityRef(entity_id=value.durable_object_id)


def _plan_payload(plan: DungeonMindPreparedProspectivePlan) -> dict[str, object]:
    return {
        "publication_id": plan.publication_id,
        "prospective_contribution": plan.prospective_contribution.model_dump(mode="json"),
        "dispositions": [item.model_dump(mode="json") for item in plan.dispositions],
        "publication": {
            "operation_ids": list(plan.publication.operation_ids),
            "created_at": plan.publication.created_at.isoformat(),
            "expected_parent_revision_id": plan.publication.expected_parent_revision_id,
        },
        "parent_graph_payload_sha256": plan.parent_graph_payload_sha256,
        "domain_contract_ref": asdict(plan.domain_contract_ref),
        "semantic_profile_ref": asdict(plan.semantic_profile_ref),
        "domain_contract": plan.domain_contract.model_dump(mode="json"),
        "semantic_profile": plan.semantic_profile.model_dump(mode="json"),
    }


def _compile_prepared_change_to_dungeonmind(
    prepared: PreparedWorldChange,
) -> DungeonMindPreparedProspectivePlan:
    """Build one compile plan before checking its sealed digest."""
    items: list[ProspectiveContributionItem] = []
    for operation in prepared.prepared_operations:
        if isinstance(operation, CreateObject):
            items.append(
                ProspectiveCreateEntity(
                    item_id=_stable_id(
                        prepared.prepared_change_id, "entity-item", operation.client_op_id
                    ),
                    client_op_id=operation.client_op_id,
                )
            )
            for fact in operation.facts:
                if isinstance(fact.value, LiteralFactValue):
                    fact_value = LiteralValue(value=thaw_json(fact.value.value))
                elif isinstance(fact.value, TermRefFactValue):
                    fact_value = TermRefValue(term=fact.value.term)
                else:  # pragma: no cover - closed union defense
                    raise ValueError("unsupported fact value")
                items.append(
                    ProspectiveCreateAssertion(
                        item_id=_stable_id(
                            prepared.prepared_change_id, "fact-item", fact.client_op_id
                        ),
                        client_op_id=fact.client_op_id,
                        subject=ProspectiveEntityRef(client_op_id=operation.client_op_id),
                        predicate=fact.predicate,
                        value=fact_value,
                        metadata=_metadata(fact.metadata),
                    )
                )
        elif isinstance(operation, CreateRelationship):
            items.append(
                ProspectiveCreateAssertion(
                    item_id=_stable_id(
                        prepared.prepared_change_id,
                        "relationship-item",
                        operation.client_op_id,
                    ),
                    client_op_id=operation.client_op_id,
                    subject=_entity_operand(operation.source),
                    predicate=operation.predicate,
                    value=ProspectiveEntityRefValue(entity=_entity_operand(operation.target)),
                    metadata=_metadata(operation.metadata),
                )
            )
    contribution = ProspectiveKnowledgeContribution(
        contribution_id=_stable_id(
            prepared.prepared_change_id, "contribution", prepared.prepared_change_id
        ),
        space_id=prepared.space_id,
        producer=prepared.producer,
        produced_at=prepared.prepared_at,
        source_refs=sorted({item.source_artifact_id for item in prepared.evidence_witnesses}),
        status="finalized",
        items=items,
    )
    plan = DungeonMindPreparedProspectivePlan(
        prospective_contribution=contribution,
        dispositions=tuple(
            ContributionDisposition(item_id=item.item_id, disposition="accepted")
            for item in contribution.items
        ),
        publication=GovernedPublicationIdentity(
            operation_ids=(prepared.prepared_change_id,),
            created_at=prepared.prepared_at,
            expected_parent_revision_id=prepared.expected_parent_revision_id,
        ),
        domain_contract=DomainContractDescriptor.model_validate_json(
            prepared._domain_contract_json
        ),
        semantic_profile=parse_semantic_profile_descriptor(
            json.loads(prepared._semantic_profile_json)
        ),
        publication_id=prepared.dungeonmind_publication_id,
        parent_graph_payload_sha256=prepared.parent_graph_payload_sha256,
        domain_contract_ref=prepared.domain_contract_ref,
        semantic_profile_ref=prepared.semantic_profile_ref,
    )
    return plan


def compiled_plan_digest(plan: DungeonMindPreparedProspectivePlan) -> str:
    """Canonical digest of every authority-bearing compile-ready value."""
    return canonical_sha256(_plan_payload(plan))


def compute_prepared_plan_digest(prepared: PreparedWorldChange) -> str:
    """Compute the canonical integrity witness while sealing a preparation."""
    if prepared.dungeonmind_publication_id != prepared.prepared_change_id:
        raise ValueError("DungeonMind publication identity must equal prepared identity")
    return compiled_plan_digest(_compile_prepared_change_to_dungeonmind(prepared))


def compile_prepared_change_to_dungeonmind(
    prepared: PreparedWorldChange,
) -> DungeonMindPreparedProspectivePlan:
    """Compile only an intact prepared meaning to accepted V5.4 syntax."""
    if prepared.dungeonmind_publication_id != prepared.prepared_change_id:
        raise ValueError("DungeonMind publication identity must equal prepared identity")
    plan = _compile_prepared_change_to_dungeonmind(prepared)
    actual_digest = compiled_plan_digest(plan)
    if actual_digest != prepared.compiled_plan_digest:
        raise ValueError("prepared compiled plan digest mismatch")
    return plan
