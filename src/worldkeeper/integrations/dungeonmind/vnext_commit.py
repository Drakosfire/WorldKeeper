"""DungeonMind V5.4 publication and exact-child verification for WK-4."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, TypeVar

from dungeonmind.application.vnext.builder import build_parsed_knowledge_revision
from dungeonmind.application.vnext.errors import (
    KnowledgePublicationIdempotencyConflictError,
    KnowledgePublicationOutcomeUnknownError,
    KnowledgeStaleParentRevisionError,
)
from dungeonmind.application.vnext.materialization import decode_native_graph_payload
from dungeonmind.application.vnext.model import ParsedKnowledgeRevision
from dungeonmind.application.vnext.ports import KnowledgeRevisionRepository
from dungeonmind.application.vnext.prospective import publish_prospective_contribution
from dungeonmind.application.vnext.records import StoredKnowledgeRevision
from dungeonmind.contracts.vnext.domain import Assertion, EntityRefValue
from dungeonmind.contracts.vnext.prospective import (
    DurableEntityRef,
    EntityOperand,
    KnowledgeProspectivePublication,
    ProspectiveCreateAssertion,
    ProspectiveCreateEntity,
    ProspectiveEntityRef,
    ProspectiveEntityRefValue,
    ProspectiveResultBinding,
)
from dungeonmind.domain.errors import (
    ImmutableRevisionConflictError,
    PersistenceIntegrityError,
    PersistenceUnavailableError,
)

from worldkeeper.application.authority import CommitAuthorityWitness, CommitResultBinding
from worldkeeper.application.commit import (
    CommitAuthorityIntegrityFailure,
    CommittedChangeOutcomeUnknown,
    CommittedChangeVerificationIntegrityFailure,
    CommittedChangeVerificationUnavailable,
    PreparedChangeConflict,
    PreparedChangeIntegrityFailure,
    PreparedChangeStale,
)
from worldkeeper.application.contracts import PreparedWorldChange

from .vnext_prepare import (
    DungeonMindPreparedProspectivePlan,
    compile_prepared_change_to_dungeonmind,
)

_T = TypeVar("_T")


class DungeonMindVNextCommitAuthority:
    """Commit one intact prepared value and verify its exact immutable child."""

    def __init__(self, repository: KnowledgeRevisionRepository) -> None:
        self._repository = repository

    def commit_and_verify(self, prepared: PreparedWorldChange) -> CommitAuthorityWitness:
        try:
            plan = compile_prepared_change_to_dungeonmind(prepared)
        except (TypeError, ValueError) as exc:
            raise PreparedChangeIntegrityFailure("prepared meaning failed integrity") from exc

        stored_parent = self._before_commit(
            lambda: self._repository.get_revision(
                prepared.space_id, prepared.expected_parent_revision_id
            )
        )
        if stored_parent is None:
            raise CommitAuthorityIntegrityFailure("prepared parent revision is missing")
        parent = self._parse(stored_parent, committed=False, prepared=prepared)
        if (
            parent.space_id != prepared.space_id
            or parent.revision_id != prepared.expected_parent_revision_id
            or parent.graph_payload_sha256 != prepared.parent_graph_payload_sha256
            or parent.domain_contract_ref.domain_id != prepared.domain_contract_ref.authority_id
            or parent.domain_contract_ref.domain_revision != prepared.domain_contract_ref.revision
            or parent.domain_contract_ref.descriptor_sha256
            != prepared.domain_contract_ref.descriptor_sha256
            or parent.semantic_profile_ref.profile_id != prepared.semantic_profile_ref.authority_id
            or parent.semantic_profile_ref.profile_revision
            != prepared.semantic_profile_ref.revision
            or parent.semantic_profile_ref.descriptor_sha256
            != prepared.semantic_profile_ref.descriptor_sha256
        ):
            raise CommitAuthorityIntegrityFailure("prepared parent authority drift")

        try:
            aggregate = publish_prospective_contribution(
                parent=parent,
                prospective_contribution=plan.prospective_contribution,
                dispositions=plan.dispositions,
                publication=plan.publication,
                publication_id=plan.publication_id,
                domain_contract=plan.domain_contract,
                semantic_profile=plan.semantic_profile,
                repository=self._repository,
            )
        except KnowledgeStaleParentRevisionError as exc:
            raise PreparedChangeStale(str(exc)) from exc
        except KnowledgePublicationIdempotencyConflictError as exc:
            raise PreparedChangeConflict(str(exc)) from exc
        except KnowledgePublicationOutcomeUnknownError as exc:
            raise CommittedChangeOutcomeUnknown(
                prepared_change_id=prepared.prepared_change_id,
                publication_id=exc.publication_id,
                expected_published_revision_id=exc.expected_published_revision_id,
            ) from exc
        except ImmutableRevisionConflictError as exc:
            raise PreparedChangeConflict(str(exc)) from exc
        except PersistenceUnavailableError as exc:
            self._raise_if_known_commit(prepared, unavailable=True, cause=exc)
            raise CommitAuthorityIntegrityFailure("DungeonMind publication unavailable") from exc
        except PersistenceIntegrityError as exc:
            self._raise_if_known_commit(prepared, unavailable=False, cause=exc)
            raise CommitAuthorityIntegrityFailure(
                "DungeonMind publication integrity failure"
            ) from exc

        receipt = aggregate.publication_receipt
        result = aggregate.prospective_result
        child_id = receipt.published_revision_id
        try:
            stored_child = self._repository.get_revision(prepared.space_id, child_id)
        except PersistenceUnavailableError as exc:
            raise CommittedChangeVerificationUnavailable(
                prepared_change_id=prepared.prepared_change_id,
                publication_id=prepared.dungeonmind_publication_id,
                child_revision_id=child_id,
            ) from exc
        except Exception as exc:
            raise CommittedChangeVerificationIntegrityFailure(
                prepared_change_id=prepared.prepared_change_id,
                publication_id=prepared.dungeonmind_publication_id,
                child_revision_id=child_id,
            ) from exc
        if stored_child is None:
            raise CommittedChangeVerificationIntegrityFailure(
                prepared_change_id=prepared.prepared_change_id,
                publication_id=prepared.dungeonmind_publication_id,
                child_revision_id=child_id,
            )
        child = self._parse(stored_child, committed=True, prepared=prepared, child_id=child_id)
        try:
            self._verify_child(prepared, plan, aggregate, child, stored_child.graph_payload)
        except CommittedChangeVerificationIntegrityFailure:
            raise
        except Exception as exc:
            raise CommittedChangeVerificationIntegrityFailure(
                prepared_change_id=prepared.prepared_change_id,
                publication_id=prepared.dungeonmind_publication_id,
                child_revision_id=child_id,
            ) from exc
        return CommitAuthorityWitness(
            space_id=prepared.space_id,
            publication_id=result.publication_id,
            expected_parent_revision_id=receipt.expected_parent_revision_id or "",
            child_revision_id=child_id,
            child_graph_payload_sha256=receipt.graph_payload_sha256,
            results=tuple(
                CommitResultBinding(item.client_op_id, item.result_kind, item.durable_id)
                for item in result.results
            ),
        )

    def _raise_if_known_commit(
        self,
        prepared: PreparedWorldChange,
        *,
        unavailable: bool,
        cause: Exception,
    ) -> None:
        try:
            aggregate = self._repository.get_prospective_publication(
                prepared.space_id, prepared.dungeonmind_publication_id
            )
        except Exception:
            return
        if aggregate is None:
            return
        error_type = (
            CommittedChangeVerificationUnavailable
            if unavailable
            else CommittedChangeVerificationIntegrityFailure
        )
        raise error_type(
            prepared_change_id=prepared.prepared_change_id,
            publication_id=prepared.dungeonmind_publication_id,
            child_revision_id=aggregate.prospective_result.published_revision_id,
        ) from cause

    def _before_commit(self, callback: Callable[[], _T]) -> _T:
        try:
            return callback()
        except Exception as exc:
            raise CommitAuthorityIntegrityFailure("prepared parent authority unavailable") from exc

    @staticmethod
    def _parse(
        stored: StoredKnowledgeRevision,
        *,
        committed: bool,
        prepared: PreparedWorldChange,
        child_id: str = "",
    ) -> ParsedKnowledgeRevision:
        try:
            return build_parsed_knowledge_revision(
                revision=stored.revision,
                decoded_content=decode_native_graph_payload(stored.graph_payload),
            )
        except Exception as exc:
            if committed:
                raise CommittedChangeVerificationIntegrityFailure(
                    prepared_change_id=prepared.prepared_change_id,
                    publication_id=prepared.dungeonmind_publication_id,
                    child_revision_id=child_id,
                ) from exc
            raise CommitAuthorityIntegrityFailure("prepared parent failed integrity") from exc

    @staticmethod
    def _verify_child(
        prepared: PreparedWorldChange,
        plan: DungeonMindPreparedProspectivePlan,
        aggregate: KnowledgeProspectivePublication,
        child: ParsedKnowledgeRevision,
        payload: dict[str, Any],
    ) -> None:
        receipt = aggregate.publication_receipt
        result = aggregate.prospective_result
        if (
            receipt.space_id != prepared.space_id
            or result.space_id != prepared.space_id
            or receipt.space_id != result.space_id
            or result.publication_id != prepared.prepared_change_id
            or receipt.publication_id != prepared.prepared_change_id
            or receipt.published_revision_id != result.published_revision_id
            or child.revision_id != result.published_revision_id
            or child.revision_id != receipt.published_revision_id
            or child.parent_revision_id != prepared.expected_parent_revision_id
            or child.graph_payload_sha256 != receipt.graph_payload_sha256
            or receipt.expected_parent_revision_id != prepared.expected_parent_revision_id
        ):
            raise ValueError("published identity drift")
        prospective_items = tuple(
            item
            for item in plan.prospective_contribution.items
            if isinstance(item, ProspectiveCreateEntity | ProspectiveCreateAssertion)
        )
        expected = {
            item.client_op_id: "entity"
            if isinstance(item, ProspectiveCreateEntity)
            else "assertion"
            for item in prospective_items
        }
        bindings = {item.client_op_id: item for item in result.results}
        if set(bindings) != set(expected) or any(
            bindings[key].result_kind != kind for key, kind in expected.items()
        ):
            raise ValueError("result binding mismatch")
        raw_entities = {item["entity_id"] for item in payload.get("entities", [])}
        raw_assertions = {item["assertion_id"]: item for item in payload.get("assertions", [])}
        plan_items = {item.client_op_id: item for item in prospective_items}
        for key, binding in bindings.items():
            if binding.result_kind == "entity":
                if (
                    binding.durable_id not in raw_entities
                    or binding.durable_id not in child.entities_by_id
                ):
                    raise ValueError("bound entity absent from child")
                continue
            if (
                binding.durable_id not in raw_assertions
                or binding.durable_id not in child.assertions_by_id
            ):
                raise ValueError("bound assertion absent from child")
            item = plan_items[key]
            assert isinstance(item, ProspectiveCreateAssertion)
            expected_assertion = Assertion(
                assertion_id=binding.durable_id,
                subject_entity_id=_resolve_operand(item.subject, bindings),
                predicate=item.predicate,
                value=EntityRefValue(entity_id=_resolve_operand(item.value.entity, bindings))
                if isinstance(item.value, ProspectiveEntityRefValue)
                else item.value,
                metadata=item.metadata,
            ).model_dump(mode="json")
            if raw_assertions[binding.durable_id] != expected_assertion:
                raise ValueError("published assertion meaning mismatch")


def _resolve_operand(value: EntityOperand, bindings: Mapping[str, ProspectiveResultBinding]) -> str:
    if isinstance(value, DurableEntityRef):
        return value.entity_id
    if isinstance(value, ProspectiveEntityRef):
        binding = bindings[value.client_op_id]
        if binding.result_kind != "entity":
            raise ValueError("endpoint binding is not an entity")
        return binding.durable_id
    raise ValueError("unsupported endpoint")
