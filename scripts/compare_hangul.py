"""Build isolated Regular-only Hangul scale comparisons; run from repository root."""

import argparse
import csv
import json
from pathlib import Path
from urllib.request import urlopen

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from gyeol_mono.builder import BuildTarget
from gyeol_mono.font_builder import (
    SourceLayout,
    _merge_codepoints,
    _normalize_metadata,
    _save_woff2,
    is_hangul,
    is_japanese,
    validate_built_font,
)
from gyeol_mono.japanese import JapaneseSource
from gyeol_mono.metrics import CJK_ADVANCE, CJK_GUARD, CJK_SCALE_CANDIDATES, HANGUL_Y_ANCHOR
from gyeol_mono.models import FACES
from gyeol_mono.upstream import load_manifest, sha256

RIDI_URL = "https://ridicorp.com/wp-content/themes/ridicorp/css/font/RIDIBatang.otf"
RIDI_SHA256 = "f13a49c0815d254ac15e392953a0b056613dec08ceb378e54eeed14c4fda9a54"
OUTPUT = Path("comparisons/hangul")
CENTERED_SCALES = (1.10, 1.15)
# Raising Hangul by N units equals lowering Latin by N relative to it.
HANGUL_Y_SHIFTS = (10, 20, 30, 40, 50)


