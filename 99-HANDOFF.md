# 99-HANDOFF

## 현재 작업 위치
`~/.claude/commands/papillon/wtth.md` (신규 설치) + `01-Planning/04-wtth/ac/` — wtth 스킬 설계서 기반 신규 작성 + 설계서↔스킬 gap 점검 완료 (2026-04-16 새벽, 집)

## 직전 작업: 2026-04-16 새벽 (집) — wtth 스킬 신규 작성 + gap 점검

집 머신 wtth 스킬 부재가 CODE AC 실측 dry run의 최대 블로커였음. 설계서(`04-wtth/02-design/00-core.md` + `01/02/03-review-*.md`) 기반으로 `~/.claude/commands/papillon/wtth.md` 신규 작성 (592줄). 작성 후 Explore 에이전트로 독립 gap 점검 수행.

### 오늘 작업 (커밋 없음 — 스킬 소스는 `~/.claude/commands/` 경로, 레포 밖)

| 항목 | 내용 |
|---|---|
| 신규 | `~/.claude/commands/papillon/wtth.md` (592줄) — 5모드 + 전문가 거버넌스 + 수렴 메커니즘 + RDR/ADR 전부 반영 |
| 점검 | 설계서 SSOT 4건 + common-spec §2/§6/§9/§12 + `_schema.md` 대조. Explore 에이전트 독립 검증 |

### Gap 점검 결과 (미수정, 다음 세션 선결)

**P0 누락 3건 (행동 왜곡 가능):**
1. 스킬 §2.4 — "리뷰 세션 = RDR 1개 단위, 대화 컨텍스트와 무관" 용어 정의 누락. 출처: 설계서 §1.3
2. 스킬 §3.1 — `.pre-review.md` 삭제 시점 "(리뷰 종료 시 아님)" 구분 누락. 최종 확인 중 AS-IS 참조 누락 위험. 출처: 설계서 §3.3
3. 스킬 §4.3 — 경량 통합 체크 후 "**이상 없으면** 다음 라운드 시작" 완료 조건 누락. 출처: 설계서 §2.1

**P1 축약 2건:** §3.1 백업 용도 맥락 약화 / §4.3 "Opus/Sonnet 1회 호출 수준" 스케일 가이드 누락

**P2 제안 2건:** §1.1 단독 실행 시 복수 모드 발견 → §1.3 직진 연쇄 명시 / §2.4 복합 모드에서 `excluded_experts`는 세션 전체 적용 (모드별 제외 불가) 명시

**양호:** 복합 모드 4단계 확정 흐름·최종 확인 P0 전수/P1 샘플링 문자열 일치 검증·RDR/ADR 포맷 전부 정확.

### 이전 세션 (2026-04-15 저녁 집) 커밋

| Commit | 내용 |
|---|---|
| `24f1324` | wtth reviewer AC v0.1.0 — 공통 베이스(common-v0.1.0.md) + CODE 페르소나(code-v0.1.0.md) 초안 |
| `8398390` | CODE AC v0.1.0 수동 dry run 리포트 + HANDOFF 갱신 |

### 이전 커밋 (2026-04-14 + 회사)

| Commit | 내용 |
|---|---|
| `6cd7713` | Issue-05 AI-1·AI-2 + Issue-03-02 상태 동기화 (높음·P1 Open 0건 달성) |
| `36e6592` | 파일럿 정량 지표 프로토콜 신설 — common-spec §13 + `01-Planning/07-metrics/retro-template.md` |
| `00ede23` | AC Template v3.2 + Inquisition AC v0.1.0 + VOCABULARY.yaml 등록 |
| `a54de43` | HANDOFF stale 문구 정정 |
| `651f1e4` | 빠삐용 수학적 정의 L0 착수 — `01-Planning/09-formal/` 신규 |
| `9d81a73` | L0 셀프 린트 P0 3건 + P1 2건 반영 |
| `1eb5ff6` | L0 §3.3 추정 가능성 노트 추가 (̂P_N의 L1 의존 명시) |
| `2229165` | (회사) Python CLI 유틸 3종 + Template v3.3 승격 + common-spec §9.1 (SKILL.md 포맷) + ART-IQ-02 실측 92.86% PASS |

