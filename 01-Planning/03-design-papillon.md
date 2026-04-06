# 03-design-papillon: papillon 스킬 설계서

## Context
- **Parent:** [00-index.md](../00-index.md)
- **Related:** [01-prd.md](./01-prd.md), [02-common-spec.md](./02-common-spec.md), [04-design-wtth/00-core.md](./04-design-wtth/00-core.md), [05-design-inquisition.md](./05-design-inquisition.md)
- **Status:**
  - Work: Draft
  - Review: None

---

## Input / Dependency
- PRD: [01-prd.md](./01-prd.md)
- 공통 규격: [02-common-spec.md](./02-common-spec.md)
- wtth v2 설계: [04-design-wtth/00-core.md](./04-design-wtth/00-core.md)
- 런북 템플릿: [50-runbook-template.md](./50-runbook-template.md)
- 문서 작성 가이드: `~/Work/common-prompt/documentation/`

---

## 1. 전체 파이프라인

```
사람: /papillon 호출
  │
  ▼
[진입] 컨텍스트 스캔
  │  CWD에서 산출물 탐색 (00-index.md, docs/decisions/, 00-interview/)
  │  ★ 사람에게 스캔 결과 제시 + 진입점 제안 → 사람이 승인 또는 오버라이드
  │
  ▼
[Phase 1] 인터뷰 + 체급 판정 + 초안
  │  Step 1: 구조화 인터뷰 (Opus)
  │    - Opus가 요구사항 분석 → 인터뷰 필요 여부 제안 → ★ 사람 결정
  │    - 인터뷰 시: 문맥 단위로 00-interview/ 하위에 파일 분리 기록
  │    - ★ 사람에게 확인 질문 (함의/제약 감지, 보정 질문, 미결 환기)
  │    + 체급 판정: 인터뷰 맥락 기반 종합 판단 → S / M / L / XL → ★ 사람 승인
  │  Step 2: 체급별 분기
  │    - S → Phase 4(구현)로 직행
  │    - M → Step 3(설계 초안) → Phase 1.5 이후 계속
  │    - L → 조감도 + 태스크 목록 생성 → 파일 저장 → 파이프라인 종료
  │    - XL → PRD 작성 → Phase 2~3(PRD 리뷰 모드) → Phase 분할 → 파일 저장 → 파이프라인 종료
  │  Step 3: Draft 생성 (M 체급, Sonnet)
  │    - 인터뷰 결과 + doc-standard 기준으로 설계 초안 작성
  │    - 핵심 제약은 index에 명시적으로 기재
  │
  ▼ (자동 전환, M 체급)
[Phase 1.5] 태스크 크기 점검 (1차)
  │  초안 기반으로 판단: 문서 길이 A4 2장 초과? API 수 3개 초과?
  │  초과 시 → 분할 제안 ★ 사람: 승인 후 분할 / 그대로 진행
  │
  ▼ (자동 전환)
[Phase 2] 설계 리뷰
  │  wtth 호출 (설계 전문가 풀)
  │  리뷰 1라운드 후 wtth이 결과 분석하여 태스크 크기 경고 가능 (2차 안전망)
  │  ★ 사람: finding별 수용/기각
  │  → RDR 자동 생성
  │  → ADR 승격 대상 있으면:
  │     [Phase 2.1] ADR 작성 → wtth 호출 → ★ 사람: 의사결정 → RDR 생성
  │       → 승인: ADR 확정
  │       → 방향 기각: ADR 재작성 → Phase 2.1 재진입
  │       → 불필요 판정: ADR 드롭, 구현에서 처리
  │
  ▼ (자동 전환)
[Phase 3] 종결 판단
  │  오케스트레이터가 미해결 P0/P1 기준으로 종결 가능 여부 제안
  │  ★ 사람: 승인 → Phase 4 / 거부 → Phase 2 반복
  │
  ▼ (자동 전환)
[Phase 4] 구현
  │  확정된 설계서 기반 코딩 수행
  │  4-A. 개발 작업: 코드 작성
  │  4-B. 인프라/수행 작업: 런북 생성 → wtth(운영 절차 리뷰) → ★ 사람 의사결정 → 실행 → 검증
  │
  ▼ (자동 전환, 4-A인 경우)
[Phase 5] 코드 리뷰
  │  wtth 호출 (코드 전문가 풀: CODE + TEST)
  │  AI 전문가가 finding 도출 → 오케스트레이터가 diff 생성
  │  ★ 사람: AS-IS / TO-BE diff 전문을 확인하고 승인/반려
  │  → 반려 시 사유와 함께 재수정 싸이클
  │  → 오케스트레이터 종결 제안 또는 사람 종결 ← 미종결 시 반복
  │
  ▼ (자동 전환)
[Phase 6] 커밋 + PR + 완료
  │  커밋 (/commit-plugin:commit)
  │  PR 생성 여부: 프로젝트 CLAUDE.md의 Git.Platform 값에 따라 분기
  │  ★ 사람: "다음 태스크" → Phase 1 / "종료"

※ L/XL은 Phase 1에서 구조만 만들고 종료.
   각 하위 태스크는 별도 세션에서 S/M으로 이 파이프라인에 재진입.
```

