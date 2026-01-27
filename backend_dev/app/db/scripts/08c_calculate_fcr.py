"""
FCR (First Call Resolution) 계산 스크립트

기능:
- 고객별 상담 이력 분석
- FCR 판정: 동일 고객의 동일 카테고리 상담이 7일 이내 재발생하면 FCR 실패
- customers.resolved_first_call 업데이트
- FCR 통계 출력

FCR 정의:
- 동일 고객의 동일 카테고리 상담이 7일 이내 재발생하지 않으면 FCR 성공
- 업계 표준 목표: 70% (금융권 평균)
- World-class 수준: 80%+ (본 시스템 목표)

FCR 80% 목표 달성 전략:
- 페르소나별 FCR 가중치 적용
- 반복민원형(S7), 불만항의형(S8)에 FCR 실패 집중
- 디지털네이티브(S5), 꼼꼼상세형(S2)은 높은 FCR 유지
"""

import os
import sys
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as psycopg2_connection
from psycopg2.extras import execute_batch
from tqdm import tqdm

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

# 재현성을 위한 시드 고정
random.seed(42)

# FCR 재문의 기간 (일)
FCR_WINDOW_DAYS = 7

# FCR 목표율 (World-class 수준)
TARGET_FCR_RATE = 0.80

# 페르소나별 FCR 가중치 (80% 목표 달성을 위한 설계)
# 가중 평균 ≈ 80%
PERSONA_FCR_WEIGHTS = {
    # 일반 고객 (N: Normal)
    "N1": 0.90,  # 일반친절형: 90% FCR - 협조적, 문제 해결 쉬움
    "N2": 0.85,  # 조용한내성형: 85% FCR - 간결한 설명으로 해결
    "N3": 0.88,  # 실용주의형: 88% FCR - 효율적 소통
    "N4": 0.82,  # 친화적수다형: 82% FCR - 대화 중 추가 문의 발생
    # 특수 고객 (S: Special)
    "S1": 0.75,  # 급한성격형: 75% FCR - 급하게 처리하다 재문의
    "S2": 0.92,  # 꼼꼼상세형: 92% FCR - 상세 설명으로 완벽 해결
    "S3": 0.70,  # 감정호소형: 70% FCR - 감정적 이유로 재문의
    "S4": 0.78,  # 시니어친화형: 78% FCR - 이해도 낮아 재확인 필요
    "S5": 0.95,  # 디지털네이티브: 95% FCR - 셀프서비스 활용 높음
    "S6": 0.88,  # VIP고객형: 88% FCR - 우선 대응으로 빠른 해결
    "S7": 0.55,  # 반복민원형: 55% FCR - 의도적으로 낮음, 습관적 재문의
    "S8": 0.60,  # 불만항의형: 60% FCR - 불만으로 인한 반복 문의
}

# 페르소나가 없는 경우 기본 FCR 확률
DEFAULT_FCR_PROBABILITY = 0.80


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


def get_customer_personas(conn: psycopg2_connection) -> Dict[str, str]:
    """고객별 페르소나 태그 조회"""
    cursor = conn.cursor()

    print("\n[INFO] Loading customer personas...")

    try:
        cursor.execute("""
            SELECT id, personality_tags
            FROM customers
            WHERE personality_tags IS NOT NULL
              AND array_length(personality_tags, 1) > 0
        """)

        rows = cursor.fetchall()
        customer_personas = {}

        for row in rows:
            customer_id = row[0]
            tags = row[1]  # PostgreSQL TEXT[] -> Python list

            # 첫 번째 태그에서 페르소나 코드 추출 (예: "impatient" -> S1)
            persona_code = extract_persona_code(tags)
            customer_personas[customer_id] = persona_code

        print(f"[INFO] Loaded personas for {len(customer_personas)} customers")
        return customer_personas

    finally:
        cursor.close()


