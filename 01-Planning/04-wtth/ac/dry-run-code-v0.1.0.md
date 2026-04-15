# wtth Reviewer — CODE AC v0.1.0 Dry Run (수동)

## Context
- **Parent:** [code-v0.1.0.md](./code-v0.1.0.md)
- **일시:** 2026-04-15 (집)
- **방법:** 완전 수동 dry run. Fixture runner 미구현·wtth 스킬 미설치 상태에서 AC 구조 검증용.
- **목적:** AC가 실전에서 발동 가능한지, 구멍이 있는지 확인. 편향을 인정하되 구조적 결함 탐지에 집중.
- **한계:** reviewer 역할(Claude)과 AC 설계자(Claude)가 동일 → confirmation bias 있음. 발견 내용은 "구멍 후보"이며 실제 스킬 실행 dry run에서 재검증 필요.

---

## 1. 절차

1. **AC 미참조 단계**: `personas/code.md`만 읽고 FIX-CODE-01의 code snippet에 대한 finding을 작성.
2. **AC 대조 단계**: 작성된 output을 공통 AC(`common-v0.1.0.md`) + CODE AC(`code-v0.1.0.md`) + fixture expected와 수동 대조.
3. **구멍 기록**: 불일치·과엄격·과관대·모호함을 등급 매겨 기록.

---

## 2. Fixture 입력 (FIX-CODE-01)

```javascript
async function getUser(id) {
  const conn = await pool.getConnection();
  try {
    return await conn.query('SELECT * FROM users WHERE id = ?', [id]);
  } catch (e) {
    console.error('DB error', e);
    return null;
  }
}
```

---

## 3. 생성된 Output (AC 미참조, 페르소나만 참조)

```markdown
## Findings

### 1. `getUser()` DB 커넥션 누수 (P0)

`getUser()`에서 `pool.getConnection()`으로 획득한 `conn`이 성공·실패·예외 어느 경로에서도 `conn.release()`로 반환되지 않습니다. try 블록이 정상 종료되든 catch로 빠지든 release 경로가 없어, 반복 호출 시 커넥션 풀이 고갈되어 전체 서비스가 응답 불가 상태가 됩니다. `try-finally`를 추가하여 모든 경로에서 `conn.release()`를 호출하도록 수정해야 합니다 (P0). [체크리스트: 리소스 누수]

### 2. `getUser()` catch 블록의 에러 삼킴 (P1)

`catch (e)` 블록에서 `console.error`만 하고 `null`을 반환합니다. 호출자 입장에서 "해당 ID의 사용자가 없어서 null"인지 "DB 오류가 발생해서 null"인지 구분할 수 없어, 에러 전파가 끊어집니다. 에러를 다시 던지거나 (`throw e`) 구체적 에러 객체를 반환하도록 수정해야 합니다 (P1). [체크리스트: 에러 처리]
```

---

## 4. AC 대조 결과

### 4.1. 공통 AC invariants

| ID | 규칙 | 결과 | 비고 |
|---|---|---|---|
| INV-WREV-01 | Findings 섹션 1개 이상 | ✅ | `## Findings` 존재 |
| INV-WREV-02 | P0~P3 태그 1회 이상 | ✅ | "(P0)", "(P1)" 등장 |
| INV-WREV-03 | 모호 표현 금지 | ✅ | "꼼꼼히"·"좀 더"·"적절히"·"알아서" 부재 |
| INV-WREV-04 | 길이 100~20000 | ✅ | 약 550자 |
| INV-WREV-05 | scoped required patterns 전수 | ✅ | P[0-3] scope:all 충족 |

### 4.2. CODE 특화 invariants

| ID | 규칙 | 결과 | 비고 |
|---|---|---|---|
| INV-CODE-01 | `[체크리스트: 항목명]` 1회 이상 | ✅ | "[체크리스트: 리소스 누수]", "[체크리스트: 에러 처리]" |
| INV-CODE-02 | 함수명(`foo()`) 또는 파일:라인 | ✅ | `getUser()`, `pool.getConnection()`, `conn.release()` 등 다수 |

