# Baseline Probability — 확률 bucket 어휘 + Prior 카탈로그 v0.1

## 0. 문서 성격

Issue-08 §축 E 의 정본. reviewer 페르소나가 finding 심각도 판정 시 참조하는 **공용 확률 prior 카탈로그**.

- **버전**: v0.1 (2026-04-21 초안)
- **갱신 주기**: 분기 1~2회 메타 리뷰 + 인시던트 발생 시 즉시
- **관리**: 수동 (Josh)
- **초안 한계**: 일반적 prior 중심. 내부 실측 prior (특정 워크로드/인프라 조합) 는 메타 리뷰로 점진 보강.

---

## 1. 확률 bucket 어휘 (5단계 고정)

| Bucket | 기준 빈도 | Tag |
|---|---|---|
| **극미** | 연 1회 이하 | `extremely-low` |
| **낮음** | 분기 1회 이하 | `low` |
| **중간** | 월 수회 | `medium` |
| **높음** | 주 수회 | `high` |
| **매우 높음** | 일 수회, 또는 재현 1시간 이내 | `very-high` |

**결합 확률 bucket 계산**:
- 단일 조건: 해당 조건의 bucket.
- 병목 조건 1개가 전체를 결정하는 경우: 병목의 bucket.
- 여러 독립 조건 AND 필요: **가장 낮은 bucket** 채택 (AND = min).
- 여러 조건 OR: 가장 높은 bucket (OR = max).

**실례**:
- "Elasticache 45분+ 장애 → 유실" = 극미 (AWS SLA 99.99%) → P2 이하 하향.
- "락 없는 공유 변수 경합 → 데이터 유실" = 매우 높음 (1h 재현) → P0 유지.

---

## 2. 영향 × 확률 매트릭스 (common-spec §1 확장 참조)

| 영향\확률 | 극미 | 낮음 | 중간 | 높음 | 매우 높음 |
|---|---|---|---|---|---|
| **치명** (복구 불가 데이터 유실, 보안 사고) | P2 | P1 | P0 | P0 | P0 |
| **높음** (사용자 기능 불능, 수동 복구 필요) | P3 | P2 | P1 | P0 | P0 |
| **중간** (일부 기능 degrade, 자동 복구) | — | P3 | P2 | P1 | P0 |
| **낮음** (관측 품질 저하, 기능 영향 없음) | — | — | P3 | P2 | P1 |

