from __future__ import annotations
import pytest
from src.core.build_library_engine import BuildLibraryEngine

def test_build_library_load(tmp_path) -> None:
    engine = BuildLibraryEngine(library_dir=tmp_path)
    assert len(engine.load_library()) == 0

def test_build_library_add_update(tmp_path) -> None:
    engine = BuildLibraryEngine(library_dir=tmp_path)
    engine.add_or_update_build("Soma Prime", ["Serration"], "None", "Slash")
    builds = engine.load_library()
    assert len(builds) == 1
    assert builds[0]["weapon"] == "Soma Prime"

def test_build_library_delete(tmp_path) -> None:
    engine = BuildLibraryEngine(library_dir=tmp_path)
    engine.add_or_update_build("Soma Prime", ["Serration"], "None", "Slash")
    engine.delete_build("Soma Prime")
    assert len(engine.load_library()) == 0

def test_build_library_toggle_favorite(tmp_path) -> None:
    engine = BuildLibraryEngine(library_dir=tmp_path)
    engine.add_or_update_build("Soma Prime", ["Serration"], "None", "Slash", is_favorite=False)
    engine.toggle_favorite("Soma Prime")
    builds = engine.load_library()
    assert builds[0]["is_favorite"] is True
