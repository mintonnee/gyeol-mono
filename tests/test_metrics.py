import pytest

from gyeol_mono.metrics import (
    CJK_ADVANCE,
    CJK_GUARD,
    CJK_SCALE_CANDIDATES,
    LATIN_ADVANCE,
    Cell,
    is_valid_advance,
)


def test_duospace_metrics_match_specification() -> None:
    assert LATIN_ADVANCE == 600
    assert CJK_ADVANCE == 2 * LATIN_ADVANCE
    assert CJK_GUARD == 12
    assert CJK_SCALE_CANDIDATES == (1.00, 1.05, 1.10, 1.15)
    assert is_valid_advance(600)
    assert is_valid_advance(1_200)
    assert not is_valid_advance(970)


def test_cell_rejects_inverted_bounds() -> None:
    with pytest.raises(ValueError, match="positive width and height"):
        Cell(x_min=600, x_max=0, y_min=-275, y_max=1_025)
