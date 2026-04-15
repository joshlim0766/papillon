# Inquisition Skill — Acceptance Criteria

> papillon AC Template v3.3 적용.
> test_mode: single_turn (인터뷰 없이 1회 생성. multi_turn은 deferred.)

---

## 메타 정보

```yaml
skill_name: "inquisition"
version: "0.1.0"
previous_version: null
tier: "tier_2"
output_type: "document"
domain_vocabulary: ["심문", "라운드", "확정점", "미확정점", "요구사항", "PRD", "스코프"]
test_mode: "single_turn"          # default: "single_turn". multi_turn은 별도 benchmark track으로 deferred.
created_by: "Josh"
created_at: "2026-04-13"
updated_at: "2026-04-13"
```

---

## 1. Skill Identity

```yaml
identity:
  purpose: |
    사용자의 초기 요구사항을 구조화된 인터뷰(심문)를 통해
    후속 설계 단계가 즉시 착수할 수 있는 수준의 요구사항 문서로 변환한다.

  trigger_conditions:
    - "사용자가 새로운 기능/프로젝트 개발을 요청할 때"
    - "요구사항이 모호하거나 불완전한 상태에서 설계를 시작해야 할 때"
    - "기존 요구사항을 재정리/보강해야 할 때"

  non_trigger_conditions:
    - "이미 완성된 PRD/요구사항 문서가 존재하고 수정이 불필요한 경우"
    - "단순 버그 수정처럼 요구사항 심문이 불필요한 경우"
    - "설계/구현/리뷰 단계에서 호출 (해당 단계는 wtth/shackled 담당)"

  input_spec:
    description: |
      사용자의 초기 요청 텍스트. 형식 제한 없음.
      한 줄짜리 "주문 시스템 만들어줘"부터 수 페이지의 초안까지 다양.

  output_spec:
    type: "document"
    description: |
      Markdown 요구사항 문서. 다음 필수 섹션을 포함:
      - 개요 (프로젝트/기능 한줄 요약)
      - 배경 및 목적
      - 스코프 (포함/미포함 명시)
      - 기능 요구사항 (확정점/미확정점 구분)
      - 비기능 요구사항
      - 제약 조건
      - 용어 정의 (해당 시)
      - 미결 사항
```

---

## 2. Hard AC — Variant B: Document Output

```yaml
hard_ac_document:
  required_sections:
    - heading: "개요"
      level: 2
      required: true
    - heading: "배경 및 목적"
      level: 2
      required: true
    - heading: "스코프"
      level: 2
      required: true
    - heading: "기능 요구사항"
      level: 2
      required: true
    - heading: "비기능 요구사항"
      level: 2
      required: true
    - heading: "제약 조건"
      level: 2
      required: true
    - heading: "미결 사항"
      level: 2
      required: true
    - heading: "용어 정의"
      level: 2
      required: false

  format_constraints:
    min_length_chars: 1500
    max_length_chars: 8000

    # v3.2: forbidden/required_patterns 모두 {pattern, scope} 객체 배열.
    # scope: "all" | "exclude_section:X" | "only_section:X"
    forbidden_patterns:
      - pattern: "TODO"
        scope: "exclude_section:미결 사항"
      - pattern: "TBD"
        scope: "exclude_section:미결 사항"
      - pattern: "\\[placeholder\\]"
        scope: "all"
      - pattern: "\\[미정\\]"
        scope: "exclude_section:미결 사항"
      - pattern: "추후 결정"
        scope: "exclude_section:미결 사항"

    required_patterns:
      - pattern: "## 개요"
        scope: "all"
      - pattern: "## 스코프"
        scope: "all"
      - pattern: "확정"
        scope: "only_section:기능 요구사항"
        # "확정"이 문서 어딘가에 있는 게 아니라, 기능 요구사항 섹션 안에 있어야 의미 있음.
      - pattern: "## 미결 사항"
        scope: "all"

  invariants:
    - id: "INV-IQ-01"
      rule: "필수 섹션 7개가 모두 존재"
      check: |
        required = ["개요", "배경 및 목적", "스코프", "기능 요구사항",
                    "비기능 요구사항", "제약 조건", "미결 사항"]
        # heading 비교 시 v3.2 부록 E heading_normalization 적용
        all(normalize(h) in [normalize(x) for x in output_headings] for h in required)

    - id: "INV-IQ-02"
      rule: "문서 길이 범위 이내"
      check: "1500 <= len(output_text) <= 8000"

    - id: "INV-IQ-03"
      rule: "scoped forbidden patterns 전수 통과"
      check: |
        for fp in forbidden_patterns:
          if fp.scope == "all":
            text = output_text
          elif fp.scope.startswith("exclude_section:"):
            section_name = fp.scope.split(":", 1)[1]
            text = exclude_section(output, section_name)
          elif fp.scope.startswith("only_section:"):
            section_name = fp.scope.split(":", 1)[1]
            text = extract_section(output, section_name)
          assert not re.search(fp.pattern, text)

    - id: "INV-IQ-04"
      rule: "스코프 섹션에 '포함'과 '미포함(제외)' 구분이 존재"
      check: |
        scope = extract_section(output, "스코프")
        has_inclusion = bool(re.search(r"포함", scope))
        has_exclusion = bool(re.search(r"미포함|제외", scope))
        has_inclusion and has_exclusion

    - id: "INV-IQ-05"
      rule: "scoped required patterns 전수 충족"
      check: |
        for rp in required_patterns:
          if rp.scope == "all":
            text = output_text
          elif rp.scope.startswith("exclude_section:"):
            section_name = rp.scope.split(":", 1)[1]
            text = exclude_section(output, section_name)
          elif rp.scope.startswith("only_section:"):
            section_name = rp.scope.split(":", 1)[1]
            text = extract_section(output, section_name)
          assert re.search(rp.pattern, text)

  verification: "구조 파싱 + scoped regex 매칭 자동 실행. 1개라도 fail → reject."
```

