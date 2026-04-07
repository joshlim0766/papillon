# 03-review-task: 코드 / 운영 절차 리뷰 모드

## Context
- **Parent:** [00-core.md](./00-core.md)
- **Related:** [01-review-prd.md](./01-review-prd.md), [02-review-design.md](./02-review-design.md)
- **Status:**
  - Work: Draft
  - Review: None

---

## 1. 코드 리뷰

### 1.1. 대상

diff, 소스 파일

### 1.2. 전문가 풀

| 기본 풀 | 선택적 투입 |
|---|---|
| CODE, TEST | ARCH, SEC (단독 실행 시 오케스트레이터가 제안 가능) |

### 1.3. 의사결정 방식

AI 자동 수정 + diff 승인/반려/직접수정 (코어 [2.2](./00-core.md#22-ai-자동-수정--diff-승인반려-코드-리뷰) 참조)

### 1.4. 모드 특화 사항

- **papillon 경유 시**: Phase 4-A 완료 후 자동으로 대상 결정
- **단독 실행 시**: 오케스트레이터가 `$ARGUMENTS`를 분석하여 대상을 결정한다. 인자가 없으면 사람에게 아래 중 선택을 요청:
  - staged 변경사항 (`git diff --cached`)
  - 특정 브랜치 대비 변경사항 (`git diff <branch>...HEAD`)
  - 특정 커밋 범위 (`git diff <commit1>..<commit2>`)
- AI 전문가가 지적 + 자동 수정 수행
- 오케스트레이터가 finding 간 코드 영향 범위를 분석하여 diff 단위 결정 (코어 [2.2](./00-core.md#22-ai-자동-수정--diff-승인반려-코드-리뷰) 상세 참조)

---

## 2. 운영 절차 리뷰

### 2.1. 대상

- **런북**: 장애 대응·배포·롤백 등 반복 실행되는 운영 절차. [50-runbook-template.md](../../50-runbook-template.md) 규격 적용
- **절차서**: 마이그레이션·권한 변경·인프라 작업 등 일회성 또는 비정기 운영 절차. 런북 규격을 따르되, 반복 실행 전제 항목(스케줄, 트리거 조건 등)은 생략 가능

### 2.2. 전문가 풀

| 기본 풀 | 선택적 투입 |
|---|---|
| SRE, SEC | DBA (오케스트레이터가 DB 변경 포함 여부를 분석하여 추가 제안) |

### 2.3. 의사결정 방식

finding별 수용/기각 (코어 [2.1](./00-core.md#21-finding별-수용기각-prd--설계--운영-절차-리뷰) 참조)

### 2.4. 모드 특화 사항

런북 작성 규격은 [50-runbook-template.md](../../50-runbook-template.md) 참조.

---

## References
- 코어: [00-core.md](./00-core.md)
- 전문가 정의: [../../51-expert-definitions.md](../../51-expert-definitions.md)
- 런북 템플릿: [../50-runbook-template.md](../50-runbook-template.md)
