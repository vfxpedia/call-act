"""
상담사 배정 로직 개선 및 사전 검증 스크립트

기능:
- 메모리에서만 실행 (DB 적재 없이)
- 배정 로직 개선 (tolerance, random_ratio 조정)
- 사전 검증 (표준편차, Max-Min 확인)
- 상담 ID 변환 함수 포함
- 반복 테스트 및 파라미터 최적화

사용법:
    python 09_test_assignment_logic.py [--tolerance TOLERANCE] [--random-ratio RATIO] [--seed SEED]

옵션:
    --tolerance: 허용 편차 (기본값: 4)
    --random-ratio: 랜덤 배분 비율 (기본값: 0.05)
    --seed: 랜덤 시드 (기본값: 42)
"""

import argparse
import json
import os
import random
import sys
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(Path(__file__).parent / '.env', override=False)
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env', override=False)

# config.py에서 경로 가져오기
from config import (
    HANA_RDB_METADATA_FILE,
    EMPLOYEES_DATA_FILE
)

# ==================== 대분류 매핑 (57개 카테고리 → 8개 대분류) ====================

# 대분류별 담당 풀 크기 설정 (60명 기준 - 상담 업무 담당자)
# 계획에 따라 수정된 풀 크기
MAIN_CATEGORY_POOL_SIZES = {
    "결제/승인": 12,      # ~1,559건
    "이용내역": 9,        # ~919건
    "한도": 7,            # ~564건
    "분실/도난": 6,       # ~400건
    "수수료/연체": 4,     # ~163건
    "포인트/혜택": 4,     # ~223건
    "정부지원": 3,        # ~167건
    "기타": None          # ~1,538건 (전체 상담사 순차)
}

# 대분류 매핑 딕셔너리 (57개 카테고리 → 8개 대분류)
CATEGORY_TO_MAIN_CATEGORY = {
    # 분실/도난 (긴급 처리 필요)
    "도난/분실 신청/해제": "분실/도난",
    "카드 분실 신고": "분실/도난",
    "카드 분실": "분실/도난",
    "도난 신고": "분실/도난",
    "분실 신청": "분실/도난",
    "분실 해제": "분실/도난",
    
    # 한도 (한도 관련)
    "한도상향 접수/처리": "한도",
    "한도 안내": "한도",
    "한도 조회": "한도",
    "한도 상향": "한도",
    "한도 증액": "한도",
    
    # 결제/승인 (결제 및 승인 관련)
    "선결제/즉시출금": "결제/승인",
    "결제대금 안내": "결제/승인",
    "승인취소/매출취소 안내": "결제/승인",
    "결제 안내": "결제/승인",
    "결제 확인": "결제/승인",
    "승인 취소": "결제/승인",
    "매출 취소": "결제/승인",
    "즉시 출금": "결제/승인",
    "선결제": "결제/승인",
    
    # 이용내역 (이용내역 관련)
    "이용내역 안내": "이용내역",
    "이용내역 조회": "이용내역",
    "이용 내역": "이용내역",
    
    # 수수료/연체 (수수료 및 연체 관련)
    "연체대금 즉시출금": "수수료/연체",
    "연체 수수료 안내": "수수료/연체",
    "연체대금 안내": "수수료/연체",
    "수수료 안내": "수수료/연체",
    "연체 안내": "수수료/연체",
    
    # 포인트/혜택 (포인트 및 혜택 관련)
    "이벤트 안내": "포인트/혜택",
    "포인트 적립": "포인트/혜택",
    "포인트 사용": "포인트/혜택",
    "포인트 안내": "포인트/혜택",
    "혜택 안내": "포인트/혜택",
    
    # 정부지원 (정부지원 관련)
    "정부지원 바우처 (등유, 임신 등)": "정부지원",
    "정부지원 바우처": "정부지원",
    "바우처 안내": "정부지원",
    
    # 기본값: "기타"로 처리 (위에 매핑되지 않은 모든 카테고리)
}