이 매트릭스는 `02-common-spec.md §1` 심각도 기준 확장 시 정본이 됨 (Issue-08 실행 계획 #3).

---

## 3. Prior 카탈로그

### 3.1. 인프라 장애 (AWS 관리형)

| 시나리오 | Bucket | 근거 |
|---|---|---|
| AWS Elasticache 단일 AZ 45분+ 장애 | 극미 | SLA 99.99% (연 52분 이내 총 downtime) |
| AWS RDS Multi-AZ failover 장애 3분+ | 낮음 | SLA 99.95% + 운영 경험 |
| AWS RDS Multi-AZ 완전 불능 (쓰기·읽기) | 극미 | Multi-AZ 설계상 드뭄 |
| AWS EC2 단일 인스턴스 하드웨어 장애 | 낮음 | 연 수회 |
| AWS EBS volume 성능 degrade | 중간 | 월 수회 (burstable volume) |
| AZ 1개 완전 불능 (리전 유지) | 극미 | 연 1회 이하 |
| AWS 리전 전체 장애 | 극미 | 수년 1회 |
| AWS IAM token 만료 | 낮음 | 운영 미숙 시 중간 |
| AWS VPC peering 일시 단절 | 낮음 | 운영 경험 |

### 3.2. 동시성·동기화

| 시나리오 | Bucket | 근거 |
|---|---|---|
| 락 없는 공유 변수 경합 | 매우 높음 | 재현 테스트 1시간 내 100% |
| 잘못된 `volatile` / `@Synchronized` 사용 | 높음 | 주 수회 실제 버그 |
| async/await Deadlock (실수) | 중간 | 월 수회 |
| ThreadLocal leak | 중간 | pool reuse 환경에서 |
| 재진입 (re-entrant) 불가 락에서 재진입 시도 | 높음 | 재현 가능 버그 |
| race condition in test setup | 높음 | flaky 테스트의 전형적 원인 |

### 3.3. 데이터베이스 (MySQL / jOOQ)

| 시나리오 | Bucket | 근거 |
|---|---|---|
| 트랜잭션 deadlock (중규모 트래픽) | 중간~높음 | 주 수회 |
| 쿼리 timeout (인덱스 미사용) | 중간 | 월 수회 (부하 spike 시 높음) |
| 연결 pool 고갈 | 중간 | 특정 부하 패턴에서 |
| 마이그레이션 락 (대형 테이블 ALTER) | 낮음 | 배포 시 |
| Replication lag 10s+ | 중간 | 월 수회 |
| Primary/replica split-brain | 극미 | Multi-AZ 설계상 드뭄 |
| Unique 제약 위반 (race 상 NOT EXISTS → INSERT) | 중간 | 동시 요청 누적 시 |
| AUTO_INCREMENT 소진 | 극미 | BIGINT 기준 |

### 3.4. Kafka / 메시징

| 시나리오 | Bucket | 근거 |
|---|---|---|
| Consumer lag 10분+ | 중간 | 월 수회 (트래픽 spike) |
| Broker 단일 장애 | 낮음 | 분기 1회 이하 |
| 메시지 순서 변경 (partition 내) | 극미 | Kafka 보장 |
| 메시지 순서 변경 (partition 간) | 매우 높음 | partition key 설계 필수 고려 |
| DLT publish 실패 (broker under-min-ISR) | 낮음 | 극소수 |
| Consumer group rebalance 지연 | 중간 | 배포 시 |
| Offset 리셋 실수 | 낮음 | 운영자 개입 필요 |
| max.poll.interval.ms 초과 | 중간 | 무거운 배치 처리 시 |
| Duplicate delivery (at-least-once) | 매우 높음 | Kafka 기본 semantics |

### 3.5. Redis / Cache

| 시나리오 | Bucket | 근거 |
|---|---|---|
| Eviction (LRU, 메모리 부족) | 중간 | 부하 패턴 의존 |
| 연결 일시 실패 (네트워크 blip) | 중간 | 월 수회 |
| 레플리카 지연 100ms+ | 높음 | 기대 동작 (eventually consistent) |
| Elasticache 단일 AZ 장애 45분+ | 극미 | SLA 99.99% |
| Cluster failover 시 쓰기 유실 (최소 단위) | 낮음 | failover 드문 편 |
| TTL 만료 직후 stampede | 중간 | 핫키 패턴 |
| Lua script timeout | 낮음 | 특수 사용 |

### 3.6. HTTP / 외부 API

| 시나리오 | Bucket | 근거 |
|---|---|---|
| 5xx 일시 응답 (backoff 내 회복) | 중간 | 일반적 |
| timeout (외부 서비스 slow) | 중간 | 월 수회 |
| rate limit (429) | 중간 | 버스티 트래픽 |
| SSL 인증서 만료 | 낮음 (모니터링 부재 시 중간) | 운영 성숙도 의존 |
| DNS 해결 실패 (일시) | 낮음 | 운영 경험 |
| TLS handshake 실패 | 낮음 | 인증서 체인 문제 |
| Connection refused (외부 방화벽) | 낮음 | 드문 설정 오류 |

### 3.7. 배포·운영

| 시나리오 | Bucket | 근거 |
|---|---|---|
| 롤백 필요 (버그 즉시 노출) | 낮음 | 운영 성숙도 의존 |
| 설정 오류 (yml typo, 환경변수 누락) | 중간 | 코드 리뷰 부재 시 높음 |
| 시크릿 만료 미알림 | 낮음 (모니터링 있을 때) | 드문 |
| 용량 초과 (디스크/메모리) | 낮음 (모니터링 있을 때) | 급증 이벤트 시 |
| Rolling update 중 짧은 다운타임 | 높음 (기대 동작) | 기대되는 상태 |
| Blue/green 배포 중 db 마이그레이션 race | 중간 | 경험 prior |
| Graceful shutdown 미준수로 요청 drop | 중간 | 설정 누락 시 |

### 3.8. 네트워크

| 시나리오 | Bucket | 근거 |
|---|---|---|
| 네트워크 일시 단절 500ms 이하 | 높음 | 클라우드 환경 일상 |
| Packet loss 1% 이상 1분+ | 중간 | 드문 |
| TCP keepalive 실패 | 낮음 | 특수 환경 |
| VPN 장애 | 낮음 | 운영 환경 의존 |
| Load balancer health check 일시 실패 | 중간 | 배포·재시작 시 |

---

## 4. 사용 규칙

### 4.1. reviewer 프롬프트 참조 방식

reviewer 는 finding 발견 시:

1. **발생 조건 열거**: 이 finding 이 실제 발생하려면 어떤 조건 N가지가 필요한가?
2. **조건별 bucket 대조**: 각 조건을 §3 카탈로그와 대조하여 bucket 추정.
3. **결합 확률**: §1 결합 계산 규칙으로 전체 bucket 도출.
4. **매트릭스 적용**: §2 매트릭스로 심각도 판정.
5. **RDR 박제**: 조건 열거 + bucket 추정 + 매트릭스 결과를 RDR 에 명시.

### 4.2. 카탈로그 외 시나리오

§3 에 없는 시나리오는 reviewer 의 도메인 경험 prior 로 추정 → RDR 에 근거 박제 → 메타 리뷰 시 카탈로그 승격 후보.

### 4.3. 메타 리뷰 주기 (분기)

- 실측 vs prior 대조: "극미" 로 판정됐는데 실제 발생한 사례 있음? → 해당 항목 bucket 상향.
- 방어 대비 기각 패턴: 특정 bucket 의 finding 이 반복 기각 → 해당 bucket 의 심각도 판정 기준 하향.
- 신규 인프라 도입: 해당 카테고리 추가 (예: 신규 리전, 신규 매니지드 서비스).

---

## 5. Known Limitations (v0.1)

- **조직 특화 prior 미반영**: MZ·MegaBird 실제 운영 데이터 기반 prior 아직 통합 안 됨.
- **체급별 구분 없음**: 같은 "중간" bucket 이라도 L 체급 시스템과 S 체급에서 체감 빈도 다를 수 있음.
- **상호작용 효과 미모델링**: 조건 A와 조건 B가 **상관** (예: 동일 인프라 장애로 연쇄) 인 경우 AND 단순 min 이 과소 추정.

→ v0.2 이후 점진 보강.

---

## 6. 참조

- Issue-08: [80-Issue/08-Issue-08/00-index-issue-08.md](../80-Issue/08-Issue-08/00-index-issue-08.md)
- `02-common-spec.md` §1 (심각도 기준) — §2 매트릭스 박제 대상 (Issue-08 실행 #3)
- `04-wtth` reviewer 페르소나 — §4.1 참조 지침 반영 대상 (Issue-08 실행 #4)
- `01-Planning/08-ac/` reviewer AC — 확률 축 invariant 반영 대상 (Issue-08 실행 #7)
- AWS Service Level Agreements — https://aws.amazon.com/legal/service-level-agreements/ (권위 소스)
