from gyeol_mono.japanese import FINAL_JAPANESE_SOURCE, JapaneseSource, candidate


def test_only_ibm_plex_sans_jp_remains() -> None:
    assert list(JapaneseSource) == [JapaneseSource.IBM_PLEX_SANS_JP]
    assert candidate(JapaneseSource.IBM_PLEX_SANS_JP).preview_label == "B"


def test_final_source_is_preview_b() -> None:
    assert FINAL_JAPANESE_SOURCE is JapaneseSource.IBM_PLEX_SANS_JP
