# 4-1: 다이어그램에 모델명(Opus/Sonnet) 노출

**심각도:** 높음
**분류:** 모순
**상태:** Closed

## 문제

다이어그램에서 "Step 1: 구조화 인터뷰 (Opus)", "Step 3: Draft 생성 (M 체급, Sonnet)" 등 하위 스킬의 모델명을 노출하고 있다. 오케스트레이터는 스킬을 호출하는 것이지 모델을 지정하는 것이 아니므로, 하위 스킬의 모델 선택이 변경되면 papillon 설계서도 수정해야 하는 커플링 발생. "하위 스킬은 단독 실행 가능, papillon에 의존하지 않는다"는 설계 원칙과 충돌.

## 논의

- 모델 선택 책임은 각 스킬/스텝이 자기 설계서에 기재하는 패턴 채택 (inquisition이 이미 이 패턴 사용 중)
- Step 3 Draft 생성은 별도 스킬이 아닌 papillon 내부 로직으로 유지 — Draft → wtth 리뷰 → 사람 확인 사이클이 오케스트레이터 루프이므로 분리 불필요
- Step 3 모델은 Sonnet으로 결정. 근거: 인터뷰 품질은 inquisition(Opus)이, 문서 구조는 common-spec/doc-standard가 보장하므로 초안 작성 자체는 Sonnet이면 충분. 이후 wtth 리뷰 사이클에서 품질 보정


## 처리

5곳 수정:

| 위치 | Before | After |
|---|---|---|
| 다이어그램 Step 1 제목 | `구조화 인터뷰 (Opus)` | `구조화 인터뷰 (inquisition)` |
| 다이어그램 Step 1 설명 | `Opus가 요구사항 분석` | `inquisition이 요구사항 분석` |
| 다이어그램 Step 3 제목 | `Draft 생성 (M 체급, Sonnet)` | `Draft 생성 (M 체급)` |
| 상세 Step 2 제목 | `체급별 분기 (Opus)` | `체급별 분기` |
| 상세 Step 3 제목 | `Draft 생성 (M 체급, Sonnet)` | `Draft 생성 (M 체급)` |

원칙: 모델 선택은 각 하위 스킬 설계서의 책임. 오케스트레이터는 스킬명/역할만 참조.

## 결과