### 4.3. FIX-CODE-01 expected 대조

| 필드 | 기대 | 결과 | 비고 |
|---|---|---|---|
| must_match_patterns: "P0" | 포함 | ✅ | `(P0)` 등장 |
| must_match_patterns: "커넥션\|리소스\|누수\|release" | 포함 | ✅ | 4개 키워드 모두 등장 |
| must_match_patterns: `\[체크리스트:\s*리소스\s*누수\]` | 포함 | ✅ | 정확히 일치 |
| must_include: "finally" | 포함 | ✅ | "try-finally" 언급 |
| min_length: 100 | ≥100자 | ✅ | 약 550자 |

**전체 결과: AC 전수 통과.**

---

## 5. 발견된 구멍

AC 전수 통과에도 불구하고 실전에서 터질 가능성이 있는 지점들.

### 5.1. [P1] INV-WREV-01의 heading 형식 경직성

**발견**: 제가 처음 output을 작성할 때 `## Findings`가 아닌 `**Findings**` (bold) 형식으로 쓸 유혹이 있었습니다. Heading으로 쓴 것은 의식적 선택이었고, 실제 reviewer가 매번 `## Findings` heading으로 쓴다는 보장이 없습니다.

**위험**: 실전 reviewer output이 다음 형식이면 false negative 발생:
- `**Findings**` (bold, heading 아님)
- heading 없이 바로 `### 1. ...`로 시작
- `## 검토 결과` (한국어, alternatives에 포함되지만)
- `# 리뷰` (level 1, level 2 요구와 불일치)

**대책 후보**:
1. **페르소나 정의에 output format 규약 추가**: `code.md`에 "output은 반드시 `## Findings` heading으로 시작"을 명시. 페르소나가 format을 유도.
2. **INV-WREV-01 완화**: Findings heading 부재 허용하되, `### N. 제목` 형식의 finding subheading이 최소 1개 있으면 통과.
3. **혼합**: 페르소나에서 format 규약 박되, INV-WREV-01은 subheading fallback 허용.

**권고**: 혼합. Format 규약은 페르소나에서, invariant는 관대하게. 다음 버전 반영 대상.

### 5.2. [P2] fixture expected `must_match_patterns` 정밀도 문제

**발견**: `"\\[체크리스트:\\s*리소스\\s*누수\\]"` 패턴이 이번 output에는 정확히 매칭됐으나, 실전에서 reviewer가 다음 변형으로 쓸 가능성:
- `[체크리스트: 리소스누수]` (공백 없음)
- `[체크리스트: 리소스 누수 처리]` (한 단어 추가)
- `[체크리스트:리소스 누수]` (콜론 뒤 공백 없음)

현재 패턴은 중간 공백은 `\s*`로 허용하지만 추가 단어·조사 변형은 실패.

**대책**: 패턴을 `\[체크리스트:\s*[^\]]*리소스[^\]]*누수[^\]]*\]`로 관대하게 변경. 또는 더 간단히 `\[체크리스트:.*?리소스.*?누수.*?\]`.

### 5.3. [P2] 공통 AC `forbidden_patterns` false positive 위험

**발견**: 현재 금지 목록:
- `꼼꼼히` — 확실히 모호
- `좀\s*더` — "좀 더 구체적으로" 같은 **정당한** 맥락에서도 걸림
- `적절히` — 항상 모호하진 않음 (예: "적절히 null 처리 필요 — 구체적으로 X")
- `알아서` — 대부분 모호

**위험**: reviewer가 "좀 더 구체적 타입 선언 필요"처럼 합리적으로 쓴 경우도 reject.

**대책 후보**:
1. 현재 유지 — false positive는 "구체성 강화 유도"로 긍정 해석
2. 완화 — "좀 더"만 제거 (다른 3개는 대부분 모호)
3. 엄격 — 현재 유지 + reviewer에게 "이 단어를 쓰지 말고 구체적으로 대체"를 프롬프트로 유도

