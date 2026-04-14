# Papillon Skill Acceptance Criteria Template v3.3

> 설계문서가 곧 test spec이다.
> 모든 AC는 검증 가능한 형태로 기술한다.
> 검증 비용과 스킬 위험도에 비례하여 AC 깊이를 조절한다.
> **동일 input에 대한 output 일관성(Stability)은 모든 Tier에서 검증한다.**

## v3.2 → v3.3 변경 요약

첫 Python 구현(`tools/ac-validator/`) 과정에서 발견된 스펙 공백 2건을 메움.

1. **부록 D 토크나이저 재정의** — 스크립트별 연속 토큰 추출로 전환. 혼합 스크립트 토큰("reviewer를", "TW는")이 자동 분리되어 도메인 vocabulary 매칭이 제대로 동작한다.
2. **부록 D 한글 1글자 목적격 조사 제거 단계 신설** — "결과를"→"결과", "초안을"→"초안". '을'/'를'만 대상이며 '으로' 같은 2자 조사는 보존.
3. **부록 E `extract_headings()` 명세 추가** — 문서 내 모든 heading을 normalize된 형태로 추출. `extract_section()` 내부 구현의 공통 기반이며, inquisition AC `INV-IQ-01`의 `output_headings` 참조를 정당화한다.

v3.3은 v3.2와 출력 호환되지 않는 경우가 있다 (예: 부록 D example 1/3이 v3.3에서만 spec을 만족). v3.2를 기반으로 작성된 스킬 AC는 재검증이 필요하다.

---

## Tier 분류 기준

```yaml
tier_decision:
  tier_1:
    description: "기본. 모든 스킬에 적용."
    criteria:
      - "신규 스킬"
      - "파이프라인 내 단일 단계 담당"
      - "output 오류가 후속 단계에서 catch 가능"
    includes:
      - Skill Identity
      - Hard AC (invariants + stability)
      - Artifact AC
      - Fixture AC (3~5개, output_type별 pass_rate 차등)
      - Retry Policy

  tier_2:
    description: "선택. 아래 조건 중 하나 이상 해당 시."
    criteria:
      - "파이프라인 전체 흐름에 영향 (orchestrator, gate 판정 등)"
      - "output 오류가 후속 단계에서 catch 불가 (silent failure)"
      - "보안/비용/데이터 무결성에 직접 영향"
      - "3개 이상의 다른 스킬이 이 스킬의 output에 의존"
      - "downstream 전체 품질을 결정하는 상류 스킬"
    adds:
      - Semantic AC
      - Regression AC
      - Drift Budget

  default: "tier_1"

  promotion:
    trigger: "동일 스킬에서 HITL escalation 3회 누적"
    action: "propose_to_human"

  demotion:
    trigger: "Tier 2에서 10회 연속 전체 pass AND 해당 기간 HITL 0회"
    action: "propose_to_human"
```

---

## Output Type 분류

```yaml
output_type:
  structured:
    description: "JSON, YAML 등 파싱 가능한 정형 output"
    examples: ["reviewer 선택", "task sizing 결과", "risk classification"]
    hard_ac_strategy: "schema validation + invariant assertion"
    fixture_pass_rate: 1.0

  document:
    description: "Markdown, 설계서, 리뷰 코멘트 등 비정형 문서 output"
    examples: ["설계 문서 초안", "코드 리뷰 피드백", "구현 계획서", "ADR"]
    hard_ac_strategy: "구조 검증 (필수 섹션 존재) + 길이/포맷 제약"
    fixture_pass_rate: 0.8

  code:
    description: "소스 코드, 스크립트, 설정 파일 등"
    examples: ["구현 코드", "테스트 코드", "CI/CD 설정"]
    hard_ac_strategy: "syntax validation + lint + 실행 가능성"
    fixture_pass_rate: 1.0

  hybrid:
    description: "위 유형이 혼합된 output"
    examples: ["코드 + 설명 문서", "설계서 내 JSON 스키마 포함"]
    hard_ac_strategy: "블록 추출 후 각 부분에 해당 유형 검증 개별 적용"
    fixture_pass_rate: 0.9
    parsing_rules:
      code_blocks: "``` 펜스로 감싸진 블록 → code variant 적용"
      json_blocks: "```json 또는 ```yaml 블록 → structured variant 적용"
      remaining: "위 블록 제외 나머지 → document variant 적용"
