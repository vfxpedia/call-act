"""
상담 고객 재배정 스크립트

기능:
- hana_rdb_metadata.json의 client_id를 customers 테이블의 customer_id로 재배정
- 상담 횟수별 분포 적용 (1회 35%, 3회 45%, 5회 17%, 10회+ 3%)
- 동일 성별/연령대 고객에게 배정 (가능한 경우)
- consultations.customer_id UPDATE
- customers.total_consultations, last_consultation_date UPDATE
"""

import json
import os
import sys
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as psycopg2_connection
from psycopg2.extras import execute_batch
from tqdm import tqdm

# 환경 변수 로드
load_dotenv(Path(__file__).parent / '.env', override=False)
load_dotenv(Path(__file__).parent.parent.parent / '.env', override=False)

# config.py에서 경로 가져오기
from config import HANA_RDB_METADATA_FILE

# 재현성을 위한 랜덤 시드 고정
# 모든 팀원이 동일한 데이터를 생성하도록 보장
random.seed(42)

# 환경 변수
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "callact_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "callact_pwd1")
DB_NAME = os.getenv("DB_NAME", "callact_db")
BATCH_SIZE = int(os.getenv("DB_LOAD_BATCH_SIZE", "100"))

# 상담 횟수별 고객 분포 (업계 표준 기반)
# 2,500명 기준
CONSULTATION_TIERS = {
    'one_time': {'ratio': 0.35, 'min_calls': 1, 'max_calls': 1},      # 1회: 35% = 875명
    'regular': {'ratio': 0.45, 'min_calls': 2, 'max_calls': 4},       # 2-4회: 45% = 1,125명
    'frequent': {'ratio': 0.17, 'min_calls': 5, 'max_calls': 9},      # 5-9회: 17% = 425명
    'high_touch': {'ratio': 0.03, 'min_calls': 10, 'max_calls': 20},  # 10회+: 3% = 75명
}


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
        print(f"[DB 연결 성공] {DB_NAME}@{DB_HOST}:{DB_PORT}")
        return conn
    except psycopg2.OperationalError as e:
        print(f"\n[오류] 데이터베이스 연결 실패!")
        print(f"  호스트: {DB_HOST}:{DB_PORT}")
        print(f"  데이터베이스: {DB_NAME}")
        print(f"  사용자: {DB_USER}")
        print(f"\n[디버깅 정보]")
        print(f"  {e}")
        print(f"\n[해결방법]")
        print(f"  1. PostgreSQL 서버가 실행 중인지 확인하세요")
        print(f"  2. .env 파일의 DB 설정을 확인하세요")
        print(f"  3. 네트워크 연결을 확인하세요")
        sys.exit(1)
    except Exception as e:
        print(f"[오류] 예상치 못한 오류: {e}")
        sys.exit(1)


def load_original_metadata() -> List[Dict]:
    """원본 hana_rdb_metadata.json 로드"""
    print(f"\n[원본 메타데이터 로드]")
    print(f"  경로: {HANA_RDB_METADATA_FILE}")

    if not HANA_RDB_METADATA_FILE.exists():
        print(f"\n[오류] 파일을 찾을 수 없습니다!")
        print(f"  경로: {HANA_RDB_METADATA_FILE}")
        print(f"\n[해결방법]")
        print(f"  1. data-preprocessing 서브모듈을 업데이트하세요:")
        print(f"     git submodule update --init --recursive")
        print(f"  2. hana_rdb_metadata.json 파일이 존재하는지 확인하세요")
        return []

    with open(HANA_RDB_METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"  [로드 완료] {len(data):,}건의 상담 데이터")
    return data