def map_to_main_category(category: str) -> str:
    """
    세부 카테고리를 대분류로 매핑
    
    Args:
        category: 세부 카테고리 (예: "선결제/즉시출금")
    
    Returns:
        대분류 (예: "결제/승인")
    """
    # 정확한 매칭 시도
    if category in CATEGORY_TO_MAIN_CATEGORY:
        return CATEGORY_TO_MAIN_CATEGORY[category]
    
    # 부분 매칭 (키워드 기반)
    category_lower = category.lower()
    
    # 분실/도난
    if any(keyword in category_lower for keyword in ["분실", "도난", "분실 신고"]):
        return "분실/도난"
    
    # 한도
    if any(keyword in category_lower for keyword in ["한도"]):
        return "한도"
    
    # 결제/승인
    if any(keyword in category_lower for keyword in ["결제", "승인", "매출", "즉시출금", "선결제"]):
        return "결제/승인"
    
    # 이용내역
    if any(keyword in category_lower for keyword in ["이용내역", "이용 내역"]):
        return "이용내역"
    
    # 수수료/연체
    if any(keyword in category_lower for keyword in ["연체", "수수료"]):
        return "수수료/연체"
    
    # 포인트/혜택
    if any(keyword in category_lower for keyword in ["포인트", "혜택", "이벤트"]):
        return "포인트/혜택"
    
    # 정부지원
    if any(keyword in category_lower for keyword in ["바우처", "정부지원"]):
        return "정부지원"
    
    # 기본값: "기타"
    return "기타"


def get_agent_pool_by_main_category(
    employees_data: List[Dict],
    main_category: str,
    used_agents_by_category: Dict[str, set] = None
) -> List[str]:
    """
    대분류별 상담사 풀 생성 (중복 최소화)
    
    Args:
        employees_data: 상담사 데이터 리스트
        main_category: 대분류 (예: "결제/승인")
        used_agents_by_category: 다른 대분류에서 이미 사용된 상담사 집합 (중복 방지용)
    
    Returns:
        상담사 ID 리스트 (예: ["EMP-001", "EMP-002", ...])
    """
    # EMP-TEDDY-DEFAULT 제외, active 상태만
    active_employees = [
        emp for emp in employees_data
        if emp.get('id') != 'EMP-TEDDY-DEFAULT' and emp.get('status') == 'active'
    ]
    
    if main_category == "기타":
        # "기타"는 모든 상담사에게 순차 분배
        return [emp['id'] for emp in active_employees]
    else:
        # 대분류별 풀 크기 결정
        pool_size = MAIN_CATEGORY_POOL_SIZES.get(main_category, 5)
        
        # 다른 대분류에서 사용된 상담사 제외 (중복 최소화)
        # 단, "기타"는 모든 상담사가 포함되므로 제외 대상에서 제외
        if used_agents_by_category:
            # 현재 대분류와 "기타"를 제외한 다른 대분류에서 사용된 상담사 집합
            other_used_agents = set()
            for cat, agents in used_agents_by_category.items():
                if cat != main_category and cat != "기타":
                    other_used_agents.update(agents)
            
            # 사용되지 않은 상담사 우선 선택
            if other_used_agents:
                available_employees = [
                    emp for emp in active_employees
                    if emp['id'] not in other_used_agents
                ]
            else:
                available_employees = active_employees
        else:
            available_employees = active_employees
        
        # 풀 크기만큼 선택
        return [emp['id'] for emp in available_employees[:pool_size]]


