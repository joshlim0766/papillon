# 3-1: PRD 산출물에 inquisition, shackled 누락

**심각도:** 높음
**분류:** 용어/참조 일관성
**상태:** Closed

## 문제

PRD(01-prd.md) 산출물 섹션에 `papillon.md`와 `papillon:wtth.md` 두 가지만 나열되어 있다. `inquisition`과 `shackled`가 독립 스킬로 분리되었으므로 PRD에도 반영 필요. papillon 설계서 자체의 문제는 아니지만 cross-reference 불일치.

추가 발견:
- 제약 R2: 커밋 도구 하드코딩 (설계서에서 이미 제거한 도구 의존성)
- 제약 R5: wtth만 단독 실행 가능으로 언급 (inquisition, shackled도 해당)
- Output/Results: 산출물 2개만 나열

## 논의

용어/맥락 불일치는 허용하지 않는다. 승인된 PRD라도 스코프가 실제로 확장된 것이므로 PRD를 수정한다.

## 처리

- 섹션 4 산출물: inquisition, shackled 추가 + 하단 설명 수정
- 제약 R2: 도구 의존성 제거 → "개발 규칙(CLAUDE.md)에 따름"
- 제약 R5: "하위 스킬(wtth, inquisition, shackled) 단독 실행 가능 유지"
- Output/Results: inquisition, shackled 추가

## 결과

2026-04-07 수정 완료.