```

---

## 메타 정보

```yaml
skill_name: ""
version: ""
previous_version: ""              # null이면 regression AC 비활성
tier: ""                          # tier_1 | tier_2
output_type: ""                   # structured | document | code | hybrid
domain_vocabulary: []             # 이 스킬 고유의 도메인 용어 (길이 기준 무시, keyword로 강제 채택)
                                  # 예: ["핑", "퐁", "심문", "라운드"]
                                  # global vocabulary(VOCABULARY.yaml)와 합산하여 사용
test_mode: ""                     # single_turn | multi_turn
                                  # single_turn: 1회 생성으로 output 검증
                                  # multi_turn: 대화형 상호작용 포함 검증 (별도 benchmark track)
created_by: ""
created_at: ""
updated_at: ""
```

---

## 1. Skill Identity

모든 Tier 공통.

```yaml
identity:
  purpose: ""
  trigger_conditions:
    - ""
  non_trigger_conditions:
    - ""
  input_spec:
    description: ""
  output_spec:
    type: ""                      # structured | document | code | hybrid
    description: ""
```

---

## 2. Hard AC

output_type에 따라 variant가 달라진다.
**모든 variant에 Stability Invariant가 포함된다.**

### 공통: Stability Invariant

```yaml
stability:
  tier_1_runs: 3
  tier_2_runs: 5
  check: |
    모든 실행 결과가 Hard AC invariants를 전수 통과해야 한다.
    (output이 매번 동일할 필요는 없음. 각 실행이 개별적으로 invariant를 만족하면 pass.)
    ※ stability(개별 fixture 내부 일관성)와 fixture_pass_rate(fixture 집합 통과율)는
      다른 개념임. 값이 우연히 같을 수 있으나 측정 대상이 다름.
  fixture_consistency: |
    동일 fixture input에 대해 N회 실행 결과의 expected 조건 충족 여부가
    모두 동일해야 한다. (3회 중 2회 pass, 1회 fail이면 stability fail.)
    단, output_type: document인 경우 N회 중 (N-1)회 이상 동일 판정이면 pass.

  optimization:
    policy: "대표 fixture 선택 실행"
    selection_rule:
      tier_1: "fixture 중 complexity 최상위 1개에만 stability runs 적용"
      tier_2: "fixture 중 critical 전원 + major 1개(랜덤)에만 stability runs 적용"
    fallback: |
      대표 fixture가 stability fail → 즉시 전체 fixture로 stability 재검증.
      (평소엔 싸게, 문제 생기면 깊게.)
```

### Variant A: Structured Output

```yaml
hard_ac_structured:
  schema:
    required_keys: []
    types: {}
    constraints: {}

  invariants:
    - id: ""
      rule: ""
      check: ""                   # Python expression. output 변수로 접근.

  verification: "assertion 자동 실행. 1개라도 fail → reject."
```

### Variant B: Document Output

```yaml
hard_ac_document:
  required_sections:
    - heading: ""
      level: 2
      required: true

  format_constraints:
    min_length_chars: 0
    max_length_chars: 0

    forbidden_patterns:
      # 각 패턴에 적용 범위(scope)를 명시.
      # scope 옵션:
      #   "all"                    — 문서 전체에서 검사
      #   "exclude_section:X"      — 섹션 X를 제외한 나머지에서 검사
      #   "only_section:X"         — 섹션 X 안에서만 검사
      - pattern: ""
        scope: "all"
      # 예:
      # - pattern: "TODO"
      #   scope: "exclude_section:미결 사항"
      # - pattern: "\\[placeholder\\]"
      #   scope: "all"

    required_patterns:
      # scope 옵션은 forbidden_patterns와 동일.
      - pattern: ""
        scope: "all"
      # 예:
      # - pattern: "## 개요"
      #   scope: "all"
      # - pattern: "확정"
      #   scope: "only_section:기능 요구사항"

  invariants:
    - id: ""
      rule: ""
      check: ""

  verification: "구조 파싱 + regex 매칭 자동 실행. 1개라도 fail → reject."
```

### Variant C: Code Output

```yaml
hard_ac_code:
  language: ""
  syntax_valid: true
  lint_clean: false
  executable: false

  invariants:
    - id: ""
      rule: ""
      check: ""

  verification: "syntax check + lint + invariant assertion. 1개라도 fail → reject."
```

### Variant D: Hybrid Output

```yaml
hard_ac_hybrid:
  parsing:
    code_block_fence: "```"
    json_yaml_fence: ["```json", "```yaml"]
    remaining: "document"

  structured_part:
    schema: {}
    invariants: []
  document_part:
    required_sections: []
    format_constraints: {}
    invariants: []
  code_part:
    language: ""
    syntax_valid: true
    invariants: []

  verification: "블록 추출 → 각 variant 검증 순차 실행. 1개라도 fail → reject."
