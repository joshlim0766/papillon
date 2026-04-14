"""Measure ART-IQ-02 match_rate for the inquisition skill.

Usage (from tools/ac-validator/):
    uv run python scripts/measure_art_iq_02.py

Artifacts read:
  - 01-Planning/05-inquisition/ac-v0.1.0.md  (identity.purpose + domain_vocabulary)
  - VOCABULARY.yaml                          (global vocabulary)
  - ~/.claude/commands/papillon/inquisition.md (installed SKILL.md, `## 개요` section)

ART-IQ-02 (from inquisition AC v0.1.0):
  keywords = extract_keywords(purpose, merged_vocabulary)
  match_rate = sum(1 for kw in keywords if kw in skill_md.description) / len(keywords)
  match_rate >= 0.7
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from papillon_ac.keywords import extract_keywords
from papillon_ac.markdown_utils import extract_section

REPO_ROOT = Path(__file__).resolve().parents[3]
AC_FILE = REPO_ROOT / "01-Planning" / "05-inquisition" / "ac-v0.1.0.md"
VOCAB_FILE = REPO_ROOT / "VOCABULARY.yaml"
SKILL_FILE = Path.home() / ".claude" / "commands" / "papillon" / "inquisition.md"

THRESHOLD = 0.70


def _first_yaml_block(section_text: str) -> dict:
    """Extract the first ```yaml ... ``` code block from a section's text."""
    match = re.search(r"```yaml\s*\n(.*?)\n```", section_text, re.DOTALL)
    if not match:
        raise ValueError("No YAML block found in section")
    return yaml.safe_load(match.group(1))


def load_purpose_and_vocab() -> tuple[str, list[str]]:
    ac_text = AC_FILE.read_text(encoding="utf-8")

    # Identity block is under "## 1. Skill Identity"
    identity_section = extract_section(ac_text, "1. Skill Identity")
    identity = _first_yaml_block(identity_section)
    purpose = identity["identity"]["purpose"]

    # Metadata block is under "## 메타 정보"
    meta_section = extract_section(ac_text, "메타 정보")
    meta = _first_yaml_block(meta_section)
    skill_vocab = meta.get("domain_vocabulary") or []

    with VOCAB_FILE.open(encoding="utf-8") as f:
        vocab_doc = yaml.safe_load(f)
    global_vocab = vocab_doc.get("terms") or []

    merged = []
    seen = set()
    for term in list(global_vocab) + list(skill_vocab):
        if term not in seen:
            seen.add(term)
            merged.append(term)
    return purpose, merged


def load_description() -> str:
    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    description = extract_section(skill_text, "개요")
    return description


def main() -> int:
    purpose, merged_vocab = load_purpose_and_vocab()
    description = load_description()

    if not description.strip():
        print(f"FAIL: '## 개요' section is empty or missing in {SKILL_FILE}")
        return 2

    keywords = extract_keywords(purpose, merged_vocab)
    if not keywords:
        print("FAIL: purpose produced zero keywords — measurement undefined")
        return 2

    matched = [kw for kw in keywords if kw in description]
    missed = [kw for kw in keywords if kw not in description]
    match_rate = len(matched) / len(keywords)

    print("=== ART-IQ-02 Measurement: inquisition ===")
    print(f"Purpose (설계 AC):\n  {purpose.strip()}")
    print()
    print(f"Merged vocabulary ({len(merged_vocab)}): {merged_vocab}")
    print()
    print(f"Extracted keywords ({len(keywords)}):")
    for kw in keywords:
        mark = "✓" if kw in description else "✗"
        print(f"  {mark} {kw}")
    print()
    print(f"Matched ({len(matched)}/{len(keywords)}): {matched}")
    print(f"Missed  ({len(missed)}): {missed}")
    print()
    print(f"match_rate = {len(matched)}/{len(keywords)} = {match_rate:.2%}")
    print(f"threshold  = {THRESHOLD:.0%}")
    verdict = "PASS" if match_rate >= THRESHOLD else "FAIL"
    print(f"verdict    = {verdict}")
    return 0 if match_rate >= THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
