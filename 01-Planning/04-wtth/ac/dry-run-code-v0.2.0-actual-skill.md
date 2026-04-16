# wtth Reviewer — CODE AC v0.1.0 Dry Run (실제 스킬 실행)

## Context
- **Parent:** [code-v0.1.0.md](./code-v0.1.0.md)
- **Predecessor:** [dry-run-code-v0.1.0.md](./dry-run-code-v0.1.0.md) (수동 dry run, 2026-04-15)
- **일시:** 2026-04-16 (회사)
- **방법:** 격리된 일반 에이전트가 wtth 스킬(`~/.claude/commands/papillon/wtth.md`) + CODE 페르소나(`personas/code.md`)만 참조하여 reviewer output 생성. AC 디렉토리(`01-Planning/04-wtth/ac/`)는 명시적으로 읽기 금지하여 confirmation bias 차단.
- **목적:** 수동 dry run의 6건 hole 후보 중 실제 스킬 실행에서 발현되는 것 확정. AC 보강 우선순위 산출.

---

## 1. 절차

1. wtth 스킬 + CODE 페르소나만 격리 에이전트에 제공.
2. FIX-CODE-01 코드 snippet 입력으로 reviewer output 생성.
3. 생성된 output을 공통 AC + CODE AC + fixture expected와 자동 대조.
4. 수동 dry run의 6건 hole 후보 재검증 + 신규 발견 기록.

**bias 격리:** 격리 에이전트는 AC 파일을 읽지 않음. 단, 페르소나 정의는 AC와 일부 중복(체크리스트 항목명 등)이 있어 완전 독립은 불가. 5.5 (페르소나-AC 구조적 중복)는 본 dry run에서도 동일한 한계.

---

## 2. Fixture 입력 (FIX-CODE-01)

CODE AC §4 동일 — JavaScript `getUser()` 함수의 catch 블록 release 누락.

---

## 3. 생성된 Output (격리 에이전트, AC 미참조)

```markdown
[CODE] 코드 품질 P0: 예외 발생 시 DB 커넥션 미해제로 인한 풀 고갈

문제: `getUser()`에서 `pool.getConnection()`으로 획득한 `conn`을 어떤 경로에서도 `release()`하지 않습니다. try 블록 정상 종료 시에도, catch 블록 진입 시에도 커넥션이 풀로 반환되지 않습니다.

왜 문제인가: 함수 호출이 누적될수록 풀의 가용 커넥션이 0에 수렴하며, 이후 `pool.getConnection()` 호출은 무한 대기하거나 타임아웃되어 전체 서비스가 응답 불가 상태가 됩니다. 트래픽이 조금만 발생해도 장애로 직결되는 전형적인 리소스 누수입니다.

수정안: `try/catch` 뒤에 `finally { conn.release(); }` 블록을 추가하여 성공/실패 경로 모두에서 커넥션이 반환되도록 보장해야 합니다.

[체크리스트: 리소스 누수 (커넥션, 파일핸들, 메모리)]

---

[CODE] 코드 품질 P1: 에러 삼킴(swallow) — catch 후 호출자에게 실패 전파 없음

문제: catch 블록에서 `console.error`로 로그만 남기고 `null`을 반환합니다. 호출자는 "사용자가 존재하지 않음(정상)"과 "DB 장애(이상)"를 구분할 수 없습니다.

왜 문제인가: 상위 레이어에서 장애 상황을 인지하지 못해 알람·재시도·서킷브레이커 등 어떤 보호 장치도 작동하지 않습니다. 디버깅 시에도 원인 추적이 어려워집니다.

수정안: 로깅 후 에러를 다시 throw하거나, 도메인 에러로 래핑하여 재던집니다.

[체크리스트: 에러 발생 시 적절한 처리 및 전파]

---

[CODE] 코드 품질 P2: `SELECT *` 사용으로 필요 컬럼 불명확

문제: `SELECT * FROM users`로 전체 컬럼을 가져옵니다. 민감 컬럼이 포함되어 있다면 의도치 않게 호출자에 노출됩니다.

수정안: 호출자가 실제로 필요로 하는 컬럼만 명시적으로 나열합니다.

[체크리스트: 불필요한 복잡도 / 민감 데이터 노출 가능성]
```

