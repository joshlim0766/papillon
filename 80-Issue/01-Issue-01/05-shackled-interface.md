# 5-1: shackled 호출 인터페이스 미정의

**심각도:** 높음
**분류:** 누락
**상태:** Closed

## 문제

wtth 호출 인터페이스는 파라미터(리뷰 대상, 리뷰 모드, 기존 RDR/ADR 경로, 코드베이스 컨텍스트)를 명시적으로 정의하고 있다. shackled 호출 인터페이스는 어디에도 정의되어 있지 않다. shackled에 무엇을 전달하는지(설계서 경로, 태스크 ID, 체급, 실행 모드 4-A/4-B 등)가 누락. shackled 설계서가 아직 작성 전이지만, 오케스트레이터 관점의 "호출 시 전달 정보"는 papillon 설계서에 있어야 한다.

## 논의

- shackled 인터뷰 파일(01-implementation-mode, 02-skill-architecture, 04-execution-and-error)에서 입력 관련 사항 취합
- 산출물 유형(code/runbook)은 인터뷰 결과/설계서에서 오케스트레이터가 판별하여 전달하는 것이 자연스러움 — papillon이 이미 4-A/4-B 판별 로직을 갖고 있으므로
- 재개 시 태스크 ID, 실행 모드(auto/pair)는 선택 파라미터로 분류

## 처리

papillon 설계서 Phase 4에 shackled 호출 인터페이스 테이블 추가:
- `context_path` (필수): 설계서 또는 인터뷰 요약 경로
- `weight` (필수): S/M 체급
- `output_type` (필수): code/runbook — 오케스트레이터가 판별
- `task_id` (선택): 중단 후 재개 시
- `exec_mode` (선택): auto/pair — 기본값 auto

## 결과

papillon 설계서 Phase 4 섹션에 호출 인터페이스 정의 완료.