### Stability Invariant

```yaml
stability:
  tier_2_runs: 5
  optimization:
    # v3.3 template 규칙 준수: "critical 전원 + major 1개(랜덤)"
    # fixture ID를 하드코딩하지 않음 — fixture 추가/제거 시 자동 반영.
    selection_rule: "severity == critical 전원 + severity == major 랜덤 1개"
    fallback: "대표 fixture stability fail → 전체 fixture로 확대 재검증"
  check: |
    선택된 fixture에 대해 5회 실행.
    각 실행이 개별적으로 Hard AC invariants를 전수 통과해야 함.
    document output이므로 5회 중 4회 이상 동일 fixture 판정이면 pass.
```

---

## 3. Artifact AC

```yaml
artifact_ac:
  # v3.3 template Section 3의 기본 4항목 그대로 적용.
  # inquisition-specific override 없음.
  # check 내 merged_vocabulary = global(VOCABULARY.yaml) ∪ skill-local(domain_vocabulary)

  frontmatter_checks:
    - id: "ART-IQ-01"
      rule: "SKILL.md name == 'inquisition'"
      check: "skill_md.name == 'inquisition'"

    - id: "ART-IQ-02"
      rule: "SKILL.md description이 purpose 핵심 키워드 70% 이상 포함"
      check: |
        keywords = extract_keywords(purpose, merged_vocabulary)
        match_rate = sum(1 for kw in keywords if kw in skill_md.description) / len(keywords)
        match_rate >= 0.7

    - id: "ART-IQ-03"
      rule: "trigger_conditions 핵심 키워드가 SKILL.md에 반영"
      check: |
        for tc in trigger_conditions:
          keywords = extract_keywords(tc, merged_vocabulary)
          assert any(kw in skill_md_full_text for kw in keywords)

    - id: "ART-IQ-04"
      rule: "non_trigger_conditions가 부정 표현과 함께 SKILL.md에 반영"
      check: |
        negation_markers = ["안 ", "않", "아닌", "불필요", "제외",
                           "NOT", "not", "except", "exclude", "DO NOT"]
        for ntc in non_trigger_conditions:
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

> Fixture expected 필드 스키마는 v3.3 template Section 4에 정의됨. 여기서 중복 선언하지 않음.

### Fixtures

```yaml
fixtures:
  # === Critical ===

  - id: "FIX-IQ-01"
    description: "한 줄짜리 모호한 요청 → 구조화된 요구사항 문서"
    severity: "critical"
    input:
      user_request: "주문 시스템 만들어줘"
    expected:
      must_contain_section:
        - "개요"
        - "배경 및 목적"
        - "스코프"
        - "기능 요구사항"
        - "비기능 요구사항"
        - "제약 조건"
        - "미결 사항"
      must_match_patterns:
        - "주문"
      scope_has_inclusion_exclusion: true
      min_length: 1500
      must_not_match_pattern_outside_section:
        section: "미결 사항"
        patterns: ["TODO", "TBD"]

  - id: "FIX-IQ-02"
    description: "여러 도메인에 걸친 복잡한 요청"
    severity: "critical"
    input:
      user_request: |
        실시간 채팅 + 화상회의 + 파일 공유가 가능한 협업 플랫폼 만들어줘.
        사내용이고, 동시 접속 500명 지원해야 해. AWS 기반으로.
    expected:
      must_contain_section:
        - "개요"
        - "스코프"
        - "기능 요구사항"
        - "비기능 요구사항"
        - "제약 조건"
      must_match_patterns:
        - "채팅|화상|파일\\s*공유"
        - "500|동시\\s*접속"
        - "AWS"
      min_length: 2000
      max_length: 8000

  - id: "FIX-IQ-03"
    description: "기존 요구사항 보강 요청"
    severity: "critical"
    input:
      user_request: |
        기존에 만든 주문 시스템에 결제 기능을 추가해줘.
        PG사는 토스페이먼츠 쓰고, 카드/계좌이체 지원.
        환불은 7일 이내만 가능하게.
    expected:
      must_contain_section:
        - "개요"
        - "스코프"
        - "기능 요구사항"
        - "제약 조건"
      must_match_patterns:
        - "결제|토스|PG"
        - "카드|계좌"
        - "환불|7일"
      scope_has_inclusion_exclusion: true

  # === Major ===

  - id: "FIX-IQ-04"
    description: "영어 요청 처리"
    severity: "major"
    input:
      user_request: |
        Build a REST API for user management.
        Need CRUD operations, JWT auth, role-based access control.
        PostgreSQL backend, deploy on ECS.
    expected:
      must_contain_section:
        - "개요"
        - "기능 요구사항"
        - "비기능 요구사항"
        - "제약 조건"
      must_match_patterns:
        - "REST|API|user\\s*management"
        - "JWT|auth|RBAC|role"
        - "PostgreSQL|ECS"
      min_length: 1500

  - id: "FIX-IQ-05"
    description: "의도적으로 모순된 요구사항 → 미결 사항으로 포착"
    severity: "major"
    meta:                           # v3.2: fixture 루트가 아닌 meta 하위에 선언
      has_contradiction: true
    input:
      user_request: |
        오프라인 전용 앱인데 실시간 동기화도 돼야 해.
        예산은 100만원이고 AI 추천 엔진도 넣어줘.
    expected:
      must_contain_section:
        - "미결 사항"
      must_match_pattern_in_section:
        section: "미결 사항"
        patterns:
          - "오프라인|동기화|모순|충돌|상충"
      min_length: 1500

