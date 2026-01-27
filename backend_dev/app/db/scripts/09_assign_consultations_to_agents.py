"""
상담사 배정 스크립트 (균등 배정 알고리즘 v2)

기능:
- 60명 상담사에게 6,533건 상담을 균등 배분
- 목표: 표준편차 ≤15, 범위 ≤40건, 평균 ~109건

핵심 알고리즘:
- 글로벌 최소값 우선 배정 (Global Min-First)
- 카테고리 풀 제거 → 모든 상담사가 모든 카테고리 처리 가능
- 항상 가장 적게 배정된 상담사에게 배정
"""

import json
import os
import sys
import random
import statistics
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as psycopg2_connection
from psycopg2.extras import execute_batch
from tqdm import tqdm

# 환경 변수 로드
load_dotenv(Path(__file__).parent / '.env', override=False)
load_dotenv(Path(__file__).parent.parent.parent / '.env', override=False)

# config.py에서 경로 가져오기
from config import HANA_RDB_METADATA_FILE, EMPLOYEES_DATA_FILE

# 환경 변수
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "callact_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "callact_pwd1")
DB_NAME = os.getenv("DB_NAME", "callact_db")
BATCH_SIZE = int(os.getenv("DB_LOAD_BATCH_SIZE", "100"))

# 재현성을 위한 시드 고정
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# 목표 기준
TARGET_STD_DEV = 15
TARGET_RANGE = 40

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
        print(f"[DB 연결 성공] {DB_NAME}@{DB_HOST}:{DB_PORT}")
        return conn
    except psycopg2.OperationalError as e:
        print(f"\n[오류] 데이터베이스 연결 실패!")
        print(f"  호스트: {DB_HOST}:{DB_PORT}")
        print(f"  에러: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[오류] 예상치 못한 오류: {e}")
        sys.exit(1)


def load_employees() -> List[str]:
    """상담사 목록 로드 (60명)"""
    print(f"\n[상담사 로드]")
    print(f"  경로: {EMPLOYEES_DATA_FILE}")

    if not EMPLOYEES_DATA_FILE.exists():
        print(f"  [오류] 파일이 존재하지 않습니다!")
        sys.exit(1)

    with open(EMPLOYEES_DATA_FILE, 'r', encoding='utf-8') as f:
        employees = json.load(f)

    # 상담사만 필터링 (IT/관리/교육팀 제외)
    counselors = [
        emp['id'] for emp in employees
        if emp['id'] not in EXCLUDED_AGENT_IDS
    ]

    excluded_count = len(employees) - len(counselors)
    print(f"  [로드 완료] 상담사 {len(counselors)}명 (비상담사 {excluded_count}명 제외)")

    return counselors


def load_consultations() -> List[Dict]:
    """상담 데이터 로드"""
    print(f"\n[상담 데이터 로드]")
    print(f"  경로: {HANA_RDB_METADATA_FILE}")

    if not HANA_RDB_METADATA_FILE.exists():
        print(f"  [오류] 파일이 존재하지 않습니다!")
        sys.exit(1)

    with open(HANA_RDB_METADATA_FILE, 'r', encoding='utf-8') as f:
        consultations = json.load(f)

    print(f"  [로드 완료] {len(consultations):,}건의 상담 데이터")

    return consultations


