"""AC Markdown 파서 — YAML-in-Markdown 블록에서 검증 구조체 추출."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import yaml


_YAML_BLOCK_RE = re.compile(
    r"```ya?ml\s*\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE
)


def extract_yaml_blocks(markdown: str) -> list[dict[str, Any]]:
    """Markdown에서 모든 ```yaml 블록을 추출하여 파싱."""
    results = []
    for m in _YAML_BLOCK_RE.finditer(markdown):
        raw = m.group(1)
        try:
            parsed = yaml.safe_load(raw)
            if isinstance(parsed, dict):
                results.append(parsed)
        except yaml.YAMLError:
            continue
    return results


@dataclass
class PatternRule:
    pattern: str
    scope: str = "all"


@dataclass
class Invariant:
    id: str
    rule: str
    check: str = ""


@dataclass
class FixtureExpected:
    must_match_patterns: list[str] = field(default_factory=list)
    must_include: list[str] = field(default_factory=list)
    min_length: int = 0
    max_length: int = 0


@dataclass
class Fixture:
    id: str
    description: str
    input_code: str = ""
    expected: FixtureExpected = field(default_factory=FixtureExpected)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedAC:
    """공통 AC + 페르소나 AC 합산 결과."""
    version: str = ""
    forbidden_patterns: list[PatternRule] = field(default_factory=list)
    required_patterns: list[PatternRule] = field(default_factory=list)
    invariants: list[Invariant] = field(default_factory=list)
    fixtures: list[Fixture] = field(default_factory=list)
    min_length_chars: int = 100
    max_length_chars: int = 20000
    required_sections_heading: str = "Findings"
    required_sections_alternatives: list[str] = field(default_factory=list)
    heading_required: bool = True


def _parse_patterns(items: list[dict]) -> list[PatternRule]:
    rules = []
    for item in items:
        if isinstance(item, dict):
            rules.append(PatternRule(
                pattern=item.get("pattern", ""),
                scope=item.get("scope", "all"),
            ))
        elif isinstance(item, str):
            rules.append(PatternRule(pattern=item))
    return rules


def _parse_invariants(items: list[dict]) -> list[Invariant]:
    return [
        Invariant(
            id=item.get("id", ""),
            rule=item.get("rule", ""),
            check=item.get("check", ""),
        )
        for item in items
        if isinstance(item, dict)
    ]


def _parse_fixture(item: dict) -> Fixture:
    expected_raw = item.get("expected", {})
    expected = FixtureExpected(
        must_match_patterns=expected_raw.get("must_match_patterns", []),
        must_include=expected_raw.get("must_include", []),
        min_length=expected_raw.get("min_length", 0),
        max_length=expected_raw.get("max_length", 0),
    )
    input_raw = item.get("input", {})
    input_code = input_raw.get("code_snippet", "") if isinstance(input_raw, dict) else ""
    return Fixture(
        id=item.get("id", ""),
        description=item.get("description", ""),
        input_code=input_code,
        expected=expected,
        meta=item.get("meta", {}),
    )


def parse_common_ac(markdown: str) -> ParsedAC:
    """공통 AC Markdown에서 검증 구조체 추출."""
    blocks = extract_yaml_blocks(markdown)
    ac = ParsedAC()

    for block in blocks:
        if "version" in block and "skill_name" in block:
            ac.version = str(block["version"])

        if "hard_ac_document" in block:
            doc = block["hard_ac_document"]

            sections = doc.get("required_sections", [])
            if sections and isinstance(sections[0], dict):
                sec = sections[0]
                ac.required_sections_heading = sec.get("heading", "Findings")
                ac.required_sections_alternatives = sec.get("alternatives", [])
                ac.heading_required = sec.get("required", True)
                if "fallback_when_absent" in sec:
                    ac.heading_required = False

            fmt = doc.get("format_constraints", {})
            ac.min_length_chars = fmt.get("min_length_chars", 100)
            ac.max_length_chars = fmt.get("max_length_chars", 20000)
            ac.forbidden_patterns = _parse_patterns(
                fmt.get("forbidden_patterns", [])
            )
            ac.required_patterns = _parse_patterns(
                fmt.get("required_patterns", [])
            )
            ac.invariants = _parse_invariants(
                doc.get("invariants", [])
            )

    return ac


def parse_persona_ac(markdown: str, base: ParsedAC) -> ParsedAC:
    """페르소나 AC를 파싱하여 base(공통 AC)에 합산."""
    blocks = extract_yaml_blocks(markdown)

    for block in blocks:
        if "version" in block and "skill_name" in block:
            base.version = str(block["version"])

        if "hard_ac_document_additions" in block:
            additions = block["hard_ac_document_additions"]
            base.required_patterns.extend(
                _parse_patterns(additions.get("required_patterns_additional", []))
            )
            base.invariants.extend(
                _parse_invariants(additions.get("invariants_additional", []))
            )

        if "fixtures" in block:
            for item in block["fixtures"]:
                if isinstance(item, dict):
                    base.fixtures.append(_parse_fixture(item))

    return base