```

---

## 3. Artifact AC

생성된 스킬 자체(SKILL.md)가 설계문서와 일치하는지 검증.
모든 Tier 공통.

```yaml
artifact_ac:
  frontmatter_checks:
    - id: "ART-001"
      rule: "SKILL.md의 name이 설계문서 skill_name과 일치"
      check: "skill_md.name == design_doc.skill_name"

    - id: "ART-002"
      rule: "SKILL.md description이 설계문서 purpose 핵심 키워드를 포함"
      check: |
        keywords = extract_keywords(design_doc.purpose, merged_vocabulary)
        match_rate = sum(1 for kw in keywords if kw in skill_md.description) / len(keywords)
        match_rate >= 0.7

    - id: "ART-003"
      rule: "설계문서의 trigger_conditions가 SKILL.md에 반영"
      check: |
        for tc in design_doc.trigger_conditions:
          keywords = extract_keywords(tc, merged_vocabulary)
          assert any(kw in skill_md_full_text for kw in keywords)

    - id: "ART-004"
      rule: "설계문서의 non_trigger_conditions가 SKILL.md에 부정 표현과 함께 반영"
      check: |
        negation_markers = ["안 ", "않", "아닌", "불필요", "제외",
                           "NOT", "not", "except", "exclude", "DO NOT"]
        for ntc in design_doc.non_trigger_conditions:
          keywords = extract_keywords(ntc, merged_vocabulary)
          for kw in keywords:
            if kw in skill_md_full_text:
              sentence = get_sentence_containing(skill_md_full_text, kw)
              assert any(neg in sentence for neg in negation_markers)
              break

  verification: "keyword extraction + string match. 자동 실행."
```

---

## 4. Fixture AC

### Fixture 구조 스키마

```yaml
# 각 fixture의 정규 구조.
fixture_schema:
  # --- 필수 필드 ---
  id: "string"                    # 고유 식별자. "FIX-XXX-NNN" 형식 권장.
  description: "string"           # 무엇을 테스트하는지 한 줄 설명.
  input: "object"                 # 스킬에 전달할 input. 형식은 스킬마다 다름.
  expected: "object"              # 아래 fixture_expected_schema 참조.

  # --- Tier 2 필드 ---
  severity: "critical | major | minor"    # Tier 2에서만 사용. Tier 1에서는 생략.

  # --- 선택적 메타 필드 ---
  # Semantic AC judge에게 사전 정보를 제공하거나, 검증 로직을 분기하는 용도.
  meta:
    # 예시 (스킬별로 자유롭게 확장 가능):
    # has_contradiction: true     # input에 의도적 모순이 포함됨. SEM judge에게 전달.
    # language: "en"              # input 언어. 다국어 스킬에서 검증 분기.
    # complexity: "high"          # stability target 선정에 참고.
    # tags: ["edge_case", "regression_from_v0.2"]  # 분류/필터링용.
```

### Fixture Expected 필드 스키마

```yaml
fixture_expected_schema:
  # ┌──────────────────────────────────────────────────────────────┐
  # │  중요: Tier 1 fixture의 expected는                             │
  # │  regex 또는 string match로 검증 가능한 항목만 포함한다.           │
  # │  의미 판단(semantic matching)이 필요한 항목은                     │
  # │  Tier 2 Semantic AC에서 다룬다.                                │
  # └──────────────────────────────────────────────────────────────┘

  # === 공통 필드 ===
  min_length:
    type: "integer"
    description: "output 최소 문자 수"
  max_length:
    type: "integer"
    description: "output 최대 문자 수"

  # === Structured output 필드 ===
  must_include:
    type: "array<string>"
    description: "output에 포함되어야 하는 값 (exact string match)"
  must_exclude:
    type: "array<string>"
    description: "output에 포함되면 안 되는 값 (exact string match)"

  # === Document output 필드 ===
  must_contain_section:
    type: "array<string>"
    description: "존재해야 하는 섹션 heading 목록 (heading normalization 적용, 부록 E 참조)"

  must_match_patterns:
    type: "array<string>"
    description: |
      문서 전체에서 매칭되어야 하는 regex 패턴 목록. 각 패턴이 독립적으로 매칭.
      ※ 반드시 복수형(patterns). 단수 must_match_pattern 사용 금지 (YAML 키 중복 방지).

  must_match_pattern_in_section:
    type: "object"
    description: "특정 섹션 내에서만 매칭되어야 하는 패턴"
    schema:
      section: "string"           # 섹션 heading (normalization 적용)
      patterns: "array<string>"   # regex 패턴 목록

  must_not_match_pattern_outside_section:
    type: "object"
    description: "특정 섹션 외부에서 매칭되면 안 되는 패턴"
    schema:
      section: "string"
      patterns: "array<string>"

  scope_has_inclusion_exclusion:
    type: "boolean"
    description: "스코프 섹션에 포함/미포함(제외) 구분이 존재하는지"

  # === Code output 필드 ===
  must_compile:
    type: "boolean"
    description: "컴파일/파싱 성공해야 함"
  must_include_class:
    type: "string"
    description: "포함되어야 하는 클래스명"
  test_passes:
    type: "boolean"
    description: "함께 생성된 테스트가 통과하는지"

  # === BAD (Tier 1에 넣으면 안 됨) ===
  # must_mention: ["주문 관련 내용"]    ← "관련"이 의미 판단 필요
  # tone: "formal"                     ← semantic 판단 필요
  # quality: "high"                    ← 주관적 판단
