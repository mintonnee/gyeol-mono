"""OpenType and artifact naming rules for release and preview families."""

from dataclasses import dataclass

from gyeol_mono.japanese import JapaneseSource, candidate
from gyeol_mono.models import Style

BASE_FAMILY = "Gyeol Mono"


@dataclass(frozen=True, slots=True)
class FontNames:
    family: str
    subfamily: str
    full_name: str
    postscript_name: str
    file_name: str


def family_name(*, powerline: bool, preview_source: JapaneseSource | None = None) -> str:
    if preview_source is None:
        family = BASE_FAMILY
    else:
        family = f"{BASE_FAMILY} Preview {candidate(preview_source).preview_label}"
    return f"{family} PL" if powerline else family


def names_for(
    style: Style,
    *,
    powerline: bool,
    preview_source: JapaneseSource | None = None,
) -> FontNames:
    family = family_name(powerline=powerline, preview_source=preview_source)
    compact_family = family.replace(" ", "")
    compact_style = style.compact_name
    return FontNames(
        family=family,
        subfamily=style.value,
        full_name=f"{family} {style.value}",
        postscript_name=f"{compact_family}-{compact_style}",
        file_name=f"{compact_family}-{compact_style}.ttf",
    )
