from pathlib import Path

import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from gyeol_mono.emoji import EmojiDataError, load_emoji_presentation, parse_emoji_presentation
from gyeol_mono.font_builder import (
    _alias_codepoints,
    _remove_codepoints,
    _verify_glyph_inventory,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EMOJI_DATA = """\
# emoji-data.txt fixture
0023          ; Emoji                # E0.0   [1] (#️) hash sign
2665          ; Emoji                # E0.6   [1] (♥️) heart suit
26A1          ; Emoji                # E0.6   [1] (⚡) high voltage
231A..231B    ; Emoji_Presentation   # E0.6   [2] (⌚..⌛) watch..hourglass done
26A1          ; Emoji_Presentation   # E0.6   [1] (⚡) high voltage
274C          ; Emoji_Presentation   # E0.6   [1] (❌) cross mark
1F600         ; Emoji_Presentation   # E1.0   [1] (😀) grinning face
"""


def test_parser_keeps_only_emoji_presentation() -> None:
    assert parse_emoji_presentation(EMOJI_DATA) == {0x231A, 0x231B, 0x26A1, 0x274C, 0x1F600}


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "no Emoji_Presentation"),
        ("231A ; Emoji_Presentation ; extra\n", "expected 2 fields"),
        ("XYZ ; Emoji_Presentation\n", "invalid range"),
        ("231B..231A ; Emoji_Presentation\n", "reversed range"),
    ],
)
def test_parser_rejects_malformed_data(text: str, message: str) -> None:
    with pytest.raises(EmojiDataError, match=message):
        parse_emoji_presentation(text)


def test_fetched_unicode_data_excludes_text_presentation_symbols() -> None:
    path = PROJECT_ROOT / "upstream" / "unicode-emoji-data" / "emoji-data.txt"
    if not path.is_file():
        pytest.skip("run `gyeol-mono fetch --source unicode-emoji-data` first")

    codepoints = load_emoji_presentation(path)

    assert {0x274C, 0x26A1, 0x2705, 0x1F44D} <= codepoints
    assert codepoints.isdisjoint({0x23, 0x30, 0xA9, 0x2630, 0x2665, 0x2605})


def test_remove_unmaps_and_prunes_only_unreachable_glyphs() -> None:
    font = _font(
        {
            0x41: "A",
            0x231A: "watch",
            0x231B: "shared",
            0x2373: "shared",
            0x274C: "cross",
            0x26A1: "bolt",
            0x1F600: "smile",
        },
        composites={"Acomp": "cross"},
        features="feature liga { sub A A by bolt; } liga;",
    )

    removed = _remove_codepoints(font, parse_emoji_presentation(EMOJI_DATA))

    assert removed == (0x231A, 0x231B, 0x26A1, 0x274C, 0x1F600)
    for table in font["cmap"].tables:
        assert table.cmap.keys().isdisjoint(removed)
    assert font.getBestCmap()[0x2373] == "shared"
    order = set(font.getGlyphOrder())
    assert {"watch", "smile"}.isdisjoint(order)
    # Still reachable through another codepoint, a composite or GSUB.
    assert {"shared", "cross", "bolt"} <= order
    assert "watch" not in font["hmtx"].metrics
    _verify_glyph_inventory(font)


def test_cross_mark_outline_survives_as_ballot_x() -> None:
    font = _font({0x41: "A", 0x274C: "cross"}, composites={}, features="")

    assert _alias_codepoints(font, {0x274C: 0x2717}) == {0x2717: "cross"}
    _remove_codepoints(font, parse_emoji_presentation(EMOJI_DATA))

    assert 0x274C not in font.getBestCmap()
    for table in font["cmap"].tables:
        assert table.cmap[0x2717] == "cross"
    assert "cross" in font.getGlyphOrder()


def test_alias_never_replaces_an_existing_glyph() -> None:
    font = _font({0x274C: "cross", 0x2717: "ballot"}, composites={}, features="")

    assert _alias_codepoints(font, {0x274C: 0x2717}) == {}
    assert font.getBestCmap()[0x2717] == "ballot"


def _font(
    cmap: dict[int, str],
    *,
    composites: dict[str, str],
    features: str,
):
    glyph_order = [".notdef", *dict.fromkeys(cmap.values()), *composites]
    glyphs = {}
    for glyph_name in glyph_order:
        pen = TTGlyphPen(glyphs)
        if glyph_name in composites:
            pen.addComponent(composites[glyph_name], (1, 0, 0, 1, 0, 0))
        else:
            pen.moveTo((100, 0))
            pen.lineTo((100, 700))
            pen.lineTo((500, 700))
            pen.closePath()
        glyphs[glyph_name] = pen.glyph()

    builder = FontBuilder(1_000, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(dict.fromkeys(glyph_order, (600, 100)))
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.addOpenTypeFeatures(features)
    return builder.font
