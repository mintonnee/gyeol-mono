from gyeol_mono.builder import BuildPlan, BuildStage
from gyeol_mono.japanese import JapaneseSource


def test_preview_plan_contains_sixteen_unique_targets() -> None:
    plan = BuildPlan.preview()

    assert len(plan.targets) == 16
    assert len({target.names.file_name for target in plan.targets}) == 16


def test_release_plan_contains_eight_targets_without_preview_names() -> None:
    plan = BuildPlan.release(JapaneseSource.KLEE_ONE)

    assert len(plan.targets) == 8
    assert all("Preview" not in target.names.family for target in plan.targets)


def test_powerline_is_patched_before_cjk_merge() -> None:
    target = next(target for target in BuildPlan.preview().targets if target.powerline)

    assert target.stages.index(BuildStage.PATCH_POWERLINE) < target.stages.index(
        BuildStage.MERGE_CJK
    )
