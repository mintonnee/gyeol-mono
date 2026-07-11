"""Japanese source candidates retained by specification 001."""

from dataclasses import dataclass
from enum import StrEnum


class JapaneseSource(StrEnum):
    KLEE_ONE = "klee-one"
    IBM_PLEX_SANS_JP = "ibm-plex-sans-jp"


FINAL_JAPANESE_SOURCE = JapaneseSource.IBM_PLEX_SANS_JP


@dataclass(frozen=True, slots=True)
class JapaneseCandidate:
    source: JapaneseSource
    display_name: str
    preview_label: str


CANDIDATES = {
    JapaneseSource.KLEE_ONE: JapaneseCandidate(
        JapaneseSource.KLEE_ONE,
        display_name="Klee One",
        preview_label="A",
    ),
    JapaneseSource.IBM_PLEX_SANS_JP: JapaneseCandidate(
        JapaneseSource.IBM_PLEX_SANS_JP,
        display_name="IBM Plex Sans JP",
        preview_label="B",
    ),
}


def candidate(source: JapaneseSource) -> JapaneseCandidate:
    return CANDIDATES[source]