fixture_policy:
  # v3.3 template 기본값 참조. inquisition-specific override만 기술.
  tier_2_minimum: 5
  severity_policy:
    critical_fail: "전체 reject"
    major_minor_pass_rate: 0.8
  verification: "regex, string match, numeric comparison. LLM 호출 없음."
```

---

## 5. Retry Policy

```yaml
# v3.3 template 기본값 그대로 적용. override 없음.
retry_policy:
  hard_ac_retry: 3
  stability_retry: 2
  artifact_ac_retry: 2
  fixture_ac_retry: 2
  semantic_ac_retry: 1
  regression_ac_retry: 0

  total_max_retry: 5

  retry_context:
    include_failed_assertions: true
    include_failed_fixtures: true
    include_stability_diff: true
    include_judge_feedback: true
```

---

## 6. Semantic AC (Tier 2)

```yaml
semantic_ac:
  judge_model: "opus"
  cross_judge: "gemini-pro"
  evaluation_runs: 3
  fixture_meta_injection: true    # v3.2: fixture.meta를 judge prompt에 자동 주입

  checklist:
    - id: "SEM-IQ-01"
      criterion: |
        output의 기능 요구사항이 input에서 언급된 기능을 모두 포함하는가
      scoring: "binary"
      weight: 2

    - id: "SEM-IQ-02"
      criterion: |
        스코프 '포함' 항목과 기능 요구사항 범위가 일치하는가
        (스코프에는 있는데 기능 요구사항에 없는 항목, 또는 그 반대가 없는가)
      scoring: "binary"
      weight: 2

    - id: "SEM-IQ-03"
      criterion: |
        비기능 요구사항에 수치적 기준이 최소 1개 이상 포함되어 있는가
        (예: 동시 접속 N명, 응답 시간 Nms, 가용성 N%)
      scoring: "binary"
      weight: 1

    - id: "SEM-IQ-04"
      criterion: |
        input에 모순/비현실적 조건이 존재하는 경우, 미결 사항 섹션에 식별되어 있는가
      scoring: "binary"
      weight: 2
      note: |
        fixture.meta.has_contradiction가 true이면 judge에게 사전 안내.
        has_contradiction이 없거나 false인 fixture에서는 이 항목 자동 pass.

    - id: "SEM-IQ-05"
      criterion: |
        output이 input scope를 벗어난 내용을 포함하지 않는가
        (input에서 언급하지 않은 기능을 임의 추가하지 않았는가)
      scoring: "binary"
      weight: 1

  pass_threshold:
    method: "weighted_score"
    # 총 가중치: 2+2+1+2+1 = 8
    minimum_ratio: 0.75
    minimum_weighted_score: 6

  judge_prompt_template: |
    당신은 'inquisition' 스킬의 output 품질을 평가하는 judge입니다.
    이 스킬은 사용자의 초기 요구사항을 구조화된 인터뷰를 통해
    후속 설계가 즉시 착수 가능한 수준의 요구사항 문서로 변환합니다.

    ## 평가 대상
    - Input (사용자 원래 요청): {input}
    - Output (생성된 요구사항 문서): {output}
    - Fixture meta: {fixture_meta}

    ## Checklist
    {checklist_items}

    ## 응답 형식 (JSON만, 다른 텍스트 없이)
    {
      "judgments": [
        {"id": "SEM-IQ-01", "pass": true, "reason": "1~2문장 근거"},
        {"id": "SEM-IQ-02", "pass": true, "reason": "1~2문장 근거"},
        {"id": "SEM-IQ-03", "pass": true, "reason": "1~2문장 근거"},
        {"id": "SEM-IQ-04", "pass": true, "reason": "1~2문장 근거"},
        {"id": "SEM-IQ-05", "pass": true, "reason": "1~2문장 근거"}
      ]
    }
