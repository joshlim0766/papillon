"""Tests for markdown utilities (부록 E)."""

from __future__ import annotations

from papillon_ac.markdown_utils import (
    exclude_section,
    extract_headings,
    extract_section,
    get_sentence_containing,
    normalize_heading,
)


# --- normalize_heading ---


def test_normalize_heading_basic():
    assert normalize_heading("## 개요") == "개요"


def test_normalize_heading_multiple_spaces():
    assert normalize_heading("##  배경 및  목적 ") == "배경 및 목적"


def test_normalize_heading_no_space_after_hash():
    assert normalize_heading("###API 명세") == "API 명세"


def test_normalize_heading_leading_trailing_whitespace():
    assert normalize_heading("  개요  ") == "개요"


def test_normalize_heading_idempotent():
    once = normalize_heading("## 스코프")
    twice = normalize_heading(once)
    assert once == twice == "스코프"


# --- extract_headings ---


def test_extract_headings_basic():
    doc = "## 개요\n내용\n## 스코프\n상세"
    headings = extract_headings(doc)
    assert len(headings) == 2
    assert headings[0].normalized == "개요"
    assert headings[0].level == 2
    assert headings[1].normalized == "스코프"


def test_extract_headings_multiple_levels():
    doc = "# Top\n## Sub\n### Sub-sub\n## Sub2"
    headings = extract_headings(doc)
    levels = [h.level for h in headings]
    names = [h.normalized for h in headings]
    assert levels == [1, 2, 3, 2]
    assert names == ["Top", "Sub", "Sub-sub", "Sub2"]


def test_extract_headings_ignores_non_heading_lines():
    doc = "일반 문장\n## 제목\n하위 내용\n##또 제목"
    headings = extract_headings(doc)
    # "##또 제목"은 `##` 바로 뒤에 공백 없지만 normalize는 가능.
    # 실제 패턴이 `#+\s*(.*)`이므로 공백 없어도 매칭됨.
    assert [h.normalized for h in headings] == ["제목", "또 제목"]


# --- extract_section ---


SAMPLE_DOC = """## 개요
프로젝트 소개입니다.
## 스코프
포함: A, B
미포함: C
## 기능 요구사항
기능 1"""


def test_extract_section_first_section():
    assert extract_section(SAMPLE_DOC, "개요") == "프로젝트 소개입니다."


def test_extract_section_middle_section():
    assert extract_section(SAMPLE_DOC, "스코프") == "포함: A, B\n미포함: C"


def test_extract_section_last_section_goes_to_eof():
    assert extract_section(SAMPLE_DOC, "기능 요구사항") == "기능 1"


def test_extract_section_not_found_returns_empty():
    assert extract_section(SAMPLE_DOC, "없는 섹션") == ""


def test_extract_section_normalizes_heading_input():
    # heading 인자에 `## ` prefix가 붙어도 동작해야 함
    assert extract_section(SAMPLE_DOC, "## 개요") == "프로젝트 소개입니다."


def test_extract_section_stops_at_same_or_higher_level():
    # h2 섹션 안의 h3는 섹션 내부. 다음 h2가 경계.
    doc = "## A\n내용A\n### A-sub\n내용A-sub\n## B\n내용B"
    result = extract_section(doc, "A")
    assert result == "내용A\n### A-sub\n내용A-sub"


def test_extract_section_higher_level_boundary():
    # h2 A 안에서 h1 B가 나오면 경계가 됨 (h2보다 상위)
    doc = "## A\n내용A\n# B\n내용B"
    result = extract_section(doc, "A")
    assert result == "내용A"


# --- exclude_section ---


def test_exclude_section_removes_target():
    result = exclude_section(SAMPLE_DOC, "스코프")
    assert "스코프" not in result
    assert "포함: A, B" not in result
    assert "프로젝트 소개입니다." in result
    assert "기능 요구사항" in result


def test_exclude_section_not_found_returns_original():
    assert exclude_section(SAMPLE_DOC, "없는 섹션") == SAMPLE_DOC


def test_exclude_section_last_section():
    result = exclude_section(SAMPLE_DOC, "기능 요구사항")
    assert "기능 1" not in result
    assert "프로젝트 소개입니다." in result


# --- get_sentence_containing ---


def test_get_sentence_basic():
    text = "첫 번째 문장. 두 번째 문장. 세 번째 문장."
    assert get_sentence_containing(text, "두 번째") == "두 번째 문장."


def test_get_sentence_newline_separated():
    text = "첫 줄\n두 줄 keyword 여기\n세 줄"
    assert get_sentence_containing(text, "keyword") == "두 줄 keyword 여기"


def test_get_sentence_case_insensitive():
    text = "Line one. Line TWO here. Line three."
    assert get_sentence_containing(text, "two") == "Line TWO here."


def test_get_sentence_list_item():
    text = "일반 문장.\n- 리스트 아이템 첫 번째\n- 리스트 아이템 second\n- 리스트 아이템 셋째"
    assert get_sentence_containing(text, "second") == "- 리스트 아이템 second"


def test_get_sentence_numbered_list():
    text = "1. 첫 항목\n2. 두 번째 key 항목\n3. 세 항목"
    assert get_sentence_containing(text, "key") == "2. 두 번째 key 항목"


def test_get_sentence_keyword_not_found():
    assert get_sentence_containing("아무것도 없음", "xyz") == ""


def test_get_sentence_empty_keyword():
    assert get_sentence_containing("some text", "") == ""


def test_get_sentence_returns_first_only():
    text = "alpha. alpha beta. alpha gamma."
    # "alpha" 포함 문장이 3개. 첫 번째 반환.
    assert get_sentence_containing(text, "alpha") == "alpha."
