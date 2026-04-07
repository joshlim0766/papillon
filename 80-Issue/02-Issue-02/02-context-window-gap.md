# 2: 컨텍스트 윈도우 제약이 설계에 구체적으로 반영되지 않음

**심각도:** 높음
**분류:** 제약
**상태:** Open

## 문제

파이프라인의 가장 큰 물리적 제약은 Claude의 컨텍스트 윈도우인데, 설계 어디에서도 이걸 정면으로 다루지 않는다.

papillon 오케스트레이터가 하나의 세션에서 inquisition → 체급 판정 → Draft 생성 → wtth 리뷰 → 종결 판단 → shackled 구현 → 코드 리뷰 → 커밋까지 돌리려면, 각 Phase의 프롬프트 + 누적 대화가 윈도우를 채울 수 있다.

- M 체급도 전체 파이프라인을 한 세션에서 소화하기 어려울 수 있음
- wtth 발산 2~3라운드 시 finding + 사람 응답이 상당한 토큰 소모
- L/XL은 세션 분할이 있지만, Phase 중간에 윈도우가 부족해지면 어떻게 하는지 미정의

## 참조

- Issue-01 `22-context-window-constraint.md` — 이전에 이미 지적되었으나 구체적 반영 부족
- `01-Planning/03-papillon/02-design/00-design-papillon.md` Phase 6 "새 세션 시작을 권장한다" 수준만 존재
