# Issue-06 TDD-ready 설계서 Exemplar (익명화 복제본)

## 개요

이 디렉토리는 TDD-ready 설계서 exemplar 10건의 **익명화 복제본**이다. Issue-06 v0.2.0 환류의 tracing 대상 4건 분석에 사용한다.

## Snapshot 정보

- **복제 시점**: 2026-04-20 12:16 KST
- **원본 위치**: `~/Work/example/example-work-plan/PROJ-101/PROJ-102/50-pipeline/T1-stats-consumer/` (마스킹 후 표기)
- **복제 방식**: `tools/anonymize-exemplar.py` 일괄 실행 (468+ 치환 × 10 파일)

## 중요 — snapshot 시점의 지시서 상태

복제 시점 기준 각 지시서 상태 (2026-04-20 12:16 KST):

- `shackled-phase2e-upsert-service.md` — **wtth 리뷰 반영본 + shackled TDD 실행 + 코드 구현 완료**. 이 지시서로 완전 사이클이 돌아간 상태 → 환류 §8 tracing의 실측 근거로 사용 가능.
- `shackled-phase2f-pipeline-assembly.md` — **shackled TDD 진행 준비 중**. 2f shackled 실행·코드 구현은 아직. 완료 후 재평가 데이터 추가 예정.
- 나머지 8건 (2a/2b/2c/2d + overview + phase1 + use-block + use-tenant) — 이미 구현 완료 또는 선행 자산. snapshot 이후 변동 가능성 낮음.

재복제 방법은 아래 §"재복제 방법" 참조.

## 익명화 규칙 요약

**얕은 익명화** 채택. 회사/프로젝트 식별자만 마스킹, 도메인 용어(테이블·컬럼·채널 코드)는 exemplar 가독성 유지를 위해 보존.

| 분류 | 원본 패턴 | 마스킹 |
|---|---|---|
| 회사명 | `megabird`, 메가버드 | `example-corp`, 본사 |
| 레포 | `megabird-stats-billing`, `megabird-database` | `example-stats-billing`, `example-database` |
| 프로젝트 코드 | `QLSN-476` / `QLSN-478` | `PROJ-101` / `PROJ-102` |
| Datasource | `megabird-ds` / `coupang-ds` | `primary-ds` / `secondary-ds` |
| 테넌트 (8종) | `coupang`, `ces`, `cfs`, `cls`, `cmgmarketing`, `coupangeats`, `coupangflex`, `ddnayo` | `tenant-a` ~ `tenant-h` |
| 외부 시스템 | `__bms__`, `BMS_TENANT`, `BmsEventValidator`, `mapBms` | `__ext__`, `EXT_TENANT`, `ExtEventValidator`, `mapExt` |
| 상수 | `TenantCode.MEGABIRD` | `TenantCode.PRIMARY` |
| 패키지 | `com.megabird.*` | `com.example.*` |
| URL | `nexus.megabird-dev.com` | `nexus.example-dev.com` |
| 한국어 | 쿠팡 테넌트, 메가버드 | 외부 테넌트, 본사 |
| 유지 (선택) | `TNT_INTG_MSG_SND`, `TMG_MSG_TGUS`, `SVC_KND_CD`, `TKA`/`SMS`/`LMS`... | 그대로 |

원본↔마스킹 **완전 매핑**은 `anonymization-mapping.md` (gitignore). 복원키이므로 레포 공개 금지.

## 파일 목록 (10건)

| 파일 | 체급 | Issue-06 재평가 적합도 |
|---|---|---|
| `shackled-phase1-directive.md` | L | N/A (TDD 제외, 골격) |
| `shackled-phase2-00-overview.md` | — | 공통 제약 (★★★★★) |
| `shackled-phase2a-bms-validator.md` | S | ★★★★★ |
| `shackled-phase2b-channel-type-code.md` | S | ★★★★★ (신규 exemplar 후보) |
| `shackled-phase2c-original-lookup.md` | M | ★★★★★ (상향 제안) |
| `shackled-phase2d-dimension-mapper.md` | S | ★★★★★ (신규 exemplar 후보) |
| `shackled-phase2e-upsert-service.md` | L | ★★★★ (상향 제안, shackled+구현 완료) |
| `shackled-phase2f-pipeline-assembly.md` | L | ★★★★★ (신규 exemplar 후보, 착수 전) |
| `shackled-shared-tenant-context-use-block.md` | XS | ★★★★☆ |
| `shackled-use-tenant-directive.md` | S | ★★★★ |

상세: [`../tdd-ready-evaluation-memo-2026-04-20.md`](../tdd-ready-evaluation-memo-2026-04-20.md)

## 재복제 방법

phase2e/2f 확정 또는 원본 변경 시:

```bash
cd ~/Work/improve-review-hell
rm -f 80-Issue/06-Issue-06/exemplar/shackled-*.md
python3 tools/anonymize-exemplar.py
```

스크립트는 멱등적 (동일 입력 → 동일 출력). 원본 megabird 레포는 무변경.

## 참조

- Issue-06 #1 스펙 초안: [`../tdd-ready-spec-v0.1.0-draft.md`](../tdd-ready-spec-v0.1.0-draft.md)
- 재평가 메모: [`../tdd-ready-evaluation-memo-2026-04-20.md`](../tdd-ready-evaluation-memo-2026-04-20.md)
- 인덱스: [`../00-index-issue-06.md`](../00-index-issue-06.md)
- 익명화 스크립트: [`../../../tools/anonymize-exemplar.py`](../../../tools/anonymize-exemplar.py)
