# 00-index: AI-Driven Work Pipeline

> papillon 네임스페이스 하위에 스킬을 구성. 파이프라인은 자동, 사람은 의사결정만.
> 호출: `/papillon` (오케스트레이터), `/papillon:wtth` (리뷰 단독)

---

## 1. 디렉토리 구조

```text
root/
├── 00-index.md
├── 00-problem-and-proposals.md          # 문제 분석 및 초기 제안 (2026-04-02 대화 기반)
└── 01-Planning/
    ├── 01-prd.md                        # PRD
    ├── 02-common-spec.md               # 공통 규격 (심각도, RDR/ADR, 디렉토리 구조)
    ├── 03-design-papillon.md           # papillon 스킬 설계서
    ├── 04-design-wtth.md         # wtth v2 스킬 설계서
    ├── 50-runbook-template.md           # 런북 작성 템플릿
    └── 51-expert-definitions.md         # 리뷰 전문가 정의
```

---

## 2. 문서 현황

| 파일 | Work | Review | Summary |
|---|---|---|---|
| 00-problem-and-proposals.md | Completed | None | 문제 진단 + Sonnet 대화 기반 제안 정리 |
| 01-Planning/01-prd.md | Completed | Approved (Human) | PRD — 문제 정의, 목표, 산출물, 제약 조건 |
| 01-Planning/02-common-spec.md | Draft | None | 공통 규격 — 심각도, RDR/ADR 포맷, 디렉토리 구조 |
| 01-Planning/03-design-papillon.md | Draft | None | papillon — 파이프라인 Phase, 체급 분류, 호출 인터페이스 |
| 01-Planning/04-design-wtth.md | Draft | None | wtth v2 — 4모드, 전문가 풀, 수렴 메커니즘 |
| 01-Planning/50-runbook-template.md | Completed | Approved (Human) | 런북 템플릿 — 필수 구조, 커맨드/검증/롤백 규칙 |
| 01-Planning/51-expert-definitions.md | Completed | Approved (Human) | 전문가 정의 — 10명 관점/금기/판단기준/체크리스트 |

---

## 3. 변경 이력

| 날짜 | 변경 파일 | 내용 | 작성자 |
|---|---|---|---|
| 2026-04-03 | 01-Planning/02-common-spec.md | 최초 작성 — 공통 규격 분리 | AI |
| 2026-04-03 | 01-Planning/03, 04 | 설계서 리넘버링 + 공통 부분을 02로 분리 | AI |
| 2026-04-03 | 01-Planning/50-runbook-template.md | 최초 작성 — 런북 템플릿 (Approved) | AI |
| 2026-04-03 | 01-Planning/01-prd.md | PRD 확정 (Approved) | Human / AI |
| 2026-04-03 | 00-index.md | 최초 작성 | AI |

> 최신 5건만 유지. 초과분은 삭제한다.

---

## 4. 현재 진행 중인 작업

- [ ] 공통 규격 리뷰 — 담당: Human — 관련 파일: 01-Planning/02-common-spec.md
- [ ] papillon 설계서 리뷰 — 담당: Human — 관련 파일: 01-Planning/03-design-papillon.md
- [ ] wtth v2 설계서 리뷰 — 담당: Human — 관련 파일: 01-Planning/04-design-wtth.md
