"""The WK-2 package can be consumed without a service host."""


def test_worldkeeper_imports_as_an_independent_package() -> None:
    import worldkeeper

    assert worldkeeper.GovernedWorldAuthority.__module__.startswith("worldkeeper.")
    assert not hasattr(worldkeeper, "prepare_change")
    assert not hasattr(worldkeeper, "commit_prepared_change")
