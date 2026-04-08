# 99-HANDOFF

## 현재 작업 위치
`01-Planning/` 전체 — 풀사이클 실험 중, Issue-04 수정 반영 완료

## 직전 작업: Issue-04 S+doc 파이프라인 경로 버그 수정 (2026-04-08)

풀사이클 실험 중 발견된 중대 버그. S 체급 + 설계 문서 수정 태스크가 Phase 4(구현, code/runbook 전용)로 라우팅되어 파이프라인이 꼬이는 문제.

**근본 원인:** Phase 4의 `output_type`이 `code`/`runbook`만 존재. 설계 문서 수정은 어디에도 안 맞음. Step 3-B(설계 수정 경로)는 M 체급 전용이라 S에서 진입 불가.

**해결:** S 체급에 `output_type` 기반 이중 분기 추가.
- S + code/runbook → Phase 4 → Phase 5 → Phase 6 (기존 그대로)
- S + doc → Step 3-B(설계 수정) → Phase 2(설계 리뷰) → Phase 3 → Phase 6 (Phase 4/5 건너뜀)

**변경 파일 (설계서):**
- `01-Planning/03-papillon/02-design/00-design-papillon.md` — 흐름도, Step 2 분기, Step 3 스코프, 입출력 매핑, Phase 3 분기
- `01-Planning/05-inquisition/02-design/00-design-inquisition.md` — 체급 판정에 `output_type` 판정 추가 (code/runbook/doc), 핸드오프 브리프 조건

**변경 파일 (스킬):**
- `~/.claude/commands/papillon.md` — 동일 변경사항 반영
- `~/.claude/commands/papillon/inquisition.md` — 동일 변경사항 반영

**추가:** 스킬 설치 구조 변경 — `papillon.md`를 `commands/papillon/` 내부에서 `commands/` 루트로 이동하여 `/papillon`으로 호출 가능하도록 변경. 관련 설계서(PRD, common-spec, papillon, wtth, shackled, 이슈 문서) 경로 일괄 동기화.

## 다음 작업: 파이프라인 실험 계속

Issue-04 수정이 반영된 스킬로 풀사이클 실험 재개. 별도 오퍼스 세션에서 만든 설계 문서를 인퀴지션에 던져서 파이프라인 실험.

**Issue-02 검증:** 파이프라인 실험 과정에서 #2(컨텍스트 윈도우), #3(사람 개입), #5(산출물 생명주기), #6(캘리브레이션) 자연 검증.

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

## Issue-04: S+doc 파이프라인 경로 버그 (2026-04-08) — Closed

풀사이클 실험 중 발견. S 체급 설계 문서 수정 태스크가 Phase 4(code/runbook 전용)로 라우팅되어 코드 리뷰 진입. 해결: S 체급에 output_type 기반 이중 분기 추가 (S+doc → Step 3-B → Phase 2 → Phase 3 → Phase 6).

## Issue-03: 파이프라인 수정 경로 (2026-04-08~)

| # | 심각도 | 제목 | 상태 |
|---|---|---|---|
| 00 | 높음 | 수정 경로 미정의 | 반영 완료 (Step 3-B + §2.3) |
| 01 | 높음 | 라운드 간 통합 체크 부재 | 반영 완료 |
| 02 | 높음 | 수렴 판정 조건이 반영 검증 미포함 | **Open** — 수렴 조건에 "수용 건 전건 반영 완료" 추가 필요 (wtth §4.1) |
