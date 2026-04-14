"""Tests for resolve_scoped_text (inquisition AC INV-IQ-03/05 지원)."""

from __future__ import annotations

import pytest

from papillon_ac.scope import resolve_scoped_text

DOC = """## 개요
개요 내용.
## 미결 사항
TODO 남음.
## 기능 요구사항
확정: 사항 A."""


def test_scope_all_returns_full_document():
    assert resolve_scoped_text(DOC, "all") == DOC


def test_scope_exclude_section_removes_target():
    result = resolve_scoped_text(DOC, "exclude_section:미결 사항")
    assert "TODO 남음" not in result
    assert "개요 내용" in result
    assert "확정: 사항 A" in result


def test_scope_only_section_returns_target_content():
    result = resolve_scoped_text(DOC, "only_section:기능 요구사항")
    assert result == "확정: 사항 A."


def test_scope_exclude_section_not_found_returns_original():
    result = resolve_scoped_text(DOC, "exclude_section:없는 섹션")
    assert result == DOC


def test_scope_only_section_not_found_returns_empty():
    result = resolve_scoped_text(DOC, "only_section:없는 섹션")
    assert result == ""


def test_scope_malformed_raises():
    with pytest.raises(ValueError):
        resolve_scoped_text(DOC, "bogus_scope")


def test_scope_exclude_section_with_colon_in_name():
    # 섹션명에 콜론이 포함된 경우 (split로 안전 처리 확인)
    doc = "## A:B\n내용1\n## C\n내용2"
    result = resolve_scoped_text(doc, "exclude_section:A:B")
    assert "내용1" not in result
    assert "내용2" in result
