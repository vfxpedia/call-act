"""
전체 배정 검증 스크립트

기능:
- 상담사 배정 균등성 검증 (std dev, range)
- FCR 80% 목표 달성 검증
- 카드 타입 실제 상품명 검증
- 고객-상담 연결 무결성 검증
- 전체 데이터 정합성 확인

실행 순서:
1. 09_assign_consultations_to_agents.py (상담사 배정)
2. 08c_calculate_fcr.py (FCR 계산)
3. 09a_update_agent_statistics.py (상담사 통계)
4. 09b_verify_all_assignments.py (본 스크립트)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as psycopg2_connection
import statistics

# 환경 변수 로드
load_dotenv(Path(__file__).parent / '.env', override=False)
load_dotenv(Path(__file__).parent.parent.parent / '.env', override=False)

# 환경 변수
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "callact_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "callact_pwd1")
DB_NAME = os.getenv("DB_NAME", "callact_db")

# 검증 기준
TARGETS = {
    'std_dev': 15,          # 상담사 배정 표준편차 목표
    'range': 40,            # 상담사 배정 범위 목표
    'fcr_rate': 80.0,       # FCR 목표율 (%)
    'fcr_tolerance': 3.0,   # FCR 허용 오차 (%)
    'total_customers': 2500,
    'total_consultations': 6533,
    'total_counselors': 60,
}

# 제외할 상담사 (IT팀, 관리팀, 교육팀)
EXCLUDED_AGENT_IDS = [
    "EMP-061", "EMP-062", "EMP-063", "EMP-064", "EMP-065",  # IT팀
    "EMP-066", "EMP-067", "EMP-068",  # 관리팀
    "EMP-069", "EMP-070",  # 교육팀
]


def connect_db() -> psycopg2_connection:
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print(f"[INFO] Connected to database: {DB_NAME}")
        return conn
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        sys.exit(1)


class VerificationResult:
    """검증 결과 클래스"""

    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.checks = []
        self.warnings = []
        self.errors = []

    def add_check(self, description: str, passed: bool, actual: str, expected: str = None):
        status = "✓" if passed else "✗"
        self.checks.append({
            'description': description,
            'passed': passed,
            'actual': actual,
            'expected': expected,
            'status': status
        })
        if not passed:
            self.passed = False

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_error(self, message: str):
        self.errors.append(message)
        self.passed = False

    def print_results(self):
        status = "PASSED" if self.passed else "FAILED"
        print(f"\n{'=' * 60}")
        print(f"[{self.name}] {status}")
        print("=" * 60)

        for check in self.checks:
            print(f"  {check['status']} {check['description']}")
            print(f"      Actual: {check['actual']}")
            if check['expected']:
                print(f"      Expected: {check['expected']}")

        if self.warnings:
            print(f"\n  Warnings:")
            for w in self.warnings:
                print(f"    ⚠ {w}")

        if self.errors:
            print(f"\n  Errors:")
            for e in self.errors:
                print(f"    ✗ {e}")


def verify_agent_distribution(conn: psycopg2_connection) -> VerificationResult:
    """상담사 배정 균등성 검증"""
    result = VerificationResult("Agent Distribution")
    cursor = conn.cursor()

    try:
        # 상담사별 배정 건수
        cursor.execute("""
            SELECT agent_id, COUNT(*) as count
            FROM consultations
            WHERE agent_id IS NOT NULL
              AND agent_id LIKE 'EMP-%%'
            GROUP BY agent_id
            ORDER BY agent_id
        """)

        rows = cursor.fetchall()

        # 상담사만 필터링
        counselor_counts = [
            count for agent_id, count in rows
            if agent_id not in EXCLUDED_AGENT_IDS
        ]

        if not counselor_counts:
            result.add_error("No counselor assignments found")
            return result

        # 통계 계산
        total = sum(counselor_counts)
        num_agents = len(counselor_counts)
        min_count = min(counselor_counts)
        max_count = max(counselor_counts)
        avg_count = statistics.mean(counselor_counts)
        std_dev = statistics.stdev(counselor_counts) if len(counselor_counts) > 1 else 0
        range_val = max_count - min_count

        # 검증
        result.add_check(
            "Number of counselors",
            num_agents == TARGETS['total_counselors'],
            f"{num_agents}",
            f"{TARGETS['total_counselors']}"
        )

        result.add_check(
            "Total assigned consultations",
            total >= TARGETS['total_consultations'] * 0.99,  # 99% 이상
            f"{total}",
            f">= {int(TARGETS['total_consultations'] * 0.99)}"
        )

        result.add_check(
            "Standard deviation",
            std_dev <= TARGETS['std_dev'],
            f"{std_dev:.2f}",
            f"<= {TARGETS['std_dev']}"
        )

        result.add_check(
            "Range (max - min)",
            range_val <= TARGETS['range'],
            f"{range_val}",
            f"<= {TARGETS['range']}"
        )

        result.add_check(
            "Average per agent",
            True,  # 정보 표시용
            f"{avg_count:.1f}",
            f"~{TARGETS['total_consultations'] / TARGETS['total_counselors']:.1f}"
        )

        # 상위/하위 에이전트 경고
        sorted_counts = sorted(
            [(agent_id, count) for agent_id, count in rows if agent_id not in EXCLUDED_AGENT_IDS],
            key=lambda x: x[1],
            reverse=True
        )

        if sorted_counts:
            top_agent, top_count = sorted_counts[0]
            bottom_agent, bottom_count = sorted_counts[-1]
            result.add_warning(f"Highest: {top_agent} with {top_count} consultations")
            result.add_warning(f"Lowest: {bottom_agent} with {bottom_count} consultations")

    except Exception as e:
        result.add_error(f"Query failed: {e}")
    finally:
        cursor.close()

    return result


def verify_fcr_rate(conn: psycopg2_connection) -> VerificationResult:
    """FCR 비율 검증"""
    result = VerificationResult("FCR Rate")
    cursor = conn.cursor()

    try:
        # 전체 FCR 비율
        cursor.execute("""
            SELECT
                SUM(resolved_first_call) as fcr_success,
                SUM(total_consultations) as total,
                ROUND(
                    SUM(resolved_first_call)::numeric /
                    NULLIF(SUM(total_consultations), 0) * 100, 1
                ) as fcr_rate
            FROM customers
            WHERE total_consultations > 0
        """)

        row = cursor.fetchone()
        fcr_success = row[0] or 0
        total = row[1] or 0
        fcr_rate = float(row[2] or 0)

        # 검증
        target_low = TARGETS['fcr_rate'] - TARGETS['fcr_tolerance']
        target_high = TARGETS['fcr_rate'] + TARGETS['fcr_tolerance']

        result.add_check(
            "Overall FCR rate",
            target_low <= fcr_rate <= target_high,
            f"{fcr_rate}%",
            f"{target_low}% - {target_high}%"
        )

        result.add_check(
            "FCR success count",
            True,
            f"{fcr_success}",
            None
        )

        result.add_check(
            "Total consultations",
            True,
            f"{total}",
            None
        )

        # 등급별 FCR
        cursor.execute("""
            SELECT
                grade,
                ROUND(
                    SUM(resolved_first_call)::numeric /
                    NULLIF(SUM(total_consultations), 0) * 100, 1
                ) as fcr_rate
            FROM customers
            WHERE total_consultations > 0
            GROUP BY grade
            ORDER BY
                CASE grade
                    WHEN 'VIP' THEN 1
                    WHEN 'GOLD' THEN 2
                    WHEN 'SILVER' THEN 3
                    ELSE 4
                END
        """)

        for grade_row in cursor.fetchall():
            grade = grade_row[0]
            grade_fcr = float(grade_row[1] or 0)
            result.add_warning(f"{grade} FCR: {grade_fcr}%")

    except Exception as e:
        result.add_error(f"Query failed: {e}")
    finally:
        cursor.close()

    return result


def verify_card_types(conn: psycopg2_connection) -> VerificationResult:
    """카드 타입 검증"""
    result = VerificationResult("Card Types")
    cursor = conn.cursor()

    try:
        # 카드 타입 분포
        cursor.execute("""
            SELECT card_type, COUNT(*) as count
            FROM customers
            WHERE card_type IS NOT NULL
            GROUP BY card_type
            ORDER BY count DESC
        """)

        rows = cursor.fetchall()

        # 기본 검증
        unique_card_types = len(rows)
        total_with_card = sum(count for _, count in rows)

        result.add_check(
            "Unique card types",
            unique_card_types >= 50,  # 최소 50개 이상 다양한 카드
            f"{unique_card_types}",
            ">= 50"
        )

        result.add_check(
            "Customers with card type",
            total_with_card >= TARGETS['total_customers'] * 0.95,
            f"{total_with_card}",
            f">= {int(TARGETS['total_customers'] * 0.95)}"
        )

        # 가짜 카드 타입 확인 (테스트용 이름이 아닌 실제 상품명인지)
        fake_types = ['테스트', 'test', '가짜', 'fake', 'dummy']
        has_fake = False
        for card_type, count in rows[:20]:
            for fake in fake_types:
                if fake.lower() in card_type.lower():
                    has_fake = True
                    result.add_warning(f"Possibly fake card type: {card_type}")

        result.add_check(
            "Real card product names",
            not has_fake,
            "No fake types detected" if not has_fake else "Some fake types detected",
            "Real product names only"
        )

        # 상위 10개 카드 타입 표시
        result.add_warning("Top 10 card types:")
        for card_type, count in rows[:10]:
            pct = count / total_with_card * 100 if total_with_card > 0 else 0
            result.add_warning(f"  {card_type}: {count} ({pct:.1f}%)")

    except Exception as e:
        result.add_error(f"Query failed: {e}")
    finally:
        cursor.close()

    return result


def verify_customer_consultation_linkage(conn: psycopg2_connection) -> VerificationResult:
    """고객-상담 연결 무결성 검증"""
    result = VerificationResult("Customer-Consultation Linkage")
    cursor = conn.cursor()

    try:
        # 고객 수 확인
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]

        result.add_check(
            "Total customers",
            customer_count == TARGETS['total_customers'],
            f"{customer_count}",
            f"{TARGETS['total_customers']}"
        )

        # 상담 수 확인
        cursor.execute("SELECT COUNT(*) FROM consultations")
        consultation_count = cursor.fetchone()[0]

        result.add_check(
            "Total consultations",
            consultation_count == TARGETS['total_consultations'],
            f"{consultation_count}",
            f"{TARGETS['total_consultations']}"
        )

        # 고아 상담 확인 (customer_id가 없는 상담)
        cursor.execute("""
            SELECT COUNT(*)
            FROM consultations c
            LEFT JOIN customers cu ON c.customer_id = cu.id
            WHERE c.customer_id IS NOT NULL
              AND cu.id IS NULL
        """)
        orphan_consultations = cursor.fetchone()[0]

        result.add_check(
            "Orphan consultations (no matching customer)",
            orphan_consultations == 0,
            f"{orphan_consultations}",
            "0"
        )

        # 상담이 없는 고객 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM customers cu
            LEFT JOIN consultations c ON cu.id = c.customer_id
            WHERE c.id IS NULL
        """)
        customers_without_consultations = cursor.fetchone()[0]

        result.add_check(
            "Customers without consultations",
            customers_without_consultations == 0 or customers_without_consultations <= TARGETS['total_customers'] * 0.05,
            f"{customers_without_consultations}",
            f"<= {int(TARGETS['total_customers'] * 0.05)}"
        )

        # 상담 횟수 일치 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM customers cu
            WHERE cu.total_consultations != (
                SELECT COUNT(*)
                FROM consultations c
                WHERE c.customer_id = cu.id
            )
        """)
        mismatched_counts = cursor.fetchone()[0]

        result.add_check(
            "Customer consultation count mismatch",
            mismatched_counts == 0,
            f"{mismatched_counts}",
            "0"
        )

    except Exception as e:
        result.add_error(f"Query failed: {e}")
    finally:
        cursor.close()

    return result


def verify_data_integrity(conn: psycopg2_connection) -> VerificationResult:
    """전체 데이터 무결성 검증"""
    result = VerificationResult("Data Integrity")
    cursor = conn.cursor()

    try:
        # 상담사 배정 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM consultations
            WHERE agent_id IS NULL OR agent_id = ''
        """)
        unassigned = cursor.fetchone()[0]

        result.add_check(
            "Consultations without agent",
            unassigned == 0,
            f"{unassigned}",
            "0"
        )

        # FCR 필드 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM consultations
            WHERE fcr IS NULL
              AND call_date IS NOT NULL
        """)
        null_fcr = cursor.fetchone()[0]

        result.add_check(
            "Consultations without FCR flag",
            null_fcr == 0,
            f"{null_fcr}",
            "0"
        )

        # 카테고리 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM consultations
            WHERE category IS NULL OR category = ''
        """)
        no_category = cursor.fetchone()[0]

        result.add_check(
            "Consultations without category",
            no_category <= TARGETS['total_consultations'] * 0.01,  # 1% 이하 허용
            f"{no_category}",
            f"<= {int(TARGETS['total_consultations'] * 0.01)}"
        )

        # 날짜 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM consultations
            WHERE call_date IS NULL
        """)
        no_date = cursor.fetchone()[0]

        result.add_check(
            "Consultations without date",
            no_date <= TARGETS['total_consultations'] * 0.01,
            f"{no_date}",
            f"<= {int(TARGETS['total_consultations'] * 0.01)}"
        )

        # 고객 필수 필드 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM customers
            WHERE name IS NULL OR phone IS NULL OR grade IS NULL
        """)
        incomplete_customers = cursor.fetchone()[0]

        result.add_check(
            "Customers with missing required fields",
            incomplete_customers == 0,
            f"{incomplete_customers}",
            "0"
        )

        # 페르소나 태그 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM customers
            WHERE personality_tags IS NULL
               OR array_length(personality_tags, 1) IS NULL
               OR array_length(personality_tags, 1) = 0
        """)
        no_persona = cursor.fetchone()[0]

        result.add_check(
            "Customers without personality tags",
            no_persona <= TARGETS['total_customers'] * 0.05,
            f"{no_persona}",
            f"<= {int(TARGETS['total_customers'] * 0.05)}"
        )

    except Exception as e:
        result.add_error(f"Query failed: {e}")
    finally:
        cursor.close()

    return result


def print_summary(results: List[VerificationResult]) -> bool:
    """전체 검증 결과 요약"""
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    all_passed = True
    for result in results:
        status = "✓ PASSED" if result.passed else "✗ FAILED"
        print(f"  {status}: {result.name}")
        if not result.passed:
            all_passed = False

    print("\n" + "-" * 70)
    if all_passed:
        print("OVERALL: ✓ ALL VERIFICATIONS PASSED")
    else:
        print("OVERALL: ✗ SOME VERIFICATIONS FAILED")
    print("-" * 70)

    return all_passed


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Verify all assignments")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--quick", action="store_true", help="Run quick verification only")

    args = parser.parse_args()

    # 데이터베이스 연결
    conn = connect_db()

    try:
        results = []

        # 검증 실행
        print("\n[INFO] Starting verification...")

        # 1. 상담사 배정 균등성
        result = verify_agent_distribution(conn)
        result.print_results()
        results.append(result)

        # 2. FCR 비율
        result = verify_fcr_rate(conn)
        result.print_results()
        results.append(result)

        if not args.quick:
            # 3. 카드 타입
            result = verify_card_types(conn)
            result.print_results()
            results.append(result)

            # 4. 고객-상담 연결
            result = verify_customer_consultation_linkage(conn)
            result.print_results()
            results.append(result)

            # 5. 데이터 무결성
            result = verify_data_integrity(conn)
            result.print_results()
            results.append(result)

        # 요약
        all_passed = print_summary(results)

        # 종료 코드
        sys.exit(0 if all_passed else 1)

    finally:
        conn.close()
        print("\n[INFO] Database connection closed")


if __name__ == "__main__":
    main()
