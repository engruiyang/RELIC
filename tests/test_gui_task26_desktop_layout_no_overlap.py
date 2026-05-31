from __future__ import annotations

import json
from pathlib import Path

import pytest

from gui.desktop_model import (
    validate_task26_layout_no_overlap,
    validate_task26_page_layout_no_overlap,
)


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_task26_example_pages_have_no_desktop_card_overlap() -> None:
    validate_task26_layout_no_overlap(Path("."))


def test_task26_overlap_validator_rejects_intersecting_grid_cards() -> None:
    page = _load("assets/layouts/task26_examples/home_page.desktop_demo.json")
    assert len(page["cards"]) >= 2
    page["cards"][0]["position"] = {"col": 1, "row": 1, "col_span": 4, "row_span": 3}
    page["cards"][1]["position"] = {"col": 3, "row": 2, "col_span": 4, "row_span": 3}

    with pytest.raises(ValueError, match="desktop cards overlap"):
        validate_task26_page_layout_no_overlap(page)


def test_task26_overlap_validator_allows_edge_touching_separate_cards() -> None:
    page = _load("assets/layouts/task26_examples/home_page.desktop_demo.json")
    page["cards"] = page["cards"][:2]
    page["cards"][0]["position"] = {"col": 1, "row": 1, "col_span": 4, "row_span": 3}
    page["cards"][1]["position"] = {"col": 5, "row": 1, "col_span": 4, "row_span": 3}

    validate_task26_page_layout_no_overlap(page)
