from gyeol_mono.models import FACES, Style


def test_ribbi_matrix_uses_semibold_sources_for_bold_outputs() -> None:
    assert [face.style for face in FACES] == list(Style)
    assert [face.output_weight for face in FACES] == [400, 400, 700, 700]
    assert [face.source_weight for face in FACES] == [400, 400, 600, 600]
    assert FACES[1].latin_source_style == "Italic"
    assert FACES[3].latin_source_style == "SemiBold Italic"
    assert all(face.cjk_source_style.endswith("upright") for face in FACES)
