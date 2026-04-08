# Issue-05: Opus × Gemini Debate Findings

**리뷰 일시:** 2026-04-09
**대상:** `01-Planning/` 전체 설계서
**리뷰어:** Claude Web (Opus) × Gemini — Josh 오케스트레이션
**원본:** `/Users/jslim/Downloads/debate-findings-2026-04-09.md`

## 즉시 반영 (P1, 2건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| AI-1 | [01-lxl-consistency-guard.md](./01-lxl-consistency-guard.md) | 공백 | L/XL 태스크 간 정합성: Phase 4 예방 + Phase 5.1 Re-baselining | Open |
| AI-2 | [02-signoff-cross-referencing.md](./02-signoff-cross-referencing.md) | 공백 | 수렴 판정 강화: Sign-off ID 인용 강제 + MCP 문자열 일치 검증 | Open (→ Issue-03-02 솔루션) |

## 실험에서 확인 (3건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| EXP-1 | [03-persona-consistency.md](./03-persona-consistency.md) | 검증 | 페르소나 일관성 — 반박 시 finding 유지 여부 관찰 | 실험 대기 |
| EXP-2 | [04-human-intervention-data.md](./04-human-intervention-data.md) | 검증 | 사람 개입 과다 — Gate/Checkpoint/FYI 분류 입력 데이터 수집 | 실험 대기 (→ Issue-02 #3) |
| EXP-3 | [05-handoff-automation.md](./05-handoff-automation.md) | 검증 | HANDOFF 자동화 — Phase 5.1/6에서 자동 생성 시범 | 실험 대기 |

## 기각된 제안

| 제안 | 출처 | 기각 사유 |
|---|---|---|
| AST 파싱 기반 반영 검증 | Gemini | 외부 도구 의존. §4.1.1 원칙 충돌 |
| AI 간 Red-Teaming / Debate | Gemini | §4.1 rationale에서 명시적 금지. 토큰 소모 + 비즈니스 맥락 부재 |
| 에이전트 파업 (Agent Strike) | Gemini | hallucinated finding으로 악용 가능. 기각+사유 기록이 더 안전 |
| 에스컬레이션 (외부 모델 소환) | Gemini | PRD R5 단독 실행 원칙 충돌. AI 동의는 책임 소재가 안 됨 |
| 페르소나 일관성 점수 시스템 | Gemini | 상태 관리는 태스크 진행용이지 페르소나 평가용 아님. 관심사 혼재 |
