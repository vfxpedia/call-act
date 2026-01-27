"""
고객 데이터 DB 적재 스크립트

기능:
- customersData.json에서 고객 데이터 로드
- customers 테이블에 INSERT (batch 처리)
- UPSERT 처리 (ON CONFLICT)
- 데이터 검증
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as psycopg2_connection
from psycopg2.extras import execute_batch, Json
from tqdm import tqdm

# 환경 변수 로드
load_dotenv(Path(__file__).parent / '.env', override=False)
load_dotenv(Path(__file__).parent.parent.parent / '.env', override=False)

# config.py에서 경로 가져오기
from config import CUSTOMERS_DATA_FILE

# 환경 변수
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "callact_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "callact_pwd1")
DB_NAME = os.getenv("DB_NAME", "callact_db")
BATCH_SIZE = int(os.getenv("DB_LOAD_BATCH_SIZE", "100"))
COMMIT_INTERVAL = int(os.getenv("DB_COMMIT_INTERVAL", "500"))


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


def ensure_table_exists(conn: psycopg2_connection) -> bool:
    """customers 테이블 존재 여부 확인"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'customers'
            )
        """)
        exists = cursor.fetchone()[0]
        if not exists:
            print("[ERROR] customers 테이블이 존재하지 않습니다.")
            print("[INFO] 07_setup_customers_table.sql을 먼저 실행하세요.")
            return False
        return True
    finally:
        cursor.close()


def map_customer_data(row: Dict) -> Tuple:
    """고객 데이터 매핑"""
    from datetime import datetime as dt

    def parse_date(date_str):
        """문자열을 DATE로 변환"""
        if date_str and isinstance(date_str, str):
            try:
                return dt.strptime(date_str, '%Y-%m-%d').date()
            except:
                return None
        return None

    return (
        row.get('id'),
        row.get('name'),
        row.get('phone'),
        row.get('gender', 'unknown'),
        row.get('age_group'),
        parse_date(row.get('birth_date')),  # DATE 타입
        row.get('address'),
        row.get('grade', 'GENERAL'),
        row.get('card_type'),
        row.get('card_number_last4'),
        row.get('card_brand'),
        parse_date(row.get('card_issue_date')),  # DATE 타입
        parse_date(row.get('card_expiry_date')),  # DATE 타입
        row.get('current_type_code'),  # VARCHAR(10) - 현재 주요 유형
        Json(row.get('type_history', [])),  # JSONB - 유형 이력
        row.get('personality_tags', []),
        Json(row.get('communication_style', {})),
        row.get('customer_type_codes', []),  # TEXT[] 배열
        row.get('llm_guidance'),
        row.get('total_consultations', 0),
        row.get('resolved_first_call', 0),
        row.get('last_consultation_date'),
    )


def load_customers(
    conn: psycopg2_connection,
    json_path: Path,
    limit: int = None
) -> int:
    """customers 테이블 적재"""

    print(f"\n[INFO] Loading customers from {json_path}...")

    # 파일 존재 확인
    if not json_path.exists():
        print(f"[ERROR] File not found: {json_path}")
        print(f"[INFO] 08_generate_customers_data.py를 먼저 실행하세요.")
        return 0

    # 데이터 로드
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if limit:
        data = data[:limit]
        print(f"[INFO] Limited to {limit} records")

    print(f"[INFO] Total records: {len(data)}")

    # 데이터 매핑
    mapped_data = []
    for row in data:
        try:
            mapped = map_customer_data(row)
            mapped_data.append(mapped)
        except Exception as e:
            print(f"[WARNING] Failed to map customer {row.get('id')}: {e}")
            continue

    # 배치 삽입
    insert_query = """
        INSERT INTO customers (
            id, name, phone, gender, age_group, birth_date, address, grade,
            card_type, card_number_last4, card_brand,
            card_issue_date, card_expiry_date,
            current_type_code, type_history,
            personality_tags, communication_style, customer_type_codes, llm_guidance,
            total_consultations, resolved_first_call, last_consultation_date,
            created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            phone = EXCLUDED.phone,
            gender = EXCLUDED.gender,
            age_group = EXCLUDED.age_group,
            birth_date = EXCLUDED.birth_date,
            address = EXCLUDED.address,
            grade = EXCLUDED.grade,
            card_type = EXCLUDED.card_type,
            card_number_last4 = EXCLUDED.card_number_last4,
            card_brand = EXCLUDED.card_brand,
            card_issue_date = EXCLUDED.card_issue_date,
            card_expiry_date = EXCLUDED.card_expiry_date,
            current_type_code = EXCLUDED.current_type_code,
            type_history = EXCLUDED.type_history,
            personality_tags = EXCLUDED.personality_tags,
            communication_style = EXCLUDED.communication_style,
            customer_type_codes = EXCLUDED.customer_type_codes,
            llm_guidance = EXCLUDED.llm_guidance,
            updated_at = NOW()
    """

    cursor = conn.cursor()

    try:
        print(f"[INFO] Inserting {len(mapped_data)} customers...")
        pbar = tqdm(total=len(mapped_data), desc="Loading customers")

        for i in range(0, len(mapped_data), BATCH_SIZE):
            batch = mapped_data[i:i+BATCH_SIZE]
            execute_batch(cursor, insert_query, batch, page_size=len(batch))

            # 주기적 커밋
            if (i + len(batch)) % COMMIT_INTERVAL == 0:
                conn.commit()

            pbar.update(len(batch))

        # 최종 커밋
        conn.commit()
        pbar.close()
        print(f"[INFO] Successfully inserted {len(mapped_data)} customers")
    except Exception as e:
        print(f"[ERROR] Failed to insert customers: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return 0
    finally:
        cursor.close()

    return len(mapped_data)


def verify_load(conn: psycopg2_connection) -> Dict:
    """적재 데이터 검증"""
    cursor = conn.cursor()

    results = {}

    try:
        # 전체 고객 수
        cursor.execute("SELECT COUNT(*) FROM customers")
        results["total_customers"] = cursor.fetchone()[0]

        # 성별 분포
        cursor.execute("""
            SELECT gender, COUNT(*),
                   ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers) * 100, 1) as pct
            FROM customers
            GROUP BY gender
        """)
        results["gender_distribution"] = cursor.fetchall()

        # 연령대 분포
        cursor.execute("""
            SELECT age_group, COUNT(*),
                   ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers) * 100, 1) as pct
            FROM customers
            GROUP BY age_group
            ORDER BY age_group
        """)
        results["age_distribution"] = cursor.fetchall()

        # 등급 분포
        cursor.execute("""
            SELECT grade, COUNT(*),
                   ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers) * 100, 1) as pct
            FROM customers
            GROUP BY grade
            ORDER BY
                CASE grade
                    WHEN 'VIP' THEN 1
                    WHEN 'GOLD' THEN 2
                    WHEN 'SILVER' THEN 3
                    ELSE 4
                END
        """)
        results["grade_distribution"] = cursor.fetchall()

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
    finally:
        cursor.close()

    return results


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Load customers data to PostgreSQL")
    parser.add_argument("--limit", type=int, help="Limit number of records to load (for testing)")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing data")

    args = parser.parse_args()

    # 데이터베이스 연결
    conn = connect_db()

    try:
        # 테이블 존재 확인
        if not ensure_table_exists(conn):
            print("\n[INFO] 테이블 생성을 위해 다음 명령을 실행하세요:")
            print("  psql -U callact_admin -d callact_db -f 07_setup_customers_table.sql")
            return

        if not args.verify_only:
            # 데이터 적재
            total_loaded = load_customers(
                conn,
                CUSTOMERS_DATA_FILE,
                limit=args.limit
            )
        else:
            total_loaded = 0

        # 검증
        print("\n[INFO] Verifying loaded data...")
        verification = verify_load(conn)

        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)

        print(f"\nTotal customers in DB: {verification.get('total_customers', 0)}")

        print("\n[Gender Distribution]")
        for row in verification.get('gender_distribution', []):
            print(f"  {row[0]}: {row[1]}명 ({row[2]}%)")

        print("\n[Age Distribution]")
        for row in verification.get('age_distribution', []):
            print(f"  {row[0]}: {row[1]}명 ({row[2]}%)")

        print("\n[Grade Distribution]")
        for row in verification.get('grade_distribution', []):
            print(f"  {row[0]}: {row[1]}명 ({row[2]}%)")

    finally:
        conn.close()
        print("\n[INFO] Database connection closed")


if __name__ == "__main__":
    main()
