#!/usr/bin/env python3
"""CLI — Fixture Runner.

Usage:
    python scripts/run_fixture.py \\
        --common 01-Planning/04-wtth/ac/common-v0.1.1.md \\
        --persona 01-Planning/04-wtth/ac/code-v0.1.1.md \\
        --output reviewer_output.txt \\
        [--fixture FIX-CODE-01]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from papillon_ac.ac_parser import parse_common_ac, parse_persona_ac
from papillon_ac.fixture_runner import run_all


def main() -> None:
    parser = argparse.ArgumentParser(description="wtth Reviewer AC Fixture Runner")
    parser.add_argument("--common", required=True, help="공통 AC Markdown 파일")
    parser.add_argument("--persona", required=True, help="페르소나 AC Markdown 파일")
    parser.add_argument("--output", required=True, help="reviewer output 텍스트 파일 (또는 - for stdin)")
    parser.add_argument("--fixture", default=None, help="특정 fixture ID만 실행")
    args = parser.parse_args()

    common_md = Path(args.common).read_text(encoding="utf-8")
    persona_md = Path(args.persona).read_text(encoding="utf-8")

    if args.output == "-":
        output_text = sys.stdin.read()
    else:
        output_text = Path(args.output).read_text(encoding="utf-8")

    ac = parse_common_ac(common_md)
    ac = parse_persona_ac(persona_md, ac)

    result = run_all(ac, output_text, fixture_id=args.fixture)

    print(result.summary())
    sys.exit(0 if result.all_passed else 1)


if __name__ == "__main__":
    main()
