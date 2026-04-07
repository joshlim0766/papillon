# 01-review-prd: PRD 리뷰 모드

## Context
- **Parent:** [00-core.md](./00-core.md)
- **Related:** [02-review-design.md](./02-review-design.md), [03-review-task.md](./03-review-task.md)
- **Status:**
  - Work: Draft
  - Review: None

---

## 1. 대상

PRD, 기획 문서

## 2. 전문가 풀

| 기본 풀 | 선택적 투입 |
|---|---|
| PM, ARCH, SEC | BE, SRE (오케스트레이터가 PRD 내 기술 제약/인프라 요소를 분석하여 추가 제안) |

## 3. 의사결정 방식

finding별 수용/기각 (코어 [2.1](./00-core.md#21-finding별-수용기각-prd--설계--운영-절차-리뷰) 참조)

## 4. 모드 특화 사항

### 4.1. 리뷰 초점

PRD 리뷰는 "구현 가능한 명세인가"를 검증한다. 전문가별 초점:

| 전문가 | 초점 |
|---|---|
| PM | 목표-측정기준 대응, 스코프 경계, 비목표 명확성 |
| ARCH | 기술적 실현 가능성, 제약 조건 충분성, 산출물 구조 |
| SEC | 보안 관련 요구사항 누락, 데이터 흐름 상의 위협 |

### 4.2. 공통 프로세스

의사결정, 수렴 메커니즘 등은 코어 공통 프로세스를 따른다.

---

## References
- 코어: [00-core.md](./00-core.md)
- 전문가 정의: [../../51-expert-definitions.md](../../51-expert-definitions.md)