def assign_consultations_balanced(
    consultations: List[Dict],
    counselors: List[str]
) -> Dict[str, str]:
    """
    균등 배정 알고리즘 (Global Min-First)

    핵심 원리:
    - 각 상담을 배정할 때, 현재 가장 적게 배정된 상담사에게 배정
    - 동점일 경우 랜덤 선택 (시드 고정으로 재현성 보장)
    """
    print(f"\n[상담사 배정 시작]")
    print(f"  총 상담: {len(consultations):,}건")
    print(f"  총 상담사: {len(counselors)}명")
    print(f"  목표 평균: {len(consultations) / len(counselors):.1f}건/명")

    # 상담사별 카운터 초기화
    agent_counts = {agent: 0 for agent in counselors}

    # 상담 ID → 상담사 ID 매핑
    assignments = {}

    # 상담 목록 셔플 (랜덤성 추가, 시드 고정으로 재현성 보장)
    shuffled_consultations = consultations.copy()
    random.shuffle(shuffled_consultations)

    # 진행률 표시
    pbar = tqdm(total=len(shuffled_consultations), desc="배정 중")

    for consultation in shuffled_consultations:
        consultation_id = consultation.get('id', '')

        # 현재 최소 배정 건수 찾기
        min_count = min(agent_counts.values())

        # 최소 건수를 가진 상담사들 찾기
        candidates = [a for a in counselors if agent_counts[a] == min_count]

        # 후보 중 랜덤 선택
        selected_agent = random.choice(candidates)

        # 배정 기록
        assignments[consultation_id] = selected_agent
        agent_counts[selected_agent] += 1

        pbar.update(1)

    pbar.close()

    # 배정 결과 요약
    counts = list(agent_counts.values())
    print(f"\n[배정 완료]")
    print(f"  평균: {statistics.mean(counts):.1f}건/명")
    print(f"  최소: {min(counts)}건")
    print(f"  최대: {max(counts)}건")

    return assignments


def validate_distribution(assignments: Dict[str, str], counselors: List[str]) -> Dict:
    """배정 결과 검증"""
    print(f"\n[검증 수행]")

    # 상담사별 건수 집계
    agent_counts = defaultdict(int)
    for consultation_id, agent_id in assignments.items():
        agent_counts[agent_id] += 1

    # 통계 계산
    counts = [agent_counts.get(a, 0) for a in counselors]
    avg_count = sum(counts) / len(counts) if counts else 0
    std_dev = statistics.stdev(counts) if len(counts) > 1 else 0
    max_count = max(counts) if counts else 0
    min_count = min(counts) if counts else 0
    range_count = max_count - min_count

    # 상위/하위 5명
    sorted_agents = sorted(counselors, key=lambda a: agent_counts.get(a, 0), reverse=True)
    top_5 = [(a, agent_counts.get(a, 0)) for a in sorted_agents[:5]]
    bottom_5 = [(a, agent_counts.get(a, 0)) for a in sorted_agents[-5:]]

    # 검증 결과
    std_pass = std_dev <= TARGET_STD_DEV
    range_pass = range_count <= TARGET_RANGE

    results = {
        'total_consultations': len(assignments),
        'total_agents': len(counselors),
        'average': avg_count,
        'std_dev': std_dev,
        'max': max_count,
        'min': min_count,
        'range': range_count,
        'std_pass': std_pass,
        'range_pass': range_pass,
        'top_5': top_5,
        'bottom_5': bottom_5,
        'agent_counts': dict(agent_counts),
    }

    return results


def print_validation_results(results: Dict) -> None:
    """검증 결과 출력"""
    print("\n" + "=" * 60)
    print("배정 결과 통계")
    print("=" * 60)

    print(f"전체 상담사 수: {results['total_agents']}명")
    print(f"총 상담 건수: {results['total_consultations']:,}건")
    print(f"평균: {results['average']:.2f}건/명")
    print(f"표준편차: {results['std_dev']:.2f}")
    print(f"최대: {results['max']}건")
    print(f"최소: {results['min']}건")
    print(f"범위 (Max - Min): {results['range']}건")

    print(f"\n검증 기준:")
    std_status = "✓ 통과" if results['std_pass'] else "✗ 실패"
    range_status = "✓ 통과" if results['range_pass'] else "✗ 실패"
    print(f"  표준편차 ≤ {TARGET_STD_DEV}: {std_status} ({results['std_dev']:.2f})")
    print(f"  범위 ≤ {TARGET_RANGE}: {range_status} ({results['range']})")

    print(f"\n상위 5명:")
    for i, (agent, count) in enumerate(results['top_5'], 1):
        print(f"  {i}위: {agent} - {count}건")

    print(f"\n하위 5명:")
    for i, (agent, count) in enumerate(results['bottom_5'], 56):
        print(f"  {i}위: {agent} - {count}건")

    print("=" * 60)


