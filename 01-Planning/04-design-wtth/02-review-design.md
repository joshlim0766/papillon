# 02-review-design: 설계 / ADR 리뷰 모드

## Context
- **Parent:** [00-core.md](./00-core.md)
- **Related:** [01-review-prd.md](./01-review-prd.md), [03-review-task.md](./03-review-task.md)
- **Status:**
  - Work: Draft
  - Review: None

---

## 1. 설계 리뷰

### 1.1. 대상
설계 문서, 명세서

### 1.2. 전문가 풀
- 기본 풀: ARCH, BE, FE, SRE, SEC, PO
- 선택적 투입: DBA (오케스트레이터가 제안 톤으로 추가 투입을 물어봄)

### 1.3. 의사결정 방식
finding별 수용/기각 (코어 [§2.1](./00-core.md#21-finding별-수용기각-prd--설계--운영-절차-리뷰) 참조)

---

## 2. ADR 리뷰

### 2.1. 대상
ADR (아키텍처 결정 기록)

### 2.2. 전문가 풀
- 기본 풀: ARCH, SEC
- 선택적 투입: BE, DBA, SRE (오케스트레이터가 ADR 내용을 분석하여 관련 도메인 전문가 추가 제안)

### 2.3. 의사결정 방식
finding별 수용/기각 (코어 [§2.1](./00-core.md#21-finding별-수용기각-prd--설계--운영-절차-리뷰) 참조)

### 2.4. ADR 승격 흐름
설계 리뷰에서 P0/P1 수용 건 중 설계 변경을 수반하는 항목에 대해 ADR 승격을 제안한다. 승격 기준 상세는 코어 [§3.2](./00-core.md#32-adr-승격-규칙) 참조.
ADR 승격 시 papillon Phase 2.1에서 본 모드(ADR 리뷰)로 호출된다.

---

## References
- 코어: [00-core.md](./00-core.md)
- 전문가 정의: [../51-expert-definitions.md](../51-expert-definitions.md)
