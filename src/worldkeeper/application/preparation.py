"""WK-3 non-mutating World change preparation service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from dungeonmind.contracts.vnext.domain import (
    DomainContractDescriptor,
    SemanticProfileDescriptorV2,
)
from dungeonmind.domain.canonical import canonical_sha256

from worldkeeper.integrations.dungeonmind.vnext_prepare import (
    compute_prepared_plan_digest,
)

from .authority import GovernedPreparationAuthority, PreparationAuthorityWitness
from .contracts import (
    AssertionMetadata,
    AuthorityRef,
    CreateFact,
    CreateObject,
    CreateRelationship,
    DomainMetadata,
    DurableObjectRef,
    LiteralFactValue,
    PreparedEvidenceWitness,
    PreparedWorldChange,
    ProspectiveHandle,
    ResultOf,
    ScopeBinding,
    TemporalScope,
    TermRefFactValue,
    UseExisting,
    Visibility,
    WorldChangeIntent,
    WorldOperation,
)


class InvalidWorldChange(ValueError):
    """The requested intent cannot be prepared without changing its meaning."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def generate_prepared_change_id() -> str:
    """Generate one fresh opaque WorldKeeper-owned preparation identity."""
    return f"prepared:{uuid4().hex}"


def _required(value: str, reason: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidWorldChange(reason)
    return value


def _metadata_copy(value: AssertionMetadata) -> AssertionMetadata:
    return AssertionMetadata(
        scope=tuple(ScopeBinding(axis=item.axis, value=item.value) for item in value.scope),
        visibility=Visibility(
            kind=value.visibility.kind,
            labels=tuple(value.visibility.labels),
        ),
        epistemic_basis=value.epistemic_basis,
        claim_mode=value.claim_mode,
        standing=value.standing,
        evidence_ref_ids=tuple(value.evidence_ref_ids),
        temporal_scope=TemporalScope(
            kind=value.temporal_scope.kind,
            valid_from=value.temporal_scope.valid_from,
            valid_until=value.temporal_scope.valid_until,
            schema_term=value.temporal_scope.schema_term,
            payload=value.temporal_scope.payload,
        ),
        domain_metadata=tuple(
            DomainMetadata(schema_term=item.schema_term, payload=item.payload)
            for item in value.domain_metadata
        ),
    )


def _fact_copy(value: CreateFact) -> CreateFact:
    if isinstance(value.value, LiteralFactValue):
        fact_value = LiteralFactValue(value=value.value.value)
    else:
        fact_value = TermRefFactValue(term=value.value.term)
    return CreateFact(
        client_op_id=value.client_op_id,
        predicate=value.predicate,
        value=fact_value,
        metadata=_metadata_copy(value.metadata),
    )


def _endpoint_copy(value: DurableObjectRef | ResultOf) -> DurableObjectRef | ResultOf:
    if isinstance(value, ResultOf):
        return ResultOf(client_op_id=value.client_op_id)
    return DurableObjectRef(durable_object_id=value.durable_object_id)


def _operation_copy(value: WorldOperation) -> WorldOperation:
    if isinstance(value, CreateObject):
        return CreateObject(
            client_op_id=value.client_op_id,
            facts=tuple(_fact_copy(item) for item in value.facts),
        )
    if isinstance(value, UseExisting):
        return UseExisting(durable_object_id=value.durable_object_id)
    return CreateRelationship(
        client_op_id=value.client_op_id,
        source=_endpoint_copy(value.source),
        predicate=value.predicate,
        target=_endpoint_copy(value.target),
        metadata=_metadata_copy(value.metadata),
    )


def _domain_ref(witness: PreparationAuthorityWitness) -> AuthorityRef:
    value = witness.domain_contract_ref
    return AuthorityRef(
        authority_id=value.authority_id,
        revision=value.revision,
        descriptor_sha256=value.descriptor_sha256,
    )


def _profile_ref(witness: PreparationAuthorityWitness) -> AuthorityRef:
    value = witness.semantic_profile_ref
    return AuthorityRef(
        authority_id=value.authority_id,
        revision=value.revision,
        descriptor_sha256=value.descriptor_sha256,
    )


class WorldChangePreparer:
    """Interpret and compile one intent against exact current authority."""

    def __init__(
        self,
        *,
        authority: GovernedPreparationAuthority,
        domain_contract: DomainContractDescriptor,
        semantic_profile: SemanticProfileDescriptorV2,
        clock: Callable[[], datetime],
        prepared_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._authority = authority
        self._domain_contract_json = domain_contract.model_dump_json()
        self._semantic_profile_json = semantic_profile.model_dump_json()
        self._prepared_id_factory = prepared_id_factory or generate_prepared_change_id
        self._clock = clock

    def prepare_change(self, intent: WorldChangeIntent) -> PreparedWorldChange:
        space_id = _required(intent.space_id, "blank_space_id")
        producer = _required(intent.producer, "blank_producer")
        operations = tuple(_operation_copy(item) for item in intent.operations)
        if not operations:
            raise InvalidWorldChange("empty_operation_list")

        witness = self._authority.read_current_space(space_id)
        if witness is None:
            raise InvalidWorldChange("missing_current_head")
        if witness.space_id != space_id:
            raise InvalidWorldChange("authority_space_mismatch")

        domain_contract = DomainContractDescriptor.model_validate_json(self._domain_contract_json)
        semantic_profile = SemanticProfileDescriptorV2.model_validate_json(
            self._semantic_profile_json
        )
        self._validate_descriptors(witness, domain_contract, semantic_profile)

        object_ids: set[str] = set()
        assertion_ids: set[str] = set()
        all_result_ids: set[str] = set()
        for operation in operations:
            if isinstance(operation, CreateObject):
                self._claim_result_id(operation.client_op_id, all_result_ids)
                object_ids.add(operation.client_op_id)
                for fact in operation.facts:
                    self._claim_result_id(fact.client_op_id, all_result_ids)
                    assertion_ids.add(fact.client_op_id)
                    _required(fact.predicate, "blank_predicate")
                    self._validate_metadata(fact.metadata)
            elif isinstance(operation, CreateRelationship):
                self._claim_result_id(operation.client_op_id, all_result_ids)
                assertion_ids.add(operation.client_op_id)
                _required(operation.predicate, "blank_predicate")
                self._validate_metadata(operation.metadata)
            else:
                _required(operation.durable_object_id, "blank_durable_object_id")

        durable_ids = set(witness.durable_entity_ids)
        used_evidence_ids: set[str] = set()
        for operation in operations:
            if isinstance(operation, CreateObject):
                for fact in operation.facts:
                    used_evidence_ids.update(fact.metadata.evidence_ref_ids)
            elif isinstance(operation, CreateRelationship):
                self._validate_endpoint(operation.source, object_ids, assertion_ids, durable_ids)
                self._validate_endpoint(operation.target, object_ids, assertion_ids, durable_ids)
                used_evidence_ids.update(operation.metadata.evidence_ref_ids)
            elif operation.durable_object_id not in durable_ids:
                raise InvalidWorldChange("durable_endpoint_absent")

        evidence_by_id = {item.evidence_ref_id: item for item in witness.evidence_witnesses}
        missing_evidence = used_evidence_ids - set(evidence_by_id)
        if missing_evidence:
            raise InvalidWorldChange("evidence_ref_absent")

        prepared_id = _required(self._prepared_id_factory(), "blank_prepared_change_id")
        prepared_at = self._clock()
        prepared = PreparedWorldChange(
            prepared_change_id=prepared_id,
            dungeonmind_publication_id=prepared_id,
            prepared_at=prepared_at,
            space_id=space_id,
            producer=producer,
            expected_parent_revision_id=witness.head_revision_id,
            parent_graph_payload_sha256=witness.graph_payload_sha256,
            domain_contract_ref=_domain_ref(witness),
            semantic_profile_ref=_profile_ref(witness),
            evidence_witnesses=tuple(
                PreparedEvidenceWitness(
                    evidence_ref_id=item.evidence_ref_id,
                    source_artifact_id=item.source_artifact_id,
                    source_revision_id=item.source_revision_id,
                    evidence_role=item.evidence_role,
                    locator=item.locator,
                    uri=item.uri,
                    source_locator=item.source_locator,
                    line_ref=item.line_ref,
                    source_span_ref_id=item.source_span_ref_id,
                )
                for item in witness.evidence_witnesses
                if item.evidence_ref_id in used_evidence_ids
            ),
            prepared_operations=operations,
            prospective_handles=tuple(
                ProspectiveHandle(client_op_id=item) for item in sorted(object_ids)
            ),
            compiled_plan_digest="0" * 64,
            _domain_contract_json=self._domain_contract_json,
            _semantic_profile_json=self._semantic_profile_json,
        )
        if not any(
            isinstance(operation, CreateObject | CreateRelationship) for operation in operations
        ):
            raise InvalidWorldChange("no_contribution_items")
        try:
            digest = compute_prepared_plan_digest(prepared)
        except (TypeError, ValueError) as exc:
            raise InvalidWorldChange("malformed_semantic_contract") from exc
        return replace(prepared, compiled_plan_digest=digest)

    @staticmethod
    def _claim_result_id(value: str, seen: set[str]) -> None:
        result_id = _required(value, "blank_client_op_id")
        if result_id in seen:
            raise InvalidWorldChange("duplicate_client_op_id")
        seen.add(result_id)

    @staticmethod
    def _validate_endpoint(
        endpoint: DurableObjectRef | ResultOf,
        object_ids: set[str],
        assertion_ids: set[str],
        durable_ids: set[str],
    ) -> None:
        if isinstance(endpoint, ResultOf):
            ref = _required(endpoint.client_op_id, "blank_result_of")
            if ref in assertion_ids:
                raise InvalidWorldChange("result_of_assertion")
            if ref not in object_ids:
                raise InvalidWorldChange("result_of_missing_create_object")
        elif endpoint.durable_object_id not in durable_ids:
            raise InvalidWorldChange("durable_endpoint_absent")

    @staticmethod
    def _validate_metadata(metadata: AssertionMetadata) -> None:
        _required(metadata.epistemic_basis, "blank_epistemic_basis")
        _required(metadata.claim_mode, "blank_claim_mode")
        _required(metadata.standing, "blank_standing")
        for evidence_id in metadata.evidence_ref_ids:
            _required(evidence_id, "blank_evidence_ref_id")
        if len(metadata.evidence_ref_ids) != len(set(metadata.evidence_ref_ids)):
            raise InvalidWorldChange("duplicate_evidence_ref_id")

    @staticmethod
    def _validate_descriptors(
        witness: PreparationAuthorityWitness,
        domain_contract: DomainContractDescriptor,
        semantic_profile: SemanticProfileDescriptorV2,
    ) -> None:
        domain_ref = witness.domain_contract_ref
        domain_digest = canonical_sha256(domain_contract.model_dump(mode="json"))
        if (
            domain_contract.domain_id != domain_ref.authority_id
            or domain_contract.domain_revision != domain_ref.revision
            or domain_digest != domain_ref.descriptor_sha256
        ):
            raise InvalidWorldChange("domain_contract_mismatch")
        profile_ref = witness.semantic_profile_ref
        profile_digest = canonical_sha256(semantic_profile.model_dump(mode="json"))
        if (
            semantic_profile.profile_id != profile_ref.authority_id
            or semantic_profile.profile_revision != profile_ref.revision
            or profile_digest != profile_ref.descriptor_sha256
        ):
            raise InvalidWorldChange("semantic_profile_mismatch")
