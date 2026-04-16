"""ac_parser 단위 테스트."""

from pathlib import Path

import pytest

from papillon_ac.ac_parser import (
    extract_yaml_blocks,
    parse_common_ac,
    parse_persona_ac,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
AC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "01-Planning" / "04-wtth" / "ac"


class TestExtractYamlBlocks:
    def test_single_block(self):
        md = "text\n```yaml\nkey: value\n```\nmore"
        blocks = extract_yaml_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["key"] == "value"

    def test_multiple_blocks(self):
        md = "```yaml\na: 1\n```\n---\n```yaml\nb: 2\n```"
        blocks = extract_yaml_blocks(md)
        assert len(blocks) == 2

    def test_invalid_yaml_skipped(self):
        md = "```yaml\n: :\n  - [\n```"
        blocks = extract_yaml_blocks(md)
        assert len(blocks) == 0

    def test_non_dict_skipped(self):
        md = "```yaml\n- a\n- b\n```"
        blocks = extract_yaml_blocks(md)
        assert len(blocks) == 0


class TestParseCommonAC:
    @pytest.fixture
    def common_v011(self):
        return parse_common_ac(
            (AC_DIR / "common-v0.1.1.md").read_text(encoding="utf-8")
        )

    @pytest.fixture
    def common_v010(self):
        return parse_common_ac(
            (AC_DIR / "common-v0.1.0.md").read_text(encoding="utf-8")
        )

    def test_version(self, common_v011):
        assert common_v011.version == "0.1.1"

    def test_heading_not_required_v011(self, common_v011):
        assert common_v011.heading_required is False

    def test_heading_required_v010(self, common_v010):
        assert common_v010.heading_required is True

    def test_forbidden_patterns_count(self, common_v011):
        assert len(common_v011.forbidden_patterns) == 6

    def test_invariants_parsed(self, common_v011):
        ids = [inv.id for inv in common_v011.invariants]
        assert "INV-WREV-01" in ids
        assert "INV-WREV-02" in ids


class TestParsePersonaAC:
    @pytest.fixture
    def merged_v011(self):
        common = parse_common_ac(
            (AC_DIR / "common-v0.1.1.md").read_text(encoding="utf-8")
        )
        return parse_persona_ac(
            (AC_DIR / "code-v0.1.1.md").read_text(encoding="utf-8"),
            common,
        )

    def test_fixtures_loaded(self, merged_v011):
        assert len(merged_v011.fixtures) == 3

    def test_fixture_ids(self, merged_v011):
        ids = [f.id for f in merged_v011.fixtures]
        assert "FIX-CODE-01" in ids
        assert "FIX-CODE-02" in ids
        assert "FIX-CODE-03" in ids

    def test_code_invariants_added(self, merged_v011):
        ids = [inv.id for inv in merged_v011.invariants]
        assert "INV-CODE-01" in ids
        assert "INV-CODE-02" in ids

    def test_fixture_01_patterns(self, merged_v011):
        fix01 = [f for f in merged_v011.fixtures if f.id == "FIX-CODE-01"][0]
        assert len(fix01.expected.must_match_patterns) == 3
        assert "P0" in fix01.expected.must_match_patterns