def assign_agent_improved(
    employees_data: List[Dict],
    consultations_data: List[Dict],
    tolerance: int = 4,
    random_ratio: float = 0.05,
    random_seed: int = 42
) -> Tuple[Dict[str, str], Dict[str, int], Dict[str, int]]:
    """
    개선된 배정 로직 실행
    
    Args:
        employees_data: 상담사 데이터 리스트
        consultations_data: 상담 데이터 리스트
        tolerance: 허용 편차 (기본값: 4)
        random_ratio: 랜덤 배분 비율 (기본값: 0.05 = 5%)
        random_seed: 랜덤 시드 (기본값: 42)
    
    Returns:
        (assignment_map, agent_counts, category_counts)
        - assignment_map: {consultation_id: agent_id}
        - agent_counts: {agent_id: count}
        - category_counts: {main_category: count}
    """
    # 랜덤 시드 고정
    random.seed(random_seed)
    
    # 입력 데이터 정렬 (재현성 확보)
    consultations_data_sorted = sorted(
        consultations_data,
        key=lambda x: (x.get('consulting_category', ''), x.get('source_id', ''))
    )
    
    # 모든 상담사 초기화
    all_agents = [
        emp['id'] for emp in employees_data
        if emp.get('id') != 'EMP-TEDDY-DEFAULT' and emp.get('status') == 'active'
    ]
    
    # #region agent log
    import json
    log_path = Path(__file__).parent.parent.parent.parent / '.cursor' / 'debug.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'A',
            'location': '09_test_assignment_logic.py:248',
            'message': '활성 상담사 수 확인',
            'data': {'active_agents_count': len(all_agents), 'all_agents': all_agents[:5]},
            'timestamp': int(datetime.now().timestamp() * 1000)
        }, ensure_ascii=False) + '\n')
    # #endregion
    
    agent_consultation_counts = {agent_id: 0 for agent_id in all_agents}
    assignment_map = {}
    category_counters = {}
    
    # 대분류별 상담 건수 집계
    category_consultation_counts = {}
    for row in consultations_data_sorted:
        category = row.get("consulting_category", "")
        main_cat = map_to_main_category(category)
        category_consultation_counts[main_cat] = category_consultation_counts.get(main_cat, 0) + 1
    
    # 대분류별 풀 미리 생성 (캐싱, 중복 최소화)
    agent_pools_cache = {}
    used_agents_by_category = {}
    
    # 상담 건수가 많은 순으로 정렬 (단, "기타"는 마지막에 처리)
    categories_to_process = [
        cat for cat, _ in sorted(category_consultation_counts.items(), key=lambda x: x[1], reverse=True)
        if cat != "기타"
    ]
    if "기타" in category_consultation_counts:
        categories_to_process.append("기타")
    
    for main_cat in categories_to_process:
        agent_pools_cache[main_cat] = get_agent_pool_by_main_category(
            employees_data, main_cat, used_agents_by_category
        )
        used_agents_by_category[main_cat] = set(agent_pools_cache[main_cat])
        
        # #region agent log
        log_path.parent.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C',
                'location': '09_test_assignment_logic.py:276',
                'message': '대분류별 풀 생성',
                'data': {
                    'main_category': main_cat,
                    'pool_size': len(agent_pools_cache[main_cat]),
                    'pool_agents': agent_pools_cache[main_cat],
                    'expected_pool_size': MAIN_CATEGORY_POOL_SIZES.get(main_cat, '전체'),
                    'consultation_count': category_consultation_counts.get(main_cat, 0)
                },
                'timestamp': int(datetime.now().timestamp() * 1000)
            }, ensure_ascii=False) + '\n')
        # #endregion
    
    # 배정 실행
    for row in consultations_data_sorted:
        consultation_id = row.get("id", "")
        category = row.get("consulting_category", "")
        main_category = map_to_main_category(category)
        
        # 대분류별 카운터 초기화
        if main_category not in category_counters:
            category_counters[main_category] = 0
        
        # 상담사 풀 가져오기
        agent_pool = agent_pools_cache[main_category]
        
        # 1. 전체 상담사 중 최소 건수 확인 (균등 배분을 위해)
        all_min_count = min(agent_consultation_counts.values())
        
        # 2. 풀 내 상담사들의 건수 확인
        pool_counts = {aid: agent_consultation_counts.get(aid, 0) for aid in agent_pool}
        pool_min_count = min(pool_counts.values())
        
        # 3. 풀 내 상담사 중에서 전체 최소 건수에 가까운 상담사 선택
        # 전체 최소 건수와의 차이가 tolerance 이내인 상담사만 후보로 선택
        candidates = [
            aid for aid in agent_pool
            if abs(pool_counts[aid] - all_min_count) <= tolerance
        ]
        
        # #region agent log
        fallback_used = False
        if len(assignment_map) % 100 == 0 or len(candidates) == 0:  # 샘플링: 100건마다 또는 후보 없을 때
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B',
                    'location': '09_test_assignment_logic.py:304',
                    'message': '후보 선택 과정',
                    'data': {
                        'main_category': main_category,
                        'all_min_count': all_min_count,
                        'tolerance': tolerance,
                        'pool_min_count': pool_min_count,
                        'pool_counts_sample': dict(list(pool_counts.items())[:3]),
                        'candidates_count_before_fallback': len(candidates),
                        'pool_size': len(agent_pool)
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }, ensure_ascii=False) + '\n')
        # #endregion
        
        # 4. 풀 내에 전체 최소 건수에 가까운 상담사가 없으면, 풀 내 최소 건수 상담사 선택 (fallback)
        if not candidates:
            candidates = [aid for aid in agent_pool if pool_counts[aid] == pool_min_count]
            fallback_used = True
            
            # #region agent log
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B',
                    'location': '09_test_assignment_logic.py:311',
                    'message': 'Fallback 발생',
                    'data': {
                        'main_category': main_category,
                        'all_min_count': all_min_count,
                        'pool_min_count': pool_min_count,
                        'gap': pool_min_count - all_min_count,
                        'candidates_after_fallback': len(candidates)
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }, ensure_ascii=False) + '\n')
            # #endregion
        
        # 5. 후보가 여러 명이면, 전체 최소 건수에 가장 가까운 상담사 우선 선택
        # 단, 차이가 2건 이내면 모두 후보로 유지 (약간의 다양성 허용)
        if len(candidates) > 1:
            min_diff = min(abs(pool_counts[aid] - all_min_count) for aid in candidates)
            # 차이가 2건 이내인 상담사들은 모두 후보로 유지
            candidates = [
                aid for aid in candidates
                if abs(pool_counts[aid] - all_min_count) <= min_diff + 2
            ]
        
        # 6. 하이브리드 배분 (95% 순차 + 5% 랜덤)
        if random.random() < random_ratio:  # 랜덤 (후보 상담사 중에서)
            agent_id = random.choice(candidates)
        else:  # 순차 (후보 상담사 중에서)
            pool_index = category_counters[main_category] % len(candidates)
            agent_id = candidates[pool_index]
        
        # 배정 및 건수 증가
        assignment_map[consultation_id] = agent_id
        agent_consultation_counts[agent_id] += 1
        category_counters[main_category] += 1
    
    return assignment_map, agent_consultation_counts, category_counters


