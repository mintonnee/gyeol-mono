"""Prototype TTF/WOFF2 builder for the non-Powerline preview families."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

from gyeol_mono.builder import BuildTarget
from gyeol_mono.japanese import JapaneseSource
from gyeol_mono.metrics import CJK_ADVANCE, LATIN_ADVANCE, POWERLINE_CELL
from gyeol_mono.models import FaceSpec
from gyeol_mono.upstream import UpstreamManifest

HANGUL_RANGES = (
    (0x1100, 0x11FF),
    (0x3130, 0x318F),
    (0xA960, 0xA97F),
    (0xAC00, 0xD7A3),
    (0xD7B0, 0xD7FF),
)
JAPANESE_RANGES = (
    (0x3000, 0x303F),
    (0x3040, 0x309F),
    (0x30A0, 0x30FF),
    (0x31F0, 0x31FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0x20000, 0x2A6DF),
    (0x2A700, 0x2EE5F),
    (0x2F800, 0x2FA1F),
    (0x30000, 0x323AF),
)


class FontBuildError(RuntimeError):
    """Raised when a source or generated font violates the build contract."""


@dataclass(frozen=True, slots=True)
class BuiltFont:
    target: BuildTarget
    ttf_path: Path
    woff2_path: Path
    hangul_glyphs: int
    japanese_glyphs: int


@dataclass(frozen=True, slots=True)
class SourceLayout:
    manifest: UpstreamManifest
    root: Path

    def font(self, source_id: str, file_name: str) -> Path:
        source = self.manifest.select((source_id,))[0]
        matches = [member for member in source.files if Path(member).name == file_name]
        if len(matches) != 1:
            raise FontBuildError(
                f"expected one {file_name} entry for {source_id}, found {len(matches)}"
            )
        path = self.root / source.id / matches[0]
        if not path.is_file():
            raise FontBuildError(f"source font is missing; run `gyeol-mono fetch`: {path}")
        return path


def is_hangul(codepoint: int) -> bool:
    return _in_ranges(codepoint, HANGUL_RANGES)


def is_japanese(codepoint: int) -> bool:
    return _in_ranges(codepoint, JAPANESE_RANGES)


def build_preview_font(
    target: BuildTarget,
    *,
    layout: SourceLayout,
    output_root: Path,
    scale: float = 1.0,
) -> BuiltFont:
    if target.powerline or not target.preview:
        raise FontBuildError("prototype builder only supports non-Powerline preview targets")
    if scale <= 0:
        raise FontBuildError("CJK scale must be positive")

    latin_path = layout.font("ibm-plex-mono", _latin_file_name(target.face))
    hangul_path = layout.font("maru-buri", _maru_file_name(target.face))
    japanese_path = layout.font(
        target.japanese_source.value,
        _japanese_file_name(target.japanese_source, target.face),
    )

    output_dir = output_root / f"preview-{_preview_label(target.japanese_source).lower()}"
    output_dir.mkdir(parents=True, exist_ok=True)
    ttf_path = output_dir / target.names.file_name
    woff2_path = ttf_path.with_suffix(".woff2")

    font = TTFont(latin_path, recalcBBoxes=True, recalcTimestamp=False)
    hangul = TTFont(hangul_path, recalcBBoxes=False, recalcTimestamp=False)
    japanese = TTFont(japanese_path, recalcBBoxes=False, recalcTimestamp=False)
    try:
        _verify_truetype(font, "IBM Plex Mono")
        _verify_outline_source(hangul, "Maru Buri")
        _verify_truetype(japanese, target.japanese_source.value)
        _verify_latin_metrics(font)

        hangul_count = _merge_codepoints(
            font,
            hangul,
            predicate=is_hangul,
            glyph_prefix="ko",
            scale=scale,
        )
        japanese_count = _merge_codepoints(
            font,
            japanese,
            predicate=is_japanese,
            glyph_prefix="ja",
            scale=scale,
        )
        _verify_glyph_inventory(font)
        _normalize_metadata(font, target)
        font.save(ttf_path, reorderTables=False)
    finally:
        japanese.close()
        hangul.close()
        font.close()

    validate_built_font(ttf_path, target)
    _save_woff2(ttf_path, woff2_path)
    validate_built_font(woff2_path, target)
    return BuiltFont(target, ttf_path, woff2_path, hangul_count, japanese_count)


def validate_built_font(path: Path, target: BuildTarget) -> None:
    font = TTFont(path, recalcTimestamp=False)
    try:
        cmap = font.getBestCmap()
        for codepoint in (0x41, 0xAC00, 0x3042, 0x65E5):
            if codepoint not in cmap:
                raise FontBuildError(f"{path} is missing U+{codepoint:04X}")

        for codepoint in range(0x20, 0x7F):
            glyph_name = cmap.get(codepoint)
            if glyph_name and font["hmtx"].metrics[glyph_name][0] != LATIN_ADVANCE:
                raise FontBuildError(f"{path}: ASCII U+{codepoint:04X} is not 600 units")
        for codepoint in (0xAC00, 0x3042, 0x65E5):
            glyph_name = cmap[codepoint]
            if font["hmtx"].metrics[glyph_name][0] != CJK_ADVANCE:
                raise FontBuildError(f"{path}: U+{codepoint:04X} is not 1200 units")

        expected_italic = target.face.italic
        expected_bold = target.face.output_weight == 700
        if font["OS/2"].usWeightClass != target.face.output_weight:
            raise FontBuildError(f"{path}: incorrect OS/2 weight")
        if bool(font["OS/2"].fsSelection & 1) != expected_italic:
            raise FontBuildError(f"{path}: incorrect italic selection bit")
        if bool(font["OS/2"].fsSelection & (1 << 5)) != expected_bold:
            raise FontBuildError(f"{path}: incorrect bold selection bit")
        if font["name"].getDebugName(1) != target.names.family:
            raise FontBuildError(f"{path}: incorrect family name")
        if font["post"].isFixedPitch != 1:
            raise FontBuildError(f"{path}: fixed-pitch flag is not set")
    finally:
        font.close()


def _merge_codepoints(
    destination: TTFont,
    source: TTFont,
    *,
    predicate: Callable[[int], bool],
    glyph_prefix: str,
    scale: float,
) -> int:
    source_cmap = source.getBestCmap()
    selected = [(cp, name) for cp, name in sorted(source_cmap.items()) if predicate(cp)]
    if not selected:
        raise FontBuildError(f"no {glyph_prefix} glyphs selected from source")

    destination_glyf = destination["glyf"]
    source_glyf = source.get("glyf")
    source_glyph_set = source.getGlyphSet() if source_glyf is None else None
    source_metrics = source["hmtx"].metrics
    target_upm = destination["head"].unitsPerEm
    source_upm = source["head"].unitsPerEm
    outline_scale = scale * target_upm / source_upm
    source_to_destination: dict[str, str] = {}
    cmap_additions: dict[int, str] = {}

    for codepoint, source_name in selected:
        destination_name = source_to_destination.get(source_name)
        if destination_name is None:
            destination_name = f"gyeol.{glyph_prefix}.{codepoint:X}"
            source_advance = source_metrics[source_name][0]
            scaled_advance = source_advance * outline_scale
            x_offset = (CJK_ADVANCE - scaled_advance) / 2
            pen = TTGlyphPen(None)
            transformed_pen = TransformPen(
                pen,
                (outline_scale, 0, 0, outline_scale, x_offset, 0),
            )
            if source_glyf is not None:
                _draw_decomposed(source_glyf, source_name, transformed_pen, stack=())
            else:
                # CFF contours have the opposite winding to TrueType contours.
                # Approximate in source coordinates to keep the error scale-independent.
                source_glyph_set[source_name].draw(
                    Cu2QuPen(
                        transformed_pen,
                        max_err=source_upm / 1000,
                        reverse_direction=True,
                    )
                )
            glyph = pen.glyph()
            destination_glyf[destination_name] = glyph
            glyph.recalcBounds(destination_glyf)
            left_side_bearing = getattr(glyph, "xMin", 0)
            destination["hmtx"].metrics[destination_name] = (
                CJK_ADVANCE,
                left_side_bearing,
            )
            source_to_destination[source_name] = destination_name
        cmap_additions[codepoint] = destination_name

    destination.setGlyphOrder(list(destination_glyf.glyphOrder))
    _update_cmap(destination, cmap_additions)
    return len(source_to_destination)


def _draw_decomposed(glyf_table, glyph_name: str, pen, *, stack: tuple[str, ...]) -> None:
    if glyph_name in stack:
        raise FontBuildError(f"cyclic composite glyph: {' -> '.join((*stack, glyph_name))}")
    glyph = glyf_table[glyph_name]
    if not glyph.isComposite():
        glyph.draw(pen, glyf_table)
        return
    for component in glyph.components:
        component_name, transform = component.getComponentInfo()
        component_pen = TransformPen(pen, transform)
        _draw_decomposed(
            glyf_table,
            component_name,
            component_pen,
            stack=(*stack, glyph_name),
        )


def _update_cmap(font: TTFont, additions: dict[int, str]) -> None:
    unicode_tables = [table for table in font["cmap"].tables if table.isUnicode()]
    for table in unicode_tables:
        for codepoint, glyph_name in additions.items():
            if codepoint <= 0xFFFF or table.format in {12, 13}:
                table.cmap[codepoint] = glyph_name

    if any(codepoint > 0xFFFF for codepoint in additions) and not any(
        table.format == 12 for table in unicode_tables
    ):
        table = CmapSubtable.newSubtable(12)
        table.platformID = 3
        table.platEncID = 10
        table.language = 0
        table.cmap = {**font.getBestCmap(), **additions}
        font["cmap"].tables.append(table)


def _normalize_metadata(font: TTFont, target: BuildTarget) -> None:
    if "DSIG" in font:
        del font["DSIG"]

    name_values = {
        1: target.names.family,
        2: target.names.subfamily,
        3: f"Gyeol Mono 0.1.0;{target.names.postscript_name}",
        4: target.names.full_name,
        6: target.names.postscript_name,
        16: target.names.family,
        17: target.names.subfamily,
    }
    name_table = font["name"]
    for name_id in name_values:
        name_table.removeNames(nameID=name_id)
    for name_id, value in name_values.items():
        name_table.setName(value, name_id, 0, 4, 0)
        name_table.setName(value, name_id, 1, 0, 0)
        name_table.setName(value, name_id, 3, 1, 0x409)

    is_bold = target.face.output_weight == 700
    is_italic = target.face.italic
    font["head"].macStyle &= ~0b11
    font["head"].macStyle |= int(is_bold) | (int(is_italic) << 1)
    font["head"].modified = font["head"].created

    os2 = font["OS/2"]
    os2.usWeightClass = target.face.output_weight
    os2.usWidthClass = 5
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6) | (1 << 9))
    os2.fsSelection |= int(is_italic) << 0
    os2.fsSelection |= int(is_bold) << 5
    if not is_bold and not is_italic:
        os2.fsSelection |= 1 << 6
    os2.sTypoAscender = POWERLINE_CELL.y_max
    os2.sTypoDescender = POWERLINE_CELL.y_min
    os2.sTypoLineGap = 0
    os2.usWinAscent = POWERLINE_CELL.y_max
    os2.usWinDescent = abs(POWERLINE_CELL.y_min)
    os2.xAvgCharWidth = LATIN_ADVANCE
    os2.panose.bProportion = 9
    os2.recalcUnicodeRanges(font)
    os2.recalcCodePageRanges(font)

    font["hhea"].ascent = POWERLINE_CELL.y_max
    font["hhea"].descent = POWERLINE_CELL.y_min
    font["hhea"].lineGap = 0
    font["hhea"].advanceWidthMax = CJK_ADVANCE
    font["post"].isFixedPitch = 1
    font["post"].formatType = 3.0


def _save_woff2(ttf_path: Path, woff2_path: Path) -> None:
    font = TTFont(ttf_path, recalcTimestamp=False)
    try:
        font.flavor = "woff2"
        font.save(woff2_path, reorderTables=False)
    finally:
        font.close()


def _verify_truetype(font: TTFont, label: str) -> None:
    if "glyf" not in font or "hmtx" not in font or "cmap" not in font:
        raise FontBuildError(f"{label} must be a TrueType-flavored font")


def _verify_outline_source(font: TTFont, label: str) -> None:
    if not {"hmtx", "cmap"}.issubset(font.keys()) or not ("glyf" in font or "CFF " in font):
        raise FontBuildError(f"{label} must contain TrueType or CFF outlines")


def _verify_latin_metrics(font: TTFont) -> None:
    cmap = font.getBestCmap()
    for codepoint in range(0x20, 0x7F):
        glyph_name = cmap.get(codepoint)
        if glyph_name is None or font["hmtx"].metrics[glyph_name][0] != LATIN_ADVANCE:
            raise FontBuildError(f"IBM Plex Mono U+{codepoint:04X} is not 600 units")


def _verify_glyph_inventory(font: TTFont) -> None:
    order = font.getGlyphOrder()
    glyph_names = set(font["glyf"].glyphs)
    order_names = set(order)
    if len(order) != len(glyph_names) or order_names != glyph_names:
        missing_from_order = sorted(glyph_names - order_names)[:5]
        missing_from_glyf = sorted(order_names - glyph_names)[:5]
        raise FontBuildError(
            "glyph order and glyf table differ: "
            f"order={len(order)}, glyf={len(glyph_names)}, "
            f"missing_from_order={missing_from_order}, "
            f"missing_from_glyf={missing_from_glyf}"
        )


def _latin_file_name(face: FaceSpec) -> str:
    return f"IBMPlexMono-{face.latin_source_style.replace(' ', '')}.ttf"


def _maru_file_name(face: FaceSpec) -> str:
    weight = "Regular" if face.source_weight == 400 else "SemiBold"
    return f"MaruBuri-{weight}.ttf"


def _japanese_file_name(source: JapaneseSource, face: FaceSpec) -> str:
    weight = "Regular" if face.source_weight == 400 else "SemiBold"
    prefix = "KleeOne" if source is JapaneseSource.KLEE_ONE else "IBMPlexSansJP"
    return f"{prefix}-{weight}.ttf"


def _preview_label(source: JapaneseSource) -> str:
    return "A" if source is JapaneseSource.KLEE_ONE else "B"


def _in_ranges(codepoint: int, ranges: Iterable[tuple[int, int]]) -> bool:
    return any(start <= codepoint <= end for start, end in ranges)
