"""Emoji presentation codepoints that must fall back to the OS emoji font."""

from pathlib import Path

EMOJI_DATA_SOURCE = "unicode-emoji-data"
EMOJI_DATA_FILE = "emoji-data.txt"
EMOJI_PRESENTATION = "Emoji_Presentation"
# IBM Plex Mono draws U+274C as a thin 1-cell cross paired with U+2713. Keep that outline at
# the text-presentation BALLOT X before U+274C is unmapped for OS emoji fallback.
TEXT_PRESENTATION_ALIASES = {0x274C: 0x2717}


class EmojiDataError(ValueError):
    """Raised when emoji-data.txt cannot be parsed."""


def parse_emoji_presentation(text: str) -> frozenset[int]:
    """Return codepoints whose ``Emoji_Presentation`` property is Yes."""
    codepoints: set[int] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        data = line.split("#", 1)[0].strip()
        if not data:
            continue
        fields = [field.strip() for field in data.split(";")]
        if len(fields) != 2:
            raise EmojiDataError(f"line {line_number}: expected 2 fields: {line!r}")
        if fields[1] != EMOJI_PRESENTATION:
            continue
        start, _, end = fields[0].partition("..")
        try:
            first = int(start, 16)
            last = int(end, 16) if end else first
        except ValueError as error:
            raise EmojiDataError(f"line {line_number}: invalid range {fields[0]!r}") from error
        if last < first:
            raise EmojiDataError(f"line {line_number}: reversed range {fields[0]!r}")
        codepoints.update(range(first, last + 1))
    if not codepoints:
        raise EmojiDataError(f"no {EMOJI_PRESENTATION} entries found")
    return frozenset(codepoints)


def load_emoji_presentation(path: Path) -> frozenset[int]:
    return parse_emoji_presentation(path.read_text(encoding="utf-8"))
