# AI-3: Inquisition 리스크 고지 강화

**심각도:** P2
**분류:** 공백
**상태:** Open

## 문제

inquisition §2.4의 Meta-Reasoning은 "이 질문이 설계의 어떤 부분에 영향을 주는지"를 설명하지만, 답변을 보류했을 때의 구체적 영향(기회비용)은 제시하지 않는다. 사람이 "나중에 결정하겠다"고 할 때 그 보류가 미치는 파급을 인지하지 못할 수 있다.

## 솔루션: Meta-Reasoning 확장

- **수정 대상:** `01-Planning/05-inquisition/02-design/00-design-inquisition.md` §2.4
- **변경 내용:** 기존 "의도 노출" 항목에 추가:
  - 질문 시 **"답변 보류 시 후속 설계에 미치는 구체적 영향"**을 함께 제시한다
  - 톤 가이드: "시스템이 무너진다" 등 위협적 표현 금지. **"X와 Y가 미확정 상태로 남게 됩니다"** 수준의 사실 전달 톤 유지
  - INQUISITOR 페르소나의 "원만하고 차분한 톤" 원칙 준수

<rationale>
역할 경계 침범이 아닌 이유: 리스크 고지는 솔루션 제안(금지)이 아니라 현상 설명(허용)이다. "Redis를 쓰세요"는 금지지만 "캐시 전략이 미정이면 설계서의 응답 시간 목표가 검증 불가 상태로 남습니다"는 사실 전달이다.
</rationale>

## 수정 대상

- `01-Planning/05-inquisition/02-design/00-design-inquisition.md` §2.4

## 참조

- `01-Planning/personas/inquisitor.md` — 페르소나 톤 원칙
