# wtth Reviewer — CODE 페르소나 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 공통 reviewer AC(`common-v0.1.1.md`)를 기반으로 CODE 페르소나 특이 사항을 override한다.
> Override되지 않은 항목은 공통 AC를 그대로 사용한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer:code"
parent_ac: "wtth:reviewer v0.1.1 (common-v0.1.1.md)"
version: "0.1.1"
previous_version: "0.1.0"
tier: "tier_1"
output_type: "document"

# 공통 AC의 domain_vocabulary에 CODE 고유 어휘를 합집합으로 추가.
# 단순 단어만 나열 (regex·공백 패턴 금지, extract_keywords 부록 D 규약).
# "API"는 영문 대문자 전용 3글자 규칙으로 자동 포착되므로 명시 불필요.
domain_vocabulary_additions: [
  "리소스", "누수", "커넥션", "핸들", "풀",
  "null", "undefined", "경계값", "엣지케이스",
  "에러", "catch", "finally", "예외",
  "인젝션", "시크릿", "키", "토큰",
  "네이밍", "컨벤션", "구현", "설계",
  "락", "동시성", "전략"
]

test_mode: "single_turn"
created_by: "Josh"
created_at: "2026-04-15"
updated_at: "2026-04-16"
```

---

## 1. Skill Identity (override)

```yaml
identity:
  purpose: |
    CODE 페르소나로서 소스 코드 또는 diff를 리뷰하여 버그·엣지케이스·
    에러 처리·성능·구현-설계 정합성·코딩 컨벤션 관련 finding을 생성한다.
    보안 관점의 명백한 패턴(하드코딩된 시크릿, 검증 없는 사용자 입력 사용
    등)도 포함한다.

  trigger_conditions:
    - "코드 리뷰 모드에서 CODE 페르소나가 투입되었을 때"
    - "wtth 단독 실행 시 리뷰 대상이 diff 또는 소스 파일로 판정된 경우"

  non_trigger_conditions:
    - "아키텍처 수준 의견 (ARCH 페르소나 영역)"
    - "테스트 코드 작성 또는 커버리지 분석 (TEST 페르소나 영역)"
    - "자동 포매팅·들여쓰기·스타일 교정 (린터/포매터 영역)"
    - "설계 문서 리뷰 (코드가 아닌 설계 단계)"

  input_spec:
    description: |
      짧은 자기완결적 소스 코드 snippet 또는 diff hunk.
      언어는 fixture별로 명시. fixture의 `meta.language` 참조.
      현 단계(v0.1.1)에서는 code snippet 형식만 지원한다. diff 형식은
      template v3.3 이후 개선 시 fixture에 meta.input_format으로 구분하여 추가.

  output_spec:
    type: "document"
    description: |
      공통 AC의 output_spec을 따른다. CODE 페르소나 특화 요구:
      - 각 finding은 **체크리스트 항목 참조** `[체크리스트: {항목명}]` 1회 이상
      - 위치 참조는 함수명 또는 변수명 포함 권장 (예: `getUser()에서...`)
```

---

## 2. Hard AC override

```yaml
# 공통 AC의 forbidden_patterns / required_patterns는 그대로 승계.
# CODE 특화 추가:

hard_ac_document_additions:
  required_patterns_additional:
    - pattern: "\\[체크리스트:\\s*[^\\]]+\\]"
      scope: "all"
      # 체크리스트 참조 표기 (예: [체크리스트: 리소스 누수]) 최소 1회 이상

  invariants_additional:
    - id: "INV-CODE-01"
      rule: "체크리스트 참조 형식 `[체크리스트: 항목명]`이 최소 1회 이상 등장"
      check: |
        import re
        matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output_text)
        assert len(matches) >= 1

    - id: "INV-CODE-02"
      rule: "위치 참조 — 함수명(괄호 포함) 또는 변수명 형태가 최소 1회 이상"
      check: |
        # 함수 호출 `foo()` 또는 파일:라인 `file.py:42` 류 패턴
        has_func = bool(re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(", output_text))
        has_file = bool(re.search(r"[\w./\\-]+\.\w+:\d+", output_text))
        has_func or has_file
```

---

## 3. Artifact AC (공통 사용, `{persona}` 치환만)

```yaml
# ART-WREV-01의 {persona} 치환:
#   rule: "SKILL.md name == 'wtth:reviewer:code'"
# 나머지 3항목은 공통 AC의 정의를 그대로 사용.
# merged_vocabulary에 domain_vocabulary_additions가 합쳐진다.
```

---

## 4. Fixture AC

```yaml
# v0.1.1 변경: 모든 체크리스트 정규식을 관대화.
# 이유: 격리 dry run에서 reviewer가 페르소나 체크리스트 항목명에 부가 설명을
# 그대로 인용함을 실측 (예: `[체크리스트: 리소스 누수 (커넥션, 파일핸들, 메모리)]`).
# 닫는 대괄호 위치를 고정한 v0.1.0 정규식은 valid 변형을 reject.
# → `[^\]]*` 와일드카드로 부가 설명 허용. 핵심 키워드의 등장과 순서만 검증.

fixtures:
  # === Critical (Tier 1이지만 fixture 설계는 명확히 3개로 시작) ===

  - id: "FIX-CODE-01"
    description: "리소스 누수 — catch 블록에서 connection.release() 누락"
    meta:
      language: "javascript"
      complexity: "high"        # stability 대표 fixture 선정용
    input:
      code_snippet: |
        async function getUser(id) {
          const conn = await pool.getConnection();
          try {
            return await conn.query('SELECT * FROM users WHERE id = ?', [id]);
          } catch (e) {
            console.error('DB error', e);
            return null;
          }
        }
    expected:
      must_match_patterns:
        - "P0"
        - "커넥션|리소스|누수|release"
        - "\\[체크리스트:[^\\]]*리소스[^\\]]*누수[^\\]]*\\]"   # v0.1.1: 부가 설명 허용
      must_include:
        - "finally"
      min_length: 100

  - id: "FIX-CODE-02"
    description: "null 미처리 — undefined 접근 가능"
    meta:
      language: "typescript"
      complexity: "medium"
    input:
      code_snippet: |
        function formatUserName(user: User | null): string {
          return user.name.toUpperCase();
        }
    expected:
      must_match_patterns:
        - "P1"
        - "null|undefined|미처리|null\\s*check"
        - "\\[체크리스트:[^\\]]*null[^\\]]*처리[^\\]]*\\]"     # v0.1.1: 부가 설명 허용
      min_length: 100

  - id: "FIX-CODE-03"
    description: "네이밍 불일치 — 프로젝트 컨벤션과 어긋남"
    meta:
      language: "python"
      complexity: "low"
    input:
      code_snippet: |
        # 프로젝트 컨벤션: snake_case
        def GetUserInfo(user_id):
            return fetch_user(user_id)

        def get_user_posts(userId):   # userId는 camelCase
            return fetch_posts(userId)
    expected:
      must_match_patterns:
        - "P[23]"                   # P2 또는 P3 급
        - "네이밍|컨벤션|snake_case|camelCase|GetUserInfo|userId"
        # v0.1.1: 부가 설명 허용 (네이밍 또는 컨벤션 키워드 포함)
        - "\\[체크리스트:[^\\]]*(네이밍|컨벤션)[^\\]]*\\]"
      min_length: 100

fixture_policy:
  # 공통 AC의 fixture_policy를 승계.
  tier_1_minimum_count_document: 3
  pass_rate: 0.8                  # document Tier 1 기본
  verification: "regex, string match, numeric comparison. LLM 호출 없음."

stability:
  # 공통 AC의 selection_rule에 따라 meta.complexity == 'high' fixture 1개 선정.
  # 여기서는 FIX-CODE-01.
  selected_fixture: "FIX-CODE-01"
  runs: 3
```

---

## 5. Retry Policy

공통 AC의 `retry_policy` 그대로 사용. override 없음.

---

## 6. Tier 2 승격 체크 항목 (CODE 특화)

공통 AC의 Tier 2 승격 후보에 더해, CODE 페르소나에서 실측으로 관찰할 것:

| 관찰 항목 | 승격 트리거 |
|---|---|
| 아키텍처 금기 위반 ("이 모듈 구조 자체가...") | 사례 3회 축적 시 SEM-CODE-01 도입 |
| 체크리스트 참조가 실제 finding과 맞는지 (예: 리소스 누수 finding인데 참조가 `[체크리스트: 네이밍]`) | 사례 2회 시 SEM-CODE-02 도입 |
| 발언 구체성 (함수명·파일명 없이 모호한 지적) | 사례 2회 시 SEM-CODE-03 도입 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-15 | 최초 작성. 공통 AC(common-v0.1.0.md) 기반 CODE 페르소나 override. fixture 3개 (critical). |
| 0.1.1 | 2026-04-16 | 격리 dry run(`dry-run-code-v0.2.0-actual-skill.md` §8.2) 결과 반영. FIX-CODE-01/02/03의 체크리스트 정규식을 `[^\]]*` 와일드카드로 관대화. parent를 common-v0.1.1.md로 갱신. |

## References
- 공통 AC: [`./common-v0.1.1.md`](./common-v0.1.1.md)
- 이전 버전: [`./code-v0.1.0.md`](./code-v0.1.0.md)
- v0.1.1 근거: [`./dry-run-code-v0.2.0-actual-skill.md`](./dry-run-code-v0.2.0-actual-skill.md) §8.2
- CODE 페르소나 정의: [`../../personas/code.md`](../../personas/code.md)
- 리뷰 모드 설계: [`../02-design/03-review-task.md`](../02-design/03-review-task.md)
- papillon AC Template: [`../../08-ac/ac-template-v3.3.md`](../../08-ac/ac-template-v3.3.md)
