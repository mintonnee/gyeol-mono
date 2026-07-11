from gyeol_mono.japanese import FINAL_JAPANESE_SOURCE, JapaneseSource, candidate


def test_preview_labels_are_stable() -> None:
    assert candidate(JapaneseSource.KLEE_ONE).preview_label == "A"
    assert candidate(JapaneseSource.IBM_PLEX_SANS_JP).preview_label == "B"


def test_final_source_is_preview_b() -> None:
    assert FINAL_JAPANESE_SOURCE is JapaneseSource.IBM_PLEX_SANS_JP
