# 01-prd: AI-Driven Work Pipeline PRD

## Context
- **Parent:** [00-index.md](../00-index.md)
- **Related:** [00-problem-and-proposals.md](../00-problem-and-proposals.md), [02-design.md](./02-design.md)
- **Status:**
  - Work: Completed
  - Review: Approved (Human)

---

## Input / Dependency
- 기존 wtth 스킬: `~/Work/work-automation/.claude/commands/wtth.md`
- 문서 작성 가이드: `~/Work/common-prompt/documentation/`
- 개발 가이드: `~/Work/common-prompt/DEVELOPMENT_GUIDE.md`
- 2026-04-02 Sonnet 대화 기반 문제 분석: [00-problem-and-proposals.md](../00-problem-and-proposals.md)

---

## 1. 배경

### 1.1. 현재 상황

현재 AI 기반 개발 작업에서 두 가지 도구를 사용하고 있다.

- **wtth**: 멀티에이전트 리뷰 시스템. 5명의 도메인 전문가(BE/FE/SRE/SEC/PO)를 독립 에이전트로 병렬 실행하고, 오케스트레이터(Agent S)가 결과를 수집·병합하여 사용자와 항목별 의사결정을 진행한다.
- **수동 파이프라인**: 사람이 각 단계(설계 초안 → 리뷰 → 확정 → 개발 → 코드 리뷰)를 직접 트리거하고 전환한다.

### 1.2. 문제

| # | 문제 | 영향 |
|---|---|---|
| P1 | **결정 망각** — 리뷰 세션 후 수용/기각 결정이 휘발됨. 다음 세션에서 동일 지적 반복 | 리뷰 라운드 증가, 사용자 피로 |
| P2 | **태스크 과대** — 태스크가 크면 전문가 5명 × 8라운드 × 30건/라운드 = ~240건 처리 | 리뷰 병목, 결과물 품질 저하 |
| P3 | **수렴 부재** — 라운드별 역할 구분 없이 매번 전체 발산 | 후반 라운드에서 P3급 지적이 계속 추가됨 |
| P4 | **수동 전환** — 설계→리뷰→개발→코드리뷰 각 단계를 사람이 직접 호출 | 사람이 오케스트레이션에 시간 소모 |
| P5 | **코드 리뷰 미지원** — wtth이 설계 문서 리뷰에 특화. 코드 diff 리뷰 시 전문가 관점이 다름 | 코드 리뷰는 별도 수단 필요 |
| P6 | **PRD 리뷰 미지원** — 대규모 작업의 PRD도 리뷰가 필요하나 현재 wtth은 설계/코드만 대상 | PRD 품질을 사람이 직접 한 줄씩 검증해야 함 |
| P7 | **요구사항 구체화 부재** — 사람이 정보를 충분히 주지 않으면 AI가 함의를 놓침 | 암시적 제약 누락 → 치명적 버그 (V1/V2 사례) |

---

## 2. 목표

### 2.1. 핵심 목표

**파이프라인은 자동으로 돌고, 사람은 리뷰 의사결정만 한다.**

### 2.2. 세부 목표

| # | 목표 | 측정 기준 |
|---|---|---|
| G1 | 리뷰 결정이 영구 기록되어 다음 세션에서 참조 가능 | RDR/ADR 파일이 자동 생성되고, 다음 리뷰에서 기결정 사항이 제외됨 |
| G2 | 리뷰가 3라운드 이내에 수렴 | 태스크 크기 기준 준수 시 4라운드 이상 진행되는 비율 < 20% |
| G3 | 사람이 단계 전환을 직접 트리거하지 않음 | 파이프라인 시작 후 사람이 하는 행위는 리뷰 의사결정과 종결 승인뿐 |
| G4 | PRD/설계/ADR/운영절차/코드 리뷰를 동일 시스템으로 처리 | wtth 하나로 5종 리뷰 수행. 각 모드별 전문가 풀과 의사결정 방식은 다름 |
| G5 | 요구사항 단계에서 암시적 제약을 명시적으로 끌어올림 | 구조화 인터뷰를 통해 핵심 제약이 index에 명시 기재됨 |
| G6 | 작업 체급에 따라 적절한 프로세스 진입 | S/M은 한 세션에 완료, L/XL은 구조만 만들고 종료 |

### 2.3. 비목표 (명시적 제외)

- Jira 연동 (cyberpink 영역, 이 프로젝트에서 다루지 않음)
- CI/CD 파이프라인 연동
- 완전 자동 리뷰 (사람 의사결정 배제) — 사람이 결정권을 가진다
- 기존 cyberpink 스킬과의 의존성

---

## 3. 사용자

- **주 사용자**: 본인 (시니어 엔지니어, AI-native 개발 워크플로우 운영)
- **향후 확장**: 팀 내 엔지니어
- **설치 위치**: 글로벌 네임스페이스 (`~/.claude/commands/papillon/`)

---

## 4. 산출물

| 산출물 | 파일명 | 역할 |
|---|---|---|
| **papillon** | `papillon.md` | 파이프라��� 오케스트레이터. 인터�� → 체급 판정 → Phase 자동 전환. 사람은 의사결정만 |
| **wtth v2** | `papillon:wtth.md` | 멀티에이��트 리뷰 엔진. PRD/설계/코드 5모드 지원. RDR/ADR 생성. 수렴 메커니즘 내��� |

- `papillon`이 네임스페이스 최상위. `~/.claude/commands/papillon/` 하위에 설치
- 호출: `/papillon` (오케스트레이터), `/papillon:wtth` (리뷰 단독)
- wtth은 papillon 없이 단독 실행 가능
- 두 스킬 모두 cyberpink에 의존하지 않음

---

## 5. 제약 조건

| # | 제약 | 이유 |
|---|---|---|
| R1 | cyberpink 스킬에 대한 의존성 없음 | cyberpink는 별도 팀의 실험적 도구. 참조는 가능 |
| R2 | 커밋/푸시는 `/commit-plugin:commit`, `/push-plugin:push` 사용 | 글로벌 CLAUDE.md 규칙 |
| R3 | 문서 생성 시 doc-standard 준수 | 글로벌 CLAUDE.md 규칙 |
| R4 | 네임스페이스 글로벌 설치 (`~/.claude/commands/papillon/`) | 특정 프로젝트에 종속되지 않아야 함. papillon이 네임스페이스 최상위 |
| R5 | wtth 단독 실행 가능 유지 | `/papillon:wtth`로 단독 호출 가능해야 함 |
| R6 | PR 플랫폼은 프로젝트 CLAUDE.md에서 선언 | `Git.Platform` 값으로 github/bitbucket/none 분기. 자동 감지하지 않음 |

---

## Output / Results

1. `papillon.md` — 파이프라인 오케스트레이터 스킬
2. `papillon:wtth.md` — 개선된 리뷰 엔진 스킬
3. 설계서: [02-design.md](./02-design.md)
4. 본 PRD의 Review: Approved (Human) 달성

---

## References
- 기존 wtth: `~/Work/work-automation/.claude/commands/wtth.md`
- 문서 작성 가이드: `~/Work/common-prompt/documentation/00-index.md`
- 개발 가이드: `~/Work/common-prompt/DEVELOPMENT_GUIDE.md`
- cyberpink task-auto (참조): `~/.claude/plugins/cache/mzc-pops-marketplace/cyberpink/1.2.1.5/commands/task-auto.md`
