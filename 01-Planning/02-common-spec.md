# 02-common-spec: 공통 ���격

## Context
- **Parent:** [00-index.md](../00-index.md)
- **Related:** [03-design-papillon.md](./03-design-papillon.md), [04-design-wtth.md](./04-design-wtth.md)
- **Status:**
  - Work: In-Progress
  - Review: None

---

## Input / Dependency
- PRD: [01-prd.md](./01-prd.md)

---

## 1. 심각도 기준 (P0~P3)

| 등급 | 기준 | 사용 맥락 |
|---|---|---|
| **P0** | 데이터 손실·보안 침해·시스템 다운 가능 | wtth: 강력 수용 권장 / papillon: 종결 불가 |
| **P1** | 운영 장애·감사 실패·주요 UX 붕괴 가능 | wtth: 수용 권장 / papillon: 종결 불가 |
| **P2** | 기술 부채·성능 저하·혼란 유발 | wtth: 수용 제안, 기각 존중 / papillon: 종결 가능 |
| **P3** | 개선 제안·코드 품질·선택적 강화 | wtth: 중립 제시 / papillon: 종결 가능 |

---

## 2. RDR (Review Decision Record) 포맷

리뷰 1회 = RDR 1개. wtth이 리뷰 종료 시 자동 생성한다.

**파일명**: `RDR-YYYY-MM-DD-{대상명}.md`
**저장 경로**: `{프로젝트}/docs/decisions/reviews/`

```markdown
# RDR-YYYY-MM-DD-{대상명}

**리뷰 대상:** {파일 경로 또는 설명}
**날짜:** YYYY-MM-DD
**리뷰 모드:** {PRD / 설계 / 운영 절차 / 코드}
**참여 전문가:** {도메인 목록}

| ID | 심각도 | 제목 | 결정 | 사유 요약 |
|---|---|---|---|---|
| SEC-01 | P0 | ... | 수용 | ... |
| BE-01 | P1 | ... | 기각 | ... |

### 주요 기각 사유
- **BE-01**: {사유}
```

---

## 3. ADR (Architecture Decision Record) 포맷

P0/P1 수용 건 중 **설계 변경을 수반하는 항목**에 대해 wtth이 승격을 제안한다.
사람이 승인하면 생성한다.

**파일명**: `ADR-NNN-{제목}.md`
**저장 경로**: `{프로젝트}/docs/decisions/`

```markdown
# ADR-NNN: {제목}

**날짜:** YYYY-MM-DD | **상태:** 확정

**결정:** {한 줄 요약}
**이유:** {근거}
**기각:** {기각된 대안과 사유}
**영향:** {영향 범위}
```

---

## 4. 작업 요약 카드 포맷

태스크 완료 시 생성한다. ADR이 "왜"를 기록한다면, 작업 요약 카드는 **"무엇을 만들었는가"**를 기록한다.
새 세션에서 LLM이 모듈의 구현 범위와 의존 관계를 빠르게 파악하는 데 사용한다.

**파일명**: `TASK-{ID}-{제목}.md` (해당 태스크 파일에 추가 또는 별도 생성)
**저장 경로**: `{프로젝트}/03-tasks/` 또는 태스크 문서 내 하단

```markdown
# TASK-A-01: 사용자 인증 API

**완료일:** YYYY-MM-DD
**관련 ADR:** ADR-001, ADR-003
**관련 RDR:** RDR-YYYY-MM-DD-auth-api
**구현 범위:** POST /auth/login, /auth/refresh
**의존:** 없음
**피의존:** 대시보드 모듈, 마이페이지 모듈
**특이사항:** refresh token rotation 적용
```

---

## 5. Phase 요약 카드 포맷 (XL 체급)

XL 체급에서 하나의 Phase가 완료될 때 생성한다. 해당 Phase 내 작업 요약 카드들의 summary이다.
새 세션에서 index → Phase 요약 → 태스크 카드 순으로 drill-down하여 맥락을 복원한다.

**저장 위치**: 해당 Phase 디렉토리의 `00-phase-summary.md`

```markdown
# Phase N 요약: {Phase 제목}

**완료일:** YYYY-MM-DD
**포함 태스크:** TASK-001, TASK-002, TASK-003

## 달성 결과
- {이 Phase에서 무엇이 만들어졌는가 / 무엇이 완료되었는가}

## 주요 결정
- ADR-002: {한 줄 요약}
- RDR 3건: 설계 리뷰 2회, 코드 리뷰 1회

## 다음 Phase를 위한 전제
- {이 Phase 결과로 확보된 조건}
- {다음 Phase 시작 전 필요한 사항}
```

