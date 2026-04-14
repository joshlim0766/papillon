"""Markdown 유틸리티 — 부록 E 구현.

모든 함수는 결정적이며 동일 입력에 동일 결과를 반환한다.

부록 E 명세 외에 추가된 함수:
  - extract_headings: 문서에서 모든 heading을 normalize된 형태로 추출.
    (inquisition AC INV-IQ-01에서 필요. 부록 E v3.3 보강 후보.)
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Heading(NamedTuple):
    """문서 내 heading 정보."""

    level: int  # '#' 개수
    normalized: str  # normalize_heading 적용 결과
    line_index: int  # 원본 문서의 줄 번호 (0-based)


_HEADING_LINE_PATTERN = re.compile(r"^(\s*)(#+)\s*(.*?)\s*$")


def normalize_heading(heading: str) -> str:
    """Normalize a markdown heading string per 부록 E.

    Algorithm:
      1. 앞뒤 공백 trim
      2. heading prefix (#, ##, ###, ...) 제거
      3. prefix 제거 후 다시 trim
      4. 연속 공백을 단일 공백으로 치환
    """
    stripped = heading.strip()
    # Remove leading '#' characters (one or more)
    stripped = re.sub(r"^#+", "", stripped)
    stripped = stripped.strip()
    # Collapse consecutive whitespace
    stripped = re.sub(r"\s+", " ", stripped)
    return stripped


def extract_headings(document: str) -> list[Heading]:
    """Extract all markdown headings from a document.

    Returns a list of Heading(level, normalized, line_index).

    Non-heading lines are ignored. Headings inside fenced code blocks are NOT
    excluded in this initial implementation; see AC Template v3.3 후보 숙제.
    """
    headings: list[Heading] = []
    for idx, raw_line in enumerate(document.splitlines()):
        match = _HEADING_LINE_PATTERN.match(raw_line)
        if not match:
            continue
        hashes = match.group(2)
        body = match.group(3)
        level = len(hashes)
        normalized = normalize_heading(body)
        headings.append(Heading(level=level, normalized=normalized, line_index=idx))
    return headings


def _find_section_range(
    document: str, heading: str
) -> tuple[int, int] | None:
    """Locate the (start_line, end_line_exclusive) range for the target section.

    The range covers the content lines AFTER the heading line, up to (but not
    including) the next heading at the same or higher (smaller-number) level.
    Returns None if heading is not found.
    """
    target = normalize_heading(heading)
    lines = document.splitlines()
    headings = extract_headings(document)

    target_idx: int | None = None
    target_level: int | None = None
    for h in headings:
        if h.normalized == target:
            target_idx = h.line_index
            target_level = h.level
            break

    if target_idx is None or target_level is None:
        return None

    start_line = target_idx + 1
    end_line = len(lines)  # default: end of document
    for h in headings:
        if h.line_index <= target_idx:
            continue
        if h.level <= target_level:
            end_line = h.line_index
            break

    return start_line, end_line


def extract_section(document: str, heading: str) -> str:
    """Extract the content of a section under the given heading.

    Args:
      document: Full markdown document text.
      heading: Target heading (normalization applied internally).

    Returns:
      The section content (heading line excluded). Trailing newline is stripped.
      Empty string if heading not found or the section is empty.
    """
    rng = _find_section_range(document, heading)
    if rng is None:
        return ""
    start, end = rng
    lines = document.splitlines()
    return "\n".join(lines[start:end])


def exclude_section(document: str, heading: str) -> str:
    """Return the document text with the target section (heading line included) removed.

    If heading is not found, returns the original document unchanged.
    """
    rng = _find_section_range(document, heading)
    if rng is None:
        return document
    start, end = rng
    # include heading line in the removal
    heading_line = start - 1
    lines = document.splitlines()
    remaining = lines[:heading_line] + lines[end:]
    return "\n".join(remaining)


# Sentence splitting for get_sentence_containing.
# - 줄바꿈
# - 마침표+공백, 물음표+공백, 느낌표+공백
# - Markdown list item prefix (-, *, or "N.") 는 독립 문장 시작
_LIST_ITEM_PREFIX = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences per 부록 E get_sentence_containing() algorithm."""
    # Step 1a: split on newlines first; each line is then sentence-split further.
    sentences: list[str] = []
    for line in text.splitlines():
        # Check for list item prefix — treat list items as their own independent units.
        # We still sentence-split within the item's body.
        m = _LIST_ITEM_PREFIX.match(line)
        if m:
            prefix_end = m.end()
            prefix = line[:prefix_end]
            body = line[prefix_end:]
            # Keep prefix on the first sub-sentence so marker context is preserved.
            body_sentences = _split_on_terminators(body)
            if not body_sentences:
                sentences.append(prefix.rstrip())
                continue
            sentences.append((prefix + body_sentences[0]).strip())
            for s in body_sentences[1:]:
                sentences.append(s.strip())
        else:
            for s in _split_on_terminators(line):
                s_stripped = s.strip()
                if s_stripped:
                    sentences.append(s_stripped)
    return sentences


def _split_on_terminators(text: str) -> list[str]:
    """Split on ". ", "? ", "! " while keeping the trailing terminator attached."""
    if not text:
        return []
    # Use a lookbehind-style split by iterating: split on the terminator followed by whitespace.
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if p]


def get_sentence_containing(text: str, keyword: str) -> str:
    """Return the first sentence containing the keyword (case-insensitive).

    Returns empty string if keyword is not found or empty.
    """
    if not keyword:
        return ""
    keyword_lower = keyword.lower()
    for sentence in _split_sentences(text):
        if keyword_lower in sentence.lower():
            return sentence
    return ""
