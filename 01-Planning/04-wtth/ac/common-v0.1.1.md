# wtth Reviewer — 공통 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 모든 reviewer 페르소나(CODE, BE, FE, SEC, TEST, ARCH, DBA 등)에 공통으로 적용되는 베이스 AC.
> 페르소나별 특이 사항은 `{persona}-v0.1.1.md`에서 override한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer"
version: "0.1.1"
previous_version: "0.1.0"
tier: "tier_1"
output_type: "document"
domain_vocabulary: ["P0", "P1", "P2", "P3", "finding", "reviewer", "RDR", "체크리스트"]
test_mode: "single_turn"
created_by: "Josh"
created_at: "2026-04-15"
updated_at: "2026-04-16"

# 이 AC는 베이스이며, 페르소나별 AC에서 override된다.
# Override 규칙:
#   - 메타 필드: 페르소나 AC의 선언이 우선
#   - Identity: 페르소나 AC가 override (persona-specific)
#   - Hard AC invariants: 공통(INV-WREV-*) + 페르소나(INV-{P}-*) 합집합
#   - forbidden_patterns / required_patterns: 공통 + 페르소나 합집합
#   - domain_vocabulary: 공통 ∪ 페르소나 (합집합)
#   - Fixture: 페르소나 AC에서만 정의
#   - Retry: 공통 사용 (페르소나에서 명시 override 없으면)
```

---

## 1. Skill Identity (베이스 — 페르소나 AC가 override)

```yaml
identity:
  purpose: |
    특정 페르소나 관점에서 대상물(설계서·diff·런북·PRD 등)을 리뷰하고
    구조화된 finding 리스트를 생성한다. finding은 심각도(P0~P3), 위치
    참조, 문제 설명, 체크리스트 참조, 수정 제안을 포함한다.

  trigger_conditions:
    - "wtth 리뷰 모드에서 해당 페르소나가 투입되었을 때"
    - "단독 실행(/papillon:wtth 또는 페르소나 직접 호출) 시"

  non_trigger_conditions:
    - "오케스트레이터 역할 (라운드 진행·수렴 판정 등은 코어 담당)"
    - "자동 수정 실행 (코드 리뷰의 AS-IS/TO-BE 생성은 코어의 diff 생성 단계)"
    - "ADR 승격 판단 (코어 §3.2)"

  input_spec:
    description: |
      리뷰 대상 원문. 설계서 Markdown, diff hunk, 소스 파일, 런북, PRD 등.
      형식은 페르소나별 AC에서 구체화한다.

  output_spec:
    type: "document"
    description: |
      Markdown 형식의 finding 리스트. 각 finding은 다음을 포함:
        - 위치 참조 (파일·섹션·함수명·줄 범위 등)
        - 심각도 태그 (P0 / P1 / P2 / P3)
        - 문제 설명 (구체적, "꼼꼼히"·"잘" 등 모호 표현 금지)
        - 체크리스트 참조 (`[체크리스트: 항목명]` 형식)
        - 수정 제안 또는 권고