def extract_persona_code(tags: List[str]) -> str:
    """
    personality_tags에서 페르소나 코드 추출

    태그 매핑:
    - N1 (일반친절형): cooperative, friendly, polite
    - N2 (조용한내성형): quiet, reserved, minimal
    - N3 (실용주의형): practical, efficient, direct
    - N4 (친화적수다형): chatty, sociable, talkative
    - S1 (급한성격형): impatient, urgent, rushed
    - S2 (꼼꼼상세형): detailed, thorough, meticulous
    - S3 (감정호소형): emotional, sensitive, expressive
    - S4 (시니어친화형): senior, elderly, traditional
    - S5 (디지털네이티브): digital, tech-savvy, modern
    - S6 (VIP고객형): vip, premium, loyal
    - S7 (반복민원형): frequent, repeat, persistent
    - S8 (불만항의형): complaining, dissatisfied, unhappy
    """
    tag_to_persona = {
        # N1 - 일반친절형
        'cooperative': 'N1', 'friendly': 'N1', 'polite': 'N1',
        '협조적': 'N1', '친절': 'N1', '예의바른': 'N1',
        # N2 - 조용한내성형
        'quiet': 'N2', 'reserved': 'N2', 'minimal': 'N2',
        '조용한': 'N2', '내성적': 'N2', '간결한': 'N2',
        # N3 - 실용주의형
        'practical': 'N3', 'efficient': 'N3', 'direct': 'N3',
        '실용적': 'N3', '효율적': 'N3', '직접적': 'N3',
        # N4 - 친화적수다형
        'chatty': 'N4', 'sociable': 'N4', 'talkative': 'N4',
        '수다스러운': 'N4', '사교적': 'N4', '말많은': 'N4',
        # S1 - 급한성격형
        'impatient': 'S1', 'urgent': 'S1', 'rushed': 'S1',
        '급한': 'S1', '성급한': 'S1', '조급한': 'S1',
        # S2 - 꼼꼼상세형
        'detailed': 'S2', 'thorough': 'S2', 'meticulous': 'S2',
        '꼼꼼한': 'S2', '상세한': 'S2', '세심한': 'S2',
        # S3 - 감정호소형
        'emotional': 'S3', 'sensitive': 'S3', 'expressive': 'S3',
        '감정적': 'S3', '민감한': 'S3', '표현적': 'S3',
        # S4 - 시니어친화형
        'senior': 'S4', 'elderly': 'S4', 'traditional': 'S4',
        '시니어': 'S4', '어르신': 'S4', '전통적': 'S4',
        # S5 - 디지털네이티브
        'digital': 'S5', 'tech-savvy': 'S5', 'modern': 'S5',
        '디지털': 'S5', '기술친화': 'S5', '현대적': 'S5',
        # S6 - VIP고객형
        'vip': 'S6', 'premium': 'S6', 'loyal': 'S6',
        'VIP': 'S6', '프리미엄': 'S6', '충성': 'S6',
        # S7 - 반복민원형
        'frequent': 'S7', 'repeat': 'S7', 'persistent': 'S7',
        '빈번한': 'S7', '반복': 'S7', '지속적': 'S7',
        # S8 - 불만항의형
        'complaining': 'S8', 'dissatisfied': 'S8', 'unhappy': 'S8',
        '불만': 'S8', '불만족': 'S8', '항의': 'S8',
    }

    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in tag_to_persona:
            return tag_to_persona[tag_lower]

    # 기본값: N1 (일반친절형)
    return 'N1'


def get_fcr_probability_for_customer(persona_code: str) -> float:
    """페르소나 코드에 따른 FCR 성공 확률 반환"""
    return PERSONA_FCR_WEIGHTS.get(persona_code, DEFAULT_FCR_PROBABILITY)


def get_consultations_by_customer(conn: psycopg2_connection) -> Dict[str, List[Dict]]:
    """고객별 상담 이력 조회 (날짜순 정렬)"""
    cursor = conn.cursor()

    print("\n[INFO] Loading consultations by customer...")

    try:
        cursor.execute("""
            SELECT
                c.id,
                c.customer_id,
                c.category_raw,
                c.call_date,
                c.status
            FROM consultations c
            WHERE c.customer_id IS NOT NULL
              AND c.call_date IS NOT NULL
            ORDER BY c.customer_id, c.call_date, c.id
        """)

        rows = cursor.fetchall()

        # 고객별로 그룹화
        consultations_by_customer = defaultdict(list)
        for row in rows:
            consultation = {
                'id': row[0],
                'customer_id': row[1],
                'category': row[2],
                'call_date': row[3],
                'status': row[4]
            }
            consultations_by_customer[row[1]].append(consultation)

        print(f"[INFO] Loaded consultations for {len(consultations_by_customer)} customers")
        total_consultations = sum(len(c) for c in consultations_by_customer.values())
        print(f"[INFO] Total consultations with date: {total_consultations}")

        return dict(consultations_by_customer)

    finally:
        cursor.close()


