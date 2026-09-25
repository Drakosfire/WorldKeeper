"""The package can be consumed without a service host or hidden write path."""

from pathlib import Path


def test_worldkeeper_imports_as_an_independent_package() -> None:
    import worldkeeper

    assert worldkeeper.GovernedWorldAuthority.__module__.startswith("worldkeeper.")
    assert hasattr(worldkeeper, "WorldChangePreparer")
    assert not hasattr(worldkeeper, "commit_change")
    assert not hasattr(worldkeeper, "commit_prepared_change")


def test_dungeonmind_integration_exports_wk2_wk3_and_wk4_authorities() -> None:
    from worldkeeper.integrations import dungeonmind

    assert "DungeonMindInProcessAuthority" in dungeonmind.__all__
    assert "DungeonMindVNextPreparationAuthority" in dungeonmind.__all__
    assert dungeonmind.DungeonMindInProcessAuthority.__module__.endswith(".in_process")
    assert dungeonmind.DungeonMindVNextPreparationAuthority.__module__.endswith(".vnext_prepare")
    assert "DungeonMindVNextCommitAuthority" in dungeonmind.__all__
    assert dungeonmind.DungeonMindVNextCommitAuthority.__module__.endswith(".vnext_commit")


def test_wk3_prepare_source_has_no_publication_or_allocator_entrypoints() -> None:
    root = Path(__file__).parents[1] / "src" / "worldkeeper"
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            root / "application" / "preparation.py",
            root / "integrations" / "dungeonmind" / "vnext_prepare.py",
        )
    )
    forbidden = (
        "publish_prospective_contribution",
        "publish_governed_materialization",
        "publish_publication(",
        "publish_prospective_publication(",
        "commit_expected_parent",
        "allocate_prospective_result_id",
    )
    assert not any(name in source for name in forbidden)


def test_wk4_commit_source_does_not_import_or_call_dungeonmind_allocator() -> None:
    root = Path(__file__).parents[1] / "src" / "worldkeeper"
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            root / "application" / "commit.py",
            root / "integrations" / "dungeonmind" / "vnext_commit.py",
        )
    )
    assert "allocate_prospective_result_id" not in source


def test_wk5_application_protocol_has_no_integration_or_transport_dependencies() -> None:
    root = Path(__file__).parents[1] / "src" / "worldkeeper"
    source = (root / "application" / "service.py").read_text(encoding="utf-8")
    forbidden = ("dungeonmind", "DungeonBuddy", "fastapi", "sqlalchemy", "repository")
    assert not any(name in source for name in forbidden)


def test_wk5_runtime_only_composes_accepted_services() -> None:
    root = Path(__file__).parents[1] / "src" / "worldkeeper"
    source = (root / "integrations" / "dungeonmind" / "runtime.py").read_text(encoding="utf-8")
    assert "WorldChangePreparer" in source
    assert "WorldChangeCommitter" in source
    forbidden = (
        "publish_prospective_contribution",
        "publish_prospective_publication",
        "allocate_prospective_result_id",
        "get_prospective_publication",
    )
    assert not any(name in source for name in forbidden)


def test_top_level_worldkeeper_does_not_export_dungeonmind_composition_types() -> None:
    import worldkeeper

    assert hasattr(worldkeeper, "WorldChangeService")
    assert not hasattr(worldkeeper, "DungeonMindWorldKeeperRuntime")
    assert not hasattr(worldkeeper, "KnowledgeRevisionRepository")
    assert not hasattr(worldkeeper, "DomainContractDescriptor")
    assert not hasattr(worldkeeper, "SemanticProfileDescriptorV2")