**★ = 사람이 개입하는 유일한 지점**

---

## 2. 파이프라인 공통 규칙

### 2.1. 작업 중 체급 변경(승격)

파이프라인 진행 중 사람 또는 AI가 체급이 맞지 않다고 판단하면 승격을 제안/요청할 수 있다. 사람이 **승인하면 승격 동작을 수행**하고, **거부하면 현재 체급으로 계속** 진행한다.

| 승격 | 트리거 | 승인 시 | 거부 시 |
|---|---|---|---|
| S → M | 구현 중 예상치 못한 설계 판단이 필요해짐 | Phase 1 Step 3(설계 초안)로 이동 | S로 계속 구현 |
| M → L | 크기 점검 또는 리뷰에서 태스크 분할이 필요해짐 | 조감도 + 태스크 목록 생성 → 파이프라인 종료 | M으로 계속 진행 |

---

## 3. Phase별 상세

### 3.0. 파이프라인 진입: 컨텍스트 스캔

papillon 호출 시 CWD에서 기존 산출물을 스캔하여 진입점을 결정한다.

| 발견된 산출물 | 추론 | 진입점 |
|---|---|---|
| `00-index.md` + 미완료 태스크 | L/XL 프로젝트 진행 중 | index 기반 다음 태스크 제안 |
| `docs/decisions/` (RDR/ADR) 존재, index 없음 | 이전 S/M 작업 이력 있음 | 마지막 RDR 요약 + "이어서 할 건지, 새 작업인지" 확인 |
| `00-interview/` 디렉토리 존재 | 인터뷰 진행 중 세션 끊김 | 미결 문맥 파일 기반 인터뷰 재개 제안 |
| 아무것도 없음 | 이 저장소에서 첫 사용 | Phase 1(인터뷰)부터 시작 |

- 스캔 결과를 사람에게 제시하고 진입점을 **제안**한다. 사람이 승인하면 해당 지점으로 진입하고, 오버라이드하면 사람이 지정한 지점으로 진입한다.
- 이 스캔은 papillon 오케스트레이터의 진입 로직이다. wtth의 "이전 결정 스캔"(Core §3.3)과는 역할이 다르다 — Core §3.3은 리뷰 시작 시 기결정 사항을 전문가에게 전달하는 것이고, 여기는 파이프라인 자체의 진입점을 결정하는 것이다.

### 3.1. Phase 1: 인터뷰 + 체급 판정 + 초안

#### Step 1: 요구사항 추출 — inquisition 호출

inquisition 스킬(`/papillon:inquisition`)을 호출한다. 상세 프로세스는 [05-design-inquisition.md](./05-design-inquisition.md) 참조.

**반환값:**
- `00-interview/` 디렉토리: 문맥 파일(관심사별, 상태: Open/Settled/Deferred) + `00-summary.md`(전체 요약 + 체급 판정 결과)

**파이프라인 내 동작:**
- 오케스트레이터는 `00-summary.md`의 체급 판정 결과를 읽고 Step 2(체급별 분기)로 진행한다.
- 체급이 기재되어 있지 않으면 inquisition이 비정상 종료된 것이다. 오케스트레이터는 사람에게 상황을 알리고 inquisition 재실행 또는 수동 체급 지정을 요청한다.

#### Step 2: 체급별 분기 (Opus)

