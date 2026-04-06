# 00-index: AI-Driven Work Pipeline

> papillon 네임스페이스 하위에 스킬을 구성. 파이프라인은 자동, 사람은 의사결정만.
> 호출: `/papillon` (오케스트레이터), `/papillon:inquisition` (요구사항 추출 단독), `/papillon:wtth` (리뷰 단독)

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
    ├── 05-design-inquisition.md        # inquisition 스킬 설계서 (요구사항 추출)
    ├── 04-design-wtth/
    │   ├── 00-core.md                  # wtth 코어 (수렴, RDR/ADR, 공통 메커니즘)
    │   ├── 01-review-prd.md            # PRD 리뷰 모드
    │   ├── 02-review-design.md         # 설계 / ADR 리뷰 모드
    │   └── 03-review-task.md           # 코드 / 운영 절차 리뷰 모드
    ├── 06-shackled/
    │   ├── 00-index.md                 # shackled 스킬 인덱스
    │   ├── 01-interview/               # inquisition 산출물
    │   └── 02-design/                  # 설계서 (작성 예정)
    ├── 50-runbook-template.md           # 런북 작성 템플릿
    ├── 51-expert-definitions.md         # 리뷰 전문가 정의 (인덱스)
    └── personas/                        # 개별 페르소나 정의
        ├── _schema.md                   # 페르소나 작성 규격
        ├── pm.md, arch.md, be.md, fe.md
        ├── sre.md, sec.md, po.md, dba.md
        ├── inquisitor.md
        └── code.md, test.md
```

---

## 2. 문서 현황

| 파일 | Work | Review | Summary |
|---|---|---|---|
| 00-problem-and-proposals.md | Completed | None | 문제 진단 + Sonnet 대화 기반 제안 정리 |
| 01-Planning/01-prd.md | Completed | Approved (Human) | PRD — 문제 정의, 목표, 산출물, 제약 조건 |
| 01-Planning/02-common-spec.md | In-Progress | None | 공통 규격 — 심각도, RDR/ADR 포맷, 디렉토리 구조 |
| 01-Planning/03-design-papillon.md | Draft | None | papillon — 파이프라인 Phase, 체급 분류, 호출 인터페이스 |
| 01-Planning/05-design-inquisition.md | Draft | None | inquisition — 요구사항 추출, 문맥 관리, 체급 판정 |
| 01-Planning/04-design-wtth/00-core.md | Draft | None | wtth 코어 — 수렴, RDR/ADR, 공통 메커니즘 |
| 01-Planning/04-design-wtth/01-review-prd.md | Draft | None | PRD 리뷰 모드 |
| 01-Planning/04-design-wtth/02-review-design.md | Draft | None | 설계 / ADR 리뷰 모드 |
| 01-Planning/04-design-wtth/03-review-task.md | Draft | None | 코드 / 운영 절차 리뷰 모드 |
| 01-Planning/06-shackled/ | Draft | None | shackled — 페어 프로그래밍 스킬 (인터뷰 완료, 설계 예정) |
| 01-Planning/50-runbook-template.md | Completed | Approved (Human) | 런북 템플릿 — 필수 구조, 커맨드/검증/롤백 규칙 |
| 01-Planning/51-expert-definitions.md | Completed | Approved (Human) | 전문가 정의 — 10명 관점/금기/판단기준/체크리스트 |

---

## 3. 변경 이력

| 날짜 | 변경 파일 | 내용 | 작성자 |
|---|---|---|---|
| 2026-04-06 | 01-Planning/05-design-inquisition.md | inquisition 스킬 독립 분리 (papillon Step 1 → 별도 설계서) | Human / AI |
| 2026-04-05 | 01-Planning/04-design-wtth/ | wtth 설계서를 관심사별 4파일로 분리 (코어 + PRD/설계/태스크) | AI |
| 2026-04-05 | 01-Planning/personas/ | 페르소나 시스템 강화 — 개별 파일 분리, 통과/실패 기준, 성격 풀 | AI |
| 2026-04-05 | 전체 | 네임스페이스 패키징 구조 반영 + 스킬 개명 | Human / AI |
| 2026-04-03 | 01-Planning/01-prd.md | PRD 확정 (Approved) | Human / AI |

> 최신 5건만 유지. 초과분은 삭제한다.

---

## 4. 현재 진행 중인 작업

- [ ] 공통 규격 리뷰 — 담당: Human — 관련 파일: 01-Planning/02-common-spec.md
- [ ] papillon 설계서 리뷰 — 담당: Human — 관련 파일: 01-Planning/03-design-papillon.md
- [ ] wtth v2 설계서 리뷰 — 담당: Human — 관련 파일: 01-Planning/04-design-wtth/