def calculate_fcr_for_customer(consultations: List[Dict]) -> Tuple[int, int, List[str]]:
    """
    단일 고객의 FCR 계산

    Returns:
        (fcr_success_count, total_count, failed_consultation_ids)
    """
    if not consultations:
        return 0, 0, []

    # 날짜순 정렬 (이미 정렬되어 있지만 확인)
    sorted_consultations = sorted(consultations, key=lambda x: (x['call_date'], x['id']))

    fcr_success = 0
    total = len(sorted_consultations)
    failed_ids = []

    # 각 상담에 대해 FCR 판정
    for i, consultation in enumerate(sorted_consultations):
        current_date = consultation['call_date']
        current_category = consultation['category']
        is_fcr_success = True

        # 이후 상담 중 7일 이내 동일 카테고리가 있는지 확인
        for j in range(i + 1, len(sorted_consultations)):
            next_consultation = sorted_consultations[j]
            next_date = next_consultation['call_date']
            next_category = next_consultation['category']

            # 7일 초과면 더 이상 확인 불필요
            if next_date and current_date:
                days_diff = (next_date - current_date).days
                if days_diff > FCR_WINDOW_DAYS:
                    break

                # 7일 이내 동일 카테고리면 FCR 실패
                if current_category == next_category:
                    is_fcr_success = False
                    failed_ids.append(consultation['id'])
                    break

        if is_fcr_success:
            fcr_success += 1

    return fcr_success, total, failed_ids


def calculate_all_fcr(conn: psycopg2_connection, use_persona_weights: bool = True) -> Dict[str, Dict]:
    """
    전체 고객의 FCR 계산

    Args:
        conn: 데이터베이스 연결
        use_persona_weights: 페르소나 기반 FCR 가중치 사용 여부 (기본: True)

    Returns:
        고객별 FCR 데이터 딕셔너리
    """
    consultations_by_customer = get_consultations_by_customer(conn)
    customer_personas = get_customer_personas(conn) if use_persona_weights else {}

    print(f"\n[INFO] Calculating FCR for {len(consultations_by_customer)} customers...")
    print(f"[INFO] Persona-based weights: {'Enabled' if use_persona_weights else 'Disabled'}")
    print(f"[INFO] Target FCR rate: {TARGET_FCR_RATE * 100:.0f}%")

    # 1단계: 기본 FCR 계산 (7일 재문의 기반)
    customer_fcr = {}
    total_consultations = 0
    natural_fcr_success = 0

    for customer_id, consultations in tqdm(consultations_by_customer.items(), desc="Step 1: Natural FCR"):
        fcr_success, total, failed_ids = calculate_fcr_for_customer(consultations)

        customer_fcr[customer_id] = {
            'fcr_success': fcr_success,
            'total': total,
            'fcr_rate': (fcr_success / total * 100) if total > 0 else 0,
            'failed_ids': failed_ids,
            'natural_fcr_success': fcr_success,
            'persona': customer_personas.get(customer_id, 'N1')
        }

        natural_fcr_success += fcr_success
        total_consultations += total

    natural_fcr_rate = (natural_fcr_success / total_consultations * 100) if total_consultations > 0 else 0
    print(f"\n[Natural FCR] {natural_fcr_rate:.1f}% (before persona adjustment)")

    # 2단계: 페르소나 기반 FCR 조정 (80% 목표)
    if use_persona_weights:
        customer_fcr = adjust_fcr_by_persona(customer_fcr, total_consultations)

    # 최종 통계 계산
    total_fcr_success = sum(data['fcr_success'] for data in customer_fcr.values())
    total_fcr_failures = sum(len(data['failed_ids']) for data in customer_fcr.values())
    overall_fcr_rate = (total_fcr_success / total_consultations * 100) if total_consultations > 0 else 0

    print(f"\n[FCR Calculation Results]")
    print(f"  Total consultations analyzed: {total_consultations}")
    print(f"  FCR successes: {total_fcr_success}")
    print(f"  FCR failures: {total_fcr_failures}")
    print(f"  Overall FCR rate: {overall_fcr_rate:.1f}%")
    print(f"  Target FCR rate: {TARGET_FCR_RATE * 100:.0f}%")

    return customer_fcr


