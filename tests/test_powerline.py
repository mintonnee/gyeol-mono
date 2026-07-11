from pathlib import Path

from gyeol_mono.powerline import (
    FORBIDDEN_PATCHER_OPTIONS,
    POWERLINE_CODEPOINTS,
    font_patcher_args,
)


def test_powerline_subset_has_specified_boundaries() -> None:
    assert {0xE0A0, 0xE0A2, 0xE0B0, 0xE0B3, 0x2630} <= POWERLINE_CODEPOINTS
    assert 0xE0D7 in POWERLINE_CODEPOINTS
    assert 0xE0D8 not in POWERLINE_CODEPOINTS


def test_patcher_uses_single_width_without_mono(tmp_path: Path) -> None:
    args = font_patcher_args(
        tmp_path / "IBMPlexMono-Italic.ttf",
        tmp_path / "patched",
        patcher=tmp_path / "font-patcher",
    )

    assert "--single-width-glyphs" in args
    assert "--cell" in args
    assert "0:600:-275:1025" in args
    assert FORBIDDEN_PATCHER_OPTIONS.isdisjoint(args)
