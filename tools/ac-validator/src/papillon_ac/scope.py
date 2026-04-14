"""Scoped patterns 공통 디스패처.

inquisition AC v0.1.0 INV-IQ-03 (forbidden_patterns) 및 INV-IQ-05
(required_patterns) 검증에 쓰이는 scope 처리 로직을 공통화한다.

scope 옵션:
  - "all"                  문서 전체에서 검사
  - "exclude_section:X"    섹션 X를 제외한 나머지에서 검사
  - "only_section:X"       섹션 X 안에서만 검사
"""

from __future__ import annotations

from papillon_ac.markdown_utils import exclude_section, extract_section


def resolve_scoped_text(document: str, scope: str) -> str:
    """Return the text region to which a scoped pattern should apply.

    Args:
      document: Full markdown document text.
      scope: One of "all", "exclude_section:X", or "only_section:X".

    Returns:
      The substring of the document to be matched against.

    Raises:
      ValueError: If the scope string is malformed.
    """
    if scope == "all":
        return document

    if scope.startswith("exclude_section:"):
        section_name = scope.split(":", 1)[1]
        return exclude_section(document, section_name)

    if scope.startswith("only_section:"):
        section_name = scope.split(":", 1)[1]
        return extract_section(document, section_name)

    raise ValueError(f"Unknown scope: {scope!r}")
