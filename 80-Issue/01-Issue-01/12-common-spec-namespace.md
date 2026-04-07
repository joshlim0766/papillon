# 3-3: common-spec 네임스페이스에 shackled 누락

**심각도:** 중간
**분류:** 용어/참조 일관성
**상태:** Closed

## 문제

common-spec 섹션 9(네임스페이스 및 패키징 구조)의 설치 구조에 `papillon.md`, `inquisition.md`, `wtth.md` 세 개만 나열. shackled은 아직 설계 전이라 빠진 것으로 이해되지만, papillon 설계서에서 이미 shackled을 Phase 4에서 호출하는 것으로 기술하고 있으므로 참조가 불완전.

## 논의

PRD 재리뷰에서도 동일 건 발견 (X-1). PRD 섹션 4에는 4개 스킬인데 common-spec §9는 3개.

## 처리

common-spec §9에 shackled 추가:
- 설치 구조: `shackled.md ← 구현 엔진 (/papillon:shackled)`
- 호출 방식 테이블: `/papillon:shackled` | 구현 엔진 단독 실행

## 결과

common-spec §9 설치 구조 + 호출 방식 테이블에 shackled 반영 완료.

