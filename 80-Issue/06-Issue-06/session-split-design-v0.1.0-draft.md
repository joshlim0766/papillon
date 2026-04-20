# Shackled TDD 분할 메커니즘 설계 v0.1.0-draft — 시간축 + 공간축

## 문서 성격

Issue-06 #4 "shackled tdd_mode 소비 로직" 의 신규 요건 초안. [`tracing-2f-2026-04-20.md`](tracing-2f-2026-04-20.md) 의 관찰 1·2 를 설계로 옮긴다. 2f 완료 후 실측으로 검증, v0.2.0 시점에 shackled 설계서 본편(`01-Planning/06-shackled/02-design/`)으로 이관 여부 결정.

**스코프 — 2차원**:
- **시간 축**: `shackled` 스킬의 `tdd` 모드 실행 시, RED / GREEN / REFACTOR 단계를 별개 세션으로 분할.
- **공간 축**: 지시서(context_path)와 태스크(`.shackled-state.json` tasks[]) 의 크기 단위 분할. 두 레이어(L1 지시서 / L2 태스크 내부) 존재.

두 축은 **독립적**이며 실제 실행에서 **교차**한다. 한 축만으로는 품질 저하 완전 해소 불가 (2f 실측이 증거).

**비 스코프**: `normal` 모드는 변경 없음. 지시서 작성 규격(Issue-06 #1)과 별도 축.

---

## 1. 문제 정의

### 1.1. 현상 — 시간 축

단일 세션에서 RED → GREEN → REFACTOR 연속 수행 시 모델 품질 저하. 실측 근거:
- 2f shackled 진행 중 Sonnet 관찰 — 사이클 누적될수록 판단 품질 저하.
- Claude Web Sonnet 독립 검증 — 동일 분석 도달.

### 1.2. 원리 — 시간 축

TDD 3단계는 각각 다른 **멘탈 모드**이며 각 단계의 핵심 신호가 상충:

| 단계 | 핵심 신호 | 금기 |
|---|---|---|
| RED | 실패가 기대값. "아직 없음" 의도적 기록 | 구현 먼저 쓰지 말 것 |
| GREEN | 성공이 기대값. 최소 변경 | 구조 최적화 금지 |
| REFACTOR | 녹색 유지하며 구조 개선 | 외부 관찰 변경 금지 |

단일 세션에 3 단계를 두면:
- RED 작성 시의 "실패 기대" 가 GREEN 중에 잔존 → 과잉 방어 구현 유도.
- GREEN 의 "최소 변경" 과 REFACTOR 의 "구조 개선" 충돌 → 타이밍 혼선.
- 실패 케이스 주변 노이즈가 compaction 시 비교 대상으로 끌려 들어와 → 잘못된 패턴 학습.

### 1.3. 현상 — 공간 축

단일 지시서 / 단일 태스크의 구현 양이 커서 context 폭발. 실측 근거:
- 2e 지시서 636줄, 2f 지시서 765줄 — "단일 관심사" 원칙으로 퉁쳤으나 실제로는 과도.
- 2f 의 경우 Opus 가 `.shackled-state.json` 의 `tasks[]` 을 3개로 자동 분할 (아래 §1.4):
  - TASK-2F-01: DedupService + DltPublisher + DltErrorReason (인프라 선제, completed, 76/76 pass)
  - TASK-2F-02: StatsBatchPipelineImpl 조립 + RED 1~12 GREEN (메인 조립, **진행 중**, **여기서 Full GC**)
  - TASK-2F-03: REFACTOR — Micrometer + MDC + yml (운영 보강, pending, mode=normal)
- **분할했음에도 가장 큰 태스크(2F-02) 가 단일 세션에 맞지 않음**. L1 분할만으로 부족, L2 분할 필요 신호.

### 1.4. Opus 의 자동 분할 패턴 (관찰)

주인님이 2f 진입 시 Opus 에게 분할 맡긴 결과 도출된 패턴:

| 태스크 | 성격 | mode | 특징 |
|---|---|---|---|
| 인프라 선제 (01) | 보조 자산 신규·확장 (TDD 포함) | tdd | 후속 태스크 미완성 상태에서 GREEN — WORKAROUND 허용 필요 |
| 메인 조립 (02) | 설계의 핵심 — 전체 RED 수 대부분 포함 | tdd | 가장 큼. L2 분할 후보 |
| 운영 보강 (03) | Metrics / MDC / yml 등 관측·환경 | normal | TDD 아님 — REFACTOR/개선 성격 |

**해석**: Opus 가 "관심사 분해" + "TDD 적용 여부 분리" 를 동시 수행. 운영 자산은 TDD 부적합으로 판단하여 mode=normal 로 전환.

**부작용**: 인프라 선제(01) 가 독립 GREEN 하려면 메인 조립(02) 미완성을 가정한 임시 코드 필요 (`StatsSendResultListener WORKAROUND 임시 전환 포함` 명시). 이는 의존 분할의 비용.

### 1.5. auto-compaction 의 한계

모델 자체 압축은:
- **타이밍**: context 한계 근처 발동 = 이미 오염된 후.
- **품질**: 압축 기준 가변. 실패 케이스 잔존 가능.
- **재현성**: 런마다 결과 다름.
- **디버깅**: 압축 결정 추적 난감.

즉 응급 처치이며 구원이 아님. **오케스트레이터 명시 분할** 이 시간·공간 양 축 모두에서 필요.

---

## 2. 시간축 설계 결정

### 2.1. 분할 단위 — 하이브리드 C→A

4가지 후보 비교:

| 옵션 | 단위 | 세션 수 (RED N개) | 비고 |
|---|---|---|---|
| A | RED 전부 / GREEN 전부 / REFACTOR 전부 | 3 | 단순. GREEN 시작 시 N개 실패 상태 한 번에 노출 — 신호 오염 |
| B | RED 개별 / GREEN 개별 / REFACTOR 개별 | 3N | 완벽 격리. 세션 오버헤드 과다 |
| C | RED 1 / GREEN+REFACTOR 1 반복 | 2N | TDD 원순환 충실. 2f 12 RED → 24 세션, 부담 |
| D | RED 1 / GREEN 1 반복 → 마지막 REFACTOR 1회 | N+1 | REFACTOR 일괄. 마지막 세션이 다시 커짐 |

**채택안**: **하이브리드 C→A**.

**규칙**:
1. 기본은 **C** (RED 1 → GREEN+REFACTOR 1 반복).
2. **의존이 독립적인 RED 2~3개는 한 세션에서 RED 작성, 이어지는 세션에서 GREEN+REFACTOR 순차**.
3. 그룹 크기는 지시서의 RED 의존 그래프 분석 결과 (단순 독립 RED 만 그룹화).

**2f 예시 (RED 12개 가정)**:
- 세션 1: RED 1~3 (parse + filter 독립)
- 세션 2: GREEN+REFACTOR 1~3
- 세션 3: RED 4~6 (lookup + map)
- 세션 4: GREEN+REFACTOR 4~6
- ...
- 총 ~8 세션 (12 RED / 3 그룹 × 2).

### 2.2. 상태 파일 확장

기존 `.shackled-state.json` 의 `tasks[*]` 에 `phase` 필드 추가:

```json
{
  "tasks": [
    {
      "id": "TASK-2F-01",
      "mode": "tdd",
      "phase": "RED_DRAFT",          // 신규
      "phase_scope": ["RED-1", "RED-2", "RED-3"],  // 신규 — 현 세션 범위
      ...
    }
  ]
}
```

**phase 허용값**:
- `NOT_STARTED`
- `RED_DRAFT` — RED 작성 중
- `RED_COMPLETE` — RED 작성 완료, GREEN 대기 (세션 분할 포인트)
- `GREEN_REFACTOR` — GREEN + REFACTOR 진행 중
- `GROUP_COMPLETE` — 그룹의 RED/GREEN/REFACTOR 전체 완료, 다음 그룹 대기
- `TASK_COMPLETE` — 태스크의 모든 그룹 완료

**phase_scope**: 현 세션이 다루는 RED 번호 범위. 세션 시작 시 오케스트레이터가 주입, 종료 시 갱신.

### 2.3. 핸드오프 노트 규격

세션 종료 시 오케스트레이터가 자동 생성. 다음 세션 진입 시 첫 입력으로 제공. 형식:

```markdown
## 현재 상태: {phase}
- 완료된 단계: {phase_scope} 중 {완료된 RED 번호}
- 다음 목표: {다음 세션이 수행할 작업}
- 건드리지 말 것: {다음 그룹의 RED 번호들}
- 관련 파일: {현 세션에서 생성/수정된 파일 목록}
- 의존 전제: {이번 세션에서 확인된 지시서 공백·단서조항 등, 있을 경우}
```

**최소 원칙**: 핸드오프 노트는 위 6 항목만. 이전 세션의 사고 과정·고려한 대안 등은 포함 금지 (신호 오염 방지).

### 2.4. 오케스트레이터 동작

```
shackled TDD 모드 진입
  ↓
지시서의 RED 의존 그래프 분석 → 그룹화 (2~3개 독립 RED)
  ↓
그룹 1 진입
  ↓ (세션 시작)
  RED 그룹 작성 → phase=RED_DRAFT
  ↓
  RED 전수 실패 확인 → phase=RED_COMPLETE → 핸드오프 노트 생성
  ↓ (세션 종료 — /clear 또는 실제 세션 전환)
  ↓ (세션 시작)
  GREEN + REFACTOR 순차 진행 → phase=GREEN_REFACTOR
  ↓
  그룹 전수 GREEN + REFACTOR 완료 → phase=GROUP_COMPLETE
  ↓
그룹 N 반복
  ↓
태스크 완료 → phase=TASK_COMPLETE
```

**세션 분할 트리거**:
- 그룹 내 RED 작성 완료 (phase=RED_COMPLETE 전환 시)
- 그룹의 GREEN+REFACTOR 완료 (phase=GROUP_COMPLETE 전환 시)

**auto-compaction 감지**:
- 모델이 compaction 을 시도하는 신호 감지 시 즉시 세션 분할 강제.
- compaction 이 이미 발생한 후에는 다음 분할까지 품질 저하 허용 (되돌릴 수 없음).

### 2.5. 세션 간 전달 컨텐츠 (필수/금지)

**필수 (세션 시작 시 제공)**:
1. 지시서 전문 (변경 없음).
2. 상태 파일 (`.shackled-state.json`) — `phase` / `phase_scope` / 완료된 그룹 요약.
3. 핸드오프 노트 — §2.3 규격.
4. 관련 파일의 현재 내용 (오케스트레이터가 파일 시스템에서 읽어 첨부).

**금지 (세션 간 전달 금지)**:
- 이전 세션의 채팅 이력 전체.
- 고려했던 대안·사고 과정.
- 실패한 구현 시도 (GREEN 이전의 실패 코드는 커밋 안 된 상태라 자연 소실).
- 이전 세션의 auto-compaction 요약 (오염 소스).

---

## 3. 공간축 설계 결정

### 3.1. 2-레이어 분할 구조

| 레이어 | 단위 | 누가 결정 | 근거 |
|---|---|---|---|
| **L1** | 지시서 → 태스크(`tasks[]`) | **shackled 오케스트레이터 (Opus)** 가 지시서 분석하여 자동 분할 | 2f 사례: 1 지시서 → 3 태스크 (인프라 선제 / 메인 조립 / 운영 보강) |
| **L2** | 태스크 내부 → RED 그룹 (시간축 §2.1과 동일) | 동일 오케스트레이터가 RED 의존 그래프 분석 | 2f TASK-2F-02 에서 L1 만으론 부족 → L2 필요 |

두 레이어는 **독립**. L1 만으로 해결 가능한 경우는 S/M 체급, L1+L2 조합이 필요한 경우는 L 체급 이상.

### 3.2. L1 분할 휴리스틱 — "관심사 + TDD 적합성" 2축

Opus 2f 분할 패턴 (§1.4) 을 휴리스틱으로 박제:

**분할 축 1 — 관심사 분해**:
- 인프라 선제 (보조 자산 신규·확장)
- 메인 조립 (설계 핵심, RED 대부분)
- 운영 보강 (관측·환경·프로파일)

**분할 축 2 — TDD 적합성**:
- `mode: "tdd"` — 행동 명세가 가능하고 테스트 우선이 의미 있는 범위.
- `mode: "normal"` — 관측·환경·설정 등 "테스트가 아닌 개선" 성격. REFACTOR 에 해당.

**휴리스틱 규칙**:
1. 지시서 줄 수 > **500** 이면 L1 분할 권고 (2e 636 / 2f 765 가 경계 근처 — 실측 후 임계 조정).
2. 지시서 내에 "Metrics / Monitoring / 관측 / 프로파일" 성격 섹션이 **15% 이상** 분량 차지하면 `mode=normal` 태스크로 분리.
3. 인프라 선제가 메인 조립 없이도 독립 GREEN 가능한지 확인. 불가능하면 태스크 경계 재조정 (또는 WORKAROUND 허용 명시).

### 3.3. L1 분할 비용 — WORKAROUND 허용

2f TASK-2F-01 이 `StatsSendResultListener WORKAROUND 임시 전환 포함` 으로 GREEN 도달한 사례:

- **원인**: 인프라 선제 태스크가 독립 GREEN 하려면 메인 조립 태스크 미완성을 가정한 임시 구현 필요.
- **허용 조건**: WORKAROUND 를 **상태 파일 `result_summary` 에 명시 박제** + 메인 태스크 완료 시 제거 계약.
- **부작용**: 메인 태스크 완료 후 WORKAROUND 제거 확인 단계 필요 (의존 그래프 역순 검증).

### 3.4. L2 분할 — 태스크 내부 RED 그룹

태스크 내부 RED 가 N 개이고 N 이 일정 임계 초과 시 §2.1 (시간축 하이브리드 C→A) 적용.

**L2 분할 트리거**:
- 태스크 내 RED 수 > **6** 이면 L2 분할 권고 (2f TASK-2F-02 가 RED 12 개로 Full GC — 경계 근처).
- 태스크 내 의존 DAG 이 2개 이상 독립 체인으로 분해 가능하면 체인별 그룹화.

### 3.5. 상태 파일 확장 (공간축용)

`.shackled-state.json` 의 `tasks[*]` 에 L1 분할 메타 추가:

```json
{
  "tasks": [
    {
      "id": "TASK-2F-01",
      "mode": "tdd",
      "concern": "infra_precursor",        // 신규 — 관심사 축
      "size_estimate_lines": 180,          // 신규 — 구현 예상 분량
      "l2_required": false,                // 신규 — L2 분할 필요 판정
      "workaround_notes": ["StatsSendResultListener WORKAROUND 임시 전환"],  // 신규
      ...
    },
    {
      "id": "TASK-2F-02",
      "mode": "tdd",
      "concern": "main_assembly",
      "size_estimate_lines": 520,
      "l2_required": true,                 // RED 12 → L2 필요
      "phase": "GREEN_REFACTOR",           // (§2.2 시간축 phase)
      "phase_scope": ["RED-4", "RED-5", "RED-6"],
      ...
    },
    {
      "id": "TASK-2F-03",
      "mode": "normal",
      "concern": "operational",
      "size_estimate_lines": 90,
      "l2_required": false,
      ...
    }
  ]
}
```

`concern` 허용값 (휴리스틱 §3.2):
- `infra_precursor` — 인프라 선제
- `main_assembly` — 메인 조립
- `operational` — 운영 보강 (주로 `mode: "normal"`)
- `custom` — 위 3 분류 미부합 시 (사람 확정 필요)

---

## 4. 축 교차 운영 — 시간+공간 결합

### 4.1. 교차 규칙

태스크 별로 **L2 필요 여부**(`l2_required`)가 시간축 분할 적용 여부를 결정:

| 태스크 상태 | 시간축 (시간 축 §2.1) | 세션 수 (예시) |
|---|---|---|
| `l2_required: false` (S/M) | 단일 세션 허용 — RED 작성 + GREEN + REFACTOR 한 번에 | 1 |
| `l2_required: true` (L+) | 하이브리드 C→A 적용 (RED 그룹 × 2 세션) | 2 × 그룹 수 |
| `mode: "normal"` (operational) | 시간축 무관 — REFACTOR 단일 세션 진행 | 1 |

### 4.2. 순서 규칙

L1 태스크 간 순서 (의존 그래프) 와 L2 세션 분할 간 순서가 교차:

1. L1 태스크 순서는 `.shackled-state.json` `tasks[]` 배열 순서로 고정 (의존 선행 태스크 먼저).
2. 각 태스크 내부 L2 세션 분할은 해당 태스크 내에서만 유효. 태스크 경계를 넘어 세션 공유 금지.
3. L1 태스크 전환 시 핸드오프 노트 (§2.3) 에 "다음 태스크 범위" 명시.

### 4.3. WORKAROUND 추적

L1 인프라 선제 태스크가 WORKAROUND 로 GREEN 도달한 경우:
- 해당 태스크의 `workaround_notes[]` 에 박제.
- 메인 태스크 완료 시 `workaround_notes` 각 항목에 대해 "제거 확인 완료" 또는 "유지 근거" 를 추가하는 단계 필수.
- 제거 미확인 상태로 태스크 전체 완료 처리 금지.

---

## 5. 대체 전략 (fallback)

세션 분할 인프라가 아직 없거나 오케스트레이터 개선 전에 사용할 임시 방안:

**수동 완화 (운영자 주도)**:
- 주인님이 단계 전환 시점 판단 → 수동 `/clear` → 핸드오프 노트 직접 작성 → 새 세션에 붙여넣기.
- 2f 진행 중 임시 방안.

**신호 감지 휴리스틱**:
- 한 세션 내 파일 변경 횟수 > N → 분할 권고.
- 한 세션 내 테스트 실행 횟수 > M → 분할 권고.
- 임계값 N/M 은 실측 후 결정 (v0.2.0 에서).

---

## 6. 열린 문제 (v0.2.0 확정 전 해결 필요)

### 시간축

1. **그룹 크기 결정 알고리즘**: RED 의존 그래프 분석이 어떻게 구현? LLM 기반 분석 vs 규칙 기반?
2. **REFACTOR 스코프**: 그룹 내 REFACTOR 만 하는가, 그룹 간 REFACTOR 세션 추가하는가?
3. **실패 세션 복구**: GREEN 세션이 실패하면 RED 세션으로 롤백? 핸드오프 노트로 RED 수정?
4. **세션 간 테스트 실행**: RED 세션 종료 후 "전수 실패 확인" 은 오케스트레이터가 테스트 돌려야. 이 확인도 세션 내?
5. **auto-compaction 감지 방식**: 모델 출력에서 compaction 신호는 어떻게 프로그래밍적으로 포착?

### 공간축

6. **L1 분할 임계값 정교화**: 현 가이드 "지시서 500줄" 은 2건 샘플 기준. 실측 누적 후 조정. 줄 수 외 지표 (RED 수 / 관심사 수) 와 결합 여부.
7. **`concern` 분류 확장**: `infra_precursor / main_assembly / operational / custom` 4 분류가 체급·도메인에 충분한가?
8. **WORKAROUND 제거 검증 메커니즘**: 메인 태스크 완료 시 WORKAROUND 제거 확인을 자동화할지, 수동 체크리스트인지?
9. **L2 분할 임계값 (RED 수)**: 현 가이드 "RED > 6" 은 2f 12 RED Full GC 발생 사례 기반 단일 샘플. 다른 shackled 사례 누적 필요.

### 축 교차

10. **체급별 분할 조합**: S (L1 불필요 + L2 불필요) / M (L1 불필요 + L2 선택) / L (L1 필수 + L2 선택) / XL (L1 필수 + L2 필수) — 체급별 기본값 제시?
11. **의존 순서 위반 감지**: L1 태스크 순서 강제 메커니즘 (런타임 검증 vs 설계 시 검증).

---

## 7. v0.2.0 발행 전제

본 draft 가 v0.2.0 에 통합되려면:

- [ ] 2f shackled 완료 — 실측 데이터로 시간축 분할 단위 + 공간축 L1/L2 조합 검증.
- [ ] 임시 수동 완화책으로 2f 진행한 경험 박제 — 어느 시점 분할이 실제 도움됐는가.
- [ ] WORKAROUND 제거 검증 사례 — 2F-01 WORKAROUND 가 2F-02 완료 후 어떻게 제거됐는가.
- [ ] L1 분할 임계값 (지시서 줄 수) 실측 조정 — 2e/2f 2건 외 추가 사례 누적.
- [ ] 열린 문제 11건 중 최소 3~5건 결정.
- [ ] shackled 설계서 본편으로 이관 여부 결정 (Issue-06 #4 범위 내 vs 별도 확장).

## 8. 참조

- 실시간 관찰: [`tracing-2f-2026-04-20.md`](tracing-2f-2026-04-20.md)
- Issue-06 #1 draft: [`tdd-ready-spec-v0.1.0-draft.md`](tdd-ready-spec-v0.1.0-draft.md)
- 기존 shackled 설계 — TDD 모드 분기: `01-Planning/06-shackled/02-design/02-state-management.md` §3.3
- Claude Web Sonnet 독립 검증 — 주인님 대화 (2026-04-20 13:48)
