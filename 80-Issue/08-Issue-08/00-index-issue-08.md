# Issue-08: 빠삐용 리스크 매트릭스 — 심각도 × 확률 축 도입

## 상태
- **Open** — 2026-04-21 개설.
- **영향 범위**: `02-common-spec.md §1 심각도 기준` + `04-wtth` reviewer 페르소나 프롬프트 + `TDD-ready spec v0.2.0` (후속 v0.2.1) + `06-shackled` + `08-ac` reviewer AC + `VOCABULARY.yaml`.
- **트리거**: 2e/2f 실측에서 reviewer 수용률 ~36% 누적 + 주인님 20년 경력 prior 와 reviewer 판정의 반복 충돌.

## 배경

주인님 실무 진행 중 제기된 의구심:

> "빠삐용이 필요 이상으로 너무 깐깐한 거 아닌가? 발생확률에 대해서 재고하지 않고 P0, P1 으로 올리는 경향이 제법 있지 않은가?"

구체 사례:

> "스레드 경합 버그는 돌려보면 1시간 내로 터진다. 이런 건 심각도 꽂아서 주면 된다. 다만, Elasticache 로 Valkey 쓰는데 **장애가 45분 이상 이어지면** 이딴 개소리가 문제된다."

20년 경력 엔지니어의 prior — "뭐가 자주 발생하고 뭐가 희박한지" — 를 현 시스템이 **확률 축 부재**로 무시하고 있다는 진단.

## 핵심 문제 — 심각도 단일 축 운용

현 `02-common-spec.md §1` 심각도 기준은 **"발생 시 영향"** 만 반영.  
리스크 = **영향 × 확률** 인데 **확률 축 부재** → reviewer 가 영향만 크면 P0/P1 승격 → 방어적 판정 누적 → 수용률 저하 + 라운드 4회.

## 실증 근거 (Issue-06 실측 연계)

| 지표 | 2e (Phase 2E) | 2f (Phase 2F) |
|---|---|---|
| Total findings | 42 | 1R 12 묶음 + 2R/3R/4R 누적 |
| 수용률 | **36%** (수용 15 / 기각 27) | 4R 선별 2건 (AB-2/AB-3) + AB-1/4/5 영구 위임 |
| 리뷰 라운드 | 1R + 경량 2R | **4R** (1R→2R→3R→4R 실용 노선 마무리) |

**결론**: 기각된 findings 상당수가 "심각도로는 P0/P1 이지만 실제 발생 확률이 희박" 케이스. 확률 축 도입으로 reviewer 프롬프트 단계에서 사전 필터 가능.

---

## 사례 대비 (개념 전달)

| 시나리오 | 영향 | 확률 | 리스크 = 영향 × 확률 | 현 reviewer 판정 | 이래야 함 |
|---|---|---|---|---|---|
| 락 없는 공유 변수 경합 | 중간 | **매우 높음** (1시간 내 재현) | 높음 | P0 | **P0 유지** |
| Elasticache 단일 AZ 45분+ 장애 → 유실 | 치명 | **극미** (AWS SLA 99.99%, 연 1회 이하) | 낮음 | P0 (**개소리**) | **P2~P3** |
| Kafka consumer lag 10분+ | 높음 | 중간 (월 수회) | 중간 | P1 | **P1 유지** |
| MySQL 트랜잭션 deadlock | 중간 | 중간~높음 (주 수회) | 높음 | P1 | **P1 유지** |

이 4행 대비가 Issue-08 의 핵심 예시. **확률 축을 도입하면 reviewer 가 Elasticache 45분+ 장애 같은 "연 1회 이하" 희귀사건을 P0 로 꽂지 않게 됨**.

---

## 핵심 설계 — 4축 솔루션

### 축 A (메인) — reviewer 프롬프트 "확률 reasoning" 강제

reviewer 페르소나가 심각도 판정 시 아래 4단계 reasoning 을 강제:

1. **발생 조건 열거**: "이 finding 이 실제 발생하려면 어떤 조건 N가지가 동시 충족돼야 하는가?"
2. **조건별 확률 추정**: "각 조건의 발생 확률을 축 E prior KB 또는 도메인 경험 기반으로 추정."
3. **결합 확률 계산**: "조건들의 결합 확률을 대략 bucket 으로."
4. **리스크 판정**: "영향 × 결합 확률 = 심각도."

**강제 규칙**:
- 결합 확률 **"매우 낮음"** 이면 영향이 치명적이어도 P2 이하.
- reasoning 없이 심각도 꽂으면 **축 C (anti-pattern)** 위반.

### 축 B (사후) — RDR 캘리브레이션

- RDR 에 reviewer 의 **조건/확률 reasoning** 박제 (공식 포맷 확장).
- 수용률/보류율 지표 (`common-spec §13` 파일럿 정량 지표 확장).
- 분기별 메타 리뷰로 prior 교정:
  - "확률 매우 낮음" 판정된 findings 중 실제로 운영에서 터진 케이스 ← prior 상향 조정.
  - 방어적 P0 로 찍었다가 기각된 케이스 ← reviewer 프롬프트 제약 강화.

### 축 C — Anti-pattern "확률 무시 방어 금지"

신규 anti-pattern 신설:

> **AP-X (Anti-Pattern — 확률 무시 방어)**: finding 의 발생 조건을 열거하지 않고 영향만 근거로 심각도 승격하는 것. 인프라 SLA / 운영 baseline 상 발생 조건이 희박한데 P0/P1 승격 시 이 anti-pattern 에 해당.

**반영 대상**:
- `TDD-ready spec v0.2.1` §5 Anti-pattern 목록에 추가.
- `04-wtth` reviewer 페르소나 프롬프트에 금기 항목으로 명시.
- `06-shackled` TDD 모드에서도 동일 규칙 적용 (test-level overkill 차단).

### 축 E — 공용 확률 prior KB (`baseline-probability.md`)

reviewer 가 참조할 **정형화된 확률 prior 목록**. 변동성 낮음 → 분기 1~2회 유지 비용.

**위치**: `01-Planning/baseline-probability.md` (신규)

**카테고리 후보**:
- 인프라 장애 (AWS RDS / Elasticache / EC2 / EBS / 네트워크)
- 동시성·동기화 (스레드 경합 / deadlock / race condition)
- 데이터베이스 (MySQL 트랜잭션 deadlock / 쿼리 timeout / 연결 pool 고갈)
- Kafka / 메시징 (consumer lag / broker 장애 / 메시지 순서 변경)
- Redis / 캐시 (eviction / 연결 실패 / 레플리카 지연)
- HTTP / 외부 API (5xx / timeout / rate limit)
- 배포·운영 (롤백 / 설정 오류 / 시크릿 만료)

**포맷 (예시)**:
```markdown
| 시나리오                                      | 확률 bucket     | 근거                         |
|---|---|---|
| AWS Elasticache 단일 AZ 45분+ 장애            | 극미 (연 1회 이하) | AWS SLA 99.99%               |
| 락 없는 공유 변수 경합                        | 매우 높음 (1h 내 재현) | 경험 prior                   |
| MySQL 트랜잭션 deadlock (중규모 트래픽)       | 중간~높음 (주 수회)  | 경험 prior                   |
| Kafka consumer lag 10분+                      | 중간 (월 수회)       | 경험 prior + 모니터링 기록   |
| ...                                           | ...                  | ...                          |
```

**확률 bucket 고정 어휘** (VOCABULARY.yaml 박제):
- `극미` (연 1회 이하)
- `낮음` (분기 1회 이하)
- `중간` (월 수회)
- `높음` (주 수회)
- `매우 높음` (일 수회 또는 재현 테스트 1시간 이내)

---

## 실행 계획 (쪼개기)

