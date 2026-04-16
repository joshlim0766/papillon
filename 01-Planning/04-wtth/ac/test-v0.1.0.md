# wtth Reviewer — TEST 페르소나 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 공통 reviewer AC(`common-v0.1.1.md`)를 기반으로 TEST 페르소나 특이 사항을 override한다.
> Override되지 않은 항목은 공통 AC를 그대로 사용한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer:test"
parent_ac: "wtth:reviewer v0.1.1 (common-v0.1.1.md)"
version: "0.1.0"
previous_version: null
tier: "tier_1"
output_type: "document"

domain_vocabulary_additions: [
  "테스트", "커버리지", "케이스",
  "happy", "path", "에러", "예외",
  "경계값", "격리", "의존",
  "회귀", "프레임워크", "mock",
  "assert", "expect", "describe"
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
    TEST 페르소나로서 소스 코드 또는 diff를 리뷰하여 테스트 커버리지·
    누락 케이스·테스트 격리·테스트 코드 품질 관련 finding을 생성한다.

  trigger_conditions:
    - "코드 리뷰 모드에서 TEST 페르소나가 투입되었을 때"
    - "wtth 단독 실행 시 리뷰 대상이 테스트 코드 또는 테스트 대상 코드인 경우"

  non_trigger_conditions:
    - "프로덕션 코드 로직 수정 (CODE 영역)"
    - "아키텍처 의견 (ARCH 영역)"
    - "네이밍/컨벤션 (CODE 영역)"
    - "포매팅 (린터 영역)"

  input_spec:
    description: |
      소스 코드 snippet 또는 diff. 프로덕션 코드 + 테스트 코드 쌍.
      언어는 fixture별로 명시.

  output_spec:
    type: "document"
    description: |
      공통 AC의 output_spec을 따른다. TEST 페르소나 특화 요구:
      - 각 finding은 체크리스트 항목 참조 `[체크리스트: {항목명}]` 1회 이상
      - 위치 참조는 함수명 또는 테스트 함수명 포함 권장
```

---

## 2. Hard AC override

```yaml
hard_ac_document_additions:
  required_patterns_additional:
    - pattern: "\\[체크리스트:\\s*[^\\]]+\\]"
      scope: "all"

  invariants_additional:
    - id: "INV-TEST-01"
      rule: "체크리스트 참조 형식 `[체크리스트: 항목명]`이 최소 1회 이상 등장"
      check: |
        import re
        matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output_text)
        assert len(matches) >= 1

    - id: "INV-TEST-02"
      rule: "위치 참조 — 함수명(괄호 포함) 또는 파일:라인 형태가 최소 1회 이상"
      check: |
        has_func = bool(re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(", output_text))
        has_file = bool(re.search(r"[\w./\\-]+\.\w+:\d+", output_text))
        has_func or has_file
```

---

## 3. Artifact AC (공통 사용, `{persona}` 치환만)

```yaml
# ART-WREV-01의 {persona} 치환:
#   rule: "SKILL.md name == 'wtth:reviewer:test'"
```

---

## 4. Fixture AC

```yaml
fixtures:
  - id: "FIX-TEST-01"
    description: "변경 코드에 테스트 전혀 없음"
    meta:
      language: "typescript"
      complexity: "high"
    input:
      code_snippet: |
        // src/services/order.ts (변경됨)
        export async function createOrder(userId: string, items: CartItem[]): Promise<Order> {
          const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
          if (total > 10000) {
            await notifyFraudTeam(userId, total);
          }
          const order = await orderRepo.create({ userId, items, total });
          await inventoryService.deduct(items);
          return order;
        }

        // tests/ 디렉토리에 createOrder 관련 테스트 파일 없음
    expected:
      must_match_patterns:
        - "P[01]"
        - "테스트.*없|테스트.*부재|커버리지|미작성"
        - "\\[체크리스트:[^\\]]*(테스트|존재)[^\\]]*\\]"
      min_length: 100

  - id: "FIX-TEST-02"
    description: "에러/예외 경로 테스트 누락"
    meta:
      language: "typescript"
      complexity: "medium"
    input:
      code_snippet: |
        // src/services/payment.ts
        export async function processPayment(orderId: string, card: CardInfo): Promise<PaymentResult> {
          const order = await orderRepo.findById(orderId);
          if (!order) throw new NotFoundError('Order not found');
          if (order.status !== 'PENDING') throw new InvalidStateError('Not payable');
          const result = await pgGateway.charge(card, order.total);
          if (!result.success) throw new PaymentFailedError(result.reason);
          await orderRepo.updateStatus(orderId, 'PAID');
          return result;
        }

        // tests/payment.test.ts
        describe('processPayment', () => {
          it('should process payment successfully', async () => {
            const result = await processPayment('order-1', validCard);
            expect(result.success).toBe(true);
          });
        });
    expected:
      must_match_patterns:
        - "P[12]"
        - "에러|예외|실패|경로|throw|NotFound|InvalidState|PaymentFailed"
        - "\\[체크리스트:[^\\]]*(에러|예외)[^\\]]*\\]"
      min_length: 100

  - id: "FIX-TEST-03"
    description: "테스트 격리 위반 — 다른 테스트에 의존"
    meta:
      language: "typescript"
      complexity: "low"
    input:
      code_snippet: |
        // tests/user.test.ts
        let createdUserId: string;

        describe('User CRUD', () => {
          it('should create user', async () => {
            const user = await createUser({ name: 'test' });
            createdUserId = user.id;
            expect(user.name).toBe('test');
          });

          it('should get user', async () => {
            const user = await getUser(createdUserId);
            expect(user.name).toBe('test');
          });

          it('should delete user', async () => {
            await deleteUser(createdUserId);
            const user = await getUser(createdUserId);
            expect(user).toBeNull();
          });
        });
    expected:
      must_match_patterns:
        - "P[23]"
        - "격리|의존|순서|공유.*상태|shared.*state|createdUserId"
        - "\\[체크리스트:[^\\]]*격리[^\\]]*\\]"
      min_length: 100

fixture_policy:
  tier_1_minimum_count_document: 3
  pass_rate: 0.8
  verification: "regex, string match, numeric comparison. LLM 호출 없음."

stability:
  selected_fixture: "FIX-TEST-01"
  runs: 3
```

---

## 5. Retry Policy

공통 AC의 `retry_policy` 그대로 사용. override 없음.

---

## 6. Tier 2 승격 체크 항목 (TEST 특화)

| 관찰 항목 | 승격 트리거 |
|---|---|
| 프로덕션 코드 수정 제안 (CODE 금기 침범) | 사례 3회 시 SEM-TEST-01 도입 |
| 체크리스트 참조와 실제 finding 불일치 | 사례 2회 시 SEM-TEST-02 도입 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-16 | 최초 작성. code-v0.1.1 구조 복제 + TEST 코드 리뷰 override. |

## References
- 공통 AC: [`./common-v0.1.1.md`](./common-v0.1.1.md)
- TEST 페르소나 정의: [`../../personas/test.md`](../../personas/test.md)
