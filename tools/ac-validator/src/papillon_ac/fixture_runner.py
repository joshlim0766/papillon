"""Fixture Runner — AC invariants + fixture expected 자동 대조 엔진."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from papillon_ac.ac_parser import ParsedAC, PatternRule, Fixture
from papillon_ac.markdown_utils import extract_headings, normalize_heading
from papillon_ac.scope import resolve_scoped_text


@dataclass
class CheckResult:
    id: str
    rule: str
    passed: bool
    detail: str = ""


@dataclass
class FixtureResult:
    fixture_id: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


@dataclass
class RunResult:
    invariant_checks: list[CheckResult] = field(default_factory=list)
    fixture_results: list[FixtureResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        inv_ok = all(c.passed for c in self.invariant_checks)
        fix_ok = all(f.passed for f in self.fixture_results)
        return inv_ok and fix_ok

    def summary(self) -> str:
        lines = []
        total_pass = 0
        total_fail = 0

        lines.append("## Invariant Checks")
        lines.append("")
        lines.append("| ID | Rule | Result | Detail |")
        lines.append("|---|---|---|---|")
        for c in self.invariant_checks:
            mark = "PASS" if c.passed else "**FAIL**"
            if c.passed:
                total_pass += 1
            else:
                total_fail += 1
            lines.append(f"| {c.id} | {c.rule} | {mark} | {c.detail} |")

        lines.append("")
        lines.append("## Fixture Checks")
        for fr in self.fixture_results:
            lines.append("")
            lines.append(f"### {fr.fixture_id}")
            lines.append("")
            lines.append("| Check | Result | Detail |")
            lines.append("|---|---|---|")
            for c in fr.checks:
                mark = "PASS" if c.passed else "**FAIL**"
                if c.passed:
                    total_pass += 1
                else:
                    total_fail += 1
                lines.append(f"| {c.rule} | {mark} | {c.detail} |")

        lines.append("")
        verdict = "PASS" if self.all_passed else "FAIL"
        lines.append(f"**Verdict: {verdict}** ({total_pass} passed, {total_fail} failed)")
        return "\n".join(lines)


def _check_heading_or_fallback(ac: ParsedAC, output: str) -> CheckResult:
    """INV-WREV-01: heading 존재 또는 finding-per-block fallback."""
    headings = extract_headings(output)
    all_alts = [ac.required_sections_heading] + ac.required_sections_alternatives
    normalized_alts = [normalize_heading(a).lower() for a in all_alts]

    has_heading = any(
        h.normalized.lower() in normalized_alts for h in headings
    )

    if has_heading:
        return CheckResult(
            id="INV-WREV-01",
            rule="Findings heading 존재",
            passed=True,
            detail="heading 매치 발견",
        )

    finding_blocks = re.findall(r"P[0-3]", output)
    has_fallback = len(finding_blocks) >= 1

    if not ac.heading_required and has_fallback:
        return CheckResult(
            id="INV-WREV-01",
            rule="Findings heading 또는 finding-per-block",
            passed=True,
            detail=f"fallback: P[0-3] 태그 {len(finding_blocks)}개 발견",
        )

    return CheckResult(
        id="INV-WREV-01",
        rule="Findings heading 또는 finding-per-block",
        passed=False,
        detail="heading 없음" + (", fallback도 미충족" if not has_fallback else ", heading_required=true"),
    )


def _check_severity_tags(output: str) -> CheckResult:
    """INV-WREV-02: P0~P3 최소 1회."""
    found = bool(re.search(r"P[0-3]", output))
    return CheckResult(
        id="INV-WREV-02",
        rule="P0~P3 태그 ≥1",
        passed=found,
        detail="" if found else "P[0-3] 태그 미발견",
    )


def _check_forbidden_patterns(ac: ParsedAC, output: str) -> list[CheckResult]:
    """INV-WREV-03: forbidden patterns 전수 통과."""
    results = []
    for fp in ac.forbidden_patterns:
        text = resolve_scoped_text(output, fp.scope)
        match = re.search(fp.pattern, text)
        results.append(CheckResult(
            id="INV-WREV-03",
            rule=f"forbidden: {fp.pattern}",
            passed=match is None,
            detail=f"매치 발견: '{match.group()}'" if match else "",
        ))
    return results


def _check_required_patterns(ac: ParsedAC, output: str) -> list[CheckResult]:
    """INV-WREV-05: required patterns 전수 충족."""
    results = []
    for rp in ac.required_patterns:
        text = resolve_scoped_text(output, rp.scope)
        found = bool(re.search(rp.pattern, text))
        results.append(CheckResult(
            id="INV-WREV-05",
            rule=f"required: {rp.pattern}",
            passed=found,
            detail="" if found else "패턴 미매치",
        ))
    return results


def _check_length(ac: ParsedAC, output: str) -> CheckResult:
    """INV-WREV-04: 길이 범위."""
    length = len(output)
    in_range = ac.min_length_chars <= length <= ac.max_length_chars
    return CheckResult(
        id="INV-WREV-04",
        rule=f"길이 {ac.min_length_chars}~{ac.max_length_chars}",
        passed=in_range,
        detail=f"실제 {length}자",
    )


def run_invariants(ac: ParsedAC, output: str) -> list[CheckResult]:
    """공통 + 페르소나 invariant 전수 실행."""
    results = []
    results.append(_check_heading_or_fallback(ac, output))
    results.append(_check_severity_tags(output))
    results.extend(_check_forbidden_patterns(ac, output))
    results.append(_check_length(ac, output))
    results.extend(_check_required_patterns(ac, output))

    # INV-CODE-01: 체크리스트 참조
    for inv in ac.invariants:
        if inv.id == "INV-CODE-01":
            matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output)
            results.append(CheckResult(
                id=inv.id,
                rule=inv.rule,
                passed=len(matches) >= 1,
                detail=f"{len(matches)}건 발견" if matches else "미발견",
            ))
        elif inv.id == "INV-CODE-02":
            has_func = bool(re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(", output))
            has_file = bool(re.search(r"[\w./\\-]+\.\w+:\d+", output))
            results.append(CheckResult(
                id=inv.id,
                rule=inv.rule,
                passed=has_func or has_file,
                detail=f"func={has_func}, file_ref={has_file}",
            ))

    return results


def run_fixture(fixture: Fixture, output: str) -> FixtureResult:
    """단일 fixture의 expected 대조."""
    checks = []
    exp = fixture.expected

    for pattern in exp.must_match_patterns:
        found = bool(re.search(pattern, output))
        checks.append(CheckResult(
            id=f"{fixture.id}/must_match",
            rule=f"pattern: {pattern}",
            passed=found,
            detail="" if found else "미매치",
        ))

    for text in exp.must_include:
        found = text in output
        checks.append(CheckResult(
            id=f"{fixture.id}/must_include",
            rule=f"includes: {text}",
            passed=found,
            detail="" if found else "미포함",
        ))

    if exp.min_length > 0:
        length = len(output)
        checks.append(CheckResult(
            id=f"{fixture.id}/min_length",
            rule=f"min_length: {exp.min_length}",
            passed=length >= exp.min_length,
            detail=f"실제 {length}자",
        ))

    if exp.max_length > 0:
        length = len(output)
        checks.append(CheckResult(
            id=f"{fixture.id}/max_length",
            rule=f"max_length: {exp.max_length}",
            passed=length <= exp.max_length,
            detail=f"실제 {length}자",
        ))

    return FixtureResult(fixture_id=fixture.id, checks=checks)


def run_all(
    ac: ParsedAC,
    output: str,
    fixture_id: Optional[str] = None,
) -> RunResult:
    """전체 검증 실행.

    Args:
        ac: 파싱된 AC (공통 + 페르소나 합산)
        output: reviewer output 텍스트
        fixture_id: 특정 fixture만 실행. None이면 전체.
    """
    inv_checks = run_invariants(ac, output)

    fixtures = ac.fixtures
    if fixture_id:
        fixtures = [f for f in fixtures if f.id == fixture_id]

    fix_results = [run_fixture(f, output) for f in fixtures]

    return RunResult(
        invariant_checks=inv_checks,
        fixture_results=fix_results,
    )
