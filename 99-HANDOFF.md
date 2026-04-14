# 99-HANDOFF

## 현재 작업 위치
`01-Planning/09-formal/` — 빠삐용 수학적 정의 L0 착수 (2026-04-14)

## 직전 작업: 2026-04-14 묶음 (집)

오늘 진행된 작업 6개 커밋. 큰 흐름은 (1) 이슈 상태 동기화 정리 → (2) 파일럿 정량 지표 프로토콜 신설 → (3) AC 프레임워크 등록 → (4) 빠삐용 수학적 정의 착수.

### 커밋 시계열

| Commit | 내용 |
|---|---|
| `6cd7713` | Issue-05 AI-1·AI-2 + Issue-03-02 상태 동기화 (높음·P1 Open 0건 달성) |
| `36e6592` | 파일럿 정량 지표 프로토콜 신설 — common-spec §13 + `01-Planning/07-metrics/retro-template.md` |
| `00ede23` | AC Template v3.2 + Inquisition AC v0.1.0 + VOCABULARY.yaml 등록 (Claude Web 대화 산출물 레포 반영) |
| `a54de43` | HANDOFF stale 문구 정정 (AC 산출물 "별도 환경 대기" → 레포 반영 완료) |
| `651f1e4` | 빠삐용 수학적 정의 L0 착수 — `01-Planning/09-formal/` 신규 |
| `9d81a73` | L0 셀프 린트 P0 3건 + P1 2건 반영 |

### 핵심 산출물

- **`01-Planning/09-formal/00-index.md`**: L0~L5 층위 인덱스
- **`01-Planning/09-formal/01-l0-scope.md`**: 단일 LLM 호출의 수학적 정의 (P0/P1 린트 반영 완료)
- **`01-Planning/08-ac/ac-template-v3.2.md`**: AC 템플릿 (Hard/Fixture/Semantic 3-layer + Stability + Regression + Drift Budget)
- **`01-Planning/05-inquisition/ac-v0.1.0.md`**: 템플릿 첫 실전 적용
- **`VOCABULARY.yaml`**: 전역 도메인 약어 14종 (레포 루트)
- **`01-Planning/02-common-spec.md` §13**: 파일럿 정량 지표 프로토콜
- **`01-Planning/07-metrics/retro-template.md`**: 파일럿 회고 양식

### 운영 변경

- **`~/.claude/CLAUDE.md` §0 신설**: 호칭 "주인님" 고정, 존댓말 고정, 전역·예외 없음

## 다음 작업: 다음 단계 후보

우선순위 순:

1. **Python 검증 CLI 구현 (회사)** — AC 산출물 전부 레포에 있음. 유틸 4개(`extract_keywords`, `extract_section`, `exclude_section`, `get_sentence_containing`) + fixture runner. 구현 중 예상 숙제: (a) `extract_headings()` 부록 E 보강(v3.3 후보), (b) INV-IQ-03/05의 `resolve_scoped_text()` 공통 함수 추출, (c) `ART-IQ-02` 70% 임계값 실측 후 튜닝.
2. **L0 후속 작업 2건** — `01-Planning/09-formal/01-l0-scope.md` §7 식별 완료: (a) 빠삐용 호출별 `(x, c, θ)` 매핑 (inquisition·wtth·shackled·papillon), (b) 관측 측정 규약 (tokenizer 종류·API usage 수집·로깅 포맷). 산출 형태(단일/다문서)는 매핑 시도 후 결정.
3. **L1 착수 (Prompt 공간 구조)** — invariance, composition. L0 후속 후 또는 병렬.
4. **L0 보류 P1 항목** — P1-2(tokenizer 정확도 가정), P1-4(Claude system/user 분리 가능성). 매핑 작업 시 자연스럽게 부딪힐 가능성, 그때 처리.
5. **L/XL 파일럿 기획 (Issue-02 #8 + #2 동시 검증)** — 의도적 미스매치 fixture 포함. 실제 L/XL 작업 기회 발생 시 끼워넣는 방식.
6. **첫 파일럿 회고** — 다음 파일럿부터 `99-retro.md` 작성. 정량 지표 6개(Q1·Q2·C1·C2·A1·A2) 첫 실측.
7. **ASEWS 모델링 문서 수학적 린트 (L5)** — 본격은 L4 이후. 사전에 ASEWS `docs/modeling/` 6종 훑기는 가능.

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
