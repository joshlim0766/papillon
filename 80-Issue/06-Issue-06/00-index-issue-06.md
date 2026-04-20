# Issue-06: TDD-ready 설계서 규격 신설

## 상태
- **Open** — 2026-04-17 발견. 스펙 초안 작업 예정.
- **영향 범위**: inquisition + wtth (설계 모드) + shackled (tdd 모드) + common-spec

## 배경

AI에게 코딩을 시킬 때 TDD가 강한 품질 개선 효과를 내는 것을 실전에서 확인. 다만 **전제 조건으로 "TDD를 잘 할 수 있는 설계서"가 필요**하다는 사실도 함께 파악.

현재 파이프라인에서 미해결 격차:

1. **설계서 리뷰가 "테스트 가능성"을 1급 체크 항목으로 보지 않음** — wtth 설계 모드의 ARCH/SPEC/IX 페르소나는 구현 가능성은 보지만 testability 렌즈가 없음.
2. **shackled `tdd` 모드 진입 조건 부재** — 이미 `normal`/`tdd` 2 모드로 분기되어 있으나, 테스트 불가능한 설계서가 들어오면 tdd 모드는 늦은 시점에 실패. 업스트림 게이트 없음.
3. **TDD 방법론 선택 시점 모호** — 현재는 shackled 진입 시점에 `tdd_mode`가 정해지는데, 그때는 설계서가 이미 고정되어 testability 소급이 불가.

## 핵심 설계 결정

### 두 축 분리 (Gate vs 품질 체크)

| 축 | 성격 | 주체 | 기록 위치 |
|---|---|---|---|
| `tdd_mode` (방법론 선택) | "이 태스크를 TDD로 갈 것인가" | **사람 결정 — Gate 등급** | 인퀴지션 `00-summary.md` |
| `tdd_ready` (설계서 품질) | "설계서가 TDD를 받쳐줄 수 있는가" | AI 판정 — 리뷰 체크 | wtth RDR |

- `tdd_mode=yes`일 때 `tdd_ready`가 **필수 게이트**로 작동.
- `tdd_mode=no`일 때 `tdd_ready`는 informational (여전히 가치 있음).

### 파이프라인 흐름

```
inquisition: tdd_mode 질문 → 사람 답변 → summary에 기록
    ↓
wtth 설계 리뷰: tdd_mode=yes면 testability invariant를 게이트로, no면 warning
    ↓
shackled: 설계서 딸린 tdd_mode 플래그로 normal/tdd 분기 (기존 로직 유지)
```

### Issue-02 #3(사람 개입 과다) 관점

`tdd_mode` 질문은 잘못 선택하면 전체 구현 방식이 바뀌므로 **Gate 등급이 맞다** (PRD G3 "사람이 결정권을 가진다"와 일치).

---

## 참조 샘플 (TDD-ready 설계서 exemplar)

위치: `~/Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer/`

| 문서 | 체급 | TDD 적합도 | 비고 |
|---|---|---|---|
| `shackled-phase1-directive.md` | L | N/A (의도적 제외) | 인프라 골격, Smoke 3건이 타당 |
| `shackled-phase2-00-overview.md` | — | — | 공통 제약 G6 "RED 먼저, 역순 금지" 못박음 |
| `shackled-phase2a-bms-validator.md` | S | ★★★★★ | 순수 함수, RED 4건, Spring Context 불필요 |
| `shackled-phase2c-original-lookup.md` | M | ★★★★ | RED 6건, I/O 계약 data class |
| `shackled-phase2e-upsert-service.md` | M | ★★★☆ | RED 8건, 일부 RED 결정성·구현 의존성 약함 |

이 문서군을 **TDD-ready 설계서의 reference exemplar**로 지정.

> **2026-04-20 회사 세션 재평가 주석**: 원본 `shackled-*.md` 10개 전수 독립 평가 완료. phase2c → ★★★★★ 상향 근거 + phase2e → ★★★★ 상향 근거(배치 재작성으로 AP-1 상류 해소) + 미등재 5건(phase2b/2d/2f/use-block/use-tenant) 각자 다른 신호 모범 확인. 본 테이블 재작성과 v0.2.0 MUST/SHOULD 재분류는 **shackled 2e/2f 실측 완료 후 회사 세션**에서 확정. 평가 상세: `tdd-ready-evaluation-memo-2026-04-20.md`.

---

## TDD-ready 신호 8개 (샘플에서 추출, 스펙 초안 후보)

