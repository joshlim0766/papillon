# O-1: PRD Status "Approved" 이후 스코프 변경

**심각도:** 중간
**분류:** outdated
**상태:** Closed

## 문제

PRD Status가 `Work: Completed, Review: Approved (Human)`이나, shackled이 산출물로 추가되는 등 스코프가 변경됨. Re-approve하거나 변경 이력을 기록하는 것이 바람직.

## 논의

- 급조된 상태(Re-review Required 등)가 아닌, doc-standard §5에 정의된 기존 상태의 역방향 천이로 처리
- Work: Completed → In-Progress (스코프 변경으로 작업 재개)
- Review: Approved → Reviewing (변경사항에 대해 re-review 필요)

## 처리

PRD Status를 `Work: In-Progress, Review: Reviewing`으로 변경.

## 결과

PRD Status 역방향 천이 완료.