```

---

## 7. Regression AC (Tier 2)

```yaml
regression_ac:
  enabled: false                  # v0.1.0 — 최초 버전.
  baseline_version: null
  baseline_fixture_results:
    path: null
```

---

## 8. Drift Budget (Tier 2)

```yaml
drift_budget:
  initial_values:
    fixture_pass_rate: 0.8
    semantic_pass_ratio: 0.75
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0-draft | 2026-04-13 | dry run 초안 (v3.1 template 적용) |
| 0.1.0 | 2026-04-13 | v3.2 template 동기화. Critical 3건 해소. |
| 0.1.0 | 2026-04-15 | template 참조 v3.2 → v3.3 업데이트 (토크나이저 재정의 + 한글 조사 제거 + `extract_headings()` 명세 반영). 본문 구조 변경 없음 — 전방호환. ART-IQ-02 실측 92.86% PASS. |

### v3.2 동기화 상세

| # | 이슈 | 해결 |
|---|------|------|
| C1 | fixture meta 필드 위치 | `has_contradiction` → `meta.has_contradiction`으로 이동 |
| C2 | required_patterns scope 불일치 | flat string → `{pattern, scope}` 객체 배열로 변경. "확정" scope를 `only_section:기능 요구사항`으로 정밀화. |
| C3 | fixture_expected_schema 중복 | 스킬 AC에서 스키마 섹션 제거. v3.2 template 참조만. |
| M4 | heading normalization | INV-IQ-01 check에 `normalize()` 명시 추가 |
| M6 | test_mode 기본값 | 메타에 `default: "single_turn"` 주석 명시 |
| O7 | stability_targets 하드코딩 | ID 하드코딩 → 규칙 기반 선정 (`severity == critical 전원 + major 랜덤 1개`) |

### v0.1.0 최종 수정 (Claude Code 리뷰 반영)

| # | 이슈 | 해결 |
|---|------|------|
| B1 | INV-IQ-03이 forbidden만 검사, required 미검사 | INV-IQ-05 신설 — scope dispatch 동일 로직으로 required_patterns 전수 검증 |