```

### Fixture Policy

```yaml
fixture_policy:
  tier_1:
    minimum_count: 3
    minimum_count_document: 5
    pass_rate_by_output_type:
      structured: 1.0
      document: 0.8
      code: 1.0
      hybrid: 0.9
    verification: "regex, string match, numeric comparison만. LLM judge 호출 없음."

  tier_2:
    minimum_count: 5
    severity_policy:
      critical_fail: "전체 reject (pass_rate 계산 안 함)"
      major_minor_pass_rate: 0.8
    verification: "Tier 1 검증 + LLM judge (semantic AC에서)"

  growth:
    trigger: "검증 실패 시 해당 케이스를 fixture로 추가"
    split_threshold: 15
```

---

## 5. Retry Policy

모든 Tier 공통.

```yaml
retry_policy:
  hard_ac_retry: 3
  stability_retry: 2
  artifact_ac_retry: 2
  fixture_ac_retry: 2
  semantic_ac_retry: 1            # Tier 2만
  regression_ac_retry: 0          # Tier 2만. 즉시 HITL.

  total_max_retry: 5

  retry_context:
    include_failed_assertions: true
    include_failed_fixtures: true
    include_stability_diff: true
    include_judge_feedback: true  # Tier 2만

escalation:
  report_includes:
    - "실패한 AC 항목 (id + 상세)"
    - "retry별 실패 패턴 (동일 항목 반복 vs 다른 항목)"
    - "output 전문 (stability fail 시 N회 output 모두 포함)"
    - "judge feedback (Tier 2 semantic AC인 경우)"
    - "regression diff (Tier 2 regression AC인 경우)"
  human_options:
    - "AC 수정 (기준이 부적절)"
    - "설계문서 수정 (의도 명확화)"
    - "fixture 수정/추가"
    - "이전 버전 유지"
    - "예외 accept (사유 기록 필수)"
```

---

# Tier 2 전용 섹션

> Tier 1 스킬은 위에서 끝. 아래는 Tier 2 스킬에만 추가.

---

## 6. Semantic AC (Tier 2)

```yaml
semantic_ac:
  judge_model: "opus"
  cross_judge: "gemini-pro"       # optional
  evaluation_runs: 3              # majority vote

  checklist:
    - id: "SEM-001"
      criterion: ""
      # binary 판단 가능한 구체적 문장으로.
      # bad:  "문서 품질이 좋은가"
      # good: "설계 문서가 변경 대상 파일명을 최소 1개 이상 직접 언급하는가"
      scoring: "binary"
      weight: 1

  pass_threshold:
    method: "weighted_score"
    minimum_ratio: 0.75

  # fixture에 meta 필드가 있으면 judge_prompt에 포함하여
  # judge의 비결정적 판단을 줄인다.
  # 예: has_contradiction: true → judge에게 "이 input에는 모순이 있다" 사전 안내.
  fixture_meta_injection: true

  judge_prompt_template: |
    당신은 '{skill_name}' 스킬의 output 품질을 평가하는 judge입니다.

    ## 평가 대상
    - Skill purpose: {purpose}
    - Input: {input}
    - Output: {output}
    - Fixture meta: {fixture_meta}

    ## Checklist
    {checklist_items}

    ## 응답 형식 (JSON만, 다른 텍스트 없이)
    {
      "judgments": [
        {"id": "SEM-001", "pass": true, "reason": "1~2문장 근거"}
      ]
    }
