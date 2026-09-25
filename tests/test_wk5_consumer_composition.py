from __future__ import annotations

from dataclasses import replace

import pytest

import test_wk4_commit_prepared_change as support
from worldkeeper import WorldChangeService
from worldkeeper.application.commit import (
    PreparedChangeIntegrityFailure,
    PreparedChangeStale,
)
from worldkeeper.integrations.dungeonmind import DungeonMindWorldKeeperRuntime


def runtime(repo, *, prepared_id_factory=None) -> DungeonMindWorldKeeperRuntime:
    contract, profile = support.descriptors()
    return DungeonMindWorldKeeperRuntime(
        repository=repo,
        domain_contract=contract,
        semantic_profile=profile,
        clock=lambda: support.NOW,
        prepared_id_factory=prepared_id_factory,
    )


def accepts_world_change_service(service: WorldChangeService) -> WorldChangeService:
    return service


def test_runtime_structurally_satisfies_world_change_service() -> None:
    service = runtime(support.repository())
    assert accepts_world_change_service(service) is service


def test_consumer_prepare_commit_and_retry_preserve_exact_result() -> None:
    repo = support.repository()
    service = runtime(repo, prepared_id_factory=lambda: "prepared:wk5-consumer")

    prepared = service.prepare_change(support.intent())
    first = service.commit_prepared_change(prepared, confirmed_by="user:keeper")
    events_after_first = repo.head_events("space:lab")
    second = service.commit_prepared_change(prepared, confirmed_by="user:keeper")

    assert first == second
    assert prepared.prepared_change_id == "prepared:wk5-consumer"
    assert first.object_results[0].client_op_id == "npc-7"
    assert first.object_results[0].durable_object_id.startswith("ent:")
    assert first.assertion_results[0].client_op_id == "rel-4"
    assert first.assertion_results[0].durable_assertion_id.startswith("asrt:")
    assert first.verification.exact_child_read_back is True
    assert repo.head_events("space:lab") == events_after_first


def test_runtime_preserves_default_and_injected_prepared_id_behavior() -> None:
    repo = support.repository()
    default_service = runtime(repo)
    first = default_service.prepare_change(support.intent())
    second = default_service.prepare_change(support.intent())
    assert first.prepared_change_id.startswith("prepared:")
    assert second.prepared_change_id.startswith("prepared:")
    assert first.prepared_change_id != second.prepared_change_id

    injected = runtime(repo, prepared_id_factory=lambda: "prepared:deterministic")
    assert injected.prepare_change(support.intent()).prepared_change_id == "prepared:deterministic"


def test_confirmation_and_prepared_integrity_errors_pass_through_unchanged() -> None:
    repo = support.repository()
    service = runtime(repo, prepared_id_factory=lambda: "prepared:wk5-errors")
    prepared = service.prepare_change(support.intent())

    with pytest.raises(ValueError, match="confirmed_by"):
        service.commit_prepared_change(prepared, confirmed_by=" ")
    with pytest.raises(PreparedChangeIntegrityFailure):
        service.commit_prepared_change(
            replace(prepared, parent_graph_payload_sha256="b" * 64),
            confirmed_by="user:keeper",
        )


def test_stale_prepared_error_passes_through_unchanged() -> None:
    repo = support.repository()
    stale_service = runtime(repo, prepared_id_factory=lambda: "prepared:wk5-stale")
    stale = stale_service.prepare_change(support.intent())
    advancing_service = runtime(repo, prepared_id_factory=lambda: "prepared:wk5-advance")
    advancing = advancing_service.prepare_change(support.intent())
    advancing_service.commit_prepared_change(advancing, confirmed_by="user:keeper")

    with pytest.raises(PreparedChangeStale):
        stale_service.commit_prepared_change(stale, confirmed_by="user:keeper")
