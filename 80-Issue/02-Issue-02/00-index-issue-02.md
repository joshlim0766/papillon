# Issue-02: 전체 프로젝트 구조 리뷰

**리뷰 일시:** 2026-04-08
**대상:** papillon 프로젝트 전체 (설계서, PRD, 페르소나, 리뷰 산출물)
**리뷰어:** Claude Web (외부 교차 리뷰)

## 높음 (3건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 1 | [01-design-vs-prompt-spec.md](./01-design-vs-prompt-spec.md) | 구조 | 설계서가 설계 근거와 프롬프트 스펙을 구분하지 않고 혼재 | **Closed** (2026-04-10) |
| 2 | [02-context-window-gap.md](./02-context-window-gap.md) | 제약 | 컨텍스트 윈도우 제약이 설계에 구체적으로 반영되지 않음 | Open (심각도 중간으로 하향) |
| 3 | [03-human-intervention-paradox.md](./03-human-intervention-paradox.md) | 모순 | PRD "사람은 의사결정만" vs 설계의 10곳+ 사람 확인 지점 | Open — 파이프라인 실험 후 |

## 중간 (2건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 4 | [04-wtth-mode-detail-gap.md](./04-wtth-mode-detail-gap.md) | 공백 | wtth 모드별 상세 파일이 얇음, 공통 메커니즘과의 상호작용 미정의 | **Closed** (2026-04-16, 설계서 + 스킬 반영) |
| 5 | [05-artifact-lifecycle.md](./05-artifact-lifecycle.md) | 공백 | 산출물 9종+의 생명주기·정합성 검증 메커니즘 부재 | Open |

## 낮음 (2건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 6 | [06-weight-class-heuristic.md](./06-weight-class-heuristic.md) | 공백 | 체급 판정 경계 heuristic이 경험적 데이터와 환류되지 않음 | Open |
| 8 | [08-shackled-lxl-premise-deviation.md](./08-shackled-lxl-premise-deviation.md) | 공백 | shackled §3.1 "상위 전제 이탈 감지" L/XL 체급 검증 미완 | Open — L/XL 파일럿 후 |

## 제안된 적용 시점

| 시점 | 이슈 | 솔루션 핵심 |
|---|---|---|
| **스킬 변환 사이클** | #1 설계 vs 프롬프트 | `<rationale>` XML 태그로 구조적 격리 (inquisition → wtth → shackled → papillon 순차) |
| **wtth 스킬 작성 시** | #4 wtth 모드별 상세 | 모드별 스킵/변형/추가 규칙 명시 |
| **파이프라인 실험 후** | #2 컨텍스트 윈도우 | Phase별 토큰 버짓 + 컨텍스트 리셋 포인트 |
| **파이프라인 실험 후** | #3 사람 개입 과다 | 확인 지점 3등급 분류 (Gate/Checkpoint/FYI) + 실행 데이터 기반 |
| **파이프라인 실험 후** | #5 산출물 생명주기 | 생명주기 매트릭스 (common-spec에 추가) |
| **파이프라인 실험 후** | #6 체급 heuristic | 캘리브레이션 사례 축적 |
| **L/XL 파일럿 시** | #8 상위 전제 이탈 감지 | 의도적 미스매치 fixture로 감지율/FP 실측 |

## 참고 (이슈 아님)

| # | 파일 | 분류 | 요약 |
|---|---|---|---|
| — | [07-meta-learning-loop.md](./07-meta-learning-loop.md) | 강점 | 메타 학습 루프가 실제로 작동하고 있음 — 프로젝트의 핵심 가치 |
