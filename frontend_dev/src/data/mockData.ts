// ==================== 공지사항 데이터 ====================
export const noticesData = [
  { 
    id: 1, 
    tag: '긴급', 
    title: 'KT 화재로 인한 통신망 장애 대응', 
    date: '2025-01-05',
    author: '관리자',
    views: 245,
    pinned: true,
    content: 'KT 아현지사 화재로 인한 통신망 장애가 발생했습니다. 고객 문의 시 다음과 같이 안내해주세요:\n\n1. 현재 일부 지역에서 통신 장애가 발생하고 있습니다.\n2. 복구 작업이 진행 중이며, 예상 복구 시간은 오후 6시입니다.\n3. 긴급한 경우 와이파이를 통한 인터넷 전화를 이용하시기 바랍니다.\n\n고객 불편 최소화를 위해 신속히 대응해주시기 바랍니다.'
  },
  { 
    id: 2, 
    tag: '이벤트', 
    title: '하나카드x메가커피 프로모션 안내', 
    date: '2025-01-05',
    author: '김민수',
    views: 189,
    pinned: true,
    content: '1월 한정 메가커피 프로모션을 안내드립니다.\n\n프로모션 기간: 2025년 1월 1일 ~ 1월 31일\n혜택: 하나카드로 결제 시 메가커피 전 메뉴 50% 할인\n조건: 1일 1회 한정\n\n고객 문의 시 위 내용을 정확히 안내해주시기 바랍니다.'
  },
  { 
    id: 3, 
    tag: '시스템', 
    title: '신규 상담 시스템 업데이트 안내', 
    date: '2025-01-04',
    author: '관리자',
    views: 312,
    pinned: false,
    content: '2025년 1월 15일부터 새로운 상담 시스템이 적용됩니다.\n\n주요 변경 사항:\n1. AI 기반 실시간 상담 지원 기능 추가\n2. 칸반보드 형태의 문서 검색 시스템\n3. 자동 상담 요약 및 후처리 기능\n\n사전 교육은 1월 10일~12일 진행됩니다.'
  },
  { 
    id: 4, 
    tag: '교육', 
    title: '신규 입사자 온보딩 교육 일정', 
    date: '2025-01-03',
    author: '인사팀',
    views: 156,
    pinned: false,
    content: '2025년 1월 신규 입사자 온보딩 교육 일정을 안내드립니다.\n\n일시: 2025년 1월 20일 ~ 1월 24일 (5일간)\n장소: 본사 교육장 (3층)\n대상: 2025년 1월 입사자 전원\n\n참석 필수이며, 불참 시 사전에 인사팀으로 연락 부탁드립니다.'
  },
  { 
    id: 5, 
    tag: '정책', 
    title: '카드 분실 신고 처리 프로세스 변경', 
    date: '2025-01-02',
    author: '운영팀',
    views: 278,
    pinned: false,
    content: '카드 분실 신고 처리 프로세스가 다음과 같이 변경됩니다.\n\n변경 사항:\n1. 본인 확인 절차 강화 (주민번호 뒷자리 → 생년월일 + 휴대폰 인증)\n2. 법인카드 분실 시 담당자 서면 승인 필수\n3. 재발급 수수료 면제 (기존 5,000원)\n\n시행일: 2025년 2월 1일부터'
  },
  { 
    id: 6, 
    tag: '근무', 
    title: '설 연휴 근무 일정 안내', 
    date: '2025-01-02',
    author: '관리팀',
    views: 201,
    pinned: false,
    content: '2025년 설 연휴 근무 일정을 안내드립니다.\n\n연휴 기간: 2025년 1월 28일 ~ 2월 1일 (5일간)\n근무 인원: 각 팀별 2명씩 순환 근무\n\n근무 희망자는 1월 15일까지 팀장님께 신청 부탁드립니다.'
  },
  { 
    id: 7, 
    tag: '복지', 
    title: '직원 건강검진 실시 안내', 
    date: '2024-12-28',
    author: '복지팀',
    views: 189,
    pinned: false,
    content: '2025년 정기 건강검진을 실시합니다.\n\n기간: 2025년 2월 1일 ~ 2월 28일\n장소: 제휴 병원 (강남세브란스, 서울아산병원 등)\n대상: 전 직원\n\n예약은 복지팀으로 연락 주시기 바랍니다.'
  },
  { 
    id: 8, 
    tag: '이벤트', 
    title: '우수 상담사 시상식 개최', 
    date: '2024-12-25',
    author: '관리자',
    views: 245,
    pinned: false,
    content: '2024년 4분기 우수 상담사 시상식을 개최합니다.\n\n일시: 2025년 1월 31일 오후 3시\n장소: 본사 대강당\n수상 대상: FCR 95% 이상 달성자, 고객 만족도 최우수자\n\n많은 참석 부탁드립니다.'
  },
  { 
    id: 9, 
    tag: '시스템', 
    title: '서버 점검으로 인한 일시 중단 안내', 
    date: '2024-12-20',
    author: '기술팀',
    views: 167,
    pinned: false,
    content: '정기 서버 점검으로 인해 시스템이 일시 중단됩니다.\n\n일시: 2025년 1월 10일 오전 2시 ~ 4시\n영향: 상담 시스템, 문서 검색 시스템 일시 중단\n\n점검 시간 동안 상담 불가하오니 양해 부탁드립니다.'
  },
  { 
    id: 10, 
    tag: '교육', 
    title: 'FCR 향상 워크샵 참가 신청', 
    date: '2024-12-18',
    author: '교육팀',
    views: 198,
    pinned: false,
    content: 'FCR 향상을 위한 워크샵을 개최합니다.\n\n일시: 2025년 1월 25일 오후 2시 ~ 5시\n장소: 본사 세미나실\n내용: FCR 향상 기법, 우수 사례 공유, Q&A\n\n참가 희망자는 1월 20일까지 신청 부탁드립니다.'
  },
  { 
    id: 11, 
    tag: '정책', 
    title: '고객 정보 보호 강화 정책 시행', 
    date: '2024-12-15',
    author: '법무팀',
    views: 289,
    pinned: false,
    content: '고객 정보 보호 강화 정책이 시행됩니다.\n\n주요 내용:\n1. 고객 정보 조회 시 2단계 인증 필수\n2. 통화 녹음 파일 보관 기간 단축 (3년 → 1년)\n3. 개인정보 유출 시 즉시 보고 의무화\n\n시행일: 2025년 1월 1일부터'
  },
  { 
    id: 12, 
    tag: '근무', 
    title: '재택근무 확대 시행 안내', 
    date: '2024-12-10',
    author: '인사팀',
    views: 234,
    pinned: false,
    content: '재택근무 제도가 확대 시행됩니다.\n\n변경 사항:\n- 기존: 주 1회 → 변경: 주 2회\n- 신청 방법: 전날 오후 5시까지 팀장 승인\n\n시행일: 2025년 1월 1일부터'
  },
  { 
    id: 13, 
    tag: '복지', 
    title: '사내 카페테리아 메뉴 개편', 
    date: '2024-12-05',
    author: '복지팀',
    views: 145,
    pinned: false,
    content: '사내 카페테리아 메뉴가 개편됩니다.\n\n변경 사항:\n- 건강식 메뉴 추가 (샐러드, 그릭요거트 등)\n- 채식 메뉴 강화\n- 디저트 종류 확대\n\n시행일: 2025년 1월 1일부터'
  },
  { 
    id: 14, 
    tag: '이벤트', 
    title: '연말 송년회 개최 안내', 
    date: '2024-12-01',
    author: '관리팀',
    views: 312,
    pinned: false,
    content: '2024년 연말 송년회를 개최합니다.\n\n일시: 2024년 12월 27일 오후 7시\n장소: 강남 ○○호텔 그랜드볼룸\n드레스코드: 비즈니스 캐주얼\n\n참석 여부는 12월 15일까지 회신 부탁드립니다.'
  },
  { 
    id: 15, 
    tag: '교육', 
    title: 'AI 상담 시스템 활용 교육', 
    date: '2024-11-28',
    author: '교육팀',
    views: 267,
    pinned: false,
    content: 'AI 상담 시스템 활용 교육을 진행합니다.\n\n일시: 2025년 1월 10일 ~ 12일 (3일간)\n시간: 오전 10시 ~ 12시\n대상: 전 상담사\n내용: AI 칸반보드 사용법, AI 어시스턴트 활용법\n\n필수 참석이며, 불참 시 사전 연락 부탁드립니다.'
  }
];

