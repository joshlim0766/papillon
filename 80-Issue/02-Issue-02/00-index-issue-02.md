# Issue-02: 전체 프로젝트 구조 리뷰

**리뷰 일시:** 2026-04-08
**대상:** papillon 프로젝트 전체 (설계서, PRD, 페르소나, 리뷰 산출물)
**리뷰어:** Claude Web (외부 교차 리뷰)

## 높음 (3건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 1 | [01-design-vs-prompt-spec.md](./01-design-vs-prompt-spec.md) | 구조 | 설계서가 설계 근거와 프롬프트 스펙을 구분하지 않고 혼재 | Open |
| 2 | [02-context-window-gap.md](./02-context-window-gap.md) | 제약 | 컨텍스트 윈도우 제약이 설계에 구체적으로 반영되지 않음 | Open |
| 3 | [03-human-intervention-paradox.md](./03-human-intervention-paradox.md) | 모순 | PRD "사람은 의사결정만" vs 설계의 10곳+ 사람 확인 지점 | Open |

## 중간 (2건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 4 | [04-wtth-mode-detail-gap.md](./04-wtth-mode-detail-gap.md) | 공백 | wtth 모드별 상세 파일이 얇음, 공통 메커니즘과의 상호작용 미정의 | Open |
| 5 | [05-artifact-lifecycle.md](./05-artifact-lifecycle.md) | 공백 | 산출물 9종+의 생명주기·정합성 검증 메커니즘 부재 | Open |

## 낮음 (1건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 6 | [06-weight-class-heuristic.md](./06-weight-class-heuristic.md) | 공백 | 체급 판정 경계 heuristic이 경험적 데이터와 환류되지 않음 | Open |

## 참고 (이슈 아님)

| # | 파일 | 분류 | 요약 |
|---|---|---|---|
| — | [07-meta-learning-loop.md](./07-meta-learning-loop.md) | 강점 | 메타 학습 루프가 실제로 작동하고 있음 — 프로젝트의 핵심 가치 |
