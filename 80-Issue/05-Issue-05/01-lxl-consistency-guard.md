# AI-1: L/XL 태스크 간 정합성 — 2단계 가드레일

**심각도:** P1
**분류:** 공백
**상태:** Closed — papillon §3.4(상위 전제 로드) + §3.5.1(Phase 5.1 Re-baselining) + shackled §3.1 반영 완료. 효과 검증(감지율·FP)은 Issue-02 #8(L/XL 파일럿)로 이관

## 문제

L/XL 체급에서 하위 S/M 태스크를 별도 세션으로 수행할 때, 한 태스크의 설계 변경(ADR 등)이 상위 `00-index.md`나 다른 태스크의 전제를 파괴하는지 감지하는 메커니즘이 없다.

- shackled 인테그레이션 체크(§3.4): 한 세션 내 태스크 간 정합성만 확인
- 컨텍스트 스캔(§3.0): index를 읽고 다음 태스크를 제안하지만 전제 충돌 검증은 미수행

## 솔루션: Phase 4 예방 + Phase 5.1 확정

### Phase 4 진입 시 (예방)

- **수정 대상:** `00-design-papillon.md` §3.4
- shackled이 `context_path`를 로드하는 §3.1 진입 단계에서, L/XL 프로젝트인 경우(상위 `00-index.md` 존재 시) 관련 태스크의 의존 관계와 전제 조건을 함께 로드
- shackled 내부 크로스 체크(§6) 시 "상위 전제 이탈 여부"를 체크 항목에 추가
- 이탈 감지 시 진행 불가 처리(§7)의 "설계 불일치" 경로로 분기

### Phase 5.1 Re-baselining (확정)

- **수정 대상:** `00-design-papillon.md` §3.5(코드 리뷰)와 §3.6(커밋) 사이에 신규 섹션 삽입
- 코드 리뷰 완료 후, 커밋 전에 수행하는 경량 단계:
  1. 현재 세션에서 생성된 RDR/ADR 및 설계 변경을 `00-index.md`의 조감도와 대조
  2. 영향받는 대기 태스크에 `[Stale: {변경 사유} — {ADR 번호}]` 플래그 기입
  3. 변경된 ADR 번호를 관련 태스크 카드에 업데이트
  4. 이 과정을 `99-HANDOFF.md`에 자동 기록
- **적용 조건:** L/XL 프로젝트의 하위 S/M 태스크 수행 시에만. 독립 S/M 작업에는 불필요.

<rationale>
Phase 4에서 예방하고 Phase 5.1에서 확정하는 이유: 구현 도중 감지하면 롤백 비용이 최소화되고(예방), 커밋 전에 index를 확정하면 다음 세션의 컨텍스트 스캔이 최신 상태를 읽을 수 있다(확정). Phase 6(커밋) 이후에 하면 이미 늦다.
</rationale>

## 수정 대상

- `01-Planning/03-papillon/02-design/00-design-papillon.md` §3.4, §3.5~§3.6 사이
- `01-Planning/06-shackled/02-design/00-design-shackled.md` §3.1 — 상위 전제 로드 로직

## 참조

- `01-Planning/06-shackled/02-design/00-design-shackled.md` §3.4 인테그레이션
- `01-Planning/03-papillon/02-design/00-design-papillon.md` §3.0 컨텍스트 스캔