```

---

## 7. Regression AC (Tier 2)

설계문서 업데이트 시에만 활성화.

```yaml
regression_ac:
  enabled: true                   # previous_version이 null이면 자동 false
  baseline_version: ""
  baseline_fixture_results:
    path: ""
    format: "yaml"
    schema: |
      version: "1.0.0"
      skill_version: ""
      generated_at: ""           # ISO 8601
      fixtures:
        - fixture_id: "FIX-001"
          fixture_input_hash: ""  # canonical JSON SHA-256
          # hash 정규화:
          #   1. input을 Python dict로 파싱
          #   2. json.dumps(input, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
          #   3. UTF-8 인코딩 후 SHA-256
          runs:
            - run_id: 1
              hard_ac_pass: true
              fixture_pass: true
              output_hash: ""
          stability_pass: true
          overall_pass: true

  policy:
    critical_regression: "hard_fail → 즉시 HITL"
    major_regression_threshold: 1
    minor_regression_threshold: 2
    input_changed_policy: "exclude_from_regression, record_as_new_baseline"

  escalation:
    report_format: |
      ## Regression Report
      - 변경: v{previous} → v{current}
      - 변경 요약: {diff_summary}
      - Regression fixtures:
        {regression_list}
      - 영향 분석: 전체 {total}개 fixture 중 {regressed}개 regression
      - 권장 조치: {recommendation}
```

---

## 8. Drift Budget (Tier 2)

모든 조정은 시스템 제안 → 사람 승인. 자동 실행 없음.

```yaml
drift_budget:
  initial_values:
    fixture_pass_rate: 0.8
    semantic_pass_ratio: 0.75

  tighten_proposal:
    trigger: "fixture 10개 이상 AND 최근 5회 연속 전체 pass"
    proposal:
      fixture_pass_rate: "+0.05"
      semantic_pass_ratio: "+0.05"
    cap:
      fixture_pass_rate: 0.95
      semantic_pass_ratio: 0.90
    action: "propose_to_human"
    proposal_format: |
      ## Drift Budget 강화 제안
      - 근거: 최근 {n}회 연속 전체 pass, fixture {count}개
      - 현재: fixture_pass_rate={current_fpr}, semantic_pass_ratio={current_spr}
      - 제안: fixture_pass_rate={proposed_fpr}, semantic_pass_ratio={proposed_spr}
      - 영향 분석: 과거 결과에 제안 기준 적용 시 {impact}회 추가 fail 예상
      - 판단: 승인 / 거부 / 수정

  relax_proposal:
    trigger: "3회 연속 HITL에서 'AC가 너무 엄격' 판단"
    proposal:
      fixture_pass_rate: "-0.05"
      semantic_pass_ratio: "-0.05"
    floor:
      fixture_pass_rate: 0.7
      semantic_pass_ratio: 0.6
    action: "propose_to_human"

  log:
    enabled: true
    records:
      - timestamp: ""
      - direction: ""             # tighten | relax
      - proposed_by: "system"
      - approved_by: ""
      - old_values: {}
      - new_values: {}
      - rationale: ""
