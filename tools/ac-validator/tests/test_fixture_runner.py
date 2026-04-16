"""fixture_runner 통합 테스트."""

from pathlib import Path

import pytest

from papillon_ac.ac_parser import parse_common_ac, parse_persona_ac
from papillon_ac.fixture_runner import run_all


AC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "01-Planning" / "04-wtth" / "ac"
FIXTURES_DIR = Path(__file__).parent / "fixtures"
OUTPUT_FILE = FIXTURES_DIR / "dry_run_output_code_01.txt"


@pytest.fixture
def output_text():
    return OUTPUT_FILE.read_text(encoding="utf-8")


@pytest.fixture
def ac_v011():
    common = parse_common_ac(
        (AC_DIR / "common-v0.1.1.md").read_text(encoding="utf-8")
    )
    return parse_persona_ac(
        (AC_DIR / "code-v0.1.1.md").read_text(encoding="utf-8"),
        common,
    )


@pytest.fixture
def ac_v010():
    common = parse_common_ac(
        (AC_DIR / "common-v0.1.0.md").read_text(encoding="utf-8")
    )
    return parse_persona_ac(
        (AC_DIR / "code-v0.1.0.md").read_text(encoding="utf-8"),
        common,
    )


class TestV011AllPass:
    def test_all_pass(self, ac_v011, output_text):
        result = run_all(ac_v011, output_text, fixture_id="FIX-CODE-01")
        assert result.all_passed

    def test_invariant_count(self, ac_v011, output_text):
        result = run_all(ac_v011, output_text)
        failed = [c for c in result.invariant_checks if not c.passed]
        assert len(failed) == 0

    def test_heading_fallback(self, ac_v011, output_text):
        result = run_all(ac_v011, output_text)
        wrev01 = [c for c in result.invariant_checks if c.id == "INV-WREV-01"][0]
        assert wrev01.passed
        assert "fallback" in wrev01.detail


class TestV010DetectsFailures:
    def test_two_failures(self, ac_v010, output_text):
        result = run_all(ac_v010, output_text, fixture_id="FIX-CODE-01")
        assert not result.all_passed

    def test_heading_fails(self, ac_v010, output_text):
        result = run_all(ac_v010, output_text)
        wrev01 = [c for c in result.invariant_checks if c.id == "INV-WREV-01"][0]
        assert not wrev01.passed

    def test_fixture_regex_fails(self, ac_v010, output_text):
        result = run_all(ac_v010, output_text, fixture_id="FIX-CODE-01")
        failed_fixtures = [
            c for fr in result.fixture_results
            for c in fr.checks if not c.passed
        ]
        assert len(failed_fixtures) == 1
        assert "체크리스트" in failed_fixtures[0].rule


class TestExitCodeBehavior:
    def test_pass_count(self, ac_v011, output_text):
        result = run_all(ac_v011, output_text, fixture_id="FIX-CODE-01")
        all_checks = result.invariant_checks + [
            c for fr in result.fixture_results for c in fr.checks
        ]
        passed = [c for c in all_checks if c.passed]
        assert len(passed) == 18

    def test_fail_count_v010(self, ac_v010, output_text):
        result = run_all(ac_v010, output_text, fixture_id="FIX-CODE-01")
        all_checks = result.invariant_checks + [
            c for fr in result.fixture_results for c in fr.checks
        ]
        failed = [c for c in all_checks if not c.passed]
        assert len(failed) == 2
