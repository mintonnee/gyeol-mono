from gyeol_mono.japanese import JapaneseSource, candidate


def test_preview_labels_are_stable() -> None:
    assert candidate(JapaneseSource.KLEE_ONE).preview_label == "A"
    assert candidate(JapaneseSource.IBM_PLEX_SANS_JP).preview_label == "B"
