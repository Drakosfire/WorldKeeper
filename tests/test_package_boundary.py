"""The package can be consumed without a service host or hidden write path."""

from pathlib import Path


def test_worldkeeper_imports_as_an_independent_package() -> None:
    import worldkeeper

    assert worldkeeper.GovernedWorldAuthority.__module__.startswith("worldkeeper.")
    assert hasattr(worldkeeper, "WorldChangePreparer")
    assert not hasattr(worldkeeper, "commit_change")
    assert not hasattr(worldkeeper, "commit_prepared_change")


def test_dungeonmind_integration_exports_wk2_and_wk3_authorities() -> None:
    from worldkeeper.integrations import dungeonmind

    assert "DungeonMindInProcessAuthority" in dungeonmind.__all__
    assert "DungeonMindVNextPreparationAuthority" in dungeonmind.__all__
    assert dungeonmind.DungeonMindInProcessAuthority.__module__.endswith(".in_process")
    assert dungeonmind.DungeonMindVNextPreparationAuthority.__module__.endswith(".vnext_prepare")


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
