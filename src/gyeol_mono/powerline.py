"""Nerd Fonts Powerline subset and patcher invocation policy."""

from pathlib import Path

from gyeol_mono.metrics import POWERLINE_CELL

POWERLINE_CORE = (
    *range(0xE0A0, 0xE0A3),
    *range(0xE0B0, 0xE0B4),
)
POWERLINE_EXTRA = (
    0xE0A3,
    *range(0xE0B4, 0xE0C9),
    0xE0CA,
    *range(0xE0CC, 0xE0D8),
    0x2630,
)
POWERLINE_CODEPOINTS = frozenset((*POWERLINE_CORE, *POWERLINE_EXTRA))

FORBIDDEN_PATCHER_OPTIONS = frozenset(
    {"--mono", "--complete", "--adjust-line-height", "--variable-width-glyphs"}
)


def font_patcher_args(
    source_font: Path,
    output_dir: Path,
    *,
    patcher: Path,
) -> list[str]:
    """Return argv without executing FontForge or touching the source font."""
    return [
        "fontforge",
        "-script",
        str(patcher.resolve()),
        str(source_font.resolve()),
        "--powerline",
        "--powerlineextra",
        "--single-width-glyphs",
        "--careful",
        "--metrics",
        "HHEA",
        "--cell",
        POWERLINE_CELL.patcher_value,
        "--makegroups",
        "-1",
        "--outputdir",
        str(output_dir.resolve()),
    ]