def quadratic_hangul(font):
    """Convert only selected CFF outlines, at 1/1000 em error, for the existing merger."""
    cmap = {cp: name for cp, name in font.getBestCmap().items() if is_hangul(cp)}
    order = [".notdef", *sorted(set(cmap.values()) - {".notdef"})]
    glyphs = {}
    glyph_set = font.getGlyphSet()
    for name in order:
        pen = TTGlyphPen(None)
        glyph_set[name].draw(Cu2QuPen(pen, font["head"].unitsPerEm / 1000, reverse_direction=True))
        glyphs[name] = pen.glyph()
    builder = FontBuilder(font["head"].unitsPerEm, isTTF=True)
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics({name: font["hmtx"][name] for name in order})
    return builder.font


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-ridi", action="store_true", help="also add RIDIBatang at 1.00")
    args = parser.parse_args()
    ridi_path = Path("upstream/ridi-batang/RIDIBatang.otf")
    if args.fetch_ridi and not ridi_path.exists():
        ridi_path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(RIDI_URL, timeout=60) as response:
            data = response.read()
        import hashlib

        if hashlib.sha256(data).hexdigest() != RIDI_SHA256:
            raise ValueError("RIDI download checksum mismatch")
        ridi_path.write_bytes(data)
    if ridi_path.exists() and sha256(ridi_path) != RIDI_SHA256:
        raise ValueError("RIDI checksum mismatch")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    layout = SourceLayout(load_manifest(Path("sources.toml")), Path("upstream"))
    latin_path = layout.font("ibm-plex-mono", "IBMPlexMono-Regular.ttf")
    jp_path = layout.font("ibm-plex-sans-jp", "IBMPlexSansJP-Regular.ttf")
    maru_path = layout.font("maru-buri", "MaruBuri-Regular.ttf")
    target = BuildTarget(JapaneseSource.IBM_PLEX_SANS_JP, FACES[0], False, True)
    summary = {
        "conditions": {
            "style": "Regular",
            "hangul_scales": {},
            "hangul_y_anchors": {},
            "hangul_y_shifts": {},
            "upm": 1000,
            "ascii_advance": 600,
            "hangul_advance": 1200,
            "hangul_guard": CJK_GUARD,
            "latin": "IBM Plex Mono 2.5.0",
            "japanese": "IBM Plex Sans JP 3.0.0",
            "cubic_conversion_max_error_em": 0.001,
        },
        "fonts": {},
    }
    variants = [
        (f"Maru{round(scale * 100)}", "마루 부리", maru_path, scale, 0, 0)
        for scale in CJK_SCALE_CANDIDATES
    ]
    variants += [
        (
            f"Maru{round(scale * 100)}C",
            "마루 부리 · 중심 고정",
            maru_path,
            scale,
            HANGUL_Y_ANCHOR,
            0,
        )
        for scale in CENTERED_SCALES
    ]
    variants += [
        (f"Maru110CU{shift}", "마루 부리 · 한글 올림", maru_path, 1.10, HANGUL_Y_ANCHOR, shift)
        for shift in HANGUL_Y_SHIFTS
    ]
    if ridi_path.exists():
        variants.append(("Ridi100", "리디바탕", ridi_path, 1.0, 0, 0))
    sample_texts = json.loads((OUTPUT / "samples.json").read_text(encoding="utf-8"))
    rows = []
    for label, title, path, scale, y_anchor, y_shift in variants:
        summary["conditions"]["hangul_scales"][label] = scale
        summary["conditions"]["hangul_y_anchors"][label] = y_anchor
        summary["conditions"]["hangul_y_shifts"][label] = y_shift
        with TTFont(path) as original, TTFont(latin_path) as font, TTFont(jp_path) as jp:
            source = quadratic_hangul(original) if "CFF " in original else original
            _merge_codepoints(
                font,
                source,
                predicate=is_hangul,
                glyph_prefix="ko",
                scale=scale,
                y_anchor=y_anchor,
                y_shift=y_shift,
            )
            _merge_codepoints(font, jp, predicate=is_japanese, glyph_prefix="ja", scale=1.0)
            _normalize_metadata(font, target)
            out = OUTPUT / f"GyeolCompare{label}-Regular.ttf"
            font.save(out)
            # Cell overflow is a comparison result here, counted below instead of failing.
            validate_built_font(out, target, check_hangul_cell=False)
            family = f"Gyeol Compare {label}"
            names = {
                1: family,
                2: "Regular",
                3: f"{family};0.1",
                4: f"{family} Regular",
                6: f"GyeolCompare{label}-Regular",
                16: family,
                17: "Regular",
            }
            for name_id, value in names.items():
                font["name"].removeNames(nameID=name_id)
                font["name"].setName(value, name_id, 3, 1, 0x409)
            font.save(out)
            _save_woff2(out, out.with_suffix(".woff2"))
            c = font.getBestCmap()
            source_cmap = original.getBestCmap()
            clipped = 0
            guarded = 0
            ink_widths = []
            for cp in sorted(cp for cp in c if is_hangul(cp)):
                g = font["glyf"][c[cp]]
                bounds = [getattr(g, k, 0) for k in ("xMin", "yMin", "xMax", "yMax")]
                overflow = bounds[0] < 0 or bounds[2] > 1200 or bounds[1] < -275 or bounds[3] > 1025
                clipped += overflow
                guarded += bounds[0] < CJK_GUARD or bounds[2] > CJK_ADVANCE - CJK_GUARD
                if 0xAC00 <= cp <= 0xD7A3:
                    ink_widths.append(bounds[2] - bounds[0])
                assert font["hmtx"][c[cp]][0] == 1200
                rows.append(
                    [
                        label,
                        f"U+{cp:04X}",
                        chr(cp),
                        original["hmtx"][source_cmap[cp]][0],
                        1200,
                        *bounds,
                        overflow,
                    ]
                )
            ink_widths.sort()
            summary["fonts"][label] = {
                "title": title,
                "scale": scale,
                "y_anchor": y_anchor,
                "y_shift": y_shift,
                "source": path.as_posix(),
                "sha256": sha256(path),
                "version": original["name"].getDebugName(5),
                "source_upm": original["head"].unitsPerEm,
                "hangul_syllables": sum(cp in source_cmap for cp in range(0xAC00, 0xD7A4)),
                "conjoining_jamo": sum(cp in source_cmap for cp in range(0x1100, 0x1200)),
                "hangul_codepoints": sum(is_hangul(cp) for cp in source_cmap),
                "cell_overflow_count": clipped,
                "guard_violation_count": guarded,
                "syllable_ink_width_median": round(ink_widths[len(ink_widths) // 2]),
                "syllable_ink_width_max": round(ink_widths[-1]),
                "missing_sample_codepoints": [
                    f"U+{cp:04X}"
                    for cp in sorted(
                        {ord(ch) for s in sample_texts for ch in s["text"] if not ch.isspace()}
                    )
                    if cp not in c
                ],
            }
            if source is not original:
                source.close()
    (OUTPUT / "metrics.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (OUTPUT / "glyph-metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "font",
                "codepoint",
                "character",
                "source_advance",
                "output_advance",
                "xMin",
                "yMin",
                "xMax",
                "yMax",
                "cell_overflow",
            ]
        )
        writer.writerows(rows)
    template = (OUTPUT / "template.html").read_text(encoding="utf-8")
    samples = (OUTPUT / "samples.json").read_text(encoding="utf-8")
    fonts = json.dumps(
        [
            {
                "id": label,
                "title": title,
                "scale": f"{scale:.2f}"
                + (f" / y{y_anchor}" if y_anchor else "")
                + (f" / +{y_shift}" if y_shift else ""),
                "shown": label in {"Maru110C", "Maru110CU30", "Maru110CU40", "Maru110CU50"},
            }
            for label, title, _, scale, y_anchor, y_shift in variants
        ],
        ensure_ascii=False,
    )
    (OUTPUT / "index.html").write_text(
        template.replace("__SAMPLES__", samples).replace("__FONTS__", fonts), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
