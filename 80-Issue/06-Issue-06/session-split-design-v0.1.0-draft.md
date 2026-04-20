# Shackled TDD 모드 세션 분할 메커니즘 설계 v0.1.0-draft

## 문서 성격

Issue-06 #4 "shackled tdd_mode 소비 로직" 의 신규 요건 초안. [`tracing-2f-2026-04-20.md`](tracing-2f-2026-04-20.md) 의 관찰 1을 설계로 옮긴다. 2f 완료 후 실측으로 검증, v0.2.0 시점에 shackled 설계서 본편(`01-Planning/06-shackled/02-design/`)으로 이관 여부 결정.

**스코프**: `shackled` 스킬의 `tdd` 모드 실행 시, RED / GREEN / REFACTOR 단계를 별개 세션으로 분할 실행하는 메커니즘.

**비 스코프**: `normal` 모드는 변경 없음. 지시서 작성 규격(Issue-06 #1)과 별도 축.

---

## 1. 문제 정의

### 1.1. 현상

단일 세션에서 RED → GREEN → REFACTOR 연속 수행 시 모델 품질 저하. 실측 근거:
- 2f shackled 진행 중 Sonnet 관찰 — 사이클 누적될수록 판단 품질 저하.
- Claude Web Sonnet 독립 검증 — 동일 분석 도달.

### 1.2. 원리

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

### 1.3. auto-compaction 의 한계

모델 자체 압축은:
- **타이밍**: context 한계 근처 발동 = 이미 오염된 후.
- **품질**: 압축 기준 가변. 실패 케이스 잔존 가능.
- **재현성**: 런마다 결과 다름.
- **디버깅**: 압축 결정 추적 난감.

즉 응급 처치이며 구원이 아님. **오케스트레이터 명시 분할** 이 필요.

---

## 2. 설계 결정

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

## 3. 대체 전략 (fallback)

세션 분할 인프라가 아직 없거나 오케스트레이터 개선 전에 사용할 임시 방안:

**수동 완화 (운영자 주도)**:
- 주인님이 단계 전환 시점 판단 → 수동 `/clear` → 핸드오프 노트 직접 작성 → 새 세션에 붙여넣기.
- 2f 진행 중 임시 방안.

**신호 감지 휴리스틱**:
- 한 세션 내 파일 변경 횟수 > N → 분할 권고.
- 한 세션 내 테스트 실행 횟수 > M → 분할 권고.
- 임계값 N/M 은 실측 후 결정 (v0.2.0 에서).

---

## 4. 열린 문제 (v0.2.0 확정 전 해결 필요)

1. **그룹 크기 결정 알고리즘**: RED 의존 그래프 분석이 어떻게 구현? LLM 기반 분석 vs 규칙 기반?
2. **REFACTOR 스코프**: 그룹 내 REFACTOR 만 하는가, 그룹 간 REFACTOR 세션 추가하는가?
3. **실패 세션 복구**: GREEN 세션이 실패하면 RED 세션으로 롤백? 핸드오프 노트로 RED 수정?
4. **세션 간 테스트 실행**: RED 세션 종료 후 "전수 실패 확인" 은 오케스트레이터가 테스트 돌려야. 이 확인도 세션 내?
5. **체급별 적용**: S/M/L 체급에서 분할 단위 다르게 가야 하나? S 는 RED 적어 C 대신 A 가 나을지도.
6. **auto-compaction 감지 방식**: 모델 출력에서 compaction 신호는 어떻게 프로그래밍적으로 포착?

---

## 5. v0.2.0 발행 전제

본 draft 가 v0.2.0 에 통합되려면:

- [ ] 2f shackled 완료 — 실측 데이터로 분할 단위 검증.
- [ ] 임시 수동 완화책으로 2f 진행한 경험 박제 — 어느 시점 분할이 실제 도움됐는가.
- [ ] 열린 문제 6건 중 최소 1~3번 결정.
- [ ] shackled 설계서 본편으로 이관 여부 결정 (Issue-06 #4 범위 내 vs 별도 확장).

## 6. 참조

- 실시간 관찰: [`tracing-2f-2026-04-20.md`](tracing-2f-2026-04-20.md)
- Issue-06 #1 draft: [`tdd-ready-spec-v0.1.0-draft.md`](tdd-ready-spec-v0.1.0-draft.md)
- 기존 shackled 설계 — TDD 모드 분기: `01-Planning/06-shackled/02-design/02-state-management.md` §3.3
- Claude Web Sonnet 독립 검증 — 주인님 대화 (2026-04-20 13:48)
