# wtth Reviewer — FE 페르소나 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 공통 reviewer AC(`common-v0.1.1.md`)를 기반으로 FE 페르소나 특이 사항을 override한다.
> Override되지 않은 항목은 공통 AC를 그대로 사용한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer:fe"
parent_ac: "wtth:reviewer v0.1.1 (common-v0.1.1.md)"
version: "0.1.0"
previous_version: null
tier: "tier_1"
output_type: "document"

domain_vocabulary_additions: [
  "에러", "상태", "로딩", "빈",
  "낙관적", "롤백", "접근성",
  "키보드", "스크린리더", "반응형",
  "멀티스텝", "이탈", "복귀",
  "UX", "피드백", "검증"
]

test_mode: "single_turn"
created_by: "Josh"
created_at: "2026-04-16"
updated_at: "2026-04-16"
```

---

## 1. Skill Identity (override)

```yaml
identity:
  purpose: |
    FE 페르소나로서 설계 문서를 리뷰하여 사용자 흐름·에러/로딩/빈 상태
    설계·낙관적 업데이트·접근성 관련 finding을 생성한다.

  trigger_conditions:
    - "설계 리뷰 모드에서 FE 페르소나가 투입되었을 때"
    - "wtth 단독 실행 시 리뷰 대상이 UI/프론트엔드 설계 문서인 경우"

  non_trigger_conditions:
    - "백엔드 로직 (BE 영역)"
    - "보안 정책 (SEC 영역)"
    - "인프라 (SRE 영역)"

  input_spec:
    description: |
      UI 설계 문서 Markdown 발췌. 화면 흐름, 상태 설계, 컴포넌트 명세 등.

  output_spec:
    type: "document"
    description: |
      공통 AC의 output_spec을 따른다. FE 페르소나 특화 요구:
      - 각 finding은 체크리스트 항목 참조 `[체크리스트: {항목명}]` 1회 이상
      - 위치 참조는 화면명, 단계명, 컴포넌트명 등 포함 권장
```

---

## 2. Hard AC override

```yaml
hard_ac_document_additions:
  required_patterns_additional:
    - pattern: "\\[체크리스트:\\s*[^\\]]+\\]"
      scope: "all"

  invariants_additional:
    - id: "INV-FE-01"
      rule: "체크리스트 참조 형식 `[체크리스트: 항목명]`이 최소 1회 이상 등장"
      check: |
        import re
        matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output_text)
        assert len(matches) >= 1

    - id: "INV-FE-02"
      rule: "위치 참조 — 화면명, 단계명, 컴포넌트명 등 구체적 식별자 최소 1회"
      check: |
        has_screen = bool(re.search(r"(화면|페이지|뷰|스크린|모달|다이얼로그)", output_text))
        has_step = bool(re.search(r"(\d+\s*단계|\d+단계|step\s*\d)", output_text, re.IGNORECASE))
        has_component = bool(re.search(r"(컴포넌트|버튼|폼|입력|목록|카드)", output_text))
        has_api = bool(re.search(r"(GET|POST|PUT|PATCH|DELETE)\s+/\S+|API\s+\S+", output_text))
        has_screen or has_step or has_component or has_api
```

---

## 3. Artifact AC (공통 사용, `{persona}` 치환만)

```yaml
# ART-WREV-01의 {persona} 치환:
#   rule: "SKILL.md name == 'wtth:reviewer:fe'"
```

---

## 4. Fixture AC

```yaml
fixtures:
  - id: "FIX-FE-01"
    description: "에러 상태 설계 완전 부재 — API 실패 시 UI 무반응"
    meta:
      language: "markdown"
      complexity: "high"
    input:
      code_snippet: |
        ## 상품 상세 페이지

        ### 화면 구성
        - 상품 이미지 갤러리
        - 상품명, 가격, 설명
        - "장바구니 담기" 버튼 → `POST /api/cart/items` 호출
        - "바로 구매" 버튼 → 결제 페이지로 이동

        ### 데이터 로드
        - `GET /api/products/{id}` 호출하여 상품 정보 표시
    expected:
      must_match_patterns:
        - "P[01]"
        - "에러|실패|오류|error"
        - "\\[체크리스트:[^\\]]*에러[^\\]]*\\]"
      min_length: 100

  - id: "FIX-FE-02"
    description: "멀티스텝 이탈 시 데이터 유실"
    meta:
      language: "markdown"
      complexity: "medium"
    input:
      code_snippet: |
        ## 회원가입 3단계 흐름

        ### 1단계: 이메일/비밀번호 입력
        - 이메일 형식 검증
        - 비밀번호 강도 체크

        ### 2단계: 프로필 정보 입력
        - 이름, 전화번호
        - 프로필 이미지 업로드

        ### 3단계: 약관 동의 및 완료
        - 필수/선택 약관 체크
        - "가입 완료" 버튼 → `POST /api/users`
    expected:
      must_match_patterns:
        - "P[12]"
        - "이탈|뒤로|복귀|유실|초기화|상태.*유지"
        - "\\[체크리스트:[^\\]]*(이탈|복귀|멀티스텝)[^\\]]*\\]"
      min_length: 100

  - id: "FIX-FE-03"
    description: "로딩/빈 상태 미설계"
    meta:
      language: "markdown"
      complexity: "low"
    input:
      code_snippet: |
        ## 주문 내역 페이지

        ### 화면 구성
        - 주문 목록 (최신순, 페이지네이션)
        - 각 주문 카드: 주문번호, 일시, 금액, 상태

        ### 데이터
        - `GET /api/orders?page=1&size=10`
    expected:
      must_match_patterns:
        - "P[23]"
        - "로딩|빈\\s*상태|데이터.*없|empty|skeleton|스피너"
        - "\\[체크리스트:[^\\]]*(로딩|빈)[^\\]]*\\]"
      min_length: 100

fixture_policy:
  tier_1_minimum_count_document: 3
  pass_rate: 0.8
  verification: "regex, string match, numeric comparison. LLM 호출 없음."

stability:
  selected_fixture: "FIX-FE-01"
  runs: 3
```

---

## 5. Retry Policy

공통 AC의 `retry_policy` 그대로 사용. override 없음.

---

## 6. Tier 2 승격 체크 항목 (FE 특화)

| 관찰 항목 | 승격 트리거 |
|---|---|
| 백엔드 로직 금기 위반 ("이 API 로직을...") | 사례 3회 시 SEM-FE-01 도입 |
| 체크리스트 참조와 실제 finding 불일치 | 사례 2회 시 SEM-FE-02 도입 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-16 | 최초 작성. code-v0.1.1 구조 복제 + FE 설계 리뷰 override. |

## References
- 공통 AC: [`./common-v0.1.1.md`](./common-v0.1.1.md)
- FE 페르소나 정의: [`../../personas/fe.md`](../../personas/fe.md)