def update_consultations_db(conn: psycopg2_connection, assignments: Dict[str, str]) -> int:
    """consultations 테이블의 agent_id 업데이트"""
    cursor = conn.cursor()

    print(f"\n[DB 업데이트]")
    print(f"  대상: {len(assignments):,}건")

    # 업데이트 데이터 준비
    updates = [(agent_id, consultation_id) for consultation_id, agent_id in assignments.items()]

    update_query = """
        UPDATE consultations
        SET agent_id = %s, updated_at = NOW()
        WHERE id = %s
    """

    try:
        pbar = tqdm(total=len(updates), desc="DB 업데이트 중")

        for i in range(0, len(updates), BATCH_SIZE):
            batch = updates[i:i+BATCH_SIZE]
            execute_batch(cursor, update_query, batch, page_size=len(batch))
            conn.commit()
            pbar.update(len(batch))

        pbar.close()
        print(f"  [완료] {len(updates):,}건 업데이트 성공")
        return len(updates)

    except Exception as e:
        print(f"  [오류] DB 업데이트 실패: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return 0
    finally:
        cursor.close()


def save_assignments_json(assignments: Dict[str, str], output_path: Path) -> None:
    """배정 결과를 JSON 파일로 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(assignments, f, ensure_ascii=False, indent=2)
    print(f"[저장 완료] {output_path}")


def main():
    """메인 함수"""
    import argparse

    print("=" * 60)
    print("상담사 배정 스크립트 (균등 배정 알고리즘 v2)")
    print("=" * 60)
    print(f"  랜덤 시드: {RANDOM_SEED} (재현성 보장 - 누가 돌려도 동일한 결과)")
    print(f"  목표: 표준편차 ≤{TARGET_STD_DEV}, 범위 ≤{TARGET_RANGE}건")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="상담사 균등 배정 스크립트")
    parser.add_argument("--dry-run", action="store_true", help="미리보기 모드 (DB 변경 없음)")
    parser.add_argument("--save-json", type=str, help="배정 결과를 JSON 파일로 저장")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="랜덤 시드 (기본: 42)")

    args = parser.parse_args()

    # 시드 설정
    random.seed(args.seed)
    if args.seed != RANDOM_SEED:
        print(f"  [주의] 커스텀 시드 사용: {args.seed}")

    # 1. 데이터 로드
    counselors = load_employees()
    consultations = load_consultations()

    # 2. 상담 배정 (균등 배정 알고리즘)
    assignments = assign_consultations_balanced(consultations, counselors)

    # 3. 검증
    results = validate_distribution(assignments, counselors)
    print_validation_results(results)

    # 4. JSON 저장 (옵션)
    if args.save_json:
        save_assignments_json(assignments, Path(args.save_json))

    # 5. DB 업데이트
    if args.dry_run:
        print("\n[미리보기 모드] DB 변경 없음")
    else:
        conn = connect_db()
        try:
            updated = update_consultations_db(conn, assignments)
            print(f"\n[DB 업데이트 완료] {updated:,}건의 상담 배정 완료")
        finally:
            conn.close()
            print("[DB 연결 종료]")

    # 최종 결과
    print("\n" + "=" * 60)
    if results['std_pass'] and results['range_pass']:
        print("✓ 상담사 배정 완료 - 목표 달성!")
    else:
        print("⚠ 상담사 배정 완료 - 일부 목표 미달")
        if not results['std_pass']:
            print(f"  - 표준편차: {results['std_dev']:.2f} (목표: ≤{TARGET_STD_DEV})")
        if not results['range_pass']:
            print(f"  - 범위: {results['range']} (목표: ≤{TARGET_RANGE})")
    print("=" * 60)

    print("\n[다음 단계]")
    print("  python 08c_calculate_fcr.py  # FCR 계산")
    print("  python 09a_update_agent_statistics.py  # 상담사 통계")
    print("")


if __name__ == "__main__":
    main()
