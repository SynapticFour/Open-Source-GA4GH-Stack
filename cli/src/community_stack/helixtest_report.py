"""Grade a HelixTest OverallReport JSON for CI.

Skip is not a pass. ``all_passed`` is true only when at least one test was
executed (status pass or fail) and none failed. A skip-only or empty report is
``verdict=not_evaluated`` with ``all_passed=false``. That distinction exists
because a green GitHub job plus skip-only JSON used to read as a full pass;
HelixTest itself documents that skip is excluded from levels and scores, and
green CI is a technical signal, not GA4GH certification.

HelixTest ``TestCaseResult.status`` is lowercase ``pass`` / ``fail`` / ``skip``.
The boolean ``passed`` is true iff status is pass; do not infer pass from
``status != fail``.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

Verdict = Literal["passed", "failed", "not_evaluated"]
TestOutcome = Literal["pass", "fail", "skip"]

# 0: passed or skip-only (not a job failure). 1: at least one real Fail.
# 2: missing or unreadable report (infrastructure; fail closed).
EXIT_OK = 0
EXIT_FAILED = 1
EXIT_INVALID = 2


@dataclass(frozen=True)
class HelixTestGrade:
    passed: int
    failed: int
    skipped: int
    ran: int
    all_passed: bool
    verdict: Verdict

    def exit_code(self) -> int:
        if self.verdict == "failed":
            return EXIT_FAILED
        return EXIT_OK


def classify_test(test: object) -> TestOutcome:
    """Map one HelixTest test object to pass, fail, or skip.

    ``status`` is authoritative. Unknown or missing status fails closed (fail),
    except a missing status with ``error`` prefixed ``skipped:`` which is skip.
    """
    if not isinstance(test, Mapping):
        return "fail"
    status = test.get("status")
    if isinstance(status, str):
        normalized = status.strip().lower()
        if normalized == "skip":
            return "skip"
        if normalized == "fail":
            return "fail"
        if normalized == "pass":
            return "pass"
        return "fail"
    error = test.get("error")
    if isinstance(error, str) and error.lower().startswith("skipped:"):
        return "skip"
    if test.get("passed") is True:
        return "pass"
    return "fail"


def grade_overall_report(data: object) -> HelixTestGrade:
    """Grade a parsed HelixTest OverallReport.

    ``skipped_services`` are skipped, not executed. They must not count as
    passed and must not set ``all_passed``.
    """
    if not isinstance(data, Mapping):
        raise ValueError("HelixTest report root must be a JSON object")
    services = data.get("services")
    if services is None:
        raise ValueError("HelixTest report missing services")
    if not isinstance(services, list):
        raise ValueError("HelixTest report services must be a list")

    passed = 0
    failed = 0
    skipped = 0
    for service in services:
        if not isinstance(service, Mapping):
            raise ValueError("HelixTest service entry must be an object")
        tests = service.get("tests", [])
        if not isinstance(tests, list):
            raise ValueError("HelixTest service tests must be a list")
        for test in tests:
            outcome = classify_test(test)
            if outcome == "pass":
                passed += 1
            elif outcome == "fail":
                failed += 1
            else:
                skipped += 1

    skipped_services = data.get("skipped_services") or []
    if not isinstance(skipped_services, list):
        raise ValueError("HelixTest skipped_services must be a list")
    skipped += len(skipped_services)

    ran = passed + failed
    if failed > 0:
        verdict: Verdict = "failed"
        all_passed = False
    elif ran == 0:
        # Skip-only / empty: not a pass. Job may stay green; all_passed must not.
        verdict = "not_evaluated"
        all_passed = False
    else:
        verdict = "passed"
        all_passed = True
    return HelixTestGrade(
        passed=passed,
        failed=failed,
        skipped=skipped,
        ran=ran,
        all_passed=all_passed,
        verdict=verdict,
    )


def grade_report_bytes(raw: bytes) -> HelixTestGrade:
    try:
        data: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"HelixTest report is not valid JSON: {exc}") from exc
    return grade_overall_report(data)


def grade_report_path(path: Path) -> HelixTestGrade:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"HelixTest report missing or empty: {path}")
    return grade_report_bytes(path.read_bytes())


def run_grade(path: Path, *, stdout: Any = None) -> int:
    """Print a grade summary and return the CI exit code."""
    out = stdout if stdout is not None else sys.stdout
    try:
        grade = grade_report_path(path)
    except ValueError as exc:
        out.write(f"HelixTest grade: invalid report ({exc})\n")
        return EXIT_INVALID
    payload = asdict(grade)
    out.write(json.dumps(payload, sort_keys=True) + "\n")
    out.write(
        "HelixTest grade: "
        f"verdict={grade.verdict} all_passed={str(grade.all_passed).lower()} "
        f"passed={grade.passed} failed={grade.failed} skipped={grade.skipped} "
        f"ran={grade.ran}\n"
    )
    return grade.exit_code()