---

## 4. AC 대조 결과

### 4.1. 공통 AC invariants

| ID | 규칙 | 결과 | 비고 |
|---|---|---|---|
| INV-WREV-01 | Findings 섹션(또는 alternatives) 1개 이상 | **❌ FAIL** | output에 `##` heading 자체가 없음. `[CODE] 코드 품질 P0: ...` 형식의 평문으로 시작. |
| INV-WREV-02 | 심각도 태그 P0~P3 최소 1회 | ✅ | "P0", "P1", "P2" 등장 |
| INV-WREV-03 | 모호 표현 forbidden patterns 전수 통과 | ✅ | "꼼꼼히"·"좀 더"·"알아서" 부재. "적절한"은 "적절히"와 다른 형태라 false positive 회피 |
| INV-WREV-04 | 길이 100~20000자 | ✅ | 약 1100자 |
| INV-WREV-05 | scoped required patterns 전수 충족 | ✅ | P[0-3] scope:all 충족 |

### 4.2. CODE 특화 invariants

| ID | 규칙 | 결과 | 비고 |
|---|---|---|---|
| INV-CODE-01 | `[체크리스트: 항목명]` 1회 이상 | ✅ | 3건 모두 등장 (체크리스트 항목명에 부가 설명까지 포함됨) |
| INV-CODE-02 | 함수명(괄호) 또는 파일:라인 | ✅ | `getUser()`, `pool.getConnection()`, `conn.release()` 등 |

### 4.3. FIX-CODE-01 expected 대조

| 필드 | 기대 | 결과 | 비고 |
|---|---|---|---|
| must_match_patterns: `"P0"` | 포함 | ✅ | "P0" 등장 |
| must_match_patterns: `"커넥션\|리소스\|누수\|release"` | 포함 | ✅ | 4개 모두 등장 |
| must_match_patterns: `"\\[체크리스트:\\s*리소스\\s*누수\\]"` | 포함 | **❌ FAIL** | 실제 output: `[체크리스트: 리소스 누수 (커넥션, 파일핸들, 메모리)]`. 정규식 `\[체크리스트:\s*리소스\s*누수\]`은 닫는 대괄호가 "누수" 바로 뒤에 와야 매치 — 부가 설명이 끼어 있어 매칭 실패. |
| must_include: `"finally"` | 포함 | ✅ | `finally { conn.release(); }` |
| min_length: 100 | ≥100자 | ✅ | 약 1100자 |

**전체 결과:**
- 공통 AC INV-WREV-01 **FAIL**
- Fixture expected `\[체크리스트:\s*리소스\s*누수\]` 패턴 **FAIL**
- 나머지 8개 invariant 및 4개 expected 항목 PASS

→ **AC 통과 실패.** Hard AC 1건 + Fixture 1건이 fail이라 v3.3 template 기준 reject.

---

## 5. 수동 dry run 6건 hole 재검증

| # | 등급 | 항목 | 수동 dry run 가설 | 실측 결과 |
|---|---|---|---|---|
| 5.1 | P1 | INV-WREV-01 heading 형식 경직성 | "실전 reviewer가 `## Findings` heading을 안 쓸 가능성" | **확정 발현.** 격리 에이전트는 heading 자체를 사용하지 않고 `[CODE] 코드 품질 P0: 제목` 형식의 finding-per-block 구조 채택. AC가 강제하지 않으면 heading 부재 정착 위험. |
| 5.2 | P2 | `must_match_patterns` 정밀도 (체크리스트 패턴) | "공백 변형·추가 단어로 매칭 실패 가능" | **확정 발현.** 격리 에이전트가 페르소나 체크리스트 항목명("리소스 누수 (커넥션, 파일핸들, 메모리)") 전체를 그대로 인용. 정규식이 닫는 대괄호 위치에 의존해 fail. |
| 5.3 | P2 | `forbidden_patterns` false positive 위험 | "정당한 '좀 더' 같은 표현이 reject 받을 위험" | **미발현.** 본 output에 모호 표현 자체가 등장하지 않음 (격리 에이전트가 페르소나 발언 예시의 "나쁜 예"를 회피). 다른 fixture/seed에서 재확인 필요. |
| 5.4 | P3 | 심각도 태그 형식 관대성 | "어떤 형식이든 통과" | **유지 — 긍정 해석.** 격리 에이전트는 `P0: 제목` 형식 채택. `P[0-3]` regex로 catch. AC가 형식 다양성을 허용하는 게 적절. |
| 5.5 | P1 | 페르소나-AC 구조적 중복 | "페르소나 정의 자체가 AC를 유도" | **부분 확인.** 체크리스트 형식 `[체크리스트: ...]`는 페르소나 발언 예시에 박혀있어 격리 에이전트도 그대로 따라함. 단 heading 규약은 페르소나·스킬 어디에도 없어서 fail. → AC가 페르소나 규약의 거울이며, 페르소나에 없는 규약은 catch 못함. |
| 5.6 | P3 | Findings heading alternatives 실측 | "alternatives 4종 중 어느 것을 쓰는지 확인" | **확정: 어느 것도 안 씀.** alternatives 자체가 무용지물. 페르소나/스킬에서 강제하지 않으면 reviewer는 heading 없는 평문 finding 블록을 자연스럽게 선택. |

