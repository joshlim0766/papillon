# wtth Reviewer — DBA 페르소나 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 공통 reviewer AC(`common-v0.1.1.md`)를 기반으로 DBA 페르소나 특이 사항을 override한다.
> Override되지 않은 항목은 공통 AC를 그대로 사용한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer:dba"
parent_ac: "wtth:reviewer v0.1.1 (common-v0.1.1.md)"
version: "0.1.0"
previous_version: null
tier: "tier_1"
output_type: "document"

domain_vocabulary_additions: [
  "쿼리", "인덱스", "복합", "커버링",
  "파티셔닝", "마이그레이션", "DDL",
  "락", "테이블", "풀스캔",
  "리플리케이션", "지연", "볼륨",
  "EXPLAIN", "백업", "복구"
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
    DBA 페르소나로서 설계 문서를 리뷰하여 쿼리 성능·인덱스 전략·
    마이그레이션 안전성·파티셔닝·리플리케이션 영향 관련 finding을 생성한다.

  trigger_conditions:
    - "설계 리뷰 모드에서 DBA 페르소나가 투입되었을 때 (선택적)"
    - "DB 스키마 변경, 대량 데이터 처리, 마이그레이션이 포함된 태스크"

  non_trigger_conditions:
    - "비즈니스 로직 (BE 영역)"
    - "API 설계 (BE 영역)"
    - "보안 정책 (SEC 영역)"

  input_spec:
    description: |
      설계 문서 Markdown 발췌. DB 스키마 변경, DDL, 마이그레이션 계획, 쿼리 설계 등.

  output_spec:
    type: "document"
    description: |
      공통 AC의 output_spec을 따른다. DBA 페르소나 특화 요구:
      - 각 finding은 체크리스트 항목 참조 `[체크리스트: {항목명}]` 1회 이상
      - 위치 참조는 테이블명, DDL 문, 쿼리 등 포함 권장
```

---

## 2. Hard AC override

```yaml
hard_ac_document_additions:
  required_patterns_additional:
    - pattern: "\\[체크리스트:\\s*[^\\]]+\\]"
      scope: "all"

  invariants_additional:
    - id: "INV-DBA-01"
      rule: "체크리스트 참조 형식 `[체크리스트: 항목명]`이 최소 1회 이상 등장"
      check: |
        import re
        matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output_text)
        assert len(matches) >= 1

    - id: "INV-DBA-02"
      rule: "위치 참조 — 테이블명, DDL, 쿼리 등 구체적 DB 식별자 최소 1회"
      check: |
        has_table = bool(re.search(r"\b[a-z_]+s?\b\s*(테이블|table)", output_text, re.IGNORECASE))
        has_ddl = bool(re.search(r"(ALTER|CREATE|DROP|ADD COLUMN|ADD INDEX)", output_text, re.IGNORECASE))
        has_sql = bool(re.search(r"(SELECT|INSERT|UPDATE|DELETE|JOIN)\b", output_text, re.IGNORECASE))
        has_table or has_ddl or has_sql
```

---

## 3. Artifact AC (공통 사용, `{persona}` 치환만)

```yaml
# ART-WREV-01의 {persona} 치환:
#   rule: "SKILL.md name == 'wtth:reviewer:dba'"
```

---

## 4. Fixture AC

```yaml
fixtures:
  - id: "FIX-DBA-01"
    description: "마이그레이션 테이블 락 — 대용량 테이블 ALTER TABLE"
    meta:
      language: "markdown"
      complexity: "high"
    input:
      code_snippet: |
        ## DB 마이그레이션 계획

        ### 변경 사항
        - orders 테이블에 `discount_amount DECIMAL(10,2) DEFAULT 0` 컬럼 추가
        - 현재 orders 테이블 행 수: 약 800만 건

        ### 실행 계획
        ```sql
        ALTER TABLE orders ADD COLUMN discount_amount DECIMAL(10,2) DEFAULT 0;
        ```

        ### 실행 시점
        - 배포 시 자동 실행 (서비스 운영 중)
    expected:
      must_match_patterns:
        - "P0"
        - "락|lock|차단|block|무중단|pt-online|gh-ost"
        - "\\[체크리스트:[^\\]]*(마이그레이션|락)[^\\]]*\\]"
      min_length: 100

  - id: "FIX-DBA-02"
    description: "인덱스 전략 부재 — 주요 조회에 풀 스캔"
    meta:
      language: "markdown"
      complexity: "medium"
    input:
      code_snippet: |
        ## 주문 조회 설계

        ### 주요 쿼리
        - 사용자별 주문 목록: `SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC`
        - 기간별 주문 통계: `SELECT status, COUNT(*) FROM orders WHERE created_at BETWEEN ? AND ? GROUP BY status`

        ### 인덱스
        - 현재: `PRIMARY KEY (id)` 만 존재
        - orders 테이블 예상 행 수: 500만 건 이상
    expected:
      must_match_patterns:
        - "P[01]"
        - "인덱스|index|풀\\s*스캔|full.*scan|user_id|created_at"
        - "\\[체크리스트:[^\\]]*인덱스[^\\]]*\\]"
      min_length: 100

  - id: "FIX-DBA-03"
    description: "파티셔닝 미고려 — 대량 로그 테이블 성장"
    meta:
      language: "markdown"
      complexity: "low"
    input:
      code_snippet: |
        ## 감사 로그 테이블 설계

        ### 스키마
        ```sql
        CREATE TABLE audit_logs (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          user_id VARCHAR(36),
          action VARCHAR(100),
          detail JSON,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        ```

        ### 데이터 규모
        - 일 평균 50만 건 적재
        - 보존 기간: 3년
        - 예상 총 행 수: 약 5.5억 건
    expected:
      must_match_patterns:
        - "P[12]"
        - "파티셔닝|partition|아카이빙|보존|볼륨|성능.*변곡"
        - "\\[체크리스트:[^\\]]*(파티셔닝|볼륨)[^\\]]*\\]"
      min_length: 100

fixture_policy:
  tier_1_minimum_count_document: 3
  pass_rate: 0.8
  verification: "regex, string match, numeric comparison. LLM 호출 없음."

stability:
  selected_fixture: "FIX-DBA-01"
  runs: 3
```

---

## 5. Retry Policy

공통 AC의 `retry_policy` 그대로 사용. override 없음.

---

## 6. Tier 2 승격 체크 항목 (DBA 특화)

| 관찰 항목 | 승격 트리거 |
|---|---|
| 비즈니스 로직 금기 위반 | 사례 3회 시 SEM-DBA-01 도입 |
| 체크리스트 참조와 실제 finding 불일치 | 사례 2회 시 SEM-DBA-02 도입 |
| API 설계 침범 ("이 엔드포인트를...") | 사례 2회 시 SEM-DBA-03 도입 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-16 | 최초 작성. 설계 리뷰 모드 fixture 3개. |

## References
- 공통 AC: [`./common-v0.1.1.md`](./common-v0.1.1.md)
- DBA 페르소나 정의: [`../../personas/dba.md`](../../personas/dba.md)
