# 임시 파일: 로그 추가용 코드 스니펫
# 410번 라인 다음에 추가할 코드:

        # #region agent log
        if len(assignment_map) % 500 == 0:  # 샘플링: 500건마다
            current_stats = {
                'min': min(agent_consultation_counts.values()),
                'max': max(agent_consultation_counts.values()),
                'mean': sum(agent_consultation_counts.values()) / len(agent_consultation_counts)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': '09_test_assignment_logic.py:410',
                    'message': '배정 진행 상황',
                    'data': {
                        'processed_count': len(assignment_map),
                        'total_count': len(consultations_data_sorted),
                        'current_stats': current_stats,
                        'main_category': main_category,
                        'assigned_agent': agent_id
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }, ensure_ascii=False) + '\n')
        # #endregion
    
    # #region agent log
    final_stats = calculate_statistics(agent_consultation_counts)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': '09_test_assignment_logic.py:412',
            'message': '최종 배정 통계',
            'data': {
                'final_stats': final_stats,
                'category_distribution': category_counts,
                'pool_sizes': {cat: len(agent_pools_cache[cat]) for cat in agent_pools_cache}
            },
            'timestamp': int(datetime.now().timestamp() * 1000)
        }, ensure_ascii=False) + '\n')
    # #endregion