---

## 6. Why/How 제시 규칙

사람에게 결정을 요청하거나 결정을 기록할 때 반드시 "왜"와 근거를 포함한다.

### 5.1. wtth finding 제시

```markdown
**문제**: reviewer_id를 클라이언트에서 받는데 인증 토큰과 대조하지 않음
**왜 문제인가**: 다른 사용자의 reviewer_id를 넣으면 타인 명의로 리뷰가 생성됨 (권한 우회)
**참조**: 코드 분석 — src/api/review.ts:42 에서 req.body.reviewerId를 검증 없이 사용
**수정안**: 인증 미들웨어에서 토큰의 user_id와 reviewer_id 일치 여부 검증
```

- "왜 문제인가"는 **인과관계**로 서술한다 ("X하면 Y가 발생한다").
- "참조"는 **있으면 필수, 없으면 추론 근거를 명시**한다.
- 3줄 초과 시 finding을 분할한다.

### 5.2. papillon 결정 요청

```markdown
체급: M
근거: 독립 작업 단위 1개 (인증 API), 하위 작업 3개 (엔드포인트, 미들웨어, 테스트)
L이 아닌 이유: 하위 작업 간 의존성이 강해 분리 실행 불가
```

- 판단 근거 + **대안을 기각한 이유**를 포함한다.

### 5.3. RDR 기록

RDR의 "결정 근거" 컬럼에 인과관계 수준으로 기록한다.
단순 요약("불필요")이 아니라 조건과 맥락을 포함한다("현재 데이터 10만건 미만, 동시 수정 빈도 낮음. 50만건 도달 시 재검토").

### 5.4. 작업 요약 카드

설계 선택이 있는 경우에만 "구현 판단" 섹션을 기재한다.
단순 로그 추가, 설정 변경 등은 생략 가능.

### 5.5. 참조(Reference) 유형

| 출처 유형 | 예시 |
|---|---|
| 설계 문서 | 설계서 §2.3, PRD 목표 G2 |
| 기존 결정 기록 | ADR-005, RDR-2026-04-02-auth |
| 코드 | `src/api/review.ts:42` |
| 외부 기준 | OWASP Top 10 A01, K8s 공식 문서 |
| KB 축적 지식 | KB 검색 결과 (인시던트, 패턴 등) |

---

## 7. 파일 산출물 디렉토리 구조

파이프라인 실행 시 생성되는 산출물의 저장 구조:

```
{프로젝트}/docs/decisions/
  reviews/
    RDR-YYYY-MM-DD-{대상명}.md
  ADR-NNN-{제목}.md
{프로젝트}/03-tasks/
  TASK-{ID}-{제목}.md              ← 작업 요약 카드 포함
```

---

## 8. L/XL 프로젝트 구조 템플릿

L/XL 체급 작업 시 papillon가 생성��는 프로젝트 구조:

```
{프로젝트}/
  00-index.md          ← 전체 조감도 + 현재 진행 상태 + 핵심 제약
  01-design/
    design.md          ← XL인 경우 PRD 포함
  02-decisions/
    reviews/
      RDR-*.md
    ADR-*.md
  03-tasks/
    TASK-001.md  ✅ 완료
    TASK-002.md  ← 다음 세션에서 S/M으로 수행
    TASK-003.md
```

- `00-index.md`에 "다음 태스크" 정보가 기재된다.
- 다음 세션에서 papillon 호출 시 이 index를 읽고 태스크를 제안한다.

---

## 9. 네임스페이스 및 패키징 구조

papillon이 네임스페이스 최상위이며, 하위 스킬은 papillon 네임스페이스 안에 설치된다.

**설치 구조:**

```
~/.claude/commands/papillon/
  papillon.md       ← 오케스트레이터 (/papillon)
  wtth.md           ← 리뷰 엔진 (/papillon:wtth)
```

**호출 방식:**

| 호출 | 동작 |
|---|---|
| `/papillon` | 파이프라인 오케스트레이터 실행 (인터뷰 → 체급 → Phase 자동 전환) |
| `/papillon:wtth` | 리뷰 엔진 단독 실행 |

**설계 원칙:**
- 하위 스킬은 단독 실행 가능해야 한다. papillon 오케스트레이터에 의존하지 않는다.
- papillon은 하위 스킬을 호출하여 파이프라인을 구성한다.
- 향후 하위 스킬이 추가될 수 있다.

---

## References
- PRD: [01-prd.md](./01-prd.md)
