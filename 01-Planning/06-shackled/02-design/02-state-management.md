# 02-state-management: 상태 관리 및 재개

## Context
- **Parent:** [00-design-shackled.md](./00-design-shackled.md)
- **Related:**
  - [01-cross-check.md](./01-cross-check.md) — cross_check_log 저장
  - [03-blocked-handling.md](./03-blocked-handling.md) — blocked 상태 전이
- **Status:**
  - Work: Draft
  - Review: Reviewing

---

## 1. 루트 개념 및 상태 파일 경로

shackled은 세 종류의 루트 개념을 구분한다. 이전에는 단일 "프로젝트 루트"로 합쳐 처리했으나, 설계서와 구현이 분리된 환경(monorepo, 샌드박스 파일럿 등)에서 충돌이 발생하여 분리한다.

### 1.1. 설계서 루트 (documentation root)

`context_path`(설계서 또는 요구사항)가 속한 디렉토리 체계의 루트. 아래 우선순위로 결정한다.

1. `context_path`가 속한 git repository의 root
2. git repository가 아닌 경우, `context_path`의 상위 디렉토리 중 `00-index.md`가 존재하는 디렉토리
3. 위 두 가지로 결정 불가 시 사람에게 직접 확인

### 1.2. 구현 루트 (implementation root)

태스크의 `code_target`(또는 runbook 저장 경로)이 실제로 쓰이는 디렉토리의 루트. 설계서 루트와 다를 수 있다 (예: monorepo에서 설계는 `docs/`, 구현은 `services/api/`).

- **태스크별로 다를 수 있음.** 각 태스크의 구현 루트는 상태 파일의 tasks[*].implementation_root에 기록한다.
- 결정 기준은 작성자 페르소나가 태스크 파싱 단계(코어 §3.2)에서 선언한다. 모호한 경우 사람에게 확인한다.
- 구현 루트가 설계서 루트와 같으면 명시적으로 동일 경로를 기록한다(생략 금지 — 재개 시 인수인계 명확성 때문).

### 1.3. 상태 파일 루트 (state root)

`.shackled-state.json`이 저장되는 디렉토리의 루트.

기본값: 설계서 루트 (§1.1과 동일 규칙).

**샌드박스 모드 옵션:** 호출 시 `sandbox_mode: true`로 선언한 경우 (파일럿 환경 등) 상태 파일 루트를 `context_path` 기준 로컬 루트로 대체할 수 있다. 이 경우 상태 파일은 설계서·구현 루트와 격리된 샌드박스 영역에 저장되며, 충돌이나 실 프로젝트 상태 오염을 방지한다. `sandbox_mode`는 자동 감지하지 않으며 반드시 명시적으로 선언해야 한다.

### 1.4. 상태 파일 경로

```
{상태 파일 루트}/03-tasks/.shackled-state.json
```

**디렉토리 자동 생성:** 상태 파일 저장 시 `03-tasks/` 디렉토리가 존재하지 않으면 자동 생성한다.

---

## 2. status 필드

| 값 | 설명 | 전이 조건 |
|---|---|---|
| `pending` | 미착수 | 초기 상태 |
| `in-progress` | 진행 중 | 태스크 구현 시작 시 |
| `completed` | 완료 | 사람 확인 승인 시 |
| `blocked` | 진행 불가 | [03-blocked-handling.md](./03-blocked-handling.md) §1 감지 조건 충족 시 |

**전면 재작성 시 전이:** 코어 프로세스(00-design-shackled.md §3.3.3)에서 사람이 "거부(전면 재작성)"를 선택하면 해당 태스크의 status는 `in-progress`를 유지한다. `cross_check_log`는 초기화하지 않고 누적한다.

<rationale>
재작성 시 로그를 초기화하지 않는 이유: 재작성 전 이력도 변천사의 일부이다. "왜 재작성이 필요했는가"의 맥락이 로그에 남아야 동일 실패를 반복하지 않을 수 있다.
</rationale>

