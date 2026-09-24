"""Immutable WorldKeeper contracts for WK-3 preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeAlias

JsonAtom: TypeAlias = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class FrozenJsonArray:
    items: tuple[FrozenJson, ...]


@dataclass(frozen=True, slots=True)
class FrozenJsonObject:
    items: tuple[tuple[str, FrozenJson], ...]


FrozenJson: TypeAlias = JsonAtom | FrozenJsonArray | FrozenJsonObject


def freeze_json(value: object) -> FrozenJson:
    """Copy canonical JSON-compatible input into an immutable representation."""
    if isinstance(value, FrozenJsonArray | FrozenJsonObject):
        return value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not value == value or value in (float("inf"), float("-inf")):
            raise ValueError("JSON numbers must be finite")
        return value
    if isinstance(value, list | tuple):
        return FrozenJsonArray(tuple(freeze_json(item) for item in value))
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        return FrozenJsonObject(
            tuple(sorted((key, freeze_json(item)) for key, item in value.items()))
        )
    raise ValueError("value must be canonical JSON-compatible data")


def thaw_json(value: FrozenJson) -> object:
    """Return an isolated JSON-compatible value for a downstream contract."""
    if isinstance(value, FrozenJsonArray):
        return [thaw_json(item) for item in value.items]
    if isinstance(value, FrozenJsonObject):
        return {key: thaw_json(item) for key, item in value.items}
    return value


@dataclass(frozen=True, slots=True)
class ScopeBinding:
    axis: str
    value: str


@dataclass(frozen=True, slots=True)
class Visibility:
    kind: str = "public"
    labels: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TemporalScope:
    kind: str = "timeless"
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    schema_term: str | None = None
    payload: FrozenJson | None = None

    def __post_init__(self) -> None:
        if self.payload is not None:
            object.__setattr__(self, "payload", freeze_json(self.payload))

    @classmethod
    def domain_ref(cls, schema_term: str, payload: object) -> TemporalScope:
        return cls(kind="domain_ref", schema_term=schema_term, payload=freeze_json(payload))


@dataclass(frozen=True, slots=True)
class DomainMetadata:
    schema_term: str
    payload: FrozenJson

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", freeze_json(self.payload))

    @classmethod
    def from_json(cls, schema_term: str, payload: object) -> DomainMetadata:
        return cls(schema_term=schema_term, payload=freeze_json(payload))


@dataclass(frozen=True, slots=True)
class AssertionMetadata:
    scope: tuple[ScopeBinding, ...]
    visibility: Visibility
    epistemic_basis: str
    claim_mode: str
    standing: str
    evidence_ref_ids: tuple[str, ...]
    temporal_scope: TemporalScope
    domain_metadata: tuple[DomainMetadata, ...] = ()


@dataclass(frozen=True, slots=True)
class LiteralFactValue:
    value: FrozenJson

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", freeze_json(self.value))

    @classmethod
    def from_json(cls, value: object) -> LiteralFactValue:
        return cls(value=freeze_json(value))


@dataclass(frozen=True, slots=True)
class TermRefFactValue:
    term: str


FactValue: TypeAlias = LiteralFactValue | TermRefFactValue


@dataclass(frozen=True, slots=True)
class DurableObjectRef:
    durable_object_id: str


@dataclass(frozen=True, slots=True)
class ResultOf:
    client_op_id: str


EndpointRef: TypeAlias = DurableObjectRef | ResultOf


@dataclass(frozen=True, slots=True)
class CreateFact:
    client_op_id: str
    predicate: str
    value: FactValue
    metadata: AssertionMetadata


@dataclass(frozen=True, slots=True)
class CreateObject:
    client_op_id: str
    facts: tuple[CreateFact, ...] = ()


@dataclass(frozen=True, slots=True)
class UseExisting:
    durable_object_id: str


@dataclass(frozen=True, slots=True)
class CreateRelationship:
    client_op_id: str
    source: EndpointRef
    predicate: str
    target: EndpointRef
    metadata: AssertionMetadata


WorldOperation: TypeAlias = CreateObject | UseExisting | CreateRelationship


@dataclass(frozen=True, slots=True)
class WorldChangeIntent:
    space_id: str
    producer: str
    operations: tuple[WorldOperation, ...]


@dataclass(frozen=True, slots=True)
class AuthorityRef:
    authority_id: str
    revision: str
    descriptor_sha256: str


@dataclass(frozen=True, slots=True)
class PreparedEvidenceWitness:
    evidence_ref_id: str
    source_artifact_id: str
    source_revision_id: str | None
    evidence_role: str
    locator: str | None
    uri: str | None
    source_locator: str | None
    line_ref: str | None
    source_span_ref_id: str | None


@dataclass(frozen=True, slots=True)
class ProspectiveHandle:
    client_op_id: str


@dataclass(frozen=True, slots=True)
class PreparedWorldChange:
    prepared_change_id: str
    dungeonmind_publication_id: str
    prepared_at: datetime
    space_id: str
    producer: str
    expected_parent_revision_id: str
    parent_graph_payload_sha256: str
    domain_contract_ref: AuthorityRef
    semantic_profile_ref: AuthorityRef
    evidence_witnesses: tuple[PreparedEvidenceWitness, ...]
    prepared_operations: tuple[WorldOperation, ...]
    prospective_handles: tuple[ProspectiveHandle, ...]
    compiled_plan_digest: str
    warnings: tuple[str, ...] = ()
    _domain_contract_json: str = field(repr=False, default="")
    _semantic_profile_json: str = field(repr=False, default="")


@dataclass(frozen=True, slots=True)
class CommittedObjectResult:
    client_op_id: str
    durable_object_id: str


@dataclass(frozen=True, slots=True)
class CommittedAssertionResult:
    client_op_id: str
    durable_assertion_id: str
    semantic_role: str


@dataclass(frozen=True, slots=True)
class CommitVerification:
    exact_child_read_back: bool = True


@dataclass(frozen=True, slots=True)
class VerifiedCommittedChange:
    prepared_change_id: str
    dungeonmind_publication_id: str
    expected_parent_revision_id: str
    child_revision_id: str
    child_graph_payload_sha256: str
    object_results: tuple[CommittedObjectResult, ...]
    assertion_results: tuple[CommittedAssertionResult, ...]
    verification: CommitVerification = field(default_factory=CommitVerification)