// ==================== 상담 내역 데이터 ====================
// agent 필드를 agent_id로 변경 (DB 스키마와 일치)
export const consultationsData = [
  { id: 'CS-20250105-1432', agent_id: 'EMP-001', customer: '김민수', category: '카드분실', status: '완료', content: '카드 분실 신고 접수 및 즉시 정지 처리. 재발급 신청 완료', datetime: '2025-01-05 14:32', duration: '05:12', isBestPractice: true, fcr: true, memo: '카드 분실 신고 및 재발급 처리 완료. 고객 만족도 높음' },
  { id: 'CS-20250105-1315', agent_id: 'EMP-019', customer: '박철수', category: '해외결제', status: '진행중', content: '해외 결제 차단 해제 요청. 본인 확인 및 추가 서류 확인 중', datetime: '2025-01-05 13:15', duration: '07:45', isBestPractice: false, fcr: false, memo: '해외 결제 차단 해제 요청 처리 중. 추가 서류 대기' },
  { id: 'CS-20250105-1205', agent_id: 'EMP-002', customer: '최영수', category: '수수료문의', status: '완료', content: '연회비 수수료 환불 조건 안내 및 처리 방법 설명', datetime: '2025-01-05 12:05', duration: '04:30', isBestPractice: false, fcr: true, memo: '연회비 수수료 환불 안내 완료' },
  { id: 'CS-20250105-1120', agent_id: 'EMP-001', customer: '강민지', category: '카드분실', status: '미완료', content: '카드 분실 신고 접수 후 고객 요청으로 보류 상태', datetime: '2025-01-05 11:20', duration: '03:20', isBestPractice: false, fcr: false, memo: '고객 요청으로 보류. 내일 재연락 예정' },
  { id: 'CS-20250105-1045', agent_id: 'EMP-022', customer: '윤서연', category: '해외결제', status: '완료', content: '해외 결제 승인 처리 및 사용 가능 국가 안내', datetime: '2025-01-05 10:45', duration: '06:15', isBestPractice: true, fcr: true, memo: '해외 결제 승인 처리 완료. 우수 상담 사례' },
  { id: 'CS-20250105-0950', agent_id: 'EMP-019', customer: '정수진', category: '기타', status: '완료', content: '일반 문의 사항 응대 및 해결', datetime: '2025-01-05 09:50', duration: '05:50', isBestPractice: false, fcr: true, memo: '일반 문의 응대 완료' },
  { id: 'CS-20250104-1650', agent_id: 'EMP-002', customer: '윤서연', category: '카드분실', status: '완료', content: '카드 재발급 신청 접수 및 배송 주소 확인', datetime: '2025-01-04 16:50', duration: '04:15', isBestPractice: false, fcr: true, memo: '카드 재발급 신청 접수 완료' },
  { id: 'CS-20250104-1520', agent_id: 'EMP-021', customer: '손흥민', category: '프로모션', status: '완료', content: '신규 프로모션 혜택 및 참여 방법 상세 안내', datetime: '2025-01-04 15:20', duration: '03:45', isBestPractice: false, fcr: true, memo: '신규 프로모션 상세 안내' },
  { id: 'CS-20250104-1340', agent_id: 'EMP-003', customer: '이강인', category: '수수료문의', status: '완료', content: '수수료 정책 및 면제 조건 상세 설명', datetime: '2025-01-04 13:40', duration: '05:00', isBestPractice: false, fcr: false, memo: '수수료 정책 상세 설명' },
  { id: 'CS-20250104-1115', agent_id: 'EMP-020', customer: '박지성', category: '해외결제', status: '완료', content: '해외 사용 설정 완료 및 이용 가능 국가 안내', datetime: '2025-01-04 11:15', duration: '04:50', isBestPractice: false, fcr: true, memo: '해외 사용 설정 완료' },
  { id: 'CS-20250104-1020', agent_id: 'EMP-034', customer: '조현우', category: '포인트', status: '완료', content: '포인트 적립 내역 확인 및 사용 방법 안내', datetime: '2025-01-04 10:20', duration: '03:30', isBestPractice: false, fcr: true, memo: '포인트 적립 및 사용 안내' },
  { id: 'CS-20250104-0935', agent_id: 'EMP-040', customer: '황희찬', category: '한도조회', status: '완료', content: '일시불 한도 조회 및 증액 신청 절차 안내', datetime: '2025-01-04 09:35', duration: '04:10', isBestPractice: false, fcr: true, memo: '일시불 한도 조회 및 증액 안내' },
  { id: 'CS-20250103-1710', agent_id: 'EMP-023', customer: '백승호', category: '카드분실', status: '완료', content: '긴급 카드 정지 처리 및 재발급 신청 접수', datetime: '2025-01-03 17:10', duration: '05:20', isBestPractice: false, fcr: true, memo: '긴급 카드 정지 및 재발급 처리' },
  { id: 'CS-20250103-1545', agent_id: 'EMP-036', customer: '김영권', category: '프로모션', status: '완료', content: '이벤트 참여 방법 및 혜택 상세 안내', datetime: '2025-01-03 15:45', duration: '03:55', isBestPractice: false, fcr: true, memo: '이벤트 참여 방법 안내' },
  { id: 'CS-20250103-1420', agent_id: 'EMP-026', customer: '정우영', category: '해외결제', status: '진행중', content: '해외 가맹점 결제 오류 원인 조사 중', datetime: '2025-01-03 14:20', duration: '06:30', isBestPractice: false, fcr: false, memo: '해외 가맹점 결제 오류 조사 중' },
  { id: 'CS-20250103-1310', agent_id: 'EMP-008', customer: '나상호', category: '포인트', status: '완료', content: '적립 포인트 사용 가능 가맹점 및 조건 안내', datetime: '2025-01-03 13:10', duration: '04:22', isBestPractice: false, fcr: true, memo: '적립 포인트 사용 가능 가맹점 안내' },
  { id: 'CS-20250103-1155', agent_id: 'EMP-015', customer: '김진수', category: '한도조회', status: '완료', content: '카드 한도 증액 신청 접수 및 심사 안내', datetime: '2025-01-03 11:55', duration: '03:48', isBestPractice: false, fcr: true, memo: '카드 한도 증액 신청 접수' },
  { id: 'CS-20250103-1030', agent_id: 'EMP-021', customer: '황인범', category: '수수료문의', status: '완료', content: '해외 사용 수수료 정책 및 면제 조건 설명', datetime: '2025-01-03 10:30', duration: '05:35', isBestPractice: false, fcr: true, memo: '해외 사용 수수료 정책 설명' },
  { id: 'CS-20250102-1725', agent_id: 'EMP-035', customer: '권경원', category: '기타', status: '완료', content: '결제일 변경 요청 처리 및 변경 완료', datetime: '2025-01-02 17:25', duration: '04:05', isBestPractice: false, fcr: true, memo: '결제일 변경 요청 처리 완료' },
  { id: 'CS-20250102-1540', agent_id: 'EMP-037', customer: '이영표', category: '프로모션', status: '완료', content: '신년 이벤트 참여 방법 및 혜택 상세 안내', datetime: '2025-01-02 15:40', duration: '03:28', isBestPractice: false, fcr: true, memo: '신년 이벤트 참여 방법 상세 안내' },
  { id: 'CS-20250102-1435', agent_id: 'EMP-038', customer: '박서준', category: '카드분실', status: '완료', content: '긴급 카드 정지 처리 및 임시 카드 발급 안내', datetime: '2025-01-02 14:35', duration: '05:42', isBestPractice: false, fcr: true, memo: '긴급 카드 정지 및 임시 카드 발급' },
  { id: 'CS-20250102-1320', agent_id: 'EMP-039', customer: '김수현', category: '해외결제', status: '완료', content: '해외 결제 실패 원인 분석 및 해결 방안 제시', datetime: '2025-01-02 13:20', duration: '06:18', isBestPractice: false, fcr: false, memo: '해외 결제 실패 원인 분석 및 해결' },
  { id: 'CS-20250102-1205', agent_id: 'EMP-041', customer: '송중기', category: '포인트', status: '완료', content: '포인트 소멸 예정 안내 및 사용 권유', datetime: '2025-01-02 12:05', duration: '04:12', isBestPractice: false, fcr: true, memo: '포인트 소멸 예정 안내 및 사용 권유' },
  { id: 'CS-20250102-1050', agent_id: 'EMP-042', customer: '이민호', category: '한도조회', status: '완료', content: '일시불 한도 확인 및 이용 가능 금액 안내', datetime: '2025-01-02 10:50', duration: '03:55', isBestPractice: false, fcr: true, memo: '일시불 한도 확인 및 안내' },
  { id: 'CS-20250102-0935', agent_id: 'EMP-043', customer: '유재석', category: '수수료문의', status: '완료', content: '카드 대금 연체 수수료 정책 및 납부 방법 안내', datetime: '2025-01-02 09:35', duration: '05:08', isBestPractice: false, fcr: true, memo: '카드 대금 연체 수수료 안내' },
];

