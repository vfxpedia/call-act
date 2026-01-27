"""
상담사 통계 업데이트 스크립트

기능:
- 상담사별 배정된 상담 건수 집계
- 상담사별 FCR 비율 계산
- 상담사별 카테고리 전문성 통계
- employees 테이블 통계 필드 업데이트

실행 순서:
1. 09_assign_consultations_to_agents.py (상담사 배정)
2. 08c_calculate_fcr.py (FCR 계산)
3. 09a_update_agent_statistics.py (본 스크립트)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as psycopg2_connection
from psycopg2.extras import execute_batch
from tqdm import tqdm
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
BATCH_SIZE = int(os.getenv("DB_LOAD_BATCH_SIZE", "100"))

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


def get_agent_consultation_stats(conn: psycopg2_connection) -> Dict[str, Dict]:
    """상담사별 상담 통계 조회"""
    cursor = conn.cursor()

    print("\n[INFO] Loading agent consultation statistics...")

    try:
        # 상담사별 기본 통계
        cursor.execute("""
            SELECT
                agent_id,
                COUNT(*) as total_consultations,
                SUM(CASE WHEN fcr = TRUE THEN 1 ELSE 0 END) as fcr_success,
                SUM(CASE WHEN fcr = FALSE THEN 1 ELSE 0 END) as fcr_failure,
                COUNT(DISTINCT customer_id) as unique_customers,
                MIN(call_date) as first_consultation,
                MAX(call_date) as last_consultation
            FROM consultations
            WHERE agent_id IS NOT NULL
              AND agent_id LIKE 'EMP-%%'
            GROUP BY agent_id
            ORDER BY agent_id
        """)

        rows = cursor.fetchall()

        agent_stats = {}
        for row in rows:
            agent_id = row[0]
            total = row[1]
            fcr_success = row[2] or 0
            fcr_failure = row[3] or 0
            unique_customers = row[4]
            first_date = row[5]
            last_date = row[6]

            fcr_rate = (fcr_success / total * 100) if total > 0 else 0

            agent_stats[agent_id] = {
                'total_consultations': total,
                'fcr_success': fcr_success,
                'fcr_failure': fcr_failure,
                'fcr_rate': fcr_rate,
                'unique_customers': unique_customers,
                'first_consultation': first_date,
                'last_consultation': last_date,
            }

        print(f"[INFO] Loaded statistics for {len(agent_stats)} agents")
        return agent_stats

    finally:
        cursor.close()


def get_agent_category_stats(conn: psycopg2_connection) -> Dict[str, Dict[str, int]]:
    """상담사별 카테고리별 상담 건수"""
    cursor = conn.cursor()

    print("\n[INFO] Loading agent category statistics...")

    try:
        cursor.execute("""
            SELECT
                agent_id,
                category,
                COUNT(*) as count
            FROM consultations
            WHERE agent_id IS NOT NULL
              AND agent_id LIKE 'EMP-%%'
              AND category IS NOT NULL
            GROUP BY agent_id, category
            ORDER BY agent_id, count DESC
        """)

        rows = cursor.fetchall()

        agent_categories = defaultdict(lambda: defaultdict(int))
        for row in rows:
            agent_id = row[0]
            category = row[1]
            count = row[2]
            agent_categories[agent_id][category] = count

        print(f"[INFO] Loaded category stats for {len(agent_categories)} agents")
        return dict(agent_categories)

    finally:
        cursor.close()


def calculate_distribution_stats(agent_stats: Dict[str, Dict]) -> Dict:
    """배정 분포 통계 계산"""
    # 상담사만 필터링 (IT/관리/교육팀 제외)
    counselor_counts = [
        data['total_consultations']
        for agent_id, data in agent_stats.items()
        if agent_id not in EXCLUDED_AGENT_IDS
    ]

    if not counselor_counts:
        return {}

    return {
        'total_agents': len(counselor_counts),
        'total_consultations': sum(counselor_counts),
        'min': min(counselor_counts),
        'max': max(counselor_counts),
        'avg': statistics.mean(counselor_counts),
        'median': statistics.median(counselor_counts),
        'stdev': statistics.stdev(counselor_counts) if len(counselor_counts) > 1 else 0,
        'range': max(counselor_counts) - min(counselor_counts),
    }


def print_agent_summary(agent_stats: Dict[str, Dict], category_stats: Dict[str, Dict]) -> None:
    """상담사 통계 요약 출력"""
    print("\n" + "=" * 70)
    print("AGENT STATISTICS SUMMARY")
    print("=" * 70)

    # 배정 분포 통계
    dist_stats = calculate_distribution_stats(agent_stats)
    print(f"\n[Distribution Statistics]")
    print(f"  Total Agents: {dist_stats.get('total_agents', 0)}")
    print(f"  Total Consultations: {dist_stats.get('total_consultations', 0)}")
    print(f"  Min: {dist_stats.get('min', 0)}")
    print(f"  Max: {dist_stats.get('max', 0)}")
    print(f"  Average: {dist_stats.get('avg', 0):.1f}")
    print(f"  Median: {dist_stats.get('median', 0):.1f}")
    print(f"  Std Dev: {dist_stats.get('stdev', 0):.2f}")
    print(f"  Range: {dist_stats.get('range', 0)}")

    # 목표 달성 여부
    stdev = dist_stats.get('stdev', 0)
    range_val = dist_stats.get('range', 0)
    print(f"\n[Target Achievement]")
    print(f"  Std Dev Target: <= 15 {'✓' if stdev <= 15 else '✗'} (current: {stdev:.2f})")
    print(f"  Range Target: <= 40 {'✓' if range_val <= 40 else '✗'} (current: {range_val})")

    # 상위/하위 상담사
    counselor_stats = [
        (agent_id, data)
        for agent_id, data in agent_stats.items()
        if agent_id not in EXCLUDED_AGENT_IDS
    ]

    sorted_by_count = sorted(counselor_stats, key=lambda x: x[1]['total_consultations'], reverse=True)

    print(f"\n[Top 5 Agents by Consultation Count]")
    for agent_id, data in sorted_by_count[:5]:
        print(f"  {agent_id}: {data['total_consultations']} consultations, FCR {data['fcr_rate']:.1f}%")

    print(f"\n[Bottom 5 Agents by Consultation Count]")
    for agent_id, data in sorted_by_count[-5:]:
        print(f"  {agent_id}: {data['total_consultations']} consultations, FCR {data['fcr_rate']:.1f}%")

    # FCR 기준 상위/하위
    sorted_by_fcr = sorted(counselor_stats, key=lambda x: x[1]['fcr_rate'], reverse=True)

    print(f"\n[Top 5 Agents by FCR Rate]")
    for agent_id, data in sorted_by_fcr[:5]:
        print(f"  {agent_id}: FCR {data['fcr_rate']:.1f}% ({data['fcr_success']}/{data['total_consultations']})")

    print(f"\n[Bottom 5 Agents by FCR Rate]")
    for agent_id, data in sorted_by_fcr[-5:]:
        print(f"  {agent_id}: FCR {data['fcr_rate']:.1f}% ({data['fcr_success']}/{data['total_consultations']})")


def update_employee_statistics(
    conn: psycopg2_connection,
    agent_stats: Dict[str, Dict],
    category_stats: Dict[str, Dict]
) -> int:
    """employees 테이블의 통계 필드 업데이트 (필드가 존재하는 경우)"""
    cursor = conn.cursor()

    print("\n[INFO] Checking if employees table has statistics columns...")

    try:
        # 컬럼 존재 여부 확인
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'employees'
              AND column_name IN ('total_consultations', 'fcr_rate', 'primary_category')
        """)

        existing_columns = {row[0] for row in cursor.fetchall()}

        if not existing_columns:
            print("[INFO] No statistics columns in employees table, skipping update")
            return 0

        print(f"[INFO] Found statistics columns: {existing_columns}")

        # 업데이트 쿼리 동적 생성
        update_parts = []
        if 'total_consultations' in existing_columns:
            update_parts.append("total_consultations = %s")
        if 'fcr_rate' in existing_columns:
            update_parts.append("fcr_rate = %s")
        if 'primary_category' in existing_columns:
            update_parts.append("primary_category = %s")

        if not update_parts:
            return 0

        update_query = f"""
            UPDATE employees
            SET {', '.join(update_parts)}, updated_at = NOW()
            WHERE id = %s
        """

        # 업데이트 데이터 준비
        updates = []
        for agent_id, data in agent_stats.items():
            # 주요 카테고리 결정
            categories = category_stats.get(agent_id, {})
            primary_category = max(categories, key=categories.get) if categories else None

            values = []
            if 'total_consultations' in existing_columns:
                values.append(data['total_consultations'])
            if 'fcr_rate' in existing_columns:
                values.append(data['fcr_rate'])
            if 'primary_category' in existing_columns:
                values.append(primary_category)
            values.append(agent_id)

            updates.append(tuple(values))

        # 배치 업데이트
        pbar = tqdm(total=len(updates), desc="Updating employees")

        for i in range(0, len(updates), BATCH_SIZE):
            batch = updates[i:i+BATCH_SIZE]
            execute_batch(cursor, update_query, batch, page_size=len(batch))
            conn.commit()
            pbar.update(len(batch))

        pbar.close()
        print(f"[INFO] Updated statistics for {len(updates)} employees")
        return len(updates)

    except Exception as e:
        print(f"[WARN] Could not update employee statistics: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()


def export_statistics_report(
    agent_stats: Dict[str, Dict],
    category_stats: Dict[str, Dict],
    output_path: Path
) -> None:
    """통계 보고서 CSV 내보내기"""
    import csv

    print(f"\n[INFO] Exporting statistics report to {output_path}...")

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # 헤더
        writer.writerow([
            'Agent ID', 'Total Consultations', 'FCR Success', 'FCR Rate (%)',
            'Unique Customers', 'Primary Category', 'First Consultation', 'Last Consultation'
        ])

        # 데이터
        for agent_id in sorted(agent_stats.keys()):
            data = agent_stats[agent_id]
            categories = category_stats.get(agent_id, {})
            primary_category = max(categories, key=categories.get) if categories else 'N/A'

            writer.writerow([
                agent_id,
                data['total_consultations'],
                data['fcr_success'],
                f"{data['fcr_rate']:.1f}",
                data['unique_customers'],
                primary_category,
                data['first_consultation'],
                data['last_consultation']
            ])

    print(f"[INFO] Report exported successfully")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Update agent statistics")
    parser.add_argument("--dry-run", action="store_true", help="Preview without updating DB")
    parser.add_argument("--export", type=str, help="Export statistics to CSV file")

    args = parser.parse_args()

    # 데이터베이스 연결
    conn = connect_db()

    try:
        # 통계 수집
        agent_stats = get_agent_consultation_stats(conn)
        category_stats = get_agent_category_stats(conn)

        # 요약 출력
        print_agent_summary(agent_stats, category_stats)

        if args.dry_run:
            print("\n[DRY RUN] No database changes made")
        else:
            # DB 업데이트 (필드가 있는 경우)
            update_employee_statistics(conn, agent_stats, category_stats)

        # CSV 내보내기
        if args.export:
            export_path = Path(args.export)
            export_statistics_report(agent_stats, category_stats, export_path)

    finally:
        conn.close()
        print("\n[INFO] Database connection closed")


if __name__ == "__main__":
    main()