def convert_to_new_consultation_id(
    old_id: str,
    agent_id: str,
    call_start_time: Optional[str] = None,
    created_at: Optional[str] = None
) -> str:
    """
    기존 상담 ID를 새 형식으로 변환
    
    Args:
        old_id: 기존 ID (예: "hana_consultation_20593")
        agent_id: 상담사 ID (예: "EMP-001")
        call_start_time: 통화 시작 시간 (ISO 형식)
        created_at: 생성 시간 (ISO 형식, fallback)
    
    Returns:
        새 형식 ID (예: "CS-EMP001-202601211430")
    """
    # 1. agent_id에서 대시 제거
    clean_agent_id = agent_id.replace("-", "")
    
    # 2. 날짜/시간 추출
    dt = None
    if call_start_time:
        try:
            dt = datetime.fromisoformat(call_start_time.replace("Z", "+00:00"))
        except:
            pass
    
    # fallback: created_at 사용
    if not dt and created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except:
            pass
    
    # fallback: 현재 시간 사용 (최후의 수단)
    if not dt:
        dt = datetime.now()
    
    # 3. 새 형식 ID 생성 (YYYYMMDDHHMM)
    timestamp_str = dt.strftime("%Y%m%d%H%M")
    return f"CS-{clean_agent_id}-{timestamp_str}"