### 핵심 산출물

- **`01-Planning/04-wtth/ac/common-v0.1.0.md`** (신규): wtth reviewer 공통 AC 베이스 (Tier 1 document)
- **`01-Planning/04-wtth/ac/code-v0.1.0.md`** (신규): CODE 페르소나 override
- **`01-Planning/04-wtth/ac/dry-run-code-v0.1.0.md`** (신규): CODE AC 수동 dry run 리포트 (편향 고지 포함)
- `01-Planning/09-formal/00-index.md`·`01-l0-scope.md`: 수학적 정의 L0 (이전 작업, stable)
- `01-Planning/08-ac/ac-template-v3.3.md`: AC 템플릿 (회사 세션에서 v3.2 → v3.3 승격)
- `01-Planning/05-inquisition/ac-v0.1.0.md`: 템플릿 첫 실전 적용 (회사 세션에서 v3.3 참조로 업데이트)
- `VOCABULARY.yaml`: 전역 도메인 약어 14종
- `01-Planning/02-common-spec.md` §13: 파일럿 정량 지표 프로토콜 / §9.1: SKILL.md 포맷 표준 (회사)
- `tools/ac-validator/`: Python CLI 유틸 3종 + ART-IQ-02 실측 스크립트 (회사, 92.86% PASS)
- `01-Planning/07-metrics/retro-template.md`: 파일럿 회고 양식

### 운영 변경

- **`~/.claude/CLAUDE.md` §0 신설**: 호칭 "주인님" 고정, 존댓말 고정, 전역·예외 없음

### 오늘 핵심 판단

- **스킬 AC 작성 순서 확정**: wtth:reviewer:code(1) → shackled(2) → wtth:orchestrator(3) → papillon/task sizing/gate(4). Tier 1 먼저, variant 다양화, 복잡도 상승.
- **wtth reviewer AC 구조**: 공통 베이스 + 페르소나별 override (옵션 B). CODE 먼저, 이후 페르소나별 copy-paste.
- **금기·발언 품질 검증은 Tier 1에서 불가**: `Tier 2 승격 후보` 섹션에 명시. 실측 후 승격 판단.
- **Dry run 수동 수행 제약**: wtth 스킬 미설치(로컬) + fixture runner 미구현이 실제 자동 dry run의 블로커. 오늘은 수동 dry run으로 AC 구조 검증만 진행.

## 다음 작업: 다음 단계 후보

우선순위 순:

1. **wtth 스킬 P0 3건 수정** (선결) — 위 §"Gap 점검 결과" P0-1·2·3. 각각 1~2줄 추가면 끝남. 수정 후 P1/P2는 판단.
2. **CODE AC 실제 스킬 실행 dry run** — wtth 스킬 수정 완료 후 바로 가능. 수동 dry run(dry-run-code-v0.1.0.md) 구멍 후보 6건을 실측으로 재검증. Fixture runner 미구현이지만 수동 AC 대조로도 진행 가능.
3. **CODE AC v0.1.1 보강** — 실측 결과 반영: (a) `INV-WREV-01` heading 형식 완화 + 페르소나 output format 규약 추가, (b) `FIX-CODE-01` expected 정규식 관대화, (c) `forbidden_patterns` "좀 더" 제거 검토.
4. **다른 reviewer 페르소나 AC 복제** — CODE 구조 안정 후 BE/FE/SEC/TEST/ARCH/DBA 복사 + override.
5. **shackled AC 착수** — code variant 첫 실전. wtth reviewer와 다른 축 (output_type=code + syntax/lint invariants).
6. **Fixture runner 최소 버전** — output 텍스트 ↔ AC invariants 자동 대조. AC 복제 확장 전에 필요.
7. **L0 후속 작업 2건** — `01-Planning/09-formal/01-l0-scope.md` §7: (a) 빠삐용 호출별 `(x, c, θ)` 매핑, (b) 관측 측정 규약.
8. **L1 착수 (Prompt 공간 구조)** — invariance, composition. input equivalence `~_input` 정의 필요.
9. **L/XL 파일럿 기획 (Issue-02 #8 + #2)** — 실제 L/XL 작업 기회 발생 시.
10. **첫 파일럿 회고** — 정량 지표 6개 첫 실측.
11. **ASEWS 모델링 문서 수학적 린트 (L5)** — 본격은 L4 이후.

### 다음 세션 체크리스트

- [x] wtth 스킬 집 머신에 설치 완료 (2026-04-16 신규 작성, 592줄)
- [ ] 회사 머신에도 동일 스킬 동기화 필요 (스킬 소스 경로 정책 결정: 레포 편입 vs 머신별 수동 복사)
- [ ] P0 3건 수정 후 CODE AC 실측 dry run 진입

## 보류 / 다른 세션에서 진행 중

- **praxis 존치 여부**: ASEWS 측에서 결정 진행. 빠삐용 실패 이벤트 → ASEWS 축적 폐루프는 praxis 결정까지 끊겨있음. 빠삐용 측에서 미리 할 수 있는 건 "실패 이벤트 스키마" 정의이나 praxis 결론에 따라 무용이 될 수 있어 보류.
- **cross-model logprobs 경로**: L4 이후. 다른 모델 과금 예산 선결.

## 작업 스택 (완료, 아카이브)

### 스킬 변환 사이클 — 전체 완료

| 순서 | 대상 | 설계서 상태 | 스킬 상태 | 태깅 | 비고 |
|---|---|---|---|---|---|
| 1 | inquisition | 완성 | 설치됨 (`inquisition.md`) | **완료** | 태깅 14건, 설계서 수정 4건, 스킬 불일치 4건 수정 |
| 2 | wtth | 완성 | 설치됨 (`wtth.md`) | **완료** | 태깅 16건 (core) + 모드별 차이점 보강 (Issue-02 #4), 스킬 신규 작성 |
| 3 | shackled | 완성 | 설치됨 (`shackled.md`) | **완료** | 태깅 9건 (메인 7 + 분리 2), 스킬 신규 작성 |
| 4 | papillon | 완성 | 설치됨 (`papillon.md`) | **완료** | 태깅 7건, 스킬 신규 작성. 풀사이클 준비 완료 |

### 이전 작업
1. **묶음 B 설계 리뷰** — 완료
   - ARCH + SPEC + IX 3인, 2라운드 + 사인오프
   - RDR: `04-wtth/03-review/RDR-2026-04-08-bundle-b.md`
   - 총 40건 수용, 0건 기각
2. **묶음 B 설계 초안 작성 (Sonnet, 수정 경로)** — 완료
   - 수정 대상: `04-wtth/02-design/00-core.md`, `personas/spec.md`, `ix.md`, `_schema.md`
   - 수정 매니페스트: `04-wtth/02-design/modification-manifest-bundle-b.md`
3. **액션 아이템** — 전부 처리 완료
   - 묶음 A(AI-3, AI-6, AI-7): 반영 완료 (fb813d8)
   - 묶음 C(AI-4 shackled 페르소나 4축): 반영 완료 (6d05a37)
   - AI-5(핸드오프 브리프): 인퀴지션 스킬에 반영 완료
   - AI-8(리뷰 중간 결과물): 반영 완료 (391c2f3)
   - AI-9(런북 실행 전담 스킬): 닫음 (필요 시 재등록)
4. **Issue-03-01**: 라운드 간 통합 체크 — 반영 완료 (01fb14f)
5. **06-shackled 설계 리뷰** — 완료
6. **06-shackled 설계서 관심사별 분리** — 완료
7. **06-shackled 설계 초안** — 완료
8. **06-shackled inquisition** — 완료


## 핵심 결정 사항
- 수정 경로: Step 3-A(신규) / Step 3-B(수정) 분기 + 수정 매니페스트 자동 생성
- 수정 경로 리뷰: §2.3 추가 체크 포인트 4개 + 매니페스트 기반 영향 범위 추적
- 투입 조건 판별: 오케스트레이터 LLM 판단 + 사람 확정, 경계 사례는 사람 확인
- 복합 모드 투입 조건: OR (하나라도 충족하면 투입)
- 복합 모드 선별 순서: 풀 합산(기본+선택적) → 투입 조건 필터 → 3인 압축
- 복합 모드 확정 흐름: 제안→확정→풀 제시→조정/승인 4단계
- mode 필드: 배열, §1 테이블 모드명 사용, 단일 모드도 배열
- experts 필드: 단일 모드는 문자열 배열, 복합 모드는 객체 배열(id+modes)
- 투입 모드 SSOT: 모드별 설계 파일이 SSOT, 페르소나 파일은 문서화 목적
- git diff 완전 제거: 외부 도구 비의존 원칙 일관 적용
- 전문가 제외: 확인 메시지 + 언제든 재투입 가능
- 라운드 간 통합 체크: §2.1 수정 반영 단계 5로 삽입
- 리뷰 전 원본 백업: §3.3 `.pre-review.md` + 종료 시 보존/삭제 확인
- RDR 대안 비교 사유: 수용 건 중 대안 비교가 있었던 건에 한해 기록 (선택적)
- 설계서 SPEC/RAT 분리: `<rationale>` XML 태그로 구조적 격리 (스킬 변환 시 태깅)
- shackled 페르소나: 작성자 셀프 체크 관점, 이중 체크 허용, SEC는 DevSecOps 성격
- SPEC/RAT 태깅 규칙: 본문 = SPEC (기본값), 예외만 `<rationale>` 태그. 판별: "빼면 AI 행동 달라지나?" (common-spec §12)
- 스팟 체크 전문가 출처: 별도 페르소나 아닌 inquisitor 도메인 렌즈 전환 (제너럴리스트 역량 활용)
- S+doc 파이프라인 경로: S 체급 + output_type=doc → Step 3-B → Phase 2 → Phase 3 → Phase 6 (Phase 4/5 건너뜀)
- output_type 판정: inquisition 체급 판정 시 산출물 유형(code/runbook/doc)도 함께 판정, 00-summary.md에 기록
- 스킬 설치 구조: 오케스트레이터는 `~/.claude/commands/papillon.md` (루트), 서브스킬은 `~/.claude/commands/papillon/` (서브디렉토리)
- shackled 실행 모드 분리: `normal`(기본) / `tdd`(테스트 우선, `output_type: code` 전용) — 태스크별 상태 파일에 기록, 기본값 normal
- shackled 루트 개념 3축: 설계서 루트 / 구현 루트(태스크별) / 상태 파일 루트 분리. 기존 `project_root`는 deprecated
- shackled sandbox_mode: 파일럿·샌드박스 환경에서 상태 파일 루트를 `context_path` 기준 로컬 루트로 격리. 자동 감지 금지, 명시 선언만 허용
- **수학적 모델링 (2026-04-14)**: bottom-up 빌드 순서 (L0→L5) 채택. 수학화 수준은 "약한 수학화 + 경험 분포 보강" — Claude logprobs 미노출 한계로 이론 분포 form은 관측 불가, N회 호출 경험 분포 `̂P_N` 활용. cross-model 경로는 L4 이후 (예산 선결).
- **L0 투영(π) 옵션 A**: Output → ProjectedSpace 투영의 존재만 L0이 선언, 구체 선택은 use site에서 결정. 측정 문맥마다 진폭 허용 폭을 재조정 가능하게 유지하기 위함.
- **L0 공리 구조**: A0.3(Independence) + A0.4(Stationarity) 결합으로 i.i.d. induce. i.i.d.를 별도 공리로 두지 않음.
- **빠삐용 ↔ ASEWS 관계**: 한 연구 프로그램의 두 축. ASEWS = 인프라(MCP·벡터·그래프·KB), 빠삐용 = 방법론·프로토콜(페르소나·AC·핑퐁·shackled). L4에서 접면.
- **백엔드 필요성**: 전통 백엔드는 불필요하나 "벡터 + 그래프 + 메타데이터 하이브리드" 형태의 비전통 백엔드는 필수 (연구 주제 3개가 종단 데이터·유사도 검색 의존). praxis 존치 논의는 "이 역할이 필요한가"가 아니라 "praxis 구현이 이 역할을 제대로 하는가"가 핵심 판단.
- **호칭/말투**: `~/.claude/CLAUDE.md` §0에 박음. "주인님" 호칭 + 존댓말, 전역·예외 없음.

## Issue-02: 전체 프로젝트 구조 리뷰 (2026-04-08, Claude Web)

상세: `80-Issue/02-Issue-02/00-index-issue-02.md`

| # | 심각도 | 제목 | 솔루션 핵심 | 적용 시점 |
|---|---|---|---|---|
| 1 | 높음 | 설계서 vs 프롬프트 스펙 혼재 | XML 태그로 구조적 격리 | **전체 적용 완료** (4개 설계서 태깅 + 4개 스킬 작성) |
| 2 | 중간 | 컨텍스트 윈도우 미반영 | Phase별 토큰 버짓 + 컨텍스트 리셋 포인트 | 파이프라인 실험 후 |
| 3 | 높음 | 사람 개입 과다 vs PRD 목표 | 확인 지점 3등급 (Gate/Checkpoint/FYI) + 실패 비용 기반 위임 | 파이프라인 실험 후 |
| 4 | 중간 | wtth 모드별 상세 부족 | 모드별 스킵/변형/추가 규칙 명시 | 반영 완료 (설계서 + 스킬) |
| 5 | 중간 | 산출물 생명주기 미정의 | 생명주기 매트릭스 (common-spec) | 파이프라인 실험 후 |
| 6 | 낮음 | 체급 heuristic 환류 부재 | 캘리브레이션 사례 축적 | 파이프라인 실험 후 |
| 8 | 낮음 | shackled §3.1 상위 전제 이탈 감지 L/XL 미검증 | 의도적 미스매치 fixture로 감지율/FP 실측 | L/XL 파일럿 시 |

## Issue-04: S+doc 파이프라인 경로 버그 (2026-04-08) — Closed

풀사이클 실험 중 발견. S 체급 설계 문서 수정 태스크가 Phase 4(code/runbook 전용)로 라우팅되어 코드 리뷰 진입. 해결: S 체급에 output_type 기반 이중 분기 추가 (S+doc → Step 3-B → Phase 2 → Phase 3 → Phase 6).

## Issue-05: Opus × Gemini Debate Findings (2026-04-09)

상세: `80-Issue/05-Issue-05/00-index-issue-05.md`

| # | 분류 | 제목 | 상태 |
|---|---|---|---|
| AI-1 | P1 | L/XL 태스크 간 정합성 — Phase 4 예방 + Phase 5.1 Re-baselining | **Closed** (2026-04-14 상태 동기화, 효과 검증은 Issue-02 #8) |
| AI-2 | P1 | 수렴 판정 강화 — Sign-off ID 인용 강제 + MCP 문자열 검증 + Sampling + 백업 시점 조정 | **Closed** (2026-04-14 상태 동기화) |
| AI-3 | P2 | Inquisition 리스크 고지 강화 — 답변 보류 시 후속 영향 제시 | **Done** |
| AI-4 | P2 | Shackled 진행 불가 시 AI 추론 대응 옵션 필수 제시 | **Done** |
| EXP-1 | 실험 | 페르소나 일관성 — 반박 시 finding 유지 여부 | 실험 대기 |
| EXP-2 | 실험 | 사람 개입 과다 — Gate/Checkpoint/FYI 입력 데이터 수집 | 실험 대기 (→ Issue-02 #3) |
| EXP-3 | 실험 | HANDOFF 자동화 — Phase 5.1/6 자동 생성 | 실험 대기 |

## Issue-03: 파이프라인 수정 경로 (2026-04-08~)

| # | 심각도 | 제목 | 상태 |
|---|---|---|---|
| 00 | 높음 | 수정 경로 미정의 | 반영 완료 (Step 3-B + §2.3) |
| 01 | 높음 | 라운드 간 통합 체크 부재 | 반영 완료 |
| 02 | 높음 | 수렴 판정 조건이 반영 검증 미포함 | **Closed** (2026-04-10, wtth §4.1 반영 — Issue-05 AI-2 솔루션) |
