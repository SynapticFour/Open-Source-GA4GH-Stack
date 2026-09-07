from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
from click.testing import CliRunner

from community_stack.helixtest_report import (
    EXIT_FAILED,
    EXIT_INVALID,
    EXIT_OK,
    classify_test,
    grade_overall_report,
    run_grade,
)
from community_stack.main import cli


def _case(
    status: str, *, passed: bool | None = None, error: str | None = None
) -> dict[str, object]:
    row: dict[str, object] = {"name": "t", "status": status}
    if passed is not None:
        row["passed"] = passed
    if error is not None:
        row["error"] = error
    return row


def test_classify_status_is_authoritative_over_passed_boolean() -> None:
    assert classify_test(_case("skip", passed=True)) == "skip"
    assert classify_test(_case("fail", passed=True)) == "fail"
    assert classify_test(_case("pass", passed=False)) == "pass"


def test_skip_only_is_not_evaluated_and_not_all_passed() -> None:
    grade = grade_overall_report(
        {
            "services": [
                {
                    "service": "Beacon",
                    "tests": [
                        _case("skip", passed=False, error="skipped: no URL"),
                        _case("skip", passed=False, error="skipped: feature off"),
                    ],
                }
            ]
        }
    )
    assert grade.verdict == "not_evaluated"
    assert grade.all_passed is False
    assert grade.ran == 0
    assert grade.passed == 0
    assert grade.failed == 0
    assert grade.skipped == 2
    assert grade.exit_code() == EXIT_OK


def test_skipped_services_are_not_passed() -> None:
    grade = grade_overall_report(
        {
            "services": [],
            "skipped_services": [{"service": "Wes", "reason": "not in --only"}],
        }
    )
    assert grade.verdict == "not_evaluated"
    assert grade.all_passed is False
    assert grade.skipped == 1
    assert grade.ran == 0


def test_all_executed_passed_sets_all_passed() -> None:
    grade = grade_overall_report(
        {
            "services": [
                {
                    "service": "Beacon",
                    "tests": [
                        _case("pass", passed=True),
                        _case("skip", passed=False, error="skipped: optional"),
                    ],
                }
            ]
        }
    )
    assert grade.verdict == "passed"
    assert grade.all_passed is True
    assert grade.ran == 1
    assert grade.passed == 1
    assert grade.skipped == 1
    assert grade.exit_code() == EXIT_OK


def test_any_fail_clears_all_passed_and_fails_exit() -> None:
    grade = grade_overall_report(
        {
            "services": [
                {
                    "service": "Wes",
                    "tests": [
                        _case("pass", passed=True),
                        _case("fail", passed=False, error="lifecycle"),
                        _case("skip", passed=False, error="skipped: trs"),
                    ],
                }
            ]
        }
    )
    assert grade.verdict == "failed"
    assert grade.all_passed is False
    assert grade.failed == 1
    assert grade.ran == 2
    assert grade.exit_code() == EXIT_FAILED


def test_counting_status_not_fail_would_wrongly_treat_skip_as_pass() -> None:
    """Guard: skip must not be lumped with pass via `status != fail`."""
    grade = grade_overall_report(
        {"services": [{"service": "Beacon", "tests": [_case("skip", passed=False)]}]}
    )
    assert grade.passed == 0
    assert grade.all_passed is False


def test_missing_services_is_invalid() -> None:
    with pytest.raises(ValueError, match="missing services"):
        grade_overall_report({})


def test_run_grade_missing_file(tmp_path: Path) -> None:
    buf = StringIO()
    code = run_grade(tmp_path / "missing.json", stdout=buf)
    assert code == EXIT_INVALID
    assert "invalid report" in buf.getvalue()


def test_run_grade_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.json"
    path.write_text("", encoding="utf-8")
    assert run_grade(path, stdout=StringIO()) == EXIT_INVALID


def test_run_grade_writes_json_and_exit(tmp_path: Path) -> None:
    path = tmp_path / "report.json"
    path.write_text(
        json.dumps({"services": [{"service": "Beacon", "tests": [_case("pass", passed=True)]}]}),
        encoding="utf-8",
    )
    buf = StringIO()
    assert run_grade(path, stdout=buf) == EXIT_OK
    first = buf.getvalue().splitlines()[0]
    payload = json.loads(first)
    assert payload["all_passed"] is True
    assert payload["verdict"] == "passed"


def test_cli_grade_helixtest_fail_exit(tmp_path: Path) -> None:
    path = tmp_path / "report.json"
    path.write_text(
        json.dumps(
            {"services": [{"service": "Wes", "tests": [_case("fail", passed=False)]}]}
        ),
        encoding="utf-8",
    )
    result = CliRunner().invoke(cli, ["grade-helixtest", str(path)])
    assert result.exit_code == EXIT_FAILED
    assert '"all_passed": false' in result.output
    assert '"verdict": "failed"' in result.output
