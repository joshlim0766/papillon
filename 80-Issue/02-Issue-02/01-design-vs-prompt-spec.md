# 1: 설계서 vs 프롬프트 스펙 정체성 혼란

**심각도:** 높음
**분류:** 구조
**상태:** Open

## 문제

모든 설계서(design-papillon, design-inquisition, design-shackled, 00-core)가 "왜 이렇게 설계했는가"(설계 근거)와 "프롬프트에 어떤 지시를 넣어야 하는가"(프롬프트 스펙)를 구분하지 않고 섞어놓았다.

**예시:**
- papillon 설계서 §3 Phase 간 입출력 매핑 테이블 → 프롬프트에 거의 그대로 들어갈 내용
- "Sonnet을 쓰는 이유(속도·비용 효율 우선)" → 설계 근거이지 프롬프트에 넣을 내용 아님

## 왜 문제인가

프롬프트 변환 단계에서 매번 "이 문장을 프롬프트에 넣어야 하나 말아야 하나"를 판단해야 한다.
- 설계 의도가 누락될 수 있음
- 역으로 설계 근거가 프롬프트에 섞여 들어가 토큰을 낭비할 수 있음

## 참조

- `01-Planning/03-papillon/02-design/00-design-papillon.md`
- `01-Planning/05-inquisition/02-design/00-design-inquisition.md`
- `01-Planning/06-shackled/02-design/00-design-shackled.md`
- `01-Planning/04-wtth/02-design/00-core.md`
