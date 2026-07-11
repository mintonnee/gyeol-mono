from gyeol_mono.japanese import JapaneseSource
from gyeol_mono.models import Style
from gyeol_mono.naming import names_for


def test_release_powerline_bold_italic_names() -> None:
    names = names_for(Style.BOLD_ITALIC, powerline=True)

    assert names.family == "Gyeol Mono PL"
    assert names.full_name == "Gyeol Mono PL Bold Italic"
    assert names.postscript_name == "GyeolMonoPL-BoldItalic"
    assert names.file_name == "GyeolMonoPL-BoldItalic.ttf"


def test_preview_names_can_be_installed_side_by_side() -> None:
    klee = names_for(
        Style.REGULAR,
        powerline=False,
        preview_source=JapaneseSource.KLEE_ONE,
    )
    plex = names_for(
        Style.REGULAR,
        powerline=False,
        preview_source=JapaneseSource.IBM_PLEX_SANS_JP,
    )

    assert klee.family == "Gyeol Mono Preview A"
    assert plex.family == "Gyeol Mono Preview B"
    assert klee.postscript_name != plex.postscript_name
