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


@pytest.mark.parametrize(
    ("y_anchor", "y_shift", "expected"),
    [(0.0, 0.0, (0, 770)), (350.0, 0.0, (-35, 735)), (350.0, 20.0, (-15, 755))],
)
def test_merge_scales_vertically_around_anchor(y_anchor, y_shift, expected) -> None:
    destination = _font({0x41: "A"}, advance=600)
    source = _font({0xAC00: "ga"}, advance=1_000)

    _merge_codepoints(
        destination,
        source,
        predicate=is_hangul,
        glyph_prefix="ko",
        scale=1.1,
        y_anchor=y_anchor,
        y_shift=y_shift,
    )

    glyph = destination["glyf"][destination.getBestCmap()[0xAC00]]
    assert (glyph.yMin, glyph.yMax) == expected


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


def _cff_font():
    from fontTools.pens.t2CharStringPen import T2CharStringPen

    builder = FontBuilder(2000, isTTF=False)
    order = [".notdef", "ga"]
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap({0xAC00: "ga"})
    charstrings = {}
    for name in order:
        pen = T2CharStringPen(1000, None)
        pen.moveTo((100, 0))
        pen.curveTo((100, 700), (500, 700), (500, 0))
        pen.closePath()
        charstrings[name] = pen.getCharString()
    builder.setupCFF("Fixture", {}, charstrings, {})
    builder.setupHorizontalMetrics(dict.fromkeys(order, (1000, 100)))
    builder.setupHorizontalHeader(ascent=1600, descent=-400)
    builder.setupNameTable({"familyName": "Fixture", "styleName": "Regular"})
    builder.setupOS2(sTypoAscender=1600, sTypoDescender=-400)
    builder.setupPost()
    return builder.font


def test_cff_merge_converts_curves_normalizes_upm_and_reverses_winding():
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.recordingPen import RecordingPen

    destination = _font({0x41: "A"}, advance=600)
    source = _cff_font()
    _merge_codepoints(destination, source, predicate=is_hangul, glyph_prefix="ko", scale=1.0)
    name = destination.getBestCmap()[0xAC00]
    glyph = destination["glyf"][name]
    assert (glyph.xMin, glyph.xMax) == (400, 600)
    assert destination["hmtx"][name][0] == 1200
    recording = RecordingPen()
    glyph.draw(recording, destination["glyf"])
    assert any(op == "qCurveTo" for op, _ in recording.value)
    assert not any(op == "curveTo" for op, _ in recording.value)
    before = AreaPen(None)
    source.getGlyphSet()["ga"].draw(before)
    after = AreaPen(None)
    glyph.draw(after, destination["glyf"])
    assert before.value * after.value < 0
    _verify_glyph_inventory(destination)


@pytest.mark.parametrize("face_index", range(4))
def test_preview_build_uses_maru_buri_at_the_face_weight(tmp_path, face_index):
    from fontTools.ttLib import TTFont

    from gyeol_mono.builder import BuildTarget
    from gyeol_mono.font_builder import build_preview_font, validate_built_font
    from gyeol_mono.japanese import JapaneseSource
    from gyeol_mono.models import FACES

    face = FACES[face_index]
    latin = tmp_path / "latin.ttf"
    _font({cp: f"g{cp}" for cp in range(32, 127)}, advance=600).save(latin)
    maru = tmp_path / "maru.ttf"
    _font({0xAC00: "ga"}, advance=1000).save(maru)
    jp = tmp_path / "jp.ttf"
    _font({0x3042: "a", 0x65E5: "day"}, advance=1000).save(jp)
    calls = []

    class Layout:
        def font(self, source_id, file_name):
            calls.append((source_id, file_name))
            return {"ibm-plex-mono": latin, "maru-buri": maru, "ibm-plex-sans-jp": jp}[source_id]

    target = BuildTarget(JapaneseSource.IBM_PLEX_SANS_JP, face, False, True)
    artifact = build_preview_font(target, layout=Layout(), output_root=tmp_path / "out")
    weight = "SemiBold" if face.output_weight == 700 else "Regular"
    assert ("maru-buri", f"MaruBuri-{weight}.ttf") in calls
    assert not any(source == "ridi-batang" for source, _ in calls)
    assert artifact.hangul_glyphs == 1
    for path in (artifact.ttf_path, artifact.woff2_path):
        validate_built_font(path, target)
        with TTFont(path) as font:
            glyph = font["glyf"][font.getBestCmap()[0xAC00]]
            # Hangul 1.10 around y=300, then +30: x 100..500 -> 160..600, y 0..700 -> 0..770.
            assert (glyph.xMin, glyph.xMax, glyph.yMin, glyph.yMax) == (160, 600, 0, 770)


def test_validate_rejects_hangul_outside_cell(tmp_path):
    from gyeol_mono.builder import BuildTarget
    from gyeol_mono.font_builder import build_preview_font
    from gyeol_mono.japanese import JapaneseSource
    from gyeol_mono.models import FACES

    paths = {
        "ibm-plex-mono": _font({cp: f"g{cp}" for cp in range(32, 127)}, advance=600),
        "maru-buri": _font({0xAC00: "ga"}, advance=1000),
        "ibm-plex-sans-jp": _font({0x3042: "a", 0x65E5: "day"}, advance=1000),
    }
    for source_id, font in paths.items():
        paths[source_id] = tmp_path / f"{source_id}.ttf"
        font.save(paths[source_id])

    class Layout:
        def font(self, source_id, file_name):
            return paths[source_id]

    target = BuildTarget(JapaneseSource.IBM_PLEX_SANS_JP, FACES[0], False, True)
    with pytest.raises(FontBuildError, match="exceeds the cell"):
        build_preview_font(target, layout=Layout(), output_root=tmp_path / "out", hangul_scale=2.0)
