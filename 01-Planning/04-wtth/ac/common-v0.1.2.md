# wtth Reviewer — 공통 Acceptance Criteria (v0.1.2)

> papillon AC Template v3.3 적용.
> 모든 reviewer 페르소나(CODE, BE, FE, SEC, TEST, ARCH, DBA 등)에 공통으로 적용되는 베이스 AC.
> 페르소나별 특이 사항은 `{persona}-v0.1.1.md` 또는 이후 버전에서 override한다.
>
> **v0.1.2 변경**: Issue-08 §축 A 연동 — 확률 reasoning 검증 invariant (`INV-WREV-06`) 신규 + 확률 bucket 어휘 vocabulary 확장.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer"
version: "0.1.2"
previous_version: "0.1.1"
tier: "tier_1"
output_type: "document"
domain_vocabulary:
  - "P0"
  - "P1"
  - "P2"
  - "P3"
  - "finding"
  - "reviewer"
  - "RDR"
  - "체크리스트"
  # v0.1.2 추가 — Issue-08 확률 축
  - "극미"
  - "낮음"
  - "중간"
  - "높음"
  - "매우 높음"
  - "bucket"
  - "발생 조건"
  - "결합 확률"
  - "영향"
test_mode: "single_turn"
created_by: "Josh"
created_at: "2026-04-15"
updated_at: "2026-04-21"

# Override 규칙 (v0.1.1 과 동일):
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
    P0/P1 finding 은 확률 reasoning (영향 × 확률 bucket) 을 함께 제시한다.

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
        - P0/P1 의 경우 확률 reasoning (발생 조건·bucket·결합 확률)
```

---

## 2. Hard AC — Variant B: Document Output (공통)

```yaml
hard_ac_document:
  required_sections:
    - heading: "Findings"
      level: 2
      required: false
      alternatives: ["검토 결과", "리뷰 결과", "지적 사항"]
      fallback_when_absent: "finding-per-block (P[0-3] 태그 ≥1)"

  format_constraints:
    min_length_chars: 100
    max_length_chars: 20000

    forbidden_patterns:
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

    # v0.1.2 신규 — Issue-08 §축 A
    - id: "INV-WREV-06"
      rule: "P0/P1 finding 존재 시 확률 bucket 어휘 최소 1회 등장 (Issue-08 §축 A)"
      check: |
        has_p0p1 = bool(re.search(r"P[01]\b", output_text))
        if has_p0p1:
          bucket_pattern = r"극미|낮음|중간|높음|매우\s*높음"
          has_bucket = bool(re.search(bucket_pattern, output_text))
          assert has_bucket, (
            "P0/P1 finding 이 있으나 확률 reasoning 부재. "
            "common-spec §1.4 5단계 절차 준수 필요. "
            "baseline-probability.md §3 카탈로그 참조."
          )

  verification: "구조 파싱 + scoped regex 매칭. 1개라도 fail → reject."
```

<rationale>
v0.1.2 에서 INV-WREV-06 을 추가한 이유는 Issue-08 §축 A 의 "확률 reasoning
강제" 를 AC 수준에서 검증하기 위함. Tier 1 수준에선 "reasoning 의 타당성"
까진 검증 불가하므로, 최소한 **확률 bucket 어휘** 가 output 에 등장하는지만
1차 감시. 2e/2f 실측에서 reviewer 가 확률 축 reasoning 을 아예 빼먹는
패턴이 수용률 저하의 주 원인으로 식별됨.

"타당성" 검증은 SEM-WREV-05 (Tier 2 승격 후보) 로 예고.

INV-WREV-06 이 false positive 가능: reviewer 가 P2/P3 만 냈는데 bucket 어휘가
함께 등장하지 않는 경우는 허용 (has_p0p1 false 시 skip). 반대로 false negative
가능: P0/P1 이 있고 output 다른 맥락에서 bucket 어휘가 등장했지만 실제 그
P0/P1 과 연결되지 않은 경우. Tier 1 한계로 받아들이고 실측 데이터로 개선.
</rationale>

### Stability Invariant

```yaml
stability:
  tier_1_runs: 3
  optimization:
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
    document: 0.8
  verification: "regex, string match, numeric comparison. LLM judge 없음."
```

---

## 5. Retry Policy (공통)

```yaml
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
| SEM-WREV-01 | 페르소나 금기 위반 없음 | Tier 1에선 검출 불가, fixture에 금기 영역 제외로 우회 |
| SEM-WREV-02 | 발언이 구체적 (파일·함수명·줄번호 등 식별자 포함) | 부분 검출 가능(required_pattern으로), 질적 판단은 Tier 2 |
| SEM-WREV-03 | 체크리스트 참조가 적절 (실제 문제와 일치) | 참조 존재 여부만 Tier 1에서 확인 |
| SEM-WREV-04 | 심각도 태깅이 타당 (P0가 정말 P0급인가) | 실측 후 fixture 기반 검증으로 간접 측정 |
| **SEM-WREV-05 (v0.1.2 추가)** | **확률 reasoning 의 타당성** (bucket 추정이 실제 prior 와 정합한가) | INV-WREV-06 은 어휘 등장 여부만 감시. 타당성은 Tier 2 로 |

승격 조건: `동일 reviewer AC에서 HITL escalation 3회 누적` 또는 `실측 결과 Tier 1 invariants가 금기 위반·발언 품질 저하를 놓치는 사례 명확`.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-15 | 최초 작성. v3.3 template 적용. CODE 페르소나 AC와 병행 작성. |
| 0.1.1 | 2026-04-16 | 격리 dry run(`dry-run-code-v0.2.0-actual-skill.md` §8.1) 결과 반영. INV-WREV-01에 finding-per-block fallback 도입 — heading 부재여도 P[0-3] 태그로 구분된 블록 ≥1이면 통과. `required_sections.required: true → false`. |
| **0.1.2** | **2026-04-21** | Issue-08 §축 A 연동. INV-WREV-06 신설 (P0/P1 존재 시 확률 bucket 어휘 최소 1회 등장). domain_vocabulary 확장 (확률 bucket 5단계 + bucket / 발생 조건 / 결합 확률 / 영향). SEM-WREV-05 Tier 2 승격 후보 추가 (확률 reasoning 타당성). output_spec 에 "P0/P1 확률 reasoning 포함" 명시. |

## References
- papillon AC Template: [`../../08-ac/ac-template-v3.3.md`](../../08-ac/ac-template-v3.3.md)
- 이전 버전: [`./common-v0.1.1.md`](./common-v0.1.1.md), [`./common-v0.1.0.md`](./common-v0.1.0.md)
- Issue-08: [`../../../80-Issue/08-Issue-08/00-index-issue-08.md`](../../../80-Issue/08-Issue-08/00-index-issue-08.md)
- baseline-probability: [`../../baseline-probability.md`](../../baseline-probability.md)
- common-spec §1.4 / §1.6: [`../../02-common-spec.md`](../../02-common-spec.md)
- wtth 코어 설계: [`../02-design/00-core.md`](../02-design/00-core.md) §2.0
- 페르소나 정의: [`../../51-expert-definitions.md`](../../51-expert-definitions.md)
