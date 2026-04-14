"""extract_keywords — 부록 D v3.3 구현.

결정적(deterministic) 함수. 동일 입력에 항상 동일 결과를 반환한다.

v3.3 변경점 (v3.2 대비):
  - 토큰화를 스크립트별 연속 실행 추출로 변경. 혼합 스크립트 토큰
    (예: "reviewer를")이 ["reviewer", "를"]로 분리된다.
  - 한글 1글자 목적격 조사 제거 단계 신설 (을/를만).
"""

from __future__ import annotations

import re
from typing import Iterable

HANGUL_STOPWORDS = frozenset(
    [
        "이", "그", "저", "것", "수", "등", "및", "또는", "그리고",
        "하지만", "때문", "위해", "대한", "통해", "경우",
        "하는", "있는", "없는", "되는", "같은",
    ]
)

ENGLISH_STOPWORDS = frozenset(
    [
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "of", "to", "in", "on", "at", "for", "with", "and", "or",
        "but", "not", "this", "that", "these", "those",
    ]
)

# 목적격 조사 (을/를). 한글 토큰 말미에 붙으면 제거한다.
# 다른 조사(이/가/은/는/의/로 등)는 의도적으로 대상 외. 예: "기반으로"는 보존.
_HANGUL_OBJECT_PARTICLES = frozenset(["을", "를"])

# 토큰 추출 — 스크립트(영문/한글/숫자)별 연속 run을 추출.
# 공백·구두점은 자동 구분자 역할을 한다.
# "reviewer를" → ["reviewer", "를"], "BE" → ["BE"], "결과를" → ["결과를"].
_TOKEN_PATTERN = re.compile(r"[A-Za-z]+|[가-힣]+|\d+")

# 대문자 전용 영문 약어 (2글자 이상, 예: DB, AI, UX, DBA)
_ALL_UPPER_EN_PATTERN = re.compile(r"^[A-Z]{2,}$")

# 한글 토큰
_HANGUL_PATTERN = re.compile(r"^[가-힣]+$")

# 영문 (소문자·대소문자 혼합)
_ALPHA_PATTERN = re.compile(r"^[A-Za-z]+$")

# 숫자 단독
_DIGIT_PATTERN = re.compile(r"^\d+$")


def extract_keywords(text: str, domain_vocabulary: Iterable[str] | None = None) -> list[str]:
    """Extract keywords from text per AC Template v3.3 부록 D.

    Algorithm:
      1. 스크립트별 연속 토큰 추출: re.findall(r"[A-Za-z]+|[가-힣]+|\\d+", text)
         — 혼합 스크립트 토큰(예: "reviewer를")은 자동 분리된다.
      2. domain_vocabulary 토큰은 길이/stopword 무관 keyword (case-insensitive 매칭)
      3. 나머지 토큰에 길이 기준 적용:
         - 한글: 2글자 이상
         - 대문자 전용 영문 2글자 이상: 약어로 포함
         - 영문 기타: 3글자 이상 (소문자 정규화)
         - 숫자 단독: 제외
      4. 한글 1글자 목적격 조사 제거: 한글 토큰 길이 ≥ 3이고 말미가 '을'/'를'이면
         해당 글자 제거. ('을'/'를'만 대상, 다른 조사는 보존.)
      5. stopword 제거 (단, domain_vocabulary 및 대문자 전용 토큰은 제외 대상에서 제외)
      6. 중복 제거, 출현 순서 보존

    Args:
      text: 키워드 추출 대상 문자열.
      domain_vocabulary: 길이 기준 무시 대상 토큰 집합 (global ∪ skill-local 합집합).

    Returns:
      추출된 keyword 리스트 (출현 순서 보존, 중복 제거).
    """
    vocab_lower = {v.lower() for v in (domain_vocabulary or [])}

    tokens = _TOKEN_PATTERN.findall(text)
    result: list[str] = []
    seen: set[str] = set()

    for token in tokens:
        kw = _classify_token(token, vocab_lower)
        if kw is None:
            continue
        if kw in seen:
            continue
        seen.add(kw)
        result.append(kw)

    return result


def _classify_token(token: str, vocab_lower: set[str]) -> str | None:
    """Return the keyword form of the token, or None if it should be dropped."""
    # (1) domain vocabulary 우선 매칭 (case-insensitive)
    if token.lower() in vocab_lower:
        return token  # 원래 표기 유지

    # (2) 숫자 단독 제외
    if _DIGIT_PATTERN.match(token):
        return None

    # (3) 대문자 전용 영문 2글자 이상 → 약어로 포함 (stopword 제외 대상 제외)
    if _ALL_UPPER_EN_PATTERN.match(token):
        return token  # 원래 표기(대문자) 유지

    # (4) 한글
    if _HANGUL_PATTERN.match(token):
        # 한글 1글자 목적격 조사 제거 (을/를). 길이 ≥ 3일 때만 적용.
        if len(token) >= 3 and token[-1] in _HANGUL_OBJECT_PARTICLES:
            token = token[:-1]
        if len(token) < 2:
            return None
        if token in HANGUL_STOPWORDS:
            return None
        return token

    # (5) 영문 (대소문자 혼합 또는 소문자) 3글자 이상
    if _ALPHA_PATTERN.match(token):
        if len(token) < 3:
            return None
        lowered = token.lower()
        if lowered in ENGLISH_STOPWORDS:
            return None
        return lowered

    # (6) 혼합 토큰(한글+영문+숫자 등)은 step_3 규칙에 명시적 정의 없음 → drop
    return None
