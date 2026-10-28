from gyeol_mono.builder import BuildPlan, BuildStage
from gyeol_mono.japanese import JapaneseSource


def test_preview_plan_contains_four_unique_targets() -> None:
    plan = BuildPlan.preview()

    assert len(plan.targets) == 4
    assert len({target.names.file_name for target in plan.targets}) == 4


def test_release_plan_contains_four_targets_without_preview_or_pl_names() -> None:
    plan = BuildPlan.release(JapaneseSource.IBM_PLEX_SANS_JP)

    assert len(plan.targets) == 4
    assert {target.names.family for target in plan.targets} == {"Gyeol Mono"}


def test_every_target_patches_powerline_before_cjk_merge() -> None:
    for target in BuildPlan.preview().targets:
        assert target.stages.index(BuildStage.PATCH_POWERLINE) < target.stages.index(
            BuildStage.MERGE_CJK
        )


def test_emoji_presentation_is_removed_after_merges_before_metadata() -> None:
    stages = BuildPlan.release(JapaneseSource.IBM_PLEX_SANS_JP).targets[0].stages

    removal = stages.index(BuildStage.REMOVE_EMOJI_PRESENTATION)
    assert stages.index(BuildStage.MERGE_CJK) < removal
    assert removal < stages.index(BuildStage.NORMALIZE_METADATA)


def test_hangul_uses_maru_buri_at_the_same_weight_as_japanese() -> None:
    targets = BuildPlan.release(JapaneseSource.IBM_PLEX_SANS_JP).targets
    for target in targets:
        plan = target.as_dict()
        is_bold = target.face.output_weight == 700
        expected = "SemiBold upright" if is_bold else "Regular upright"
        assert plan["hangul_source"] == "maru-buri"
        assert plan["hangul_source_weight"] == (600 if is_bold else 400)
        assert plan["hangul_source_style"] == expected
        assert plan["japanese_source_style"] == expected