```

---

## 2. Hard AC — Variant B: Document Output (공통)

```yaml
hard_ac_document:
  required_sections:
    # reviewer 출력은 단일 "Findings" 섹션 또는 그에 상응하는 헤딩을
    # 포함하거나, heading 없이 finding-per-block 형식(P[0-3] 태그로 구분된
    # 블록 ≥1)을 사용해도 된다. v0.1.1에서 fallback 추가.
    - heading: "Findings"
      level: 2
      required: false              # v0.1.0: true → v0.1.1: false (fallback 도입)
      alternatives: ["검토 결과", "리뷰 결과", "지적 사항"]
      fallback_when_absent: "finding-per-block (P[0-3] 태그 ≥1)"

  format_constraints:
    min_length_chars: 100
    max_length_chars: 20000

    forbidden_patterns:
      # 모호 표현 금지 (나쁜 발언 예시 기준)
      - pattern: "꼼꼼히"
        scope: "all"
      - pattern: "좀\\s*더"
        scope: "all"
      - pattern: "적절히"
        scope: "all"
      - pattern: "알아서"
        scope: "all"
      - pattern: "\\[placeholder\\]"
        scope: "all"
      - pattern: "\\[TBD\\]"
        scope: "all"

    required_patterns:
      - pattern: "P[0-3]"
        scope: "all"
        # 심각도 태그 최소 1회 이상 (finding이 최소 1개 존재함을 함의)

  invariants:
    - id: "INV-WREV-01"
      rule: "Findings 섹션(또는 alternatives) 1개 이상, 또는 finding-per-block 형식(P[0-3] 태그 ≥1)"
      check: |
        headings = extract_headings(output)
        alternatives = ["Findings", "검토 결과", "리뷰 결과", "지적 사항"]
        has_heading = any(normalize(h) in [normalize(a) for a in alternatives] for h in headings)
        # Fallback: heading 없어도 P[0-3] 태그로 명확히 구분된 finding 블록이 ≥1개면 통과.
        # 격리 dry run(2026-04-16)에서 reviewer가 heading 없이 `[CODE] 코드 품질 P0:`
        # 형식의 finding-per-block 구조를 자연스럽게 채택함을 실측. AC가 heading을
        # 강제하면 valid 출력을 reject하는 부작용 발생 → fallback 도입.
        finding_blocks = re.findall(r"P[0-3]", output_text)
        has_heading or len(finding_blocks) >= 1

    - id: "INV-WREV-02"
      rule: "심각도 태그 P0~P3이 최소 1회 이상 등장"
      check: "bool(re.search(r'P[0-3]', output_text))"

    - id: "INV-WREV-03"
      rule: "모호 표현 forbidden patterns 전수 통과"
      check: |
        for fp in forbidden_patterns:
          text = resolve_scoped_text(fp, output)
          assert not re.search(fp.pattern, text)

    - id: "INV-WREV-04"
      rule: "길이 범위 이내"
      check: "100 <= len(output_text) <= 20000"

    - id: "INV-WREV-05"
      rule: "scoped required patterns 전수 충족"
      check: |
        for rp in required_patterns:
          text = resolve_scoped_text(rp, output)
          assert re.search(rp.pattern, text)

  verification: "구조 파싱 + scoped regex 매칭. 1개라도 fail → reject."
```

<rationale>
금기(예: 아키텍처 수준 의견)와 발언 품질("구체적이고 실행 가능한가")은 의미 판단이
필요하므로 Tier 1 regex/string 검증으로 잡을 수 없다. 따라서 Tier 1 공통 AC는
"구조적 요건"(findings 섹션 존재, 심각도 태그, 모호 표현 부재)만 검증하고, 금기·발언
품질 검증은 Tier 2 승격 시 Semantic AC로 도입한다. 지금은 실측 데이터 축적 후
Tier 2 승격 판단.

v0.1.1에서 INV-WREV-01의 heading 강제를 fallback으로 완화한 이유는, 격리 dry run에서
reviewer가 heading 없는 finding-per-block 형식을 자연스럽게 선택함을 확인했기 때문.
heading 강제는 valid output을 reject하는 false negative를 만든다.
</rationale>

### Stability Invariant

```yaml
stability:
  tier_1_runs: 3
  optimization:
    # Tier 1 규칙: complexity 최상위 1개 fixture에만 stability runs 적용.
    # fixture 선정은 페르소나 AC에서 complexity meta로 표시.
    selection_rule: "fixture meta.complexity == 'high'인 것 1개 (없으면 랜덤 1개)"
    fallback: "대표 fixture stability fail → 전체 fixture로 확대 재검증"
  check: |
    선택된 fixture에 대해 3회 실행.
    각 실행이 개별적으로 Hard AC invariants를 전수 통과해야 함.
    document output이므로 3회 중 2회 이상 동일 fixture 판정이면 pass.