def assign_agent_balanced(
    employees_data: List[Dict],
    consultations_data: List[Dict],
    random_seed: int = 42,
    target_std_dev: float = 10.0
) -> Tuple[Dict[str, str], Dict[str, int], Dict[str, int]]:
    """
    균등 배분 알고리즘 (적절한 편차 포함)

    목표: 표준편차 ~10, 범위 85~130

    Args:
        employees_data: 상담사 데이터 리스트 (이미 상담팀만 필터링됨)
        consultations_data: 상담 데이터 리스트
        random_seed: 랜덤 시드 (기본값: 42)
        target_std_dev: 목표 표준편차 (기본값: 10.0)

    Returns:
        (assignment_map, agent_counts, category_counts)
    """
    import random
    random.seed(random_seed)

    # 상담사 ID 목록
    agent_ids = [emp['id'] for emp in employees_data]
    num_agents = len(agent_ids)
    total_consultations = len(consultations_data)
    mean_target = total_consultations / num_agents

    # 상담사별 목표 건수 설정 (정규분포 기반 편차 적용)
    # target_std_dev를 기준으로 각 상담사의 목표 건수를 다르게 설정
    agent_targets = {}
    for i, aid in enumerate(agent_ids):
        # 정규분포 기반 편차 (시드 기반 재현성)
        random.seed(random_seed + i)
        deviation = random.gauss(0, target_std_dev)
        target = int(mean_target + deviation)
        # 최소/최대 제한 (평균의 ±25% 범위)
        target = max(int(mean_target * 0.75), min(int(mean_target * 1.25), target))
        agent_targets[aid] = target

    # 상담 데이터 셔플 (재현성 보장)
    random.seed(random_seed)
    shuffled_consultations = list(consultations_data)
    random.shuffle(shuffled_consultations)

    # 카운터 초기화
    agent_counts = {aid: 0 for aid in agent_ids}
    assignment_map = {}
    category_counts = {}

    # 배분: 목표 대비 가장 부족한 상담사에게 배정
    for consultation in shuffled_consultations:
        consultation_id = consultation.get("id", "")
        category = consultation.get("consulting_category", "")
        main_category = map_to_main_category(category)

        # 목표 대비 달성률이 가장 낮은 상담사 찾기
        min_ratio = float('inf')
        candidates = []
        for aid in agent_ids:
            target = agent_targets[aid]
            current = agent_counts[aid]
            ratio = current / target if target > 0 else float('inf')
            if ratio < min_ratio:
                min_ratio = ratio
                candidates = [aid]
            elif ratio == min_ratio:
                candidates.append(aid)

        # 후보 중 랜덤 선택 (동점자 처리)
        agent_id = random.choice(candidates)

        # 배정
        assignment_map[consultation_id] = agent_id
        agent_counts[agent_id] += 1
        category_counts[main_category] = category_counts.get(main_category, 0) + 1

    return assignment_map, agent_counts, category_counts


def calculate_statistics(agent_counts: Dict[str, int]) -> Dict:
    """
    배정 결과 통계 계산
    
    Args:
        agent_counts: {agent_id: count}
    
    Returns:
        통계 딕셔너리
    """
    counts = list(agent_counts.values())
    if not counts:
        return {
            'mean': 0,
            'std_dev': 0,
            'min': 0,
            'max': 0,
            'range': 0,
            'total': 0,
            'count': 0
        }
    
    mean = sum(counts) / len(counts)
    variance = sum((x - mean) ** 2 for x in counts) / len(counts)
    std_dev = math.sqrt(variance)
    min_count = min(counts)
    max_count = max(counts)
    range_count = max_count - min_count
    
    return {
        'mean': mean,
        'std_dev': std_dev,
        'min': min_count,
        'max': max_count,
        'range': range_count,
        'total': sum(counts),
        'count': len(counts)
    }


