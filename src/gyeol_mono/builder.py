"""Declarative build plan; font mutation is added after upstream pins are fixed."""

from dataclasses import dataclass
from enum import StrEnum

from gyeol_mono.japanese import CANDIDATES, JapaneseSource
from gyeol_mono.models import FACES, FaceSpec
from gyeol_mono.naming import FontNames, names_for


class BuildStage(StrEnum):
    FETCH_AND_VERIFY = "fetch-and-verify"
    PREPARE_LATIN = "prepare-latin"
    PATCH_POWERLINE = "patch-powerline"
    VERIFY_LATIN_METRICS = "verify-latin-metrics"
    MERGE_CJK = "merge-cjk"
    ADD_HANGUL_CCMP = "add-hangul-ccmp"
    REMOVE_EMOJI_PRESENTATION = "remove-emoji-presentation"
    NORMALIZE_METADATA = "normalize-metadata"
    VALIDATE_TTF = "validate-ttf"
    EXPORT_WOFF2 = "export-woff2"


@dataclass(frozen=True, slots=True)
class BuildTarget:
    japanese_source: JapaneseSource
    face: FaceSpec
    preview: bool

    @property
    def names(self) -> FontNames:
        preview_source = self.japanese_source if self.preview else None
        return names_for(self.face.style, preview_source=preview_source)

    @property
    def stages(self) -> tuple[BuildStage, ...]:
        return tuple(BuildStage)

    def as_dict(self) -> dict[str, object]:
        return {
            "japanese_source": self.japanese_source.value,
            "style": self.face.style.value,
            "output_weight": self.face.output_weight,
            "source_weight": self.face.source_weight,
            "latin_source_style": self.face.latin_source_style,
            "cjk_source_style": self.face.cjk_source_style,
            "hangul_source": "maru-buri",
            "hangul_source_weight": self.face.source_weight,
            "hangul_source_style": self.face.hangul_source_style,
            "japanese_source_style": self.face.cjk_source_style,
            "family": self.names.family,
            "file_name": self.names.file_name,
            "stages": [stage.value for stage in self.stages],
        }


@dataclass(frozen=True, slots=True)
class BuildPlan:
    targets: tuple[BuildTarget, ...]

    @classmethod
    def preview(cls) -> "BuildPlan":
        return cls.from_sources(tuple(CANDIDATES), preview=True)

    @classmethod
    def release(cls, source: JapaneseSource) -> "BuildPlan":
        return cls.from_sources((source,), preview=False)

    @classmethod
    def from_sources(
        cls,
        sources: tuple[JapaneseSource, ...],
        *,
        preview: bool,
    ) -> "BuildPlan":
        targets = tuple(BuildTarget(source, face, preview) for source in sources for face in FACES)
        return cls(targets)

    def as_dict(self) -> dict[str, object]:
        return {
            "target_count": len(self.targets),
            "targets": [target.as_dict() for target in self.targets],
        }
