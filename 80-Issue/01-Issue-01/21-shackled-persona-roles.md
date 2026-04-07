# X-3: shackled 페르소나 역할 분담(작성자/크로스 체커) 미반영

**심각도:** 중간
**분류:** 참조 일관성
**상태:** Closed

## 문제

설계서 §3.4에서 shackled 전용 페르소나를 CODE, BE, FE, SRE, SEC로 플랫하게 나열. 인터뷰 결과(`03-persona-and-review.md`)에서는 작성자/크로스 체커 역할 분담이 확정:
- shackled-CODE(작성자) + shackled-BE 또는 shackled-FE(크로스 체커)
- shackled-SRE(작성자) + shackled-SEC(크로스 체커)

PRD 수준에서는 플랫 나열로 충분할 수 있으나, 설계서에는 역할 구분이 반영되어야 함.

## 논의

인터뷰에서 확정된 작성자/크로스 체커 쌍 구조를 설계서에 반영.

## 처리

플랫 나열을 작성자/크로스 체커 쌍으로 구조화: 코드(CODE + BE/FE), 런북(SRE + SEC), 풀스택(CODE + BE + FE).

## 결과

papillon 설계서 §3.4 전용 페르소나 항목 수정 완료.

