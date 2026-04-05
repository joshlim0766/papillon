# 51-expert-definitions: 리뷰 전문가 정의

## Context
- **Parent:** [00-index.md](../00-index.md)
- **Related:** [04-design-wtth.md](./04-design-wtth.md)
- **Status:**
  - Work: Completed
  - Review: Approved (Human)

---

## Input / Dependency
- wtth v2 설계: [04-design-wtth.md](./04-design-wtth.md)

---

## 1. 전문가 목록

| 전문가 | 투입 모드 | 기본/선택 | 정의 파일 |
|---|---|---|---|
| [PM](./personas/pm.md) | PRD | 기본 | `personas/pm.md` |
| [ARCH](./personas/arch.md) | PRD, 설계, ADR | 기본 | `personas/arch.md` |
| [BE](./personas/be.md) | 설계 | 기본 | `personas/be.md` |
| [FE](./personas/fe.md) | 설계 | 기본 | `personas/fe.md` |
| [SRE](./personas/sre.md) | 설계, 운영 절차 | 기본 | `personas/sre.md` |
| [SEC](./personas/sec.md) | PRD, 설계, ADR, 운영 절차 | 기본 | `personas/sec.md` |
| [PO](./personas/po.md) | 설계 | 기본 | `personas/po.md` |
| [DBA](./personas/dba.md) | 설계 | 선택적 | `personas/dba.md` |
| [CODE](./personas/code.md) | 코드 | 기본 | `personas/code.md` |
| [TEST](./personas/test.md) | 코드 | 기본 | `personas/test.md` |

---

## 2. 페르소나 규격 및 커스텀

페르소나 작성 규격: [personas/_schema.md](./personas/_schema.md)

- 각 페르소나는 **관점/금기/판단기준/체크리스트** 4축으로 정의된다
- **관점**과 **금기**는 고정 — 역할 경계를 정의한다
- **판단 기준**과 **체크리스트**는 예시이자 최소 기준선 — 맥락에 따라 추가/생략 가능
- 프로젝트 CLAUDE.md에서 페르소나 오버라이드/추가/제거 가능 (규격 참조)

---

## References
- wtth v2 설계: [04-design-wtth.md](./04-design-wtth.md)
- 페르소나 규격: [personas/_schema.md](./personas/_schema.md)