| 체급 | 동작 |
|---|---|
| **S** | 설계 생략 → 바로 Phase 4(구현) 진입 |
| **M** | 설계 초안 생성 → Phase 1.5(크기 점검) → Phase 2~6 수행 |
| **L** | 조감도(00-index.md) + 태스크 목록 생성 → **파일로 저장하고 종료**. 각 태스크는 별도 세션에서 S/M으로 수행 |
| **XL** | PRD 작성 → Phase 2(wtth PRD 리뷰 모드) → Phase 3(종결 판단) → Phase 분할 + 태스크 목록 생성 → **파일로 저장하고 종료**. 각 Phase 내 태스크는 별도 세션에서 L/M/S로 수행 |

**L/XL의 핵심 원칙:**
- L/XL은 파이프라인의 실행 단위가 아니다. **실행 결과물의 저장소이자 추적 구조**이다.
- 파이프라인이 실제로 도는 단위는 **항상 S/M**이다.
- L/XL의 산출물은 프로젝트 구조(index + 태스크 목록 + RDR/ADR + 작업 요약 카드)로 남는다.
- 다음 세션에서 papillon 호출 시 index를 읽고 "다음 태스크"를 제안한다.

L/XL 산출물 구조: [02-common-spec.md 섹션 8](./02-common-spec.md) 참조.

#### Step 3: Draft 생성 (M 체급, Sonnet)

1. 인터뷰 결과를 기반으로 doc-standard(01-doc-standard.md) 기준으로 설계 초안을 작성한다.
2. 인터뷰에서 확인된 **핵심 제약은 00-index.md에 명시적으로 기재**한다.
3. 초안을 사람에게 보여주고 Phase 1.5로 자동 전환한다.

### 3.2. Phase 1.5: 태스크 크기 점검 (1차, M 체급)

초안이 나온 직후, 리뷰 진입 전에 **실제 산출물 기반으로** 크기를 점검한다.

**Step 1: 단순 판별 (Haiku)**

| 기준 | 판단 방법 |
|---|---|
| 설계 문서 A4 2장 초과 | 초안 문서 길이 측정 |
| 관련 API 3개 초과 | 초안에서 API/엔드포인트 수 확인 |

**Step 2: 분할 제안 (Sonnet, 기준 초과 시만)**

- Haiku가 기준 초과를 판별하면 Sonnet이 분할안을 제안한다.
- ★ 사람이 승인하면 분할 후 Phase 2로, 거부하면 그대로 Phase 2로 진행.
- 리뷰 1라운드 후 wtth이 건수/심각도/패턴을 분석하여 태스크 크기 경고를 제안할 수 있다 (2차 안전망).

### 3.3. Phase 2: 설계 리뷰

1. wtth을 **설계 리뷰 모드**로 호출한다.
2. 기존 wtth 프로세스 그대로 수행 (전문가 제안 → 승인 → 병렬 실행 → 항목별 의사결정).
3. 리뷰 종료 시:
   - RDR 자동 생성 → `docs/decisions/reviews/`에 저장
   - finding 전부 처리 완료 후, P0/P1 수용 건 중 설계 변경 수반 항목 → ADR 승격 대상을 **일괄 제안**
4. ADR 승격 시 → Phase 2.1로 진입:
   - AI가 ADR 초안 자동 생성 → ★ 사람이 확인/수정 → wtth로 ADR 리뷰 (finding별 수용/기각 + RDR 생성) → ★ 사람이 ADR 자체에 대해 판단
   - **ADR 판단 분기 (wtth 리뷰 종료 후):**
     - 승인 → ADR 확정, 다음 ADR 승격 건 처리 또는 Phase 3로
     - 방향 기각 → ADR을 다른 방향으로 재작성 → Phase 2.1 재진입 (RDR에 기각 사유 기록)
     - ADR 자체 불필요 판정 → ADR 드롭, finding 수용은 유지하고 구현에서 처리 (RDR에 드롭 사유 기록)

### 3.4. Phase 3: 종결 판단

1. 오케스트레이터가 현재 상태를 분석한다:
   - 미해결 P0: 0건인가
   - 미해결 P1: 0건인가
   - 리뷰 대상 문서 Status: Work: Completed 가능한가
2. 조건 충족 시 종결을 제안한다.
3. 사람이 승인하면 설계 확정 (Status: Completed + Approved).
4. 사람이 거부하면 사유를 받고 Phase 2로 복귀.

### 3.5. Phase 4: 구현