---

## 3. 스키마

```json
{
  "context_path": "...",
  "weight": "M",
  "output_type": "code",
  "code_target": "backend",
  "exec_mode": "auto",
  "sandbox_mode": false,
  "documentation_root": "...",
  "state_root": "...",
  "session_id": "uuid-v4",
  "tasks": [
    {
      "id": "TASK-A-01",
      "title": "...",
      "mode": "tdd",
      "implementation_root": "services/api",
      "status": "completed",
      "result_summary": "POST /auth/login, /auth/refresh 엔드포인트 구현",
      "cross_check_log": [
        {
          "round": 1,
          "findings": [
            { "severity": "P1", "description": "...", "resolution": "...", "resolved": true }
          ]
        }
      ]
    },
    { "id": "TASK-A-02", "title": "...", "mode": "normal", "implementation_root": "services/api", "status": "in-progress", "result_summary": null, "cross_check_log": [] },
    { "id": "TASK-A-03", "title": "...", "mode": "normal", "implementation_root": "services/api", "status": "pending", "result_summary": null, "cross_check_log": [] }
  ],
  "last_updated": "YYYY-MM-DDTHH:MM:SS"
}
```

**필드 설명 (v3.2 추가 필드):**
- `sandbox_mode` (boolean): 파일럿/샌드박스 환경 여부. §1.3 참조. 명시 선언 필수, 기본값 `false`.
- `documentation_root` (string): 설계서 루트 절대 경로 (§1.1). 이전 `project_root`를 대체.
- `state_root` (string): 상태 파일 루트 절대 경로 (§1.3). `sandbox_mode`에 따라 결정.
- `tasks[*].mode` (enum: `"normal" | "tdd"`): 태스크별 실행 모드. 코어 설계서 §3.3 참조. 기본값 `"normal"`.
- `tasks[*].implementation_root` (string): 태스크별 구현 루트 절대 경로 (§1.2). 설계서 루트와 같은 경우에도 명시.

**호환성:** `project_root` 필드는 deprecated. 기존 상태 파일 로드 시 `project_root` 값을 `documentation_root`와 `state_root`에 동일하게 매핑하여 읽는다.

---

## 4. 저장 시점

1. 태스크 status 전이 시마다 즉시 저장 (`pending` → `in-progress`, `in-progress` → `completed` 등)
2. 크로스 체크 라운드 완료 시마다 저장 (`cross_check_log` 갱신)
3. 진행 불가 발생 시 ([03-blocked-handling.md](./03-blocked-handling.md) §4)

---

## 5. 낙관적 충돌 감지

상태 파일 저장 시 `session_id`를 기록한다. 다음 저장 전 파일을 다시 읽어 `session_id`가 자기 것인지 확인한다. 다른 세션이 수정한 경우(session_id 불일치) 사람에게 경고하고 선택지를 제시한다:
1. 자기 것으로 덮어쓰기
2. 파일 내용 확인 후 판단
3. 종료

---

## 6. 재개 흐름

`task_id`가 제공되거나 상태 파일이 발견된 경우:

1. 상태 파일을 로드하여 완료/미완료 태스크 현황을 파악한다.
2. 사람에게 현재 상태를 제시한다:
   - 완료 N건 (각 태스크의 제목 + 결과 요약)
   - 진행 중 1건 (있는 경우)
   - 미완료 N건
   - blocked 태스크 (있는 경우, 사유 포함)
3. 재개 지점을 확인한다:
   - `in-progress` 상태 태스크부터 재개 (기본)
   - 사람이 다른 지점을 지정하면 그대로 따른다.
4. 이전 컨텍스트를 다시 로드하고 지정된 태스크부터 코어 §3.3 루프를 재개한다.

**exec_mode 충돌:** 재개 시 호출 파라미터의 `exec_mode`와 상태 파일의 `exec_mode`가 불일치하면 사람에게 어느 쪽을 따를지 확인한다.