1. **RED 시나리오 번호 명시** — "RED 1~N" 블록에 입력/실행/검증 사전 열거
2. **I/O 계약을 data class 수준으로 정의** — `OriginalMessageRecord` 5 필드, `StatsDimensions` 9차원
3. **에러 경로가 타입으로 응집** — `pipeline/exceptions/` 패키지, `DltErrorReason` 매핑
4. **의존 DAG 명시** — overview §2 (2A 독립 / 2D가 2B·2C 의존)
5. **TDD 플래그를 지시서 헤더에 박음** — "TDD: Red → Green → Refactor" 또는 "없음"
6. **테스트 파일 경로 사전 지정** — 지시서 §6
7. **공통 제약으로 TDD 역순 구현 금지 못박음** — overview §5 G6
8. **상태/부작용 경계 명시** — "stateless", "megabird-ds 전용", "TenantContext.use 중첩 금지"

## Anti-pattern 3건 (샘플의 약점, 금기 섹션 후보)

1. **비결정적 RED 금지** — Phase 2E RED 7 "실제 MySQL 데드락 유발"은 타이밍 의존으로 재현 실패 가능. 번역 경로 검증이면 mock ExceptionTranslator로 축약, 실측은 별도 Verification 섹션.
2. **구현 상세 검증 RED 금지** — Phase 2E RED 8 "새 트랜잭션 증명"은 self-injection+메서드 분리 패턴에 종속. behavior 기반("첫 시도 rollback 후 두 번째 시도 성공")으로 작성.
3. **선결 환경 작업 vs TDD 범위 명시 구분** — Phase 2E L0 (ExceptionTranslator 배선)은 TDD 루프 밖 선결. TDD-ready 설계서는 둘을 섞지 말고 명시적으로 분리해 표시.

---

## 실행 계획 (쪼개기)

| # | 작업 | 산출물 | 의존 |
|---|---|---|---|
| 1 | `tdd_mode` / `tdd_ready` 두 축 분리 스펙 초안 | `02-common-spec.md` §14 (가칭) 또는 신규 섹션 | 독립 |
| 2 | 인퀴지션 `tdd_mode` 질문 추가 | `05-inquisition/02-design/` + 스킬 | #1 |
| 3 | wtth 설계 모드에 testability invariant 추가 | `04-wtth/02-design/02-review-design.md` + 스킬 | #1 |
| 4 | shackled `tdd_mode` 소비 로직 확인 | `06-shackled/02-design/` (이미 모드 분기 존재 — 게이트만 추가) | #1, #2 |
| 5 | TDD-ready 설계서 exemplar 링크 등록 | common-spec 참조 섹션 | #1 |

**우선순위**: #1 먼저 (1세션 분량 예상). 이 스펙이 나와야 #2~#5가 구체화됨.

## 기존 로드맵과의 재배치

기존 HANDOFF "다음 작업" 순서:

```
1. wtth 스킬 P0 3건 수정 (선결)
2. CODE AC v0.1.1 격리 재검증
3. 6개 페르소나 AC 중 1개 격리 dry run
...
```

**재배치 제안**:

```
1. Issue-06 #1 — tdd_mode/tdd_ready 두 축 분리 스펙 (NEW)
2. wtth 스킬 P0 3건 수정 (기존 1)
3. reviewer AC에 testability 항목 반영 (NEW, Issue-06 #3 연계)
4. CODE AC v0.1.1 격리 재검증 (기존 2)
5. 6개 페르소나 dry run (기존 3, testability 반영 후)
...
```

**근거**: 지금 dry run을 먼저 돌리면 testability 미반영 상태로 baseline이 고정되어 나중에 재작업 비용이 큼. 스펙을 먼저 정의하는 편이 경제적.

---

## 다음 세션 체크리스트 (자전거 복귀 후 또는 집에서 이어가기)

- [ ] Issue-06 #1 착수 — `tdd_mode` / `tdd_ready` 두 축 스펙 초안. common-spec §14 또는 신규 파일 결정
- [ ] exemplar 참조 경로 안정화 — megabird-work-plan 레포 외부. 상대 경로 불가, 절대 경로 또는 복제 필요 여부 결정
- [ ] 8개 신호 중 어느 것을 **MUST**, 어느 것을 **SHOULD**로 할지 분류
- [ ] anti-pattern 3건을 금기 섹션 vs checklist 어디에 놓을지 결정
- [ ] wtth 설계 모드 testability invariant 초안 (페르소나 추가 vs 기존 페르소나 체크리스트 확장 택1)

## 참조

- PRD G5 (요구사항 단계에서 암시적 제약을 명시적으로 끌어올림)
- PRD G3 (파이프라인 자동 진행, 사람은 의사결정만)
- Issue-02 #3 (사람 개입 3등급 Gate/Checkpoint/FYI)
- shackled 설계서: `01-Planning/06-shackled/02-design/` (이미 normal/tdd 2 모드 존재)
- 핵심 결정 사항 (HANDOFF): "shackled 실행 모드 분리: normal / tdd"
- exemplar: `~/Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer/shackled-phase2*.md`
