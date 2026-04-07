# O-2: cyberpink 참조 경로 버전 하드코딩

**심각도:** 낮음
**분류:** outdated
**상태:** Closed

## 문제

References의 `cyberpink task-auto (참조)` 경로에 `1.2.1.5` 버전이 하드코딩. 버전 업데이트 시 깨질 수 있다. 참조용이므로 실질적 영향은 낮음.

## 처리

버전 하드코딩을 와일드카드로 변경: `1.2.1.5` → `*`.

## 결과

PRD References 경로 수정 완료.