// ==================== 자주 찾는 문의 데이터 ====================
export const frequentInquiriesData = [
  { id: 1, keyword: '카드 분실', question: '카드를 분실했어요. 어떻게 해야 하나요?', count: 45, trend: 'up' as const },
  { id: 2, keyword: '해외 결제', question: '해외에서 카드가 안 됩니다.', count: 38, trend: 'up' as const },
  { id: 3, keyword: '포인트 적립', question: '포인트가 적립 안 됐어요.', count: 32, trend: 'same' as const },
  { id: 4, keyword: '연회비 환불', question: '연회비 환불 받을 수 있나요?', count: 28, trend: 'down' as const },
  { id: 5, keyword: '한도 증액', question: '신용한도를 올리고 싶어요.', count: 25, trend: 'up' as const },
];

// ==================== 사원 데이터 (총 45명: 상담1팀 18명, 상담2팀 15명, 상담3팀 12명) ====================
// 순위 기준: 1) consultations 높은 순, 2) fcr 높은 순, 3) avgTime 빠른 순
export const employeesData = [
  // 🥇 1위: 김민수 (상담1팀) - 145건, FCR 96%, 4:15
  { id: 'EMP-002', name: '김민수', team: '상담1팀', position: '사원', consultations: 145, fcr: 96, avgTime: '4:15', rank: 1, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-01', email: 'kim@teddycard.com', phone: '010-2345-6789' },
  
  // 🥈 2위: 최은정 (상담3팀) - 140건, FCR 96%, 4:18
  { id: 'EMP-034', name: '최은정', team: '상담3팀', position: '대리', consultations: 140, fcr: 96, avgTime: '4:18', rank: 2, trend: 'up' as const, status: 'active' as const, joinDate: '2023-07-15', email: 'choiej@teddycard.com', phone: '010-2345-6701' },
  
  // 🥉 3위: 이영희 (상담2팀) - 138건, FCR 95%, 4:20
  { id: 'EMP-019', name: '이영희', team: '상담2팀', position: '대리', consultations: 138, fcr: 95, avgTime: '4:20', rank: 3, trend: 'same' as const, status: 'active' as const, joinDate: '2023-11-20', email: 'lee@teddycard.com', phone: '010-3456-7890' },
  
  // 4위: 이영표 (상담1팀) - 135건, FCR 95%, 4:28
  { id: 'EMP-018', name: '이영표', team: '상담1팀', position: '과장', consultations: 135, fcr: 95, avgTime: '4:28', rank: 4, trend: 'up' as const, status: 'active' as const, joinDate: '2023-03-12', email: 'leeyp@teddycard.com', phone: '010-3456-7801' },
  
  // 5위: 강민지 (상담2팀) - 134건, FCR 94%, 4:25
  { id: 'EMP-021', name: '강민지', team: '상담2팀', position: '대리', consultations: 134, fcr: 94, avgTime: '4:25', rank: 5, trend: 'up' as const, status: 'active' as const, joinDate: '2023-09-12', email: 'kang@teddycard.com', phone: '010-7890-1234' },
  
  // 6위: 문성민 (상담3팀) - 133건, FCR 95%, 4:30
  { id: 'EMP-040', name: '문성민', team: '상담3팀', position: '과장', consultations: 133, fcr: 95, avgTime: '4:30', rank: 6, trend: 'up' as const, status: 'active' as const, joinDate: '2023-06-18', email: 'moonsm@teddycard.com', phone: '010-8901-2367' },
  
  // 7위: 손흥민 (상담2팀) - 132건, FCR 93%, 4:35
  { id: 'EMP-023', name: '손흥민', team: '상담2팀', position: '대리', consultations: 132, fcr: 93, avgTime: '4:35', rank: 7, trend: 'up' as const, status: 'active' as const, joinDate: '2023-12-10', email: 'son@teddycard.com', phone: '010-1234-5679' },
  
  // 8위: 서지은 (상담3팀) - 131건, FCR 94%, 4:33
  { id: 'EMP-036', name: '서지은', team: '상담3팀', position: '사원', consultations: 131, fcr: 94, avgTime: '4:33', rank: 8, trend: 'up' as const, status: 'active' as const, joinDate: '2023-12-05', email: 'seoje@teddycard.com', phone: '010-4567-8923' },
  
  // 9위: 조현우 (상담1팀) - 130건, FCR 93%, 4:40
  { id: 'EMP-008', name: '조현우', team: '상담1팀', position: '대리', consultations: 130, fcr: 93, avgTime: '4:40', rank: 9, trend: 'up' as const, status: 'active' as const, joinDate: '2023-10-15', email: 'cho@teddycard.com', phone: '010-3456-7891' },
  
  // 10위: 전지현 (상담2팀) - 129건, FCR 94%, 4:42
  { id: 'EMP-026', name: '전지현', team: '상담2팀', position: '대리', consultations: 129, fcr: 94, avgTime: '4:42', rank: 10, trend: 'up' as const, status: 'active' as const, joinDate: '2023-10-08', email: 'jeon@teddycard.com', phone: '010-4567-8923' },
  
  // 11위: 이재성 (상담1팀) - 128건, FCR 94%, 4:38
  { id: 'EMP-015', name: '이재성', team: '상담1팀', position: '대리', consultations: 128, fcr: 94, avgTime: '4:38', rank: 11, trend: 'up' as const, status: 'active' as const, joinDate: '2023-09-20', email: 'leejs@teddycard.com', phone: '010-0123-4568' },
  
  // 12위: 유진희 (상담3팀) - 128건, FCR 93%, 4:41
  { id: 'EMP-044', name: '유진희', team: '상담3팀', position: '대리', consultations: 128, fcr: 93, avgTime: '4:41', rank: 12, trend: 'up' as const, status: 'active' as const, joinDate: '2023-09-22', email: 'yujh@teddycard.com', phone: '010-2345-6701' },
  
  // 13위: 홍길동 (상담1팀) - 127건, FCR 94%, 4:32
  { id: 'EMP-001', name: '홍길동', team: '상담1팀', position: '대리', consultations: 127, fcr: 94, avgTime: '4:32', rank: 13, trend: 'up' as const, status: 'active' as const, joinDate: '2024-01-15', email: 'hong@teddycard.com', phone: '010-1234-5678' },
  
  // 14위: 한동훈 (상담3팀) - 127건, FCR 93%, 4:44
  { id: 'EMP-037', name: '한동훈', team: '상담3팀', position: '대리', consultations: 127, fcr: 93, avgTime: '4:44', rank: 14, trend: 'same' as const, status: 'active' as const, joinDate: '2023-10-20', email: 'handh@teddycard.com', phone: '010-5678-9034' },
  
  // 15위: 유재석 (상담2팀) - 126건, FCR 93%, 4:46
  { id: 'EMP-029', name: '유재석', team: '상담2팀', position: '대리', consultations: 126, fcr: 93, avgTime: '4:46', rank: 15, trend: 'up' as const, status: 'active' as const, joinDate: '2023-11-25', email: 'yoo@teddycard.com', phone: '010-7890-1256' },
  
  // 16위: 김영권 (상담1팀) - 125건, FCR 93%, 4:45
  { id: 'EMP-011', name: '김영권', team: '상담1팀', position: '대리', consultations: 125, fcr: 93, avgTime: '4:45', rank: 16, trend: 'up' as const, status: 'active' as const, joinDate: '2023-11-05', email: 'kimyk@teddycard.com', phone: '010-6789-0124' },
  
  // 17위: 정수진 (상담2팀) - 125건, FCR 93%, 4:45 (동점이지만 joinDate가 늦음)
  { id: 'EMP-020', name: '정수진', team: '상담2팀', position: '사원', consultations: 125, fcr: 93, avgTime: '4:45', rank: 17, trend: 'up' as const, status: 'vacation' as const, joinDate: '2024-02-15', email: 'jung2@teddycard.com', phone: '010-5678-9012' },
  
  // 18위: 정민우 (상담3팀) - 124건, FCR 92%, 4:47
  { id: 'EMP-035', name: '정민우', team: '상담3팀', position: '사원', consultations: 124, fcr: 92, avgTime: '4:47', rank: 18, trend: 'up' as const, status: 'active' as const, joinDate: '2024-01-25', email: 'jungmw@teddycard.com', phone: '010-3456-7812' },
  
  // 19위: 김수현 (상담2팀) - 123건, FCR 92%, 4:48
  { id: 'EMP-025', name: '김수현', team: '상담2팀', position: '사원', consultations: 123, fcr: 92, avgTime: '4:48', rank: 19, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-22', email: 'kimsh@teddycard.com', phone: '010-3456-7812' },
  
  // 20위: 강하늘 (상담3팀) - 122건, FCR 92%, 4:49
  { id: 'EMP-041', name: '강하늘', team: '상담3팀', position: '사원', consultations: 122, fcr: 92, avgTime: '4:49', rank: 20, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-11', email: 'kanghn@teddycard.com', phone: '010-9012-3478' },
  
  // 21위: 김태희 (상담2팀) - 122건, FCR 92%, 4:50
  { id: 'EMP-022', name: '김태희', team: '상담2팀', position: '과장', consultations: 122, fcr: 92, avgTime: '4:50', rank: 21, trend: 'up' as const, status: 'active' as const, joinDate: '2023-08-15', email: 'kimth@teddycard.com', phone: '010-9012-3456' },
  
  // 22위: 김진수 (상담1팀) - 121건, FCR 91%, 4:52
  { id: 'EMP-014', name: '김진수', team: '상담1팀', position: '사원', consultations: 121, fcr: 91, avgTime: '4:52', rank: 22, trend: 'up' as const, status: 'active' as const, joinDate: '2024-01-10', email: 'kimjs@teddycard.com', phone: '010-9012-3457' },
  
  // 23위: 신동엽 (상담2팀) - 120건, FCR 91%, 4:55
  { id: 'EMP-031', name: '신동엽', team: '상담2팀', position: '사원', consultations: 120, fcr: 91, avgTime: '4:55', rank: 23, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-07', email: 'shin@teddycard.com', phone: '010-9012-3478' },
  
  // 24위: 백승호 (상담1팀) - 119건, FCR 92%, 4:50
  { id: 'EMP-010', name: '백승호', team: '상담1팀', position: '사원', consultations: 119, fcr: 92, avgTime: '4:50', rank: 24, trend: 'up' as const, status: 'active' as const, joinDate: '2024-02-20', email: 'baek@teddycard.com', phone: '010-5678-9013' },
  
  // 25위: 최영수 (상담1팀) - 118건, FCR 91%, 4:55
  { id: 'EMP-004', name: '최영수', team: '상담1팀', position: '사원', consultations: 118, fcr: 91, avgTime: '4:55', rank: 25, trend: 'same' as const, status: 'active' as const, joinDate: '2024-04-01', email: 'choi@teddycard.com', phone: '010-6789-0123' },
  
  // 26위: 안수진 (상담3팀) - 118건, FCR 91%, 4:56
  { id: 'EMP-038', name: '안수진', team: '상담3팀', position: '사원', consultations: 118, fcr: 91, avgTime: '4:56', rank: 26, trend: 'up' as const, status: 'active' as const, joinDate: '2024-02-12', email: 'ansj@teddycard.com', phone: '010-6789-0145' },
  
  // 27위: 박서준 (상담2팀) - 117건, FCR 91%, 4:58
  { id: 'EMP-024', name: '박서준', team: '상담2팀', position: '사원', consultations: 117, fcr: 91, avgTime: '4:58', rank: 27, trend: 'same' as const, status: 'active' as const, joinDate: '2024-01-18', email: 'parksj@teddycard.com', phone: '010-2345-6701' },
  
  // 28위: 오수아 (상담3팀) - 116건, FCR 90%, 5:02
  { id: 'EMP-042', name: '오수아', team: '상담3팀', position: '사원', consultations: 116, fcr: 90, avgTime: '5:02', rank: 28, trend: 'same' as const, status: 'active' as const, joinDate: '2024-01-30', email: 'ohsa@teddycard.com', phone: '010-0123-4589' },
  
  // 29위: 권경원 (상담1팀) - 116건, FCR 90%, 5:08
  { id: 'EMP-017', name: '권경원', team: '상담1팀', position: '사원', consultations: 116, fcr: 90, avgTime: '5:08', rank: 29, trend: 'same' as const, status: 'active' as const, joinDate: '2024-02-28', email: 'kwon@teddycard.com', phone: '010-2345-6790' },
  
  // 30위: 박지성 (상담1팀) - 115건, FCR 91%, 5:05
  { id: 'EMP-006', name: '박지성', team: '상담1팀', position: '사원', consultations: 115, fcr: 91, avgTime: '5:05', rank: 30, trend: 'same' as const, status: 'active' as const, joinDate: '2024-05-20', email: 'parkjs@teddycard.com', phone: '010-0123-4567' },
  
  // 31위: 이수근 (상담2팀) - 115건, FCR 90%, 5:08
  { id: 'EMP-033', name: '이수근', team: '상담2팀', position: '사원', consultations: 115, fcr: 90, avgTime: '5:08', rank: 31, trend: 'same' as const, status: 'active' as const, joinDate: '2024-04-20', email: 'leesg@teddycard.com', phone: '010-1234-5690' },
  
  // 32위: 이민호 (상담2팀) - 114건, FCR 90%, 5:05
  { id: 'EMP-028', name: '이민호', team: '상담2팀', position: '사원', consultations: 114, fcr: 90, avgTime: '5:05', rank: 32, trend: 'same' as const, status: 'active' as const, joinDate: '2024-02-09', email: 'leemh@teddycard.com', phone: '010-6789-0145' },
  
  // 33위: 정우영 (상담1팀) - 113건, FCR 90%, 5:00
  { id: 'EMP-012', name: '정우영', team: '상담1팀', position: '사원', consultations: 113, fcr: 90, avgTime: '5:00', rank: 33, trend: 'same' as const, status: 'active' as const, joinDate: '2024-03-15', email: 'jung@teddycard.com', phone: '010-7890-1235' },
  
  // 34위: 박철수 (상담1팀) - 112건, FCR 92%, 5:10
  { id: 'EMP-003', name: '박철수', team: '상담1팀', position: '과장', consultations: 112, fcr: 92, avgTime: '5:10', rank: 34, trend: 'down' as const, status: 'active' as const, joinDate: '2023-05-10', email: 'park@teddycard.com', phone: '010-4567-8901' },
  
  // 35위: 배지현 (상담3팀) - 112건, FCR 89%, 5:11
  { id: 'EMP-039', name: '배지현', team: '상담3팀', position: '사원', consultations: 112, fcr: 89, avgTime: '5:11', rank: 35, trend: 'down' as const, status: 'active' as const, joinDate: '2024-04-08', email: 'baejh@teddycard.com', phone: '010-7890-1256' },
  
  // 36위: 송중기 (상담2팀) - 111건, FCR 89%, 5:12
  { id: 'EMP-027', name: '송중기', team: '상담2팀', position: '사원', consultations: 111, fcr: 89, avgTime: '5:12', rank: 36, trend: 'down' as const, status: 'active' as const, joinDate: '2024-04-14', email: 'song@teddycard.com', phone: '010-5678-9034' },
  
  // 37위: 김채원 (상담3팀) - 110건, FCR 89%, 5:14
  { id: 'EMP-045', name: '김채원', team: '상담3팀', position: '사원', consultations: 110, fcr: 89, avgTime: '5:14', rank: 37, trend: 'down' as const, status: 'active' as const, joinDate: '2024-06-08', email: 'kimcw@teddycard.com', phone: '010-3456-7812' },
  
  // 38위: 이강인 (상담1팀) - 110건, FCR 89%, 5:15
  { id: 'EMP-007', name: '이강인', team: '상담1팀', position: '사원', consultations: 110, fcr: 89, avgTime: '5:15', rank: 38, trend: 'down' as const, status: 'active' as const, joinDate: '2024-06-01', email: 'leekg@teddycard.com', phone: '010-2345-6780' },
  
  // 39위: 강호동 (상담2팀) - 109건, FCR 88%, 5:22
  { id: 'EMP-030', name: '강호동', team: '상담2팀', position: '사원', consultations: 109, fcr: 88, avgTime: '5:22', rank: 39, trend: 'down' as const, status: 'active' as const, joinDate: '2024-05-30', email: 'kanghd@teddycard.com', phone: '010-8901-2367' },
  
  // 40위: 윤서연 (상담1팀) - 108건, FCR 90%, 5:20
  { id: 'EMP-005', name: '윤서연', team: '상담1팀', position: '사원', consultations: 108, fcr: 90, avgTime: '5:20', rank: 40, trend: 'down' as const, status: 'inactive' as const, joinDate: '2024-01-20', email: 'yoon@teddycard.com', phone: '010-8901-2345' },
  
  // 41위: 임윤아 (상담3팀) - 108건, FCR 88%, 5:20
  { id: 'EMP-043', name: '임윤아', team: '상담3팀', position: '사원', consultations: 108, fcr: 88, avgTime: '5:20', rank: 41, trend: 'down' as const, status: 'active' as const, joinDate: '2024-05-17', email: 'imya@teddycard.com', phone: '010-1234-5690' },
  
  // 42위: 나상호 (상담1팀) - 107건, FCR 89%, 5:18
  { id: 'EMP-013', name: '나상호', team: '상담1팀', position: '사원', consultations: 107, fcr: 89, avgTime: '5:18', rank: 42, trend: 'down' as const, status: 'active' as const, joinDate: '2024-04-25', email: 'na@teddycard.com', phone: '010-8901-2346' },
  
  // 43위: 김희철 (상담2팀) - 106건, FCR 87%, 5:28
  { id: 'EMP-032', name: '김희철', team: '상담2팀', position: '사원', consultations: 106, fcr: 87, avgTime: '5:28', rank: 43, trend: 'down' as const, status: 'active' as const, joinDate: '2024-06-15', email: 'kimhc@teddycard.com', phone: '010-0123-4589' },
  
  // 44위: 황희찬 (상담1팀) - 105건, FCR 88%, 5:25
  { id: 'EMP-009', name: '황희찬', team: '상담1팀', position: '사원', consultations: 105, fcr: 88, avgTime: '5:25', rank: 44, trend: 'down' as const, status: 'active' as const, joinDate: '2024-07-10', email: 'hwang@teddycard.com', phone: '010-4567-8902' },
  
  // 45위: 황인범 (상담1팀) - 102건, FCR 87%, 5:30
  { id: 'EMP-016', name: '황인범', team: '상담1팀', position: '사원', consultations: 102, fcr: 87, avgTime: '5:30', rank: 45, trend: 'down' as const, status: 'active' as const, joinDate: '2024-05-05', email: 'hwangib@teddycard.com', phone: '010-1234-5679' },
  
  // ==================== 🆕 신규 사원 5명 (EMP-046 ~ EMP-050) ====================
  // 46위: 배상준 (상담2팀) - 100건, FCR 87%, 5:32
  { id: 'EMP-046', name: '배상준', team: '상담2팀', position: '사원', consultations: 100, fcr: 87, avgTime: '5:32', rank: 46, trend: 'up' as const, status: 'active' as const, joinDate: '2024-08-01', email: 'baesj@teddycard.com', phone: '010-2468-1357' },
  
  // 47위: 박소희 (상담3팀) - 98건, FCR 86%, 5:35
  { id: 'EMP-047', name: '박소희', team: '상담3팀', position: '사원', consultations: 98, fcr: 86, avgTime: '5:35', rank: 47, trend: 'up' as const, status: 'active' as const, joinDate: '2024-08-15', email: 'parksh@teddycard.com', phone: '010-3579-2468' },
  
  // 48위: 안수이 (상담1팀) - 95건, FCR 85%, 5:38
  { id: 'EMP-048', name: '안수이', team: '상담1팀', position: '사원', consultations: 95, fcr: 85, avgTime: '5:38', rank: 48, trend: 'up' as const, status: 'active' as const, joinDate: '2024-09-01', email: 'ansi@teddycard.com', phone: '010-4680-3579' },
  
  // 49위: 오흥재 (상담2팀) - 92건, FCR 84%, 5:42
  { id: 'EMP-049', name: '오흥재', team: '상담2팀', position: '사원', consultations: 92, fcr: 84, avgTime: '5:42', rank: 49, trend: 'up' as const, status: 'active' as const, joinDate: '2024-09-15', email: 'ohhj@teddycard.com', phone: '010-5791-4680' },
  
  // 50위: 왕혁준 (상담3팀) - 88건, FCR 83%, 5:45
  { id: 'EMP-050', name: '왕혁준', team: '상담3팀', position: '사원', consultations: 88, fcr: 83, avgTime: '5:45', rank: 50, trend: 'up' as const, status: 'active' as const, joinDate: '2024-10-01', email: 'wanghj@teddycard.com', phone: '010-6802-5791' },
];

// ==================== 시뮬레이션 데이터 ====================
export const simulationsData = [
  { id: 1, title: '카드 분실 신고 및 재발급', category: '기본 상담', difficulty: '초급', duration: '5분', icon: 'Target' as const, color: '#34A853' },
  { id: 2, title: '해외 결제 차단 해제 요청', category: '긴급 처리', difficulty: '중급', duration: '7분', icon: 'Shield' as const, color: '#FBBC04' },
  { id: 3, title: '진상 고객 감정 전환 마스터', category: '민원 대응', difficulty: '고급', duration: '12분', icon: 'Users' as const, color: '#EA4335' },
  { id: 4, title: '크로스셀 영업 스킬 실전', category: '영업 스킬', difficulty: '중급', duration: '8분', icon: 'TrendingUp' as const, color: '#0047AB' },
];