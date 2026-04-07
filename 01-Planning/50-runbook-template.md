# 50-runbook-template: 운영 절차서(런북) 작성 템플릿

## Context
- **Parent:** [00-index.md](../00-index.md)
- **Related:** [03-papillon/00-index.md](./03-papillon/00-index.md), [04-wtth/02-design/00-core.md](./04-wtth/02-design/00-core.md)
- **Status:**
  - Work: Completed
  - Review: Approved (Human)

---

## Input / Dependency
- papillon 설계서: [03-papillon/02-design/00-design-papillon.md](./03-papillon/02-design/00-design-papillon.md) — Phase 4-B에서 이 템플릿을 사용

---

## 1. 런북 필수 구성 요소

모든 런북은 아래 섹션을 포함해야 한다.

### 1.1. 헤더

```markdown
# 런북: {작업 제목}

**작성일:** YYYY-MM-DD
**대상 환경:** {production / staging / etc.}
**예상 소요 시간:** {시간}
**영향 범위:** {영향받는 서비스, 사용자}
**롤백 가능 여부:** 가능 / 부분 가능 / 불가능 (사유 명시)
```

### 1.2. 사전 조건

실행 전에 충족되어야 하는 조건 목록. 각 조건에 **확인 커맨드**를 포함한다.

```markdown
## 사전 조건

| # | 조건 | 확인 커맨드 | 기대값 |
|---|---|---|---|
| 1 | V2 이미지 빌드 완료 | `docker images \| grep v2` | v2-tag 존재 |
| 2 | DB 마이그레이션 완료 | `flyway info -url=...` | Success |
| 3 | 관련 팀 공지 완료 | (수동 확인) | Slack #ops 공지 확인 |
```

### 1.3. 실행 단계

각 단계는 아래 구조를 따른다.

```markdown
### Step N: {단계 제목}

**사전 조건:** {이전 Step 완료 조건 또는 "없음"}

**실행:**
\```bash
{복사해서 바로 실행 가능한 커맨드}
\```

**검증:**
\```bash
{실행 결과를 확인하는 커맨드}
# 기대값: {기대하는 출력 또는 상태}
\```

**롤백:**
\```bash
{이 단계를 되돌리는 커맨드}
\```

**이 시점 시스템 상태:** {이 단계 완료 후 시스템의 상태를 서술}
```

#### 필수 규칙

- R-01. **실행 커맨드**는 복사-붙여넣기로 바로 실행 가능해야 한다. 서술형 지시("manifest를 적용하세요") 금지.
- R-02. **검증 커맨드**는 모든 단계에 필수. 기대값을 명시한다.
- R-03. **롤백 커맨드**는 모든 단계에 필수. 롤백 불가능한 단계는 사유를 명시한다.
- R-04. **시스템 상태**는 모든 단계에 필수. 해당 시점에서 트래픽 방향, 살아있는 컴포넌트, 데이터 상태 등을 명시한다.
- R-05. 환경변수, 경로, 네임스페이스 등은 플레이스홀더가 아닌 **실제 값**을 기재한다. 불가능한 경우 헤더에 변수 치환표를 둔다.

### 1.4. 롤백 계획

전체 작업의 롤백 절차를 역순으로 정리한다.

```markdown
## 전체 롤백 계획

실행 단계의 역순으로 수행한다.

| 복원 대상 | 커맨드 | 비고 |
|---|---|---|
| Step 3 롤백 | `kubectl argo rollouts set-weight v2-rollout 0 -n production` | |
| Step 2 롤백 | `kubectl scale deployment v2 --replicas=0 -n production` | |
| Step 1 롤백 | (롤백 불필요 — 읽기 전용 작업) | |
```

### 1.5. 완료 확인

모든 단계 완료 후 최종 상태를 확인하는 체크리스트.

```markdown
## 완료 확인

| # | 확인 항목 | 커맨드 | 기대값 | 결과 |
|---|---|---|---|---|
| 1 | V2 트래픽 100% | `kubectl argo rollouts status ...` | weight=100 | |
| 2 | V1 Pod 종료 | `kubectl get pods -l app=v1` | No resources | |
| 3 | 에러율 정상 | `curl -s grafana.internal/...` | error_rate < 0.1% | |
```

---

## 2. 운영 절차 리뷰 시 검증 항목

이 템플릿으로 작성된 런북을 wtth 운영 절차 리뷰 모드에서 검증할 때, 전문가들은 아래를 확인한다.

| 검증 항목 | 내용 |
|---|---|
| 실행 순서 안전성 | 각 단계 시점의 시스템 상태를 추적하여 서비스 중단 가능성 확인 |
| 커맨드 정합성 | 커맨드가 실제로 실행 가능한가, 문법 오류, 환경변수/경로 확인 |
| 롤백 커맨드 | 각 단계의 롤백이 실제로 동작하는가, 누락 없는가 |
| 검증 커맨드 | 각 단계의 성공 판단 기준이 명확한가 |
| 시스템 상태 연속성 | Step N의 시스템 상태가 Step N+1의 사전 조건과 일치하는가 |

---

## References
- papillon 설계서 Phase 4-B: [02-design-papillon.md](./02-design-papillon.md)
