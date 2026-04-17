# Issue-07: 02-common-spec.md 분할 검토

## 상태
- **Open (보류)** — 2026-04-17 발견. 트리거 조건 도달 시 착수.
- **영향 범위**: `01-Planning/02-common-spec.md` + 이를 참조하는 전 문서·스킬

## 배경

`02-common-spec.md`의 섹션 수가 지속 증가 중이다. 2026-04-17 현재:

- §1 심각도 기준 / §2 RDR / §3 ADR / §4 작업 요약 카드 / §5~§8 (확인 필요) / §9 스킬 포맷 / §9.1 SKILL.md / §10~§11 (확인 필요) / §12 SPEC/RAT 태깅 / §13 파일럿 정량 지표
- **예정**: §14 TDD-ready 규격 (Issue-06 #1 stable 시 흡수 후보)

단일 파일 14개 이상 섹션은 가독성·검색성·참조 유지보수 측면에서 저하 신호. 분할 필요성 검토.

## 분할 후보 축 (미확정)

### 축 A: 관심사별 분할

| 신규 파일 | 담는 섹션 (가설) |
|---|---|
| `02-common-spec/01-severity.md` | §1 심각도 기준 |
| `02-common-spec/02-records.md` | §2 RDR / §3 ADR / §4 작업 요약 카드 |
| `02-common-spec/03-skill-format.md` | §9 스킬 포맷 / §9.1 SKILL.md |
| `02-common-spec/04-authoring.md` | §12 SPEC/RAT 태깅 |
| `02-common-spec/05-metrics.md` | §13 파일럿 정량 지표 |
| `02-common-spec/06-tdd-ready.md` | §14 (Issue-06 #1 흡수) |

### 축 B: 사용처별 분할

| 신규 파일 | 주 사용처 |
|---|---|
| `02-common-spec/wtth.md` | wtth 관련 규격 |
| `02-common-spec/shackled.md` | shackled 관련 규격 |
| `02-common-spec/global.md` | 전역 invariant |
| `02-common-spec/governance.md` | 거버넌스·메트릭·포맷 |

### 축 C: 안정도별 분할

| 신규 파일 | 내용 |
|---|---|
| `02-common-spec/stable.md` | 1년 이상 변경 없음 |
| `02-common-spec/evolving.md` | 활발한 변경 중 |

현 단계에서 **축 A(관심사별)가 기본 추천**. 나머지는 대안.

## 트리거 조건 (착수 기준)

하나라도 충족 시 착수:

1. **섹션 수 ≥ 18개** (현재 14개 + §14 예정 = 15개)
2. **단일 섹션 길이 ≥ 500줄**
3. **참조 깨짐 실측 3건 이상** (섹션 번호 변경으로 외부 문서 링크 depth 오류)
4. **새 섹션 추가 요청 시 "어디에 둘지" 논의가 2회 이상 반복**

트리거 미도달 시 보류 유지. 분할 자체가 규모 있는 리팩토링이며, 조기 분할은 premature abstraction.

## 진행 시 선결 결정

1. 분할 축 (A/B/C 중 택1 또는 혼합)
2. 분할 후 참조 경로 마이그레이션 방식 (일괄 git grep + sed vs 점진적)
3. 하위 파일 간 순서·인덱스 파일 형식
4. 기존 섹션 번호(§N) 참조가 전 프로젝트 몇 군데서 쓰이는지 실측

## 우선순위

**낮음**. Issue-06 우선. 트리거 도달 시 재평가.

## References

- `01-Planning/02-common-spec.md` (현 단일 파일)
- Issue-06 #1 draft: `80-Issue/06-Issue-06/tdd-ready-spec-v0.1.0-draft.md` (§14 흡수 후보)
- HANDOFF 2026-04-17 저녁 엔트리 (분할 필요성 원 발견)