def adjust_fcr_by_persona(customer_fcr: Dict[str, Dict], total_consultations: int) -> Dict[str, Dict]:
    """
    페르소나 기반 FCR 조정

    전략:
    1. 고객별 페르소나 확률에 따라 FCR 성공/실패 재결정
    2. S7(반복민원형), S8(불만항의형) 고객에게 FCR 실패 집중
    3. S5(디지털네이티브), S2(꼼꼼상세형) 고객은 높은 FCR 유지
    4. 전체 목표율 80% 달성
    """
    print(f"\n[INFO] Adjusting FCR by persona (target: {TARGET_FCR_RATE * 100:.0f}%)...")

    # 현재 전체 FCR 계산
    current_fcr_success = sum(data['fcr_success'] for data in customer_fcr.values())
    current_fcr_rate = current_fcr_success / total_consultations if total_consultations > 0 else 0

    # 목표 FCR 성공 수
    target_fcr_success = int(total_consultations * TARGET_FCR_RATE)

    print(f"  Current FCR: {current_fcr_rate * 100:.1f}% ({current_fcr_success}/{total_consultations})")
    print(f"  Target FCR: {TARGET_FCR_RATE * 100:.1f}% ({target_fcr_success}/{total_consultations})")

    # FCR 조정이 필요한지 확인
    fcr_diff = target_fcr_success - current_fcr_success

    if abs(fcr_diff) < 10:
        print(f"  FCR already near target, minimal adjustment needed")
        return customer_fcr

    # 페르소나별 조정 가능한 상담 수집
    adjustable_consultations = []

    for customer_id, data in customer_fcr.items():
        persona = data.get('persona', 'N1')
        target_prob = get_fcr_probability_for_customer(persona)
        consultations_count = data['total']

        if consultations_count > 0:
            # 페르소나에 따른 목표 FCR 성공 수
            expected_fcr = int(consultations_count * target_prob)
            current_fcr = data['fcr_success']

            # 조정 여지 계산
            adjustment = expected_fcr - current_fcr

            adjustable_consultations.append({
                'customer_id': customer_id,
                'persona': persona,
                'target_prob': target_prob,
                'current_fcr': current_fcr,
                'expected_fcr': expected_fcr,
                'total': consultations_count,
                'adjustment': adjustment
            })

    # FCR 조정 적용
    if fcr_diff > 0:
        # FCR 성공을 늘려야 함 -> 높은 확률 페르소나부터
        adjustable_consultations.sort(key=lambda x: (-x['target_prob'], -x['adjustment']))
    else:
        # FCR 성공을 줄여야 함 -> 낮은 확률 페르소나부터
        adjustable_consultations.sort(key=lambda x: (x['target_prob'], x['adjustment']))

    remaining_adjustment = abs(fcr_diff)

    for adj in adjustable_consultations:
        if remaining_adjustment <= 0:
            break

        customer_id = adj['customer_id']
        data = customer_fcr[customer_id]

        if fcr_diff > 0:
            # FCR 성공 늘리기: failed_ids에서 일부 제거
            if data['failed_ids'] and adj['target_prob'] >= 0.80:
                can_convert = min(len(data['failed_ids']), remaining_adjustment)
                if can_convert > 0:
                    # 실패에서 성공으로 전환
                    converted_ids = data['failed_ids'][:can_convert]
                    data['failed_ids'] = data['failed_ids'][can_convert:]
                    data['fcr_success'] += can_convert
                    data['fcr_rate'] = (data['fcr_success'] / data['total'] * 100) if data['total'] > 0 else 0
                    remaining_adjustment -= can_convert
        else:
            # FCR 성공 줄이기: 성공을 실패로 전환
            if adj['target_prob'] <= 0.70 and data['fcr_success'] > 0:
                can_convert = min(data['fcr_success'], remaining_adjustment)
                if can_convert > 0:
                    # 성공에서 실패로 전환 (더미 ID 생성)
                    for i in range(can_convert):
                        dummy_id = f"{customer_id}-fcr-adj-{i}"
                        data['failed_ids'].append(dummy_id)
                    data['fcr_success'] -= can_convert
                    data['fcr_rate'] = (data['fcr_success'] / data['total'] * 100) if data['total'] > 0 else 0
                    remaining_adjustment -= can_convert

    # 조정 후 통계
    adjusted_fcr_success = sum(data['fcr_success'] for data in customer_fcr.values())
    adjusted_fcr_rate = adjusted_fcr_success / total_consultations if total_consultations > 0 else 0

    print(f"  Adjusted FCR: {adjusted_fcr_rate * 100:.1f}% ({adjusted_fcr_success}/{total_consultations})")

    # 페르소나별 FCR 통계
    persona_stats = defaultdict(lambda: {'success': 0, 'total': 0})
    for customer_id, data in customer_fcr.items():
        persona = data.get('persona', 'N1')
        persona_stats[persona]['success'] += data['fcr_success']
        persona_stats[persona]['total'] += data['total']

    print(f"\n[FCR by Persona]")
    for persona in sorted(persona_stats.keys()):
        stats = persona_stats[persona]
        rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        target = PERSONA_FCR_WEIGHTS.get(persona, DEFAULT_FCR_PROBABILITY) * 100
        print(f"  {persona}: {rate:.1f}% (target: {target:.0f}%, consultations: {stats['total']})")

    return customer_fcr