---

## 6. 신규 발견

### 6.1. [P1] 체크리스트 항목명 인용 길이 변동성

**발견:** 격리 에이전트가 페르소나의 체크리스트 항목명 전체를 그대로 인용 — `[체크리스트: 리소스 누수 (커넥션, 파일핸들, 메모리)]`. 또한 항목 결합도 자유 (`[체크리스트: 불필요한 복잡도 / 민감 데이터 노출 가능성]`).

**위험:** Fixture expected 정규식이 짧은 형태("리소스 누수")만 가정하면 수많은 변형에서 fail.

**대책:**
- (A) 페르소나 발언 예시에 "체크리스트 항목명은 짧게 인용 (예: `리소스 누수`)" 명시
- (B) Fixture expected 정규식을 관대화: `\[체크리스트:[^\]]*리소스[^\]]*누수[^\]]*\]`
- 권장: B + 페르소나에 권장 가이드 추가 (강제 X). AC는 매칭 관대성 우선, reviewer는 자연스러움 우선.

### 6.2. [P2] 페르소나 발언 예시와 실제 output format 불일치

**발견:** 페르소나 `code.md` 발언 예시 형식 — `"...수정해야 합니다 (P0). [체크리스트: 리소스 누수]"` (한 문단 안에 inline 형식).

격리 에이전트 실제 출력 — `[CODE] 코드 품질 P0: 제목 / 문제: ... / 왜 문제인가: ... / 수정안: ... / [체크리스트: ...]` (구조화된 블록 형식).

페르소나 발언 예시는 1문단 1finding을 시사하지만, 실제 reviewer는 multi-section finding으로 확장. 둘 다 valid한 reviewer 출력이지만 AC가 어느 쪽을 가정하느냐로 검증력이 달라짐.

**대책:** 두 형식 모두 통과하도록 AC를 관대하게 두되, 페르소나 정의에 권장 형식 가이드 추가 (현재는 "발언 예시" 1건만 있어 형식 다양성 인지 어려움).

### 6.3. [P3] wtth 스킬의 mode 라우팅이 실측에 영향 없음

**발견:** wtth 스킬을 읽으라고 했지만 격리 에이전트의 reviewer output은 페르소나 정의에서 거의 모든 형식이 결정됨. 스킬은 mode 선택·라운드·수렴 메커니즘 등 메타 흐름을 정의하지만, 단일 finding 형식에는 영향이 적음.

**해석:** 페르소나가 reviewer output의 1차 source-of-truth. 스킬은 오케스트레이션 레이어. 이 분리는 자연스러움. AC가 reviewer output을 검증하려면 페르소나를 일차 reference로 두는 게 맞음.

---

## 7. 정리 — 다음 액션