```

---

## 3. Artifact AC (공통)

v3.3 template Section 3의 기본 4항목을 reviewer 공통으로 적용한다. `merged_vocabulary`는 `global(VOCABULARY.yaml) ∪ common(이 파일 domain_vocabulary) ∪ persona(페르소나 AC domain_vocabulary)`.

```yaml
artifact_ac:
  frontmatter_checks:
    - id: "ART-WREV-01"
      rule: "SKILL.md name == 'wtth:reviewer:{persona}'"
      # {persona}는 페르소나 AC에서 채움

    - id: "ART-WREV-02"
      rule: "SKILL.md description이 purpose 핵심 키워드 70% 이상 포함"
      check: |
        keywords = extract_keywords(purpose, merged_vocabulary)
        match_rate = sum(1 for kw in keywords if kw in skill_md.description) / len(keywords)
        match_rate >= 0.7

    - id: "ART-WREV-03"
      rule: "trigger_conditions 핵심 키워드가 SKILL.md에 반영"
      check: |
        for tc in trigger_conditions:
          keywords = extract_keywords(tc, merged_vocabulary)
          assert any(kw in skill_md_full_text for kw in keywords)

    - id: "ART-WREV-04"
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

## 4. Fixture AC (공통 정책, 구체 fixture는 페르소나에서)

```yaml
fixture_policy:
  tier_1_minimum_count_document: 3
  pass_rate_by_output_type:
    document: 0.8            # document Tier 1 기본값
  verification: "regex, string match, numeric comparison. LLM judge 없음."

# 구체 fixture 목록은 페르소나 AC의 Section 4에서 정의한다.
# 공통 AC는 fixture 스키마만 위임한다 (v3.3 template Section 4 참조).
```

---

## 5. Retry Policy (공통)

```yaml
# v3.3 template 기본값 그대로 적용. 페르소나 AC에서 명시 override 없으면 이 값 사용.
retry_policy:
  hard_ac_retry: 3
  stability_retry: 2
  artifact_ac_retry: 2
  fixture_ac_retry: 2

  total_max_retry: 5

  retry_context:
    include_failed_assertions: true
    include_failed_fixtures: true
    include_stability_diff: true
```

---

## 6. Tier 2 승격 후보 — 실측 후 판단

다음 요건은 Tier 1 regex 수준에서 검출 불가이며, 실측 데이터 축적 후 Tier 2 승격 시 Semantic AC로 도입한다.

| ID (후보) | 요건 | 현재 처리 |
|---|---|---|
| SEM-WREV-01 | 페르소나 금기 위반 없음 (예: CODE가 아키텍처 의견 내놓지 않음) | Tier 1에선 검출 불가, fixture에 금기 영역 제외로 우회 |
| SEM-WREV-02 | 발언이 구체적 (파일·함수명·줄번호 등 식별자 포함) | 부분 검출 가능(required_pattern으로), 질적 판단은 Tier 2 |
| SEM-WREV-03 | 체크리스트 참조가 적절 (실제 문제와 일치) | 참조 존재 여부만 Tier 1에서 확인 |
| SEM-WREV-04 | 심각도 태깅이 타당 (P0가 정말 P0급인가) | 실측 후 fixture 기반 검증으로 간접 측정 |

승격 조건: `동일 reviewer AC에서 HITL escalation 3회 누적` 또는 `실측 결과 Tier 1 invariants가 금기 위반·발언 품질 저하를 놓치는 사례 명확`.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-15 | 최초 작성. v3.3 template 적용. CODE 페르소나 AC와 병행 작성. |
| 0.1.1 | 2026-04-16 | 격리 dry run(`dry-run-code-v0.2.0-actual-skill.md` §8.1) 결과 반영. INV-WREV-01에 finding-per-block fallback 도입 — heading 부재여도 P[0-3] 태그로 구분된 블록 ≥1이면 통과. `required_sections.required: true → false`. |

## References
- papillon AC Template: [`../../08-ac/ac-template-v3.3.md`](../../08-ac/ac-template-v3.3.md)
- 이전 버전: [`./common-v0.1.0.md`](./common-v0.1.0.md)
- v0.1.1 근거: [`./dry-run-code-v0.2.0-actual-skill.md`](./dry-run-code-v0.2.0-actual-skill.md) §8.1
- wtth 코어 설계: [`../02-design/00-core.md`](../02-design/00-core.md)
- 리뷰 모드별 설계: [`../02-design/03-review-task.md`](../02-design/03-review-task.md)
- 페르소나 정의: [`../../personas/`](../../personas/)
