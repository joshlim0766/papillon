#!/usr/bin/env python3
"""
Issue-06 exemplar 익명화 복제 스크립트.

원본(megabird-work-plan/QLSN-476/QLSN-478/T1-stats-consumer/shackled-*.md) 10개를
improve-review-hell/80-Issue/06-Issue-06/exemplar/ 로 복제하며 얕은 익명화 적용.

회사/프로젝트 식별자만 마스킹. 도메인 용어(테이블명/컬럼명/채널 코드)는 유지.

재실행 가능 — phase2e/2f 확정 시 재복제 용도.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SOURCE_DIR = Path.home() / "Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer"
TARGET_DIR = Path.home() / "Work/improve-review-hell/80-Issue/06-Issue-06/exemplar"

FILES = [
    "shackled-phase1-directive.md",
    "shackled-phase2-00-overview.md",
    "shackled-phase2a-bms-validator.md",
    "shackled-phase2b-channel-type-code.md",
    "shackled-phase2c-original-lookup.md",
    "shackled-phase2d-dimension-mapper.md",
    "shackled-phase2e-upsert-service.md",
    "shackled-phase2f-pipeline-assembly.md",
    "shackled-shared-tenant-context-use-block.md",
    "shackled-use-tenant-directive.md",
]

# 순서 중요: 긴/특정 토큰 먼저. 순차 치환.
LITERAL_REPLACEMENTS: list[tuple[str, str]] = [
    # 1. 경로·패키지 (가장 구체적)
    ("~/Work/megabird/megabird-work-plan", "~/Work/example/example-work-plan"),
    ("~/Work/megabird/megabird-stats-billing", "~/Work/example/example-stats-billing"),
    ("~/Work/megabird/", "~/Work/example/"),
    ("com.megabird.database.megabird.Tables", "com.example.database.primary.Tables"),
    ("com.megabird.database.megabird", "com.example.database.primary"),
    ("com.megabird.database", "com.example.database"),
    ("com.megabird.tenant", "com.example.tenant"),
    ("com.megabird.canonical", "com.example.canonical"),
    ("com.megabird.stats", "com.example.stats"),
    ("com.megabird", "com.example"),
    # 파일 경로 슬래시 형
    ("com/megabird/database/megabird", "com/example/database/primary"),
    ("com/megabird/database", "com/example/database"),
    ("com/megabird/tenant", "com/example/tenant"),
    ("com/megabird/canonical", "com/example/canonical"),
    ("com/megabird/stats", "com/example/stats"),
    ("com/megabird", "com/example"),

    # 1.5. Kotlin 변수·메서드 합성어 (word boundary 매칭 실패분)
    ("megabirdDataSource", "primaryDataSource"),
    ("coupangDataSource", "secondaryDataSource"),
    ("coupangDS", "secondaryDS"),
    ("coupangTenants", "secondaryTenants"),

    # 2. 레포명·조직 식별
    ("megabird-stats-billing", "example-stats-billing"),
    ("megabird-work-plan", "example-work-plan"),
    ("megabird-database", "example-database"),
    ("nexus.megabird-dev.com", "nexus.example-dev.com"),

    # 3. Datasource / DB 이름
    ("megabird-ds", "primary-ds"),
    ("coupang-ds", "secondary-ds"),
    ("coupang-lookup-ddl.sql", "secondary-lookup-ddl.sql"),

    # 4. 프로젝트 코드
    ("QLSN-476", "PROJ-101"),
    ("QLSN-478", "PROJ-102"),

    # 5. BMS → EXT (긴 토큰 먼저)
    ("BmsOptionalFieldNullException", "ExtOptionalFieldNullException"),
    ("BmsEventValidator", "ExtEventValidator"),
    ("BMS_OPTIONAL_FIELD_NULL", "EXT_OPTIONAL_FIELD_NULL"),
    ("BMS_NEWTYPE", "EXT_NEWTYPE"),
    ("BMS_TENANT", "EXT_TENANT"),
    ("BMS_A", "EXT_A"),
    ("__bms__", "__ext__"),
    ("mapBms", "mapExt"),

    # 6. TenantCode.MEGABIRD → TenantCode.PRIMARY
    ("TenantCode.MEGABIRD", "TenantCode.PRIMARY"),
    ("MEGABIRD.code()", "PRIMARY.code()"),

    # 7. megabird RDS / DB 문맥 (tenant 상수 치환 전)
    ("megabird RDS", "primary RDS"),
    ("megabird DB", "primary DB"),
    ('"megabird"', '"example-corp"'),
    ("`megabird`", "`example-corp`"),
]

# Word boundary 치환 (짧은 토큰, 부분 매칭 방지용).
# megabird, BMS, MEGABIRD, 쿠팡 테넌트 등.
REGEX_REPLACEMENTS: list[tuple[str, str]] = [
    # 쿠팡 테넌트 (긴 것 먼저)
    (r"\bcoupangeats\b", "tenant-f"),
    (r"\bcoupangflex\b", "tenant-g"),
    (r"\bcmgmarketing\b", "tenant-e"),
    (r"\bddnayo\b", "tenant-h"),
    (r"\bcoupang\b", "tenant-a"),
    (r"\bces\b", "tenant-b"),
    (r"\bcfs\b", "tenant-c"),
    (r"\bcls\b", "tenant-d"),

    # BMS standalone (클래스 접두 Bms 는 위에서 처리됨)
    (r"\bBMS\b", "EXT"),
    (r"\bBms\b", "Ext"),

    # MEGABIRD 상수 (위에서 TenantCode.MEGABIRD·MEGABIRD.code()는 처리됨)
    (r"\bMEGABIRD\b", "PRIMARY"),

    # megabird standalone (경로·레포명은 위에서 처리됨)
    (r"\bmegabird\b", "example-corp"),

    # 한국어 (긴 구절 먼저 — 중복 치환 방지)
    (r"메가버드", "본사"),
    (r"쿠팡 테넌트", "외부 테넌트"),
    (r"쿠팡 RDS", "외부 RDS"),
    (r"쿠팡 DB", "외부 DB"),
    (r"쿠팡", "외부"),
]


def anonymize(text: str) -> tuple[str, dict[str, int]]:
    """텍스트 익명화 + 치환 카운트 반환."""
    counts: dict[str, int] = {}

    for old, new in LITERAL_REPLACEMENTS:
        if old in text:
            count = text.count(old)
            counts[f"literal:{old}"] = count
            text = text.replace(old, new)

    for pattern, replacement in REGEX_REPLACEMENTS:
        matches = re.findall(pattern, text)
        if matches:
            counts[f"regex:{pattern}"] = len(matches)
            text = re.sub(pattern, replacement, text)

    return text, counts


def main() -> int:
    if not SOURCE_DIR.exists():
        print(f"ERROR: 원본 디렉토리 없음: {SOURCE_DIR}", file=sys.stderr)
        return 1

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    total_counts: dict[str, int] = {}
    report_lines: list[str] = ["# Anonymization 실행 리포트\n"]
    report_lines.append(f"- Source: `{SOURCE_DIR}`")
    report_lines.append(f"- Target: `{TARGET_DIR}`")
    report_lines.append(f"- Files: {len(FILES)}\n")

    for filename in FILES:
        src = SOURCE_DIR / filename
        dst = TARGET_DIR / filename
        if not src.exists():
            print(f"SKIP {filename} (원본 부재)", file=sys.stderr)
            continue

        content = src.read_text(encoding="utf-8")
        anonymized, counts = anonymize(content)
        dst.write_text(anonymized, encoding="utf-8")

        print(f"OK {filename} — {sum(counts.values())} substitutions")
        for key, n in counts.items():
            total_counts[key] = total_counts.get(key, 0) + n

    report_lines.append("## 전체 치환 카운트\n")
    for key in sorted(total_counts.keys()):
        report_lines.append(f"- `{key}`: {total_counts[key]}")

    print("\n=== 총계 ===")
    print(f"총 {sum(total_counts.values())} 치환, 치환 종류 {len(total_counts)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