def get_customers_by_demographics(conn: psycopg2_connection) -> Dict:
    """성별/연령대별 고객 목록 가져오기"""
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, gender, age_group, grade
            FROM customers
            ORDER BY id
        """)
        rows = cursor.fetchall()

        # 성별/연령대별로 그룹화
        customers_by_demo = defaultdict(list)
        all_customers = []

        for row in rows:
            customer_id, gender, age_group, grade = row
            customer = {
                'id': customer_id,
                'gender': gender,
                'age_group': age_group,
                'grade': grade
            }
            all_customers.append(customer)

            # 성별+연령대 키로 그룹화
            key = (gender, age_group)
            customers_by_demo[key].append(customer)

        print(f"  [로드 완료] {len(all_customers):,}명의 고객 데이터")
        return {
            'all': all_customers,
            'by_demo': dict(customers_by_demo)
        }

    finally:
        cursor.close()


def analyze_original_consultations(metadata: List[Dict]) -> Dict:
    """원본 상담 데이터 분석 (성별/연령대 분포)"""
    client_info = {}

    for row in metadata:
        client_id = row.get('client_id', '')
        gender = row.get('client_sex', 'unknown')
        age_group = row.get('client_age', '')

        # 성별 변환
        if gender == '여':
            gender = 'female'
        elif gender == '남':
            gender = 'male'
        else:
            gender = 'unknown'

        if client_id not in client_info:
            client_info[client_id] = {
                'client_id': client_id,
                'gender': gender,
                'age_group': age_group,
                'consultations': []
            }

        client_info[client_id]['consultations'].append(row)

    print(f"\n[원본 데이터 분석 결과]")
    print(f"  고유 고객 수: {len(client_info):,}명")
    print(f"  총 상담 건수: {len(metadata):,}건")

    return client_info


def create_consultation_assignment_plan(
    total_consultations: int,
    total_customers: int
) -> Dict[str, int]:
    """상담 배정 계획 생성"""
    print(f"\n[배정 계획 생성]")
    print(f"  총 상담 건수: {total_consultations:,}건")
    print(f"  총 고객 수: {total_customers:,}명")

    # 각 티어별 고객 수 계산
    tier_customers = {}
    assigned_customers = 0

    for tier_name, tier_config in CONSULTATION_TIERS.items():
        count = int(total_customers * tier_config['ratio'])
        tier_customers[tier_name] = count
        assigned_customers += count

    # 남은 고객은 regular에 추가
    remaining = total_customers - assigned_customers
    tier_customers['regular'] += remaining

    # 각 티어의 예상 상담 건수 계산
    expected_consultations = 0
    for tier_name, customer_count in tier_customers.items():
        tier_config = CONSULTATION_TIERS[tier_name]
        avg_calls = (tier_config['min_calls'] + tier_config['max_calls']) / 2
        expected_consultations += int(customer_count * avg_calls)

    tier_names_kr = {
        'one_time': '1회 상담',
        'regular': '2-4회 상담',
        'frequent': '5-9회 상담',
        'high_touch': '10회+ 상담'
    }

    print(f"\n[티어별 배정 계획]")
    for tier_name, count in tier_customers.items():
        tier_config = CONSULTATION_TIERS[tier_name]
        tier_kr = tier_names_kr.get(tier_name, tier_name)
        print(f"  {tier_kr}: {count:,}명 (고객당 {tier_config['min_calls']}-{tier_config['max_calls']}회)")

    print(f"\n  예상 총 상담 건수: {expected_consultations:,}건")
    print(f"  실제 배정할 건수: {total_consultations:,}건")

    return tier_customers


def assign_consultations_to_customers(
    metadata: List[Dict],
    customer_data: Dict,
    tier_customers: Dict[str, int]
) -> Dict[str, str]:
    """상담을 고객에게 배정"""
    print(f"\n[상담-고객 매핑 수행]")

    all_customers = customer_data['all'].copy()
    customers_by_demo = customer_data['by_demo']

    # 원본 client_id 정보 분석
    client_info = analyze_original_consultations(metadata)

    # 고객을 티어별로 분배
    random.shuffle(all_customers)

    customer_tiers = {}
    idx = 0

    for tier_name, count in tier_customers.items():
        tier_config = CONSULTATION_TIERS[tier_name]
        for _ in range(count):
            if idx < len(all_customers):
                customer = all_customers[idx]
                # 각 고객에게 할당할 상담 건수 결정
                num_calls = random.randint(
                    tier_config['min_calls'],
                    tier_config['max_calls']
                )
                customer_tiers[customer['id']] = {
                    'tier': tier_name,
                    'target_calls': num_calls,
                    'assigned_calls': 0,
                    'customer': customer
                }
                idx += 1

    # client_id → customer_id 매핑 생성
    client_to_customer_map = {}

    # 상담을 순회하면서 고객에게 배정
    # 우선 성별/연령대가 일치하는 고객에게 배정 시도
    unassigned_consultations = []

    for consultation in metadata:
        client_id = consultation.get('client_id', '')

        # 이미 매핑된 client_id인 경우
        if client_id in client_to_customer_map:
            continue

        # 성별/연령대 추출
        gender = consultation.get('client_sex', '')
        age_group = consultation.get('client_age', '')

        if gender == '여':
            gender = 'female'
        elif gender == '남':
            gender = 'male'
        else:
            gender = 'unknown'

        # 일치하는 고객 찾기
        demo_key = (gender, age_group)
        matched_customers = customers_by_demo.get(demo_key, [])

        assigned = False
        for customer in matched_customers:
            cust_id = customer['id']
            if cust_id in customer_tiers:
                tier_info = customer_tiers[cust_id]
                if tier_info['assigned_calls'] < tier_info['target_calls']:
                    client_to_customer_map[client_id] = cust_id
                    tier_info['assigned_calls'] += 1
                    assigned = True
                    break

        if not assigned:
            unassigned_consultations.append(consultation)

    # 매칭되지 않은 상담은 빈 슬롯이 있는 고객에게 배정
    for consultation in unassigned_consultations:
        client_id = consultation.get('client_id', '')

        if client_id in client_to_customer_map:
            continue

        # 빈 슬롯이 있는 고객 찾기
        for cust_id, tier_info in customer_tiers.items():
            if tier_info['assigned_calls'] < tier_info['target_calls']:
                client_to_customer_map[client_id] = cust_id
                tier_info['assigned_calls'] += 1
                break

    # 아직 매핑되지 않은 client_id가 있으면 랜덤 배정
    remaining_clients = set()
    for consultation in metadata:
        client_id = consultation.get('client_id', '')
        if client_id and client_id not in client_to_customer_map:
            remaining_clients.add(client_id)

    if remaining_clients:
        available_customers = [
            cust_id for cust_id, tier_info in customer_tiers.items()
        ]
        for client_id in remaining_clients:
            # 랜덤하게 고객 선택 (기존 슬롯 초과 허용)
            cust_id = random.choice(available_customers)
            client_to_customer_map[client_id] = cust_id

    print(f"  [매핑 완료] {len(client_to_customer_map):,}개의 고유 client_id → customer_id")

    return client_to_customer_map


def update_consultations(
    conn: psycopg2_connection,
    client_to_customer_map: Dict[str, str],
    metadata: List[Dict]
) -> int:
    """consultations 테이블의 customer_id 업데이트"""
    cursor = conn.cursor()

    print(f"\n[상담 테이블 업데이트]")

    # 업데이트 데이터 준비
    updates = []
    for consultation in metadata:
        old_client_id = consultation.get('client_id', '')
        consultation_id = consultation.get('id', '')

        if old_client_id in client_to_customer_map:
            new_customer_id = client_to_customer_map[old_client_id]
            updates.append((new_customer_id, consultation_id))

    update_query = """
        UPDATE consultations
        SET customer_id = %s, updated_at = NOW()
        WHERE id = %s
    """

    try:
        print(f"  업데이트 대상: {len(updates):,}건")
        pbar = tqdm(total=len(updates), desc="상담 업데이트 중")

        for i in range(0, len(updates), BATCH_SIZE):
            batch = updates[i:i+BATCH_SIZE]
            execute_batch(cursor, update_query, batch, page_size=len(batch))
            conn.commit()
            pbar.update(len(batch))

        pbar.close()
        print(f"  [완료] {len(updates):,}건 업데이트 성공")
        return len(updates)

    except Exception as e:
        print(f"\n[오류] 상담 업데이트 실패!")
        print(f"  에러: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return 0
    finally:
        cursor.close()


def update_customer_statistics(conn: psycopg2_connection) -> int:
    """customers 테이블의 상담 통계 업데이트"""
    cursor = conn.cursor()

    print(f"\n[고객 통계 업데이트]")

    try:
        # total_consultations 및 last_consultation_date 업데이트
        cursor.execute("""
            UPDATE customers c
            SET
                total_consultations = subq.consultation_count,
                last_consultation_date = subq.last_date,
                updated_at = NOW()
            FROM (
                SELECT
                    customer_id,
                    COUNT(*) as consultation_count,
                    MAX(call_date) as last_date
                FROM consultations
                GROUP BY customer_id
            ) subq
            WHERE c.id = subq.customer_id
        """)

        updated = cursor.rowcount
        conn.commit()

        print(f"  [완료] {updated:,}명의 고객 통계 업데이트")
        return updated

    except Exception as e:
        print(f"\n[오류] 고객 통계 업데이트 실패: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()


def verify_reassignment(conn: psycopg2_connection) -> Dict:
    """재배정 결과 검증"""
    cursor = conn.cursor()
    results = {}

    try:
        # 고객별 상담 건수 분포
        cursor.execute("""
            SELECT
                CASE
                    WHEN total_consultations = 1 THEN '1회'
                    WHEN total_consultations BETWEEN 2 AND 4 THEN '2-4회'
                    WHEN total_consultations BETWEEN 5 AND 9 THEN '5-9회'
                    ELSE '10회+'
                END as tier,
                COUNT(*) as customer_count
            FROM customers
            WHERE total_consultations > 0
            GROUP BY tier
            ORDER BY tier
        """)
        results['consultation_distribution'] = cursor.fetchall()

        # 상담이 있는 고객 수
        cursor.execute("""
            SELECT COUNT(*) FROM customers WHERE total_consultations > 0
        """)
        results['customers_with_consultations'] = cursor.fetchone()[0]

        # 전체 상담 건수 확인
        cursor.execute("SELECT COUNT(*) FROM consultations")
        results['total_consultations'] = cursor.fetchone()[0]

        # FK 무결성 확인 (orphaned consultations)
        cursor.execute("""
            SELECT COUNT(*)
            FROM consultations c
            LEFT JOIN customers cu ON c.customer_id = cu.id
            WHERE cu.id IS NULL
        """)
        results['orphaned_consultations'] = cursor.fetchone()[0]

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
    finally:
        cursor.close()

    return results


def main():
    """메인 함수"""
    import argparse

    print("=" * 60)
    print("상담-고객 재배정 스크립트")
    print("=" * 60)
    print(f"  랜덤 시드: 42 (재현성 보장 - 누가 돌려도 동일한 결과)")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="Reassign consultations to customers")
    parser.add_argument("--dry-run", action="store_true", help="미리보기 모드 (DB 변경 없음)")
    parser.add_argument("--verify-only", action="store_true", help="검증만 수행")

    args = parser.parse_args()

    # 데이터베이스 연결
    conn = connect_db()

    try:
        if args.verify_only:
            print("\n[검증 전용 모드]")
            results = verify_reassignment(conn)

            print("\n" + "=" * 60)
            print("검증 결과")
            print("=" * 60)

            print(f"\n상담이 있는 고객 수: {results.get('customers_with_consultations', 0):,}명")
            print(f"총 상담 건수: {results.get('total_consultations', 0):,}건")
            orphaned = results.get('orphaned_consultations', 0)
            if orphaned == 0:
                print(f"고아 상담: 0건 ✓")
            else:
                print(f"[경고] 고아 상담: {orphaned}건")

            print("\n[상담 횟수별 분포]")
            for row in results.get('consultation_distribution', []):
                print(f"  {row[0]}: {row[1]:,}명")

            return

        # 원본 메타데이터 로드
        metadata = load_original_metadata()
        if not metadata:
            return

        # 고객 데이터 가져오기
        customer_data = get_customers_by_demographics(conn)
        if not customer_data['all']:
            print("\n[오류] 데이터베이스에 고객이 없습니다!")
            print("\n[해결방법]")
            print("  1. 먼저 고객 데이터를 생성하세요:")
            print("     python 08_generate_customers_data.py")
            print("  2. 그런 다음 DB에 적재하세요:")
            print("     python 08a_load_customers_to_db.py")
            return

        # 배정 계획 생성
        tier_customers = create_consultation_assignment_plan(
            len(metadata),
            len(customer_data['all'])
        )

        # 상담 배정
        client_to_customer_map = assign_consultations_to_customers(
            metadata,
            customer_data,
            tier_customers
        )

        if args.dry_run:
            print("\n[미리보기 모드] DB 변경 없음")
            print(f"  업데이트 예정: {len(metadata):,}건의 상담")
            return

        # DB 업데이트
        updated_consultations = update_consultations(conn, client_to_customer_map, metadata)

        # 고객 통계 업데이트
        updated_customers = update_customer_statistics(conn)

        # 검증
        print("\n" + "=" * 60)
        print("✓ 재배정 완료")
        print("=" * 60)

        results = verify_reassignment(conn)

        print(f"\n[결과 요약]")
        print(f"  업데이트된 상담: {updated_consultations:,}건")
        print(f"  업데이트된 고객: {updated_customers:,}명")
        orphaned = results.get('orphaned_consultations', 0)
        if orphaned == 0:
            print(f"  고아 상담 (연결 안 된 상담): 0건 ✓")
        else:
            print(f"  [경고] 고아 상담: {orphaned}건 - 확인 필요!")

        print(f"\n[상담 횟수별 고객 분포]")
        for row in results.get('consultation_distribution', []):
            print(f"  {row[0]}: {row[1]:,}명")

        print("\n[다음 단계]")
        print("  python 09_assign_consultations_to_agents.py  # 상담사 배정")
        print("  python 08c_calculate_fcr.py  # FCR 계산")
        print("")

    finally:
        conn.close()
        print("[DB 연결 종료]")


if __name__ == "__main__":
    main()
