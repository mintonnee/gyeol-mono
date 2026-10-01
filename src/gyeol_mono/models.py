"""Shared domain models derived from specification 001."""

from dataclasses import dataclass
from enum import StrEnum


class Style(StrEnum):
    REGULAR = "Regular"
    ITALIC = "Italic"
    BOLD = "Bold"
    BOLD_ITALIC = "Bold Italic"

    @property
    def compact_name(self) -> str:
        return self.value.replace(" ", "")


@dataclass(frozen=True, slots=True)
class FaceSpec:
    style: Style
    output_weight: int
    source_weight: int
    latin_source_style: str
    italic: bool

    @property
    def cjk_source_style(self) -> str:
        weight = "Regular" if self.source_weight == 400 else "SemiBold"
        return f"{weight} upright"

    @property
    def hangul_source_style(self) -> str:
        return self.cjk_source_style


FACES = (
    FaceSpec(Style.REGULAR, 400, 400, "Regular", italic=False),
    FaceSpec(Style.ITALIC, 400, 400, "Italic", italic=True),
    FaceSpec(Style.BOLD, 700, 600, "SemiBold", italic=False),
    FaceSpec(Style.BOLD_ITALIC, 700, 600, "SemiBold Italic", italic=True),
)