**권고**: 2번(완화). 다음 AC 버전에서 "좀 더" 제거 검토.

### 5.4. [P3] 심각도 태그 형식 관대성

**발견**: 제가 `(P0)` 괄호 포함 형식으로 썼지만 AC는 `P[0-3]` 정규식만 요구. 즉:
- `[P0]`, `P0:`, `- P0`, `심각도 P0` 등 어떤 형식이든 통과
- 반면 `P0`이 없이 `심각도 0` 또는 `Severity: 0`이면 실패

**평가**: 현재 관대함이 적절. 긍정 해석. 바꿀 것 없음.

### 5.5. [P1] 페르소나 정의와 AC의 구조적 중복

**발견**: `personas/code.md`의 "발언 예시 — 좋은 예"가 이미 `[체크리스트: 리소스 누수] (P0)` 형식을 명시합니다. AC는 이 형식을 거울처럼 검증합니다.

**긍정 해석**: 페르소나와 AC가 일관 — 구조적 장점. Reviewer가 페르소나를 따르면 AC를 자동으로 충족.

**부정 해석**: Dry run의 편향이 감소한 게 아니라 **페르소나 정의 자체가 AC를 유도**. "AC를 안 보고" 작성해도 페르소나를 보면 AC 준수. 이는 "AC가 reviewer output을 독립적으로 검증"하는 게 아니라 "AC가 페르소나 규약의 일부"임을 의미.

**함의**:
- Template v3.4·v3.5 수준에서 "AC와 페르소나의 분리 여부" 원칙을 명시할 필요 (부록 A 보강 후보).
- 또는 명시적으로 "AC는 페르소나 규약의 형식 검증자"로 포지셔닝.

### 5.6. [P3] 공통 AC Findings heading alternatives 목록 검증 필요

`Findings`·`검토 결과`·`리뷰 결과`·`지적 사항` 4개로 alternatives 선언. 실제 wtth reviewer가 이 중 어느 표현을 쓰는지는 실제 실행으로 확인 필요. 지금 단계에선 판단 보류.

---

## 6. 정리 — 다음 액션

| # | 등급 | 항목 | 처리 시점 |
|---|---|---|---|
| 1 | P1 | INV-WREV-01 heading 형식 경직성 + 페르소나 output format 규약 추가 | AC v0.1.1 또는 v0.2.0 |
| 2 | P1 | AC ↔ 페르소나 구조적 중복 원칙 정리 (Template v3.4 후보) | Template 차기 수정 시 |
| 3 | P2 | FIX-CODE-01 expected 정규식 관대화 | AC v0.1.1 |
| 4 | P2 | forbidden_patterns "좀 더" 제거 검토 | AC v0.1.1 |
| 5 | P3 | Findings heading alternatives 실측 확정 | 실제 스킬 실행 dry run 시 |
| 6 | P3 | 심각도 태그 형식 관대성 | 유지 |

---

## 7. 한계 고지

본 dry run은 다음 편향을 포함합니다:

- **Reviewer = AC 설계자 동일**: Claude(저)가 페르소나만 참조하려 노력했으나, 완전한 격리 불가. AC를 이미 작성한 기억이 간접적으로 output에 영향.
- **Fixture 1개만 실행**: FIX-CODE-02·03은 미실행. 그쪽 fixture에서 다른 구멍이 튀어나올 수 있음.
- **페르소나 output format 실측 없음**: 실제 reviewer가 어떤 형식으로 출력하는지는 스킬 실행 dry run에서 확인.

**따라서 §5·§6의 발견은 "강한 주장"이 아닌 "구멍 후보"**이며, 실제 스킬 실행 dry run에서 재검증 대상입니다.

---

## References
- CODE AC: [`./code-v0.1.0.md`](./code-v0.1.0.md)
- 공통 AC: [`./common-v0.1.0.md`](./common-v0.1.0.md)
- CODE 페르소나: [`../../personas/code.md`](../../personas/code.md)
- Fixture 정의: CODE AC §4
