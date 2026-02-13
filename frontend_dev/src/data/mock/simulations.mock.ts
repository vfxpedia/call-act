// ==================== 시뮬레이션 데이터 ====================
// scenarioId: 실제 시나리오 ID (scenario-1 ~ scenario-8)와 일치
export const simulationsData = [
  { id: 1, scenarioId: 'scenario-1', title: '카드 분실 신고 및 재발급', category: '카드분실', difficulty: '초급', duration: '5분', icon: 'Shield' as const, color: '#EA4335' },
  { id: 2, scenarioId: 'scenario-3', title: '해외 결제 차단 해제 요청', category: '해외결제', difficulty: '중급', duration: '7분', icon: 'Target' as const, color: '#0047AB' },
  { id: 3, scenarioId: 'scenario-5', title: '연체 상환 방법 안내', category: '연체문의', difficulty: '고급', duration: '10분', icon: 'Users' as const, color: '#FBBC04' },
  { id: 4, scenarioId: 'scenario-6', title: '포인트 적립/사용 안내', category: '포인트/혜택', difficulty: '중급', duration: '8분', icon: 'TrendingUp' as const, color: '#34A853' },
];