```

---

## 부록 A: AC 작성 가이드라인

### 공통
- "~해야 한다" → 검증 가능한 assertion 또는 checklist item으로 변환.
- Tier 1의 모든 검증은 LLM 호출 없이 코드로 실행 가능해야 한다.

### Hard AC
- Structured: JSON Schema + Python assertion
- Document: 필수 섹션 존재 + 길이 제약 + scoped regex pattern
- Code: syntax check + lint + AST assertion
- Hybrid: 블록 추출 후 각 variant 적용
- forbidden/required_patterns에는 반드시 scope를 명시할 것.

### Fixture
- expected는 exact output이 아니라 충족 조건으로 기술.
- **Tier 1: regex/string match/numeric comparison만.** 의미 판단 항목 금지.
- Tier 2: severity 분류 추가. semantic 판단은 Semantic AC에서.
- 패턴 매칭 필드는 반드시 복수형 배열(`must_match_patterns`) 사용. 단수형 키 중복 금지.
- fixture에 semantic AC judge용 사전 정보가 필요하면 `meta` 필드에 선언.

### Stability
- 모든 스킬, 모든 Tier에 적용.
- "output이 매번 같아야 한다"가 아니라 "매번 AC를 통과해야 한다".
- Document output은 1회 불일치 허용 (N회 중 N-1회 일치면 pass).

### Artifact AC
- 생성된 SKILL.md ↔ 설계문서 일치를 keyword containment로 검증.
- Semantic 수준의 일치 검증은 Tier 2 Semantic AC에서.
- extract_keywords() 명세는 부록 D 참조.

### Regression AC (Tier 2)
- baseline을 YAML로 저장. fixture input hash로 input 변경 감지.
- input이 바뀐 fixture는 regression 비교에서 제외.
- hash 정규화: canonical JSON (sort_keys + 공백 제거) → UTF-8 → SHA-256. 상세는 Section 7 참조.

---

## 부록 B: Papillon 스킬별 Tier 배정

| 스킬 | Output Type | Tier | 근거 |
|------|-------------|------|------|
| inquisition (요구사항 인터뷰) | document | **2** | downstream 전체 품질 결정. silent failure 위험. |
| wtth reviewer (개별 리뷰어) | document | 1 | 개별 output은 orchestrator가 종합 |
| wtth orchestrator | hybrid | 2 | 전체 리뷰 흐름 제어 |
| shackled (pair programming) | code | 1 | output이 wtth 리뷰를 거침 |
| papillon orchestrator | structured | 2 | 파이프라인 전체 흐름 제어 |
| task sizing (Opus) | structured | 2 | sizing 오류가 전체 일정에 영향 |
| gate 판정 | structured | 2 | HITL 분기점, 오판 시 복구 비용 큼 |

---

## 부록 C: 빠른 시작 체크리스트

```
□ 1. Tier 결정 (기본 Tier 1)
□ 2. Output Type 결정
□ 3. Skill Identity 작성
□ 4. Hard AC 작성 (해당 variant 선택, forbidden/required_patterns에 scope 명시)
□ 5. Stability Invariant 확인 (기본값 적용 or 커스텀)
□ 6. Artifact AC 확인 (보통 기본 4항목 그대로)
□ 7. Fixture 작성 (Tier 1 structured: 3개 / Tier 1 document: 5개 / Tier 2: 5개+)
     ※ Tier 1 fixture expected는 regex/string/numeric만!
     ※ 패턴 필드는 반드시 복수형 배열(must_match_patterns)!
     ※ 필요 시 meta 필드 추가 (has_contradiction 등)
□ 8. Retry Policy 확인 (보통 기본값 그대로)
□ ---- Tier 1은 여기서 끝 ----
□ 9. Semantic AC checklist 작성 (Tier 2)
□ 10. Regression baseline 설정 (Tier 2, 업데이트 시)
□ 11. Drift Budget 초기값 설정 (Tier 2)
```

---

## 부록 D: extract_keywords() 명세 (v3.3)

Artifact AC(ART-002~004)에서 사용하는 키워드 추출 함수.
**결정적(deterministic) 함수여야 하며, 동일 입력에 대해 항상 동일 결과를 반환한다.**

```yaml
extract_keywords:
  inputs:
    text: "키워드를 추출할 문자열"
    domain_vocabulary: "설계문서 메타 정보의 domain_vocabulary + global vocabulary 합집합"

  algorithm:
    step_1: |
      **스크립트별 연속 토큰 추출**:
        - 정규표현식 `[A-Za-z]+|[가-힣]+|\d+` 로 findall
        - 공백·구두점은 자동 구분자 역할
        - 혼합 스크립트 토큰은 자동 분리:
          "reviewer를" → ["reviewer", "를"]
          "TW는"       → ["TW", "는"]
          "결과를"     → ["결과를"]  (모두 한글이라 하나로 유지)
    step_2: |
      **도메인 vocabulary 우선 매칭**:
        - domain_vocabulary에 포함된 토큰은 길이/stopword/조사 제거 무관하게 keyword로 채택
        - 매칭은 case-insensitive
    step_3: |
      **나머지 토큰에 길이 기준 적용**:
        - 한글: 2글자 이상 (조사 제거 적용 전 기준)
        - 영문 대문자 전용 2글자 이상: 약어로 간주하여 포함 (예: DB, AI, UX)
        - 영문 기타: 3글자 이상 (소문자로 정규화)
        - 숫자 단독 토큰 제외
    step_4: |
      **한글 1글자 목적격 조사 제거 (을/를)**:
        - 한글 토큰의 길이가 3 이상이고 말미가 '을' 또는 '를'이면 해당 글자 제거
        - 제거 후 길이가 2 미만이 되면 토큰 자체를 drop
        - '을'/'를'만 대상. 다른 조사(이/가/은/는/의/에/로/도/만 등)는 보존
        - 이유: "결과를→결과", "초안을→초안"을 기대하면서도 "기반으로"는 원형 보존
        - 복합 조사("으로"/"에서"/"부터" 등)는 strip 대상 외. 형태소 분석은 과도하므로 1글자 목적격만 처리
    step_5: |
      **stopword 제거** (domain_vocabulary 및 대문자 전용 토큰은 제거 대상 제외):
        한글: [이, 그, 저, 것, 수, 등, 및, 또는, 그리고, 하지만, 때문, 위해, 대한, 통해, 경우, 하는, 있는, 없는, 되는, 같은]
        영문: [the, a, an, is, are, was, were, be, been, of, to, in, on, at, for, with, and, or, but, not, this, that, these, those]
    step_6: "중복 제거 후 반환 (출현 순서 보존)"

  properties:
    deterministic: true
    case_sensitive: false
    unit_test_required: true

  examples:
    - input: "요구사항 인터뷰 결과를 기반으로 설계 문서 초안을 생성한다"
      domain_vocabulary: []
      output: ["요구사항", "인터뷰", "결과", "기반으로", "설계", "문서", "초안", "생성한다"]
      note: "'결과를'→'결과', '초안을'→'초안' (step_4). '기반으로'/'생성한다'는 strip 대상 외."

    - input: "Do NOT trigger for simple typo corrections"
      domain_vocabulary: []
      output: ["NOT", "trigger", "simple", "typo", "corrections"]
      note: "'Do' 2글자 영문(대문자 전용 아님) → drop. 'NOT' 대문자 전용 3글자 → 약어 규칙."

    - input: "BE, FE reviewer를 포함하고 TW는 제외"
      domain_vocabulary: ["BE", "FE", "TW"]
      output: ["BE", "FE", "reviewer", "포함하고", "TW", "제외"]
      note: "step_1에서 'reviewer를' → ['reviewer','를'], 'TW는' → ['TW','는'] 자동 분리."

    - input: "DB 스키마 변경 시 DBA 필수"
      domain_vocabulary: ["DBA"]
      output: ["DB", "스키마", "변경", "DBA", "필수"]
      note: "'DB'는 대문자 전용 2글자 약어. 'DBA'는 vocab 매칭. '시' 1글자 → drop."

  domain_vocabulary_sources:
    global:
      location: "papillon 프로젝트 루트 VOCABULARY.yaml"
      owner: "Josh (수동 관리)"
      update_frequency: "매우 낮음 (분기 1~2회)"
      initial_content: ["BE", "FE", "SEC", "SRE", "PO", "TW", "QA", "UX", "DBA", "ARCH", "HITL", "AC", "RDR", "ADR"]
    skill_local:
      location: "각 스킬 설계문서 메타 정보의 domain_vocabulary 필드"
      owner: "스킬 작성자"
      update_frequency: "스킬 업데이트 시"
    merge_rule: "global ∪ skill_local (합집합, 중복 제거)"
