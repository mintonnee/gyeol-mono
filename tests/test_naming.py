from gyeol_mono.japanese import JapaneseSource
from gyeol_mono.models import Style
from gyeol_mono.naming import names_for


def test_release_bold_italic_names() -> None:
    names = names_for(Style.BOLD_ITALIC)

    assert names.family == "Gyeol Mono"
    assert names.full_name == "Gyeol Mono Bold Italic"
    assert names.postscript_name == "GyeolMono-BoldItalic"
    assert names.file_name == "GyeolMono-BoldItalic.ttf"


def test_preview_names_can_be_installed_beside_release() -> None:
    preview = names_for(Style.REGULAR, preview_source=JapaneseSource.IBM_PLEX_SANS_JP)
    release = names_for(Style.REGULAR)

    assert preview.family == "Gyeol Mono Preview B"
    assert preview.postscript_name != release.postscript_name
