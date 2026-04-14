# papillon-ac

Papillon AC Template v3.3 검증 유틸리티.

**정본 스펙:** `01-Planning/08-ac/ac-template-v3.3.md` (부록 D, 부록 E)

## 구성

| 모듈 | 역할 | 관련 스펙 |
|---|---|---|
| `papillon_ac.keywords` | `extract_keywords()` — Artifact AC용 키워드 추출 | 부록 D |
| `papillon_ac.markdown_utils` | `normalize_heading`, `extract_headings`, `extract_section`, `exclude_section`, `get_sentence_containing` | 부록 E |
| `papillon_ac.scope` | `resolve_scoped_text` — scoped patterns 공통 디스패처 (INV-IQ-03/05 지원) | inquisition AC v0.1.0 |

## 설치

```bash
cd tools/ac-validator
uv sync --extra dev
```

## 테스트

```bash
cd tools/ac-validator
uv run pytest
```

## 참조

- `01-Planning/08-ac/ac-template-v3.3.md` — AC Template 정본
- `01-Planning/05-inquisition/ac-v0.1.0.md` — 첫 실전 적용
- `VOCABULARY.yaml` (레포 루트) — global domain vocabulary