def print_statistics(agent_counts: Dict[str, int], category_counts: Dict[str, int]):
    """
    배정 결과 통계 출력
    
    Args:
        agent_counts: {agent_id: count}
        category_counts: {main_category: count}
    """
    stats = calculate_statistics(agent_counts)
    
    print("\n" + "=" * 60)
    print("배정 결과 통계")
    print("=" * 60)
    print(f"전체 상담사 수: {stats['count']}명")
    print(f"총 상담 건수: {stats['total']}건")
    print(f"평균: {stats['mean']:.2f}건/명")
    print(f"표준편차: {stats['std_dev']:.2f}")
    print(f"최대: {stats['max']}건")
    print(f"최소: {stats['min']}건")
    print(f"범위 (Max - Min): {stats['range']}건")
    
    # 검증 기준 확인
    print("\n검증 기준:")
    print(f"  표준편차 ≤ 15: {'✅ 통과' if stats['std_dev'] <= 15 else '❌ 실패'} ({stats['std_dev']:.2f})")
    print(f"  Max - Min ≤ 60: {'✅ 통과' if stats['range'] <= 60 else '❌ 실패'} ({stats['range']})")
    print(f"  목표 범위 80~140: {'✅ 통과' if 80 <= stats['min'] and stats['max'] <= 140 else '❌ 실패'} ({stats['min']}~{stats['max']})")
    
    # 상위/하위 5명 출력
    sorted_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\n상위 5명:")
    for i, (agent_id, count) in enumerate(sorted_agents[:5], 1):
        print(f"  {i}위: {agent_id} - {count}건")
    
    if len(sorted_agents) > 5:
        print("\n하위 5명:")
        for i, (agent_id, count) in enumerate(sorted_agents[-5:], len(sorted_agents) - 4):
            print(f"  {i}위: {agent_id} - {count}건")
    
    # 대분류별 분포
    print("\n대분류별 상담 건수:")
    for main_cat in sorted(category_counts.keys(), key=lambda x: category_counts[x], reverse=True):
        count = category_counts[main_cat]
        pool_size = MAIN_CATEGORY_POOL_SIZES.get(main_cat, '전체')
        print(f"  - {main_cat}: {count}건 (풀 크기: {pool_size})")
    
    print("=" * 60)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='상담사 배정 로직 개선 및 사전 검증')
    parser.add_argument('--tolerance', type=int, default=4, help='허용 편차 (기본값: 4)')
    parser.add_argument('--random-ratio', type=float, default=0.05, help='랜덤 배분 비율 (기본값: 0.05)')
    parser.add_argument('--seed', type=int, default=42, help='랜덤 시드 (기본값: 42)')
    parser.add_argument('--save-results', action='store_true', help='배정 결과를 JSON 파일로 저장')
    parser.add_argument('--algorithm', type=str, default='balanced', choices=['balanced', 'category'],
                       help='배정 알고리즘 선택 (balanced: 균등배분, category: 대분류별풀)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("상담사 배정 로직 개선 및 사전 검증 스크립트")
    print("=" * 60)
    print(f"파라미터:")
    print(f"  - algorithm: {args.algorithm}")
    print(f"  - tolerance: {args.tolerance} (category 알고리즘용)")
    print(f"  - random_ratio: {args.random_ratio} (category 알고리즘용)")
    print(f"  - random_seed: {args.seed}")
    print("=" * 60)
    
    # 1. 데이터 로드
    print("\n[1/4] 데이터 로드 중...")
    
    if not HANA_RDB_METADATA_FILE.exists():
        print(f"[ERROR] 하나카드 RDB 메타데이터 파일을 찾을 수 없습니다: {HANA_RDB_METADATA_FILE}")
        sys.exit(1)
    
    if not EMPLOYEES_DATA_FILE.exists():
        print(f"[ERROR] 상담사 데이터 파일을 찾을 수 없습니다: {EMPLOYEES_DATA_FILE}")
        sys.exit(1)
    
    with open(HANA_RDB_METADATA_FILE, 'r', encoding='utf-8') as f:
        consultations_data = json.load(f)
    
    with open(EMPLOYEES_DATA_FILE, 'r', encoding='utf-8') as f:
        employees_data = json.load(f)
    
    # 상담 담당 팀만 필터링 (상담1팀, 상담2팀, 상담3팀)
    counselor_teams = ['상담1팀', '상담2팀', '상담3팀']
    active_employees = [
        emp for emp in employees_data
        if emp.get('id') != 'EMP-TEDDY-DEFAULT'
        and emp.get('status') == 'active'
        and emp.get('team') in counselor_teams
    ]

    # 비상담 팀 제외 안내
    excluded_employees = [
        emp for emp in employees_data
        if emp.get('status') == 'active'
        and emp.get('team') not in counselor_teams
        and emp.get('id') != 'EMP-TEDDY-DEFAULT'
    ]
    if excluded_employees:
        excluded_teams = set(emp.get('team') for emp in excluded_employees)
        print(f"[INFO] 비상담 팀 제외: {excluded_teams} ({len(excluded_employees)}명)")

    print(f"[INFO] 총 상담 건수: {len(consultations_data)}건")
    print(f"[INFO] 상담 담당자 수: {len(active_employees)}명 (상담1/2/3팀)")
    print(f"[INFO] 목표 평균: {len(consultations_data) / len(active_employees):.2f}건/명")
    
    # 2. 배정 로직 실행
    print(f"\n[2/4] 배정 로직 실행 중... (알고리즘: {args.algorithm})")

    if args.algorithm == 'balanced':
        # 균등 배분 알고리즘 (권장)
        assignment_map, agent_counts, category_counts = assign_agent_balanced(
            employees_data=active_employees,
            consultations_data=consultations_data,
            random_seed=args.seed
        )
    else:
        # 대분류별 풀 알고리즘 (기존)
        assignment_map, agent_counts, category_counts = assign_agent_improved(
            employees_data=active_employees,
            consultations_data=consultations_data,
            tolerance=args.tolerance,
            random_ratio=args.random_ratio,
            random_seed=args.seed
        )
    
    # 3. 통계 출력
    print("\n[3/4] 통계 계산 중...")
    print_statistics(agent_counts, category_counts)
    
    # 4. 상담 ID 변환 (샘플)
    print("\n[4/4] 상담 ID 변환 샘플 (처음 5개)...")
    sample_count = 0
    for consultation_id, agent_id in assignment_map.items():
        if sample_count >= 5:
            break
        
        # 원본 데이터에서 해당 상담 찾기
        consultation = next(
            (c for c in consultations_data if c.get('id') == consultation_id),
            None
        )
        
        if consultation:
            new_id = convert_to_new_consultation_id(
                old_id=consultation_id,
                agent_id=agent_id,
                call_start_time=consultation.get('call_start_time'),
                created_at=consultation.get('created_at')
            )
            print(f"  {consultation_id} → {new_id} (상담사: {agent_id})")
            sample_count += 1
    
    # 5. 결과 저장 (옵션)
    if args.save_results:
        results_file = Path(__file__).parent / 'test_results' / f'assignment_results_t{args.tolerance}_r{args.random_ratio}_s{args.seed}.json'
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            'parameters': {
                'tolerance': args.tolerance,
                'random_ratio': args.random_ratio,
                'random_seed': args.seed
            },
            'statistics': calculate_statistics(agent_counts),
            'assignment_map': assignment_map,
            'agent_counts': agent_counts,
            'category_counts': category_counts
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n[INFO] 결과 저장: {results_file}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 배정 로직 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
