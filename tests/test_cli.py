import json

from gyeol_mono.cli import main


def test_cli_prints_preview_plan_as_json(capsys) -> None:
    assert main(["plan", "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["target_count"] == 16
