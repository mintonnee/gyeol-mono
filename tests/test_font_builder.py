from pathlib import Path

import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from gyeol_mono.font_builder import (
    FontBuildError,
    SourceLayout,
    _merge_codepoints,
    _verify_glyph_inventory,
    is_hangul,
    is_japanese,
)
from gyeol_mono.upstream import UpstreamManifest, UpstreamSource


def test_script_ownership_ranges() -> None:
    assert is_hangul(0x1100)
    assert is_hangul(0xAC00)
    assert not is_hangul(0x3042)
    assert is_japanese(0x3042)
    assert is_japanese(0x30A2)
    assert is_japanese(0x65E5)
    assert is_japanese(0x20000)
    assert not is_japanese(0x41)


def test_source_layout_requires_fetched_font(tmp_path: Path) -> None:
    source = UpstreamSource(
        id="fixture",
        role="test",
        version="1",
        release_page="https://example.com/release",
        url="https://example.com/font.zip",
        archive="font.zip",
        sha256="0" * 64,
        files=("fonts/Regular.ttf",),
    )
    layout = SourceLayout(UpstreamManifest((source,)), tmp_path)

    with pytest.raises(FontBuildError, match="gyeol-mono fetch"):
        layout.font("fixture", "Regular.ttf")


def test_consecutive_merges_keep_glyph_order_unique() -> None:
    destination = _font({0x41: "A"}, advance=600)
    hangul = _font({0xAC00: "ga"}, advance=1_000)
    japanese = _font({0x3042: "hiragana-a"}, advance=1_000)

    _merge_codepoints(
        destination,
        hangul,
        predicate=lambda _codepoint: True,
        glyph_prefix="ko",
        scale=1.0,
    )
    _merge_codepoints(
        destination,
        japanese,
        predicate=lambda _codepoint: True,
        glyph_prefix="ja",
        scale=1.0,
    )

    _verify_glyph_inventory(destination)
    assert len(destination.getGlyphOrder()) == len(set(destination.getGlyphOrder()))


def _font(cmap: dict[int, str], *, advance: int):
    glyph_order = [".notdef", *cmap.values()]
    glyphs = {}
    for glyph_name in glyph_order:
        pen = TTGlyphPen(None)
        pen.moveTo((100, 0))
        pen.lineTo((100, 700))
        pen.lineTo((500, 700))
        pen.lineTo((500, 0))
        pen.closePath()
        glyphs[glyph_name] = pen.glyph()

    builder = FontBuilder(1_000, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(dict.fromkeys(glyph_order, (advance, 100)))
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable({"familyName": "Fixture", "styleName": "Regular"})
    builder.setupOS2(sTypoAscender=800, sTypoDescender=-200)
    builder.setupPost()
    return builder.font