| # | 작업 | 산출물 | 의존 |
|---|---|---|---|
| 1 | 확률 bucket 고정 어휘 정의 + VOCABULARY 반영 | `VOCABULARY.yaml` 갱신 (5 bucket) | 독립 |
| 2 | 공용 prior KB 초안 (축 E) | `01-Planning/baseline-probability.md` (v0.1) | #1 |
| 3 | `common-spec §1` 심각도 기준 확장 — 영향 × 확률 매트릭스 | `02-common-spec.md` 갱신 | #1 |
| 4 | `04-wtth` reviewer 페르소나 프롬프트 "확률 reasoning" 지침 추가 (축 A) | 페르소나 파일 + 스킬 프롬프트 갱신 | #2, #3 |
| 5 | anti-pattern "확률 무시 방어 금지" 신설 (축 C) | `tdd-ready-spec v0.2.1` + common-spec 반영 | #3 |
| 6 | RDR 포맷 확장 — 조건/확률 reasoning 박제 (축 B) | `common-spec §2` RDR 포맷 확장 | #3 |
| 7 | reviewer AC 에 확률 축 invariant 추가 | `01-Planning/04-wtth/ac/` 7 페르소나 전부 | #4 |

**우선순위**: #1 → #2 → #3 → #4. #5/#6/#7 은 병렬 가능.

---

## 선결 결정

1. **확률 bucket 수 (5단계 고정 채택)** — `극미 / 낮음 / 중간 / 높음 / 매우 높음`. 7단계 이상은 구분 실익 미약.
2. **결합 확률 계산 방식** — 단순 곱(독립 가정) vs 최악 조건(병목). reviewer 에게 **"병목 조건 1개 선택" 지침** 으로 시작 → 단순화.
3. **prior 교정 루프 주기** — 분기 1회 메타 리뷰 + 인시던트 트리거 시 즉시.
4. **축 C anti-pattern 적용 범위** — TDD-ready spec 만 할지 common-spec 전면 박제할지. 초기엔 `common-spec` 직접 박제 (전 모드 적용).
5. **리뷰어 prompt 수정 방식** — 페르소나 파일 수정 vs 스킬 프롬프트 전역 수정. 전역(스킬) 이 DRY.

---

## 우선순위

**중간~높음**. Phase 3 배치 엔진 착수 전 **최소 축 A + E** 완료 권장. 그 이유:
- 배치 엔진 개발 시 또 4라운드 돌면 비용 큼.
- 축 E prior KB 는 2시간 이내 초안 가능.
- 축 A reviewer 프롬프트 수정은 30분 이내.

축 B/C 는 병렬 진행 또는 배치 엔진 1~2 태스크 shackled 후 실측 기반 조정.

---

## TDD-ready spec v0.3.0 환류 트리거

본 이슈의 축 B (수용률 캘리브레이션) 결과는 `tdd-ready-spec v0.2.0 §11.2` 의 v0.3.0 재검토 트리거 중 "운영 반영 결과 휴리스틱 조정 필요" 에 직접 feed. 즉 Issue-08 → TDD-ready spec v0.3.0 → common-spec 업데이트 사이클.

---

## References

- **Issue-06 v0.2.0**: [tdd-ready-spec-v0.2.0.md](../06-Issue-06/tdd-ready-spec-v0.2.0.md) §9.1 실용 노선 (사후 필터 — 축 B 와 연계) / §5 AP (축 C 와 연계)
- **Issue-06 실측**: [tracing-2e-2026-04-20.md](../06-Issue-06/tracing-2e-2026-04-20.md), [tracing-2f-2026-04-20.md](../06-Issue-06/tracing-2f-2026-04-20.md) — 수용률 36% / 4R 수렴 근거
- **PRD G3** (사람 결정권) — AI 는 발견·정보 제공, 사람이 판정 맥락 제공
- **Issue-02 #3** (사람 개입 3등급 Gate/Checkpoint/FYI) — 본 이슈와 상보
- **common-spec §1** (심각도 기준 P0~P3) — 확장 대상
- **common-spec §13** (파일럿 정량 지표) — 축 B 수용률 지표 반영 대상
- **04-wtth 설계서**: `01-Planning/04-wtth/02-design/` — 페르소나 프롬프트 수정 대상
- **VOCABULARY.yaml** — 확률 bucket 어휘 박제 대상