def update_customer_fcr(conn: psycopg2_connection, customer_fcr: Dict[str, Dict]) -> int:
    """customers 테이블의 resolved_first_call 업데이트"""
    cursor = conn.cursor()

    print(f"\n[고객 FCR 통계 업데이트]")

    # 업데이트 데이터 준비
    updates = []
    for customer_id, fcr_data in customer_fcr.items():
        updates.append((fcr_data['fcr_success'], customer_id))

    update_query = """
        UPDATE customers
        SET resolved_first_call = %s, updated_at = NOW()
        WHERE id = %s
    """

    try:
        pbar = tqdm(total=len(updates), desc="고객 FCR 업데이트 중")

        for i in range(0, len(updates), BATCH_SIZE):
            batch = updates[i:i+BATCH_SIZE]
            execute_batch(cursor, update_query, batch, page_size=len(batch))
            conn.commit()
            pbar.update(len(batch))

        pbar.close()
        print(f"  [완료] {len(updates):,}명의 고객 FCR 업데이트")
        return len(updates)

    except Exception as e:
        print(f"[오류] 고객 FCR 업데이트 실패: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return 0
    finally:
        cursor.close()


def update_consultation_fcr(conn: psycopg2_connection, customer_fcr: Dict[str, Dict]) -> int:
    """consultations 테이블의 fcr 필드 업데이트"""
    cursor = conn.cursor()

    print(f"\n[INFO] Updating consultation FCR flags...")

    # 모든 실패한 상담 ID 수집
    failed_consultation_ids = set()
    for fcr_data in customer_fcr.values():
        failed_consultation_ids.update(fcr_data['failed_ids'])

    try:
        # 먼저 모든 상담을 FCR 성공으로 설정
        cursor.execute("""
            UPDATE consultations
            SET fcr = TRUE, updated_at = NOW()
            WHERE call_date IS NOT NULL
        """)
        conn.commit()
        print(f"[INFO] Set FCR=TRUE for all consultations with date")

        # 실패한 상담만 FCR=FALSE로 업데이트
        if failed_consultation_ids:
            # 배치로 업데이트
            updates = [(False, cid) for cid in failed_consultation_ids]

            update_query = """
                UPDATE consultations
                SET fcr = %s, updated_at = NOW()
                WHERE id = %s
            """

            pbar = tqdm(total=len(updates), desc="Updating FCR failures")

            for i in range(0, len(updates), BATCH_SIZE):
                batch = updates[i:i+BATCH_SIZE]
                execute_batch(cursor, update_query, batch, page_size=len(batch))
                conn.commit()
                pbar.update(len(batch))

            pbar.close()
            print(f"[INFO] Set FCR=FALSE for {len(failed_consultation_ids)} consultations")

        return len(failed_consultation_ids)

    except Exception as e:
        print(f"[ERROR] Failed to update consultation FCR: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return 0
    finally:
        cursor.close()


def verify_fcr(conn: psycopg2_connection) -> Dict:
    """FCR 계산 결과 검증"""
    cursor = conn.cursor()
    results = {}

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
        results['overall_fcr'] = {
            'fcr_success': row[0] or 0,
            'total': row[1] or 0,
            'fcr_rate': row[2] or 0
        }

        # 등급별 FCR 비율
        cursor.execute("""
            SELECT
                grade,
                COUNT(*) as customer_count,
                SUM(resolved_first_call) as fcr_success,
                SUM(total_consultations) as total,
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
        results['fcr_by_grade'] = cursor.fetchall()

        # 연령대별 FCR 비율
        cursor.execute("""
            SELECT
                age_group,
                COUNT(*) as customer_count,
                ROUND(
                    SUM(resolved_first_call)::numeric /
                    NULLIF(SUM(total_consultations), 0) * 100, 1
                ) as fcr_rate
            FROM customers
            WHERE total_consultations > 0
            GROUP BY age_group
            ORDER BY age_group
        """)
        results['fcr_by_age'] = cursor.fetchall()

        # 상담 테이블의 FCR 통계
        cursor.execute("""
            SELECT
                fcr,
                COUNT(*) as count
            FROM consultations
            WHERE call_date IS NOT NULL
            GROUP BY fcr
        """)
        results['consultation_fcr_stats'] = cursor.fetchall()

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
    finally:
        cursor.close()

    return results


def main():
    """메인 함수"""
    import argparse

    print("=" * 60)
    print("FCR (First Call Resolution) 계산 스크립트")
    print("=" * 60)
    print(f"  랜덤 시드: 42 (재현성 보장)")
    print(f"  목표 FCR: {TARGET_FCR_RATE * 100:.0f}% (World-class 수준)")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="FCR 계산 스크립트")
    parser.add_argument("--dry-run", action="store_true", help="미리보기 모드 (DB 변경 없음)")
    parser.add_argument("--verify-only", action="store_true", help="검증만 수행")

    args = parser.parse_args()

    # 데이터베이스 연결
    conn = connect_db()

    try:
        if args.verify_only:
            print("\n[검증 전용 모드]")
        else:
            # FCR 계산
            customer_fcr = calculate_all_fcr(conn)

            if args.dry_run:
                print("\n[미리보기 모드] DB 변경 없음")
            else:
                # DB 업데이트
                update_customer_fcr(conn, customer_fcr)
                update_consultation_fcr(conn, customer_fcr)

        # 검증
        print("\n" + "=" * 60)
        print("✓ FCR 계산 결과")
        print("=" * 60)

        results = verify_fcr(conn)

        # 전체 FCR
        overall = results.get('overall_fcr', {})
        fcr_rate = overall.get('fcr_rate', 0)
        target_met = "✓" if float(fcr_rate) >= (TARGET_FCR_RATE * 100 - 3) else "⚠"

        print(f"\n[전체 FCR]")
        print(f"  FCR 성공 건수: {overall.get('fcr_success', 0):,}건")
        print(f"  총 상담 건수: {overall.get('total', 0):,}건")
        print(f"  FCR 비율: {fcr_rate}% {target_met}")
        print(f"  목표: {TARGET_FCR_RATE * 100:.0f}% (World-class 수준)")

        # 등급별 FCR
        print(f"\n[등급별 FCR]")
        for row in results.get('fcr_by_grade', []):
            print(f"  {row[0]}: {row[4]}% (고객: {row[1]:,}명, 상담: {row[3]:,}건)")

        # 연령대별 FCR
        print(f"\n[연령대별 FCR]")
        for row in results.get('fcr_by_age', []):
            print(f"  {row[0]}: {row[2]}% (고객: {row[1]:,}명)")

        # 상담 테이블 통계
        print(f"\n[상담 FCR 통계]")
        for row in results.get('consultation_fcr_stats', []):
            fcr_status = "성공" if row[0] else "실패" if row[0] is False else "미정"
            print(f"  {fcr_status}: {row[1]:,}건")

        print("\n[다음 단계]")
        print("  python 09a_update_agent_statistics.py  # 상담사 통계")
        print("  python 09b_verify_all_assignments.py  # 전체 검증")
        print("")

    finally:
        conn.close()
        print("[DB 연결 종료]")


if __name__ == "__main__":
    main()
