"""Tests for extract_keywords (부록 D v3.3).

부록 D의 4개 example 모두 테스트 커버.
"""

from __future__ import annotations

from papillon_ac.keywords import extract_keywords


def test_example_1_hangul_particle_stripping():
    """부록 D example 1: 한글 1글자 목적격 조사 제거.

    "결과를"/"초안을" → "결과"/"초안". "기반으로"/"생성한다"는 보존.
    """
    result = extract_keywords(
        "요구사항 인터뷰 결과를 기반으로 설계 문서 초안을 생성한다", []
    )
    assert result == [
        "요구사항",
        "인터뷰",
        "결과",
        "기반으로",
        "설계",
        "문서",
        "초안",
        "생성한다",
    ]


def test_example_2_english_with_stopwords_and_uppercase():
    """부록 D example 2: 영문 + stopword + 대문자 전용 약어.

    'Do' → 2글자 영문이지만 대문자 전용 아님 → drop.
    'NOT' → 대문자 전용 3글자 → 포함 (약어 규칙).
    'for' → 영문 stopword → drop.
    """
    result = extract_keywords("Do NOT trigger for simple typo corrections", [])
    assert result == ["NOT", "trigger", "simple", "typo", "corrections"]


def test_example_3_mixed_script_token_separation():
    """부록 D example 3: 혼합 스크립트 토큰 자동 분리.

    "reviewer를" → ["reviewer", "를"], "TW는" → ["TW", "는"].
    """
    result = extract_keywords(
        "BE, FE reviewer를 포함하고 TW는 제외",
        ["BE", "FE", "TW"],
    )
    assert result == ["BE", "FE", "reviewer", "포함하고", "TW", "제외"]


def test_example_4_uppercase_abbrev_and_vocab():
    """부록 D example 4: DB (대문자 전용 약어 규칙) + DBA (vocab 매칭)."""
    result = extract_keywords("DB 스키마 변경 시 DBA 필수", ["DBA"])
    assert result == ["DB", "스키마", "변경", "DBA", "필수"]


def test_number_only_token_dropped():
    result = extract_keywords("버전 3 릴리스 2026 년", [])
    # 숫자 단독 토큰("3", "2026")은 제외. "년"은 1글자 한글이라 탈락.
    assert result == ["버전", "릴리스"]


def test_particle_stripping_respects_length_floor():
    """목적격 조사 제거 후 길이가 2 미만이 되면 drop."""
    # "가를" (2 chars) — 규칙은 len≥3일 때만 strip이므로 strip 안함 → 유지
    # "집를" (2 chars) — 동일
    # "집을" (2 chars) — strip 안함 → 유지 (단어는 희한하지만 테스트용)
    result = extract_keywords("집을", [])
    assert result == ["집을"]

    # "집콕을" (3 chars) → strip → "집콕" (2 chars) → 유지
    result = extract_keywords("집콕을", [])
    assert result == ["집콕"]


def test_compound_particle_preserved():
    """'으로' 등 2자 조사는 strip 대상 아님."""
    result = extract_keywords("기반으로 진행", [])
    assert result == ["기반으로", "진행"]


def test_duplicate_tokens_removed_order_preserved():
    result = extract_keywords("알파 베타 알파 감마 베타", [])
    assert result == ["알파", "베타", "감마"]


def test_hangul_stopwords_filtered():
    result = extract_keywords("그리고 하지만 문서", [])
    assert result == ["문서"]


def test_short_hangul_filtered():
    result = extract_keywords("을 를 이 가 요구사항", [])
    assert result == ["요구사항"]


def test_empty_input():
    assert extract_keywords("", []) == []


def test_none_vocabulary():
    assert extract_keywords("hello world", None) == ["hello", "world"]


def test_deterministic():
    """동일 입력 N회 호출이 동일 결과를 반환 (부록 D properties.deterministic)."""
    text = "Do NOT trigger for simple typo corrections"
    runs = [tuple(extract_keywords(text, [])) for _ in range(5)]
    assert len(set(runs)) == 1