오케스트레이터가 태스크 내용을 분석하여 4-A/4-B를 판별한다:
- **4-A** — 산출물이 코드인 경우 (기능 구현, 버그 수정, 리팩토링 등)
- **4-B** — 산출물이 실행 절차인 경우 (인프라 조작, 데이터 마이그레이션, 환경 설정 등)

판별 결과를 사람에게 제시하고 확인받는다.

**4-A. 개발 작업 (코드)**
1. 확정된 설계서의 태스크 목록을 순서대로 구현한다.
2. Phase 5로 자동 전환.

**4-B. 인프라/수행 작업**
1. 태스크 내용을 기반으로 **런북(절차서)을 생성**한다. 런북은 [50-runbook-template.md](./50-runbook-template.md)의 형식을 따른다.
2. wtth을 **운영 절차 리뷰 모드**로 호출한다.
3. ★ 사람: finding별 수용/기각.
4. 절차서 확정 후, 각 단계를 순서대로 실행한다.
5. 각 단계의 검증 커맨드를 수행하여 성공 여부를 판단한다.
6. 전체 완료 확인 후:
   - 커밋 대상이 있는 경우 (런북, 설정 파일, RDR 등) → Phase 6으로 전환
   - 커밋 대상이 없는 경우 → RDR 생성 후 파이프라인 종료

### 3.6. Phase 5: 코드 리뷰

wtth을 **코드 리뷰 모드**로 호출한다. 리뷰 대상은 `git diff` 기반 변경사항.
상세 프로세스(finding 도출 → diff 묶음 → 순차 제시 → 승인/반려/직접수정/기각)는 [wtth 코어 §2.2](./04-design-wtth/00-core.md) 참조.
종결 시 RDR 생성 → Phase 6.

### 3.7. Phase 6: 커밋 + PR + 완료

1. 커밋을 수행한다 (`/commit-plugin:commit` 사용, Human-Time/Ai-Driven-Time 확인).
2. **PR 생성 여부를 프로젝트 CLAUDE.md의 `Git.Platform` 값으로 결정**한다:

   ```markdown
   ## Git
   - **Platform**: github  # github | bitbucket | none
   ```

   | Platform 값 | 동작 |
   |---|---|
   | `github` | `gh pr create` — RDR/ADR/리뷰결과를 PR description에 자동 포함 |
   | `bitbucket` | Bitbucket MCP 또는 수동 안내 — 동일하게 PR description 생성 |
   | `none` / 미설정 | 커밋 + PR 본문 출력 후 종료 |

3. PR 생성 시 본문에 포함되는 내용:
   - 설계 RDR 요약
   - 코드 리뷰 RDR 요약
   - 관련 ADR 목록
   - 변경 파일 및 구현 요약
4. 사람에게 다음 행동을 묻는다:
   - "다음 태스크" → Phase 1로 복귀
   - "종료" → 파이프라인 종료

---

## 3. wtth 호출 인터페이스

papillon가 wtth을 호출할 때 전달하는 정보:

| 파라미터 | 설명 |
|---|---|
| 리뷰 대상 | 파일 경로, diff, PR URL 등 |
| 리뷰 모드 | PRD / 설계 / ADR / 운영 절차 / 코드 (Phase에 따라 자동 결정) |
| 기존 RDR/ADR 경로 | 이전 결정 스캔용 |
| 코드베이스 컨텍스트 | 프로젝트 구조, 관련 파일 등 |

wtth의 상세 동작은 [04-design-wtth/00-core.md](./04-design-wtth/00-core.md) 참조.

---

## 4. 파일 산출물

파이프라인 실행 시 생성되는 RDR/ADR의 포맷 및 디렉토리 구조: [02-common-spec.md 섹션 2~4](./02-common-spec.md) 참조.

---

## Output / Results

`papillon.md` — 파이프라인 오케스트레이터 스킬 (`~/.claude/commands/papillon/`에 설치)

---

## References
- PRD: [01-prd.md](./01-prd.md)
- 공통 규격: [02-common-spec.md](./02-common-spec.md)
- wtth v2 설계: [04-design-wtth/00-core.md](./04-design-wtth/00-core.md)
- 런북 템플릿: [50-runbook-template.md](./50-runbook-template.md)
- 문서 작성 가이드: `~/Work/common-prompt/documentation/00-index.md`
