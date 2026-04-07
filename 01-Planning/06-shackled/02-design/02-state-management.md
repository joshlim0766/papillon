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

## 1. 상태 파일

shackled은 진행 중 상태를 아래 파일에 저장한다:

**프로젝트 루트 결정 규칙:** 아래 우선순위로 결정한다.
1. `context_path`가 속한 git repository의 root
2. git repository가 아닌 경우, `context_path`의 상위 디렉토리 중 `00-index.md`가 존재하는 디렉토리
3. 위 두 가지로 결정 불가 시 사람에게 직접 확인

```
{프로젝트 루트}/03-tasks/.shackled-state.json
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

**전면 재작성 시 전이:** 코어 프로세스(00-design-shackled.md §3.3.3)에서 사람이 "거부(전면 재작성)"를 선택하면 해당 태스크의 status는 `in-progress`를 유지한다. `cross_check_log`는 초기화하지 않고 누적한다 (재작성 전 이력도 변천사의 일부).

---

## 3. 스키마

```json
{
  "context_path": "...",
  "weight": "M",
  "output_type": "code",
  "code_target": "backend",
  "exec_mode": "auto",
  "project_root": "...",
  "session_id": "uuid-v4",
  "tasks": [
    {
      "id": "TASK-A-01",
      "title": "...",
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
    { "id": "TASK-A-02", "title": "...", "status": "in-progress", "result_summary": null, "cross_check_log": [] },
    { "id": "TASK-A-03", "title": "...", "status": "pending", "result_summary": null, "cross_check_log": [] }
  ],
  "last_updated": "YYYY-MM-DDTHH:MM:SS"
}
```

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
