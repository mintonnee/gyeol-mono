"""Japanese source retained by specification 001."""

from dataclasses import dataclass
from enum import StrEnum


class JapaneseSource(StrEnum):
    IBM_PLEX_SANS_JP = "ibm-plex-sans-jp"


FINAL_JAPANESE_SOURCE = JapaneseSource.IBM_PLEX_SANS_JP


@dataclass(frozen=True, slots=True)
class JapaneseCandidate:
    source: JapaneseSource
    display_name: str
    preview_label: str


CANDIDATES = {
    JapaneseSource.IBM_PLEX_SANS_JP: JapaneseCandidate(
        JapaneseSource.IBM_PLEX_SANS_JP,
        display_name="IBM Plex Sans JP",
        preview_label="B",
    ),
}


def candidate(source: JapaneseSource) -> JapaneseCandidate:
    return CANDIDATES[source]