```

---

## 부록 E: Markdown 유틸리티 함수 명세

Document output 검증에서 사용하는 Markdown 파싱/섹션 추출 함수.
**모든 함수는 결정적이며, 동일 입력에 동일 결과를 반환한다.**

### Heading Normalization

```yaml
heading_normalization:
  description: |
    Markdown heading 문자열을 정규화하여 비교 가능한 형태로 변환.
    검증 시 모든 heading 비교는 이 정규화를 거친 후 수행.
  algorithm:
    step_1: "앞뒤 공백(whitespace) 제거 (trim)"
    step_2: "Markdown heading prefix 제거 (##, ###, 등)"
    step_3: "prefix 제거 후 다시 앞뒤 공백 제거"
    step_4: "연속 공백을 단일 공백으로 치환"
  examples:
    - input: "## 개요"
      output: "개요"
    - input: "##  배경 및  목적 "
      output: "배경 및 목적"
    - input: "###API 명세"
      output: "API 명세"
    - input: "  개요  "
      output: "개요"
  properties:
    deterministic: true
    unit_test_required: true
```

### extract_headings() — v3.3 신설

```yaml
extract_headings:
  description: |
    Markdown 문서에서 모든 heading을 추출한다.
    `extract_section()` 내부 구현의 공통 기반이며, 스킬 AC의
    `output_headings` 참조(예: inquisition AC INV-IQ-01)의 구현 근거이다.
  inputs:
    document: "string — 전체 Markdown 문서 텍스트"
  output: |
    list of Heading(level, normalized, line_index):
      - level:       '#' 개수 (1=h1, 2=h2, ...)
      - normalized:  heading 텍스트에 normalize_heading 적용한 결과
      - line_index:  원본 문서의 0-based 줄 번호
  algorithm:
    step_1: "문서를 줄 단위로 분리"
    step_2: |
      각 줄에서 heading 감지:
        - 정규표현식 `^\s*(#+)\s*(.*?)\s*$` 매칭
        - 매칭되지 않는 줄은 무시
    step_3: |
      매칭된 각 줄에 대해 (level, normalized, line_index) 생성:
        - level = '#'의 개수
        - normalized = normalize_heading(본문)
        - line_index = 줄의 0-based 인덱스
    step_4: "출현 순서대로 리스트 반환"
  edge_cases:
    no_headings: "빈 리스트 반환"
    fenced_code_blocks: |
      현재 명세는 펜스 코드 블록(``` 내부)의 '#'을 구분하지 않는다.
      필요 시 v3.4+ 후보 — 실제 fail 사례가 나올 때 추가한다.
  properties:
    deterministic: true
    unit_test_required: true
  examples:
    - document: |
        ## 개요
        내용
        ## 스코프
        상세
      output:
        - { level: 2, normalized: "개요",   line_index: 0 }
        - { level: 2, normalized: "스코프", line_index: 2 }
```

### extract_section()

```yaml
extract_section:
  description: |
    Markdown 문서에서 특정 heading의 섹션 내용을 추출.
    섹션은 해당 heading부터 동일 또는 상위 레벨의 다음 heading 직전까지.
  inputs:
    document: "string — 전체 Markdown 문서 텍스트"
    heading: "string — 추출할 섹션의 heading (normalization 적용)"
  output: "string — 해당 섹션의 내용 (heading 라인 자체는 제외)"
  algorithm:
    step_1: "문서를 줄 단위로 분리"
    step_2: |
      각 줄에서 heading 감지:
        - '#' 으로 시작하는 줄 → heading
        - heading level = '#' 개수
    step_3: |
      target heading 찾기:
        - normalize(line_heading) == normalize(heading) 인 줄
        - 여러 개 매칭 시 첫 번째 사용
    step_4: |
      섹션 범위 결정:
        - 시작: target heading 다음 줄
        - 종료: 다음에 나오는 heading 중 target과 동일 또는 상위 level인 첫 번째 줄 직전
        - 끝까지 해당 heading이 없으면 문서 끝까지
    step_5: "시작~종료 범위의 텍스트를 join하여 반환"
  edge_cases:
    heading_not_found: "빈 문자열 반환"
    empty_section: "빈 문자열 반환 (heading 바로 다음에 동일 level heading)"
  properties:
    deterministic: true
    unit_test_required: true
  examples:
    - document: |
        ## 개요
        프로젝트 소개입니다.
        ## 스코프
        포함: A, B
        미포함: C
        ## 기능 요구사항
        기능 1
      heading: "개요"
      output: "프로젝트 소개입니다."
    - document: "(위와 동일)"
      heading: "스코프"
      output: "포함: A, B\n미포함: C"
```

### exclude_section()

```yaml
exclude_section:
  description: |
    Markdown 문서에서 특정 heading의 섹션을 제외한 나머지 텍스트를 반환.
    forbidden_patterns의 scope: "exclude_section:X" 검증에 사용.
  inputs:
    document: "string — 전체 Markdown 문서 텍스트"
    heading: "string — 제외할 섹션의 heading (normalization 적용)"
  output: "string — 해당 섹션을 제외한 나머지 문서 텍스트"
  algorithm:
    step_1: "extract_section()과 동일하게 target 섹션 범위 결정"
    step_2: "해당 범위(heading 라인 포함)를 제거"
    step_3: "나머지 줄들을 join하여 반환"
  edge_cases:
    heading_not_found: "원본 문서 전체 반환 (제외할 섹션이 없으므로)"
  properties:
    deterministic: true
    unit_test_required: true
```

### get_sentence_containing()

```yaml
get_sentence_containing:
  description: |
    텍스트에서 특정 키워드를 포함하는 문장을 반환.
    Artifact AC의 negation proximity check에 사용.
  inputs:
    text: "string — 검색 대상 텍스트"
    keyword: "string — 찾을 키워드"
  output: "string — 키워드를 포함하는 첫 번째 문장"
  algorithm:
    step_1: |
      문장 분리 기준:
        - 줄바꿈 (\n)
        - 마침표+공백 (. ), 물음표+공백 (? ), 느낌표+공백 (! )
        - Markdown list item (- , * , 숫자. ) 각각을 독립 문장으로 취급
    step_2: "각 문장에서 keyword 포함 여부 확인 (case-insensitive)"
    step_3: "첫 번째 매칭 문장 반환"
  edge_cases:
    keyword_not_found: "빈 문자열 반환"
    keyword_in_multiple_sentences: "첫 번째만 반환"
  properties:
    deterministic: true
    unit_test_required: true
```
