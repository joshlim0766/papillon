# 4: wtth 모드별 상세 파일이 얇음

**심각도:** 중간
**분류:** 공백
**상태:** Open

## 문제

wtth 코어는 5모드를 하나의 공통 메커니즘으로 묶었는데, 모드별 상세 파일(01-review-prd.md, 02-review-design.md, 03-review-task.md)이 너무 얇다.

코어에 "공통 프로세스를 따른다"고만 되어 있고, 각 모드에서 공통 프로세스의 어떤 부분을 변형하는지가 거의 없다:
- 설계 리뷰: 6인 풀에서 뽑는 구조
- PRD 리뷰: 3인 고정
- 코드 리뷰: 의사결정 방식 자체가 다름 (diff 기반)

이 차이들이 공통 메커니즘과 어떻게 상호작용하는지가 불충분하다.

특히 코드 리뷰의 "diff 단위 결정"은 실제로 가장 어려운 부분인데 "오케스트레이터가 영향 범위를 분석"이라고만 되어 있다.

## 참조

- `01-Planning/04-wtth/02-design/00-core.md` §1, §2
- `01-Planning/04-wtth/02-design/01-review-prd.md`
- `01-Planning/04-wtth/02-design/02-review-design.md`
- `01-Planning/04-wtth/02-design/03-review-task.md`