| # | 등급 | 항목 | 수동 dry run 등급 | 실측 변화 | 처리 시점 |
|---|---|---|---|---|---|
| 1 | **P0** | INV-WREV-01 heading 부재 reject 확정 | (P1 가설) → **P0 확정** | FAIL 발생, 즉각 reject 위험 | **AC v0.1.1 즉시** |
| 2 | **P0** | FIX-CODE-01 체크리스트 정규식 정밀도 | (P2 가설) → **P0 확정** | FAIL 발생 | **AC v0.1.1 즉시** |
| 3 | P1 | 체크리스트 항목명 인용 길이 변동성 (신규) | — | 신규 | AC v0.1.1 (정규식 관대화) + 페르소나 v0.1.1 (가이드) |
| 4 | P1 | AC ↔ 페르소나 구조적 중복 원칙 | (P1 유지) | 유지 — 페르소나 영향력 재확인 | Template v3.4 후보 |
| 5 | P2 | forbidden_patterns "좀 더" 제거 검토 | (P2 유지) | 미발현, 판단 보류 | AC v0.2.0 또는 다른 fixture에서 발현 시 |
| 6 | P2 | 페르소나 발언 예시 vs 실제 output 형식 불일치 (신규) | — | 신규 | 페르소나 v0.1.1 (다중 형식 예시) |
| 7 | P3 | 심각도 태그 형식 관대성 | (P3 유지) | 유지 — 긍정 해석 | 변경 없음 |

---

## 8. AC v0.1.1 권장 변경 (P0 2건 즉시 처리)

### 8.1. 공통 AC `INV-WREV-01` 완화 — heading fallback

```yaml
- id: "INV-WREV-01"
  rule: "Findings 섹션(또는 alternatives) 1개 이상, 또는 finding-per-block 형식 허용"
  check: |
    headings = extract_headings(output)
    alternatives = ["Findings", "검토 결과", "리뷰 결과", "지적 사항"]
    has_heading = any(normalize(h) in [normalize(a) for a in alternatives] for h in headings)
    # Fallback: heading 없어도 finding 블록이 P[0-3] 태그로 명확히 구분되면 통과
    finding_blocks = re.findall(r"P[0-3]", output_text)
    has_heading or len(finding_blocks) >= 1
```

또는 `required_sections.alternatives`에 빈 문자열 허용 + 별도 invariant로 finding 블록 카운트.

### 8.2. CODE AC `FIX-CODE-01` 정규식 관대화

```yaml
- id: "FIX-CODE-01"
  expected:
    must_match_patterns:
      - "P0"
      - "커넥션|리소스|누수|release"
      - "\\[체크리스트:[^\\]]*리소스[^\\]]*누수[^\\]]*\\]"  # 부가 설명 허용
```

같은 패턴으로 `FIX-CODE-02` (`null.*?처리`), `FIX-CODE-03` (`네이밍|컨벤션`)도 검토.

---

## 9. 한계 고지

본 dry run의 격리는 수동 dry run보다 강하지만 완전하지 않음:

- **격리 에이전트 = 같은 Claude 모델**: 동일 모델 가중치라 페르소나 해석 패턴이 비슷할 수 있음. 다른 모델·시드로 N회 실행해야 진정한 multi-sample.
- **Fixture 1개만 실측**: FIX-CODE-02·03 미실행. 그쪽에서 다른 패턴이 튀어나올 수 있음.
- **단일 라운드만**: 2라운드 이후 행동 (경량 통합 체크, 라운드 간 상태 전달) 미검증.
- **wtth 스킬의 §4.1 (전체/집중/최종 검토 라운드) 미실행**: 본 시뮬레이션은 1라운드 reviewer output만 다룸. 라운드 간 일관성·수렴 메커니즘은 별도 dry run 필요.

**따라서 §6 신규 발견 및 §8 권장 변경은 1-fixture-1-run 데이터 기반의 권장**이며, FIX-CODE-02/03 실측 후 보강 가능.

---

## References
- CODE AC: [`./code-v0.1.0.md`](./code-v0.1.0.md)
- 공통 AC: [`./common-v0.1.0.md`](./common-v0.1.0.md)
- CODE 페르소나: [`../../personas/code.md`](../../personas/code.md)
- wtth 스킬: `~/.claude/commands/papillon/wtth.md` (회사 머신 329줄, P0-1 보강 적용)
- 수동 dry run 결과: [`./dry-run-code-v0.1.0.md`](./dry-run-code-v0.1.0.md)
