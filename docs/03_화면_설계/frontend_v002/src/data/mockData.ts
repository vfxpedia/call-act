// ==================== 사원 데이터 (총 45명: 상담1팀 18명, 상담2팀 15명, 상담3팀 12명) ====================
export const employeesData = [
  // 상담1팀 (18명)
  { id: 'EMP-001', name: '홍길동', team: '상담1팀', position: '대리', consultations: 127, fcr: 94, avgTime: '4:32', rank: 7, trend: 'up' as const, status: 'active' as const, joinDate: '2024-01-15', email: 'hong@example.com', phone: '010-1234-5678' },
  { id: 'EMP-002', name: '김민수', team: '상담1팀', position: '사원', consultations: 145, fcr: 96, avgTime: '4:15', rank: 1, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-01', email: 'kim@example.com', phone: '010-2345-6789' },
  { id: 'EMP-003', name: '박철수', team: '상담1팀', position: '과장', consultations: 112, fcr: 92, avgTime: '5:10', rank: 11, trend: 'down' as const, status: 'active' as const, joinDate: '2023-05-10', email: 'park@example.com', phone: '010-4567-8901' },
  { id: 'EMP-004', name: '최영수', team: '상담1팀', position: '사원', consultations: 118, fcr: 91, avgTime: '4:55', rank: 10, trend: 'same' as const, status: 'active' as const, joinDate: '2024-04-01', email: 'choi@example.com', phone: '010-6789-0123' },
  { id: 'EMP-005', name: '윤서연', team: '상담1팀', position: '사원', consultations: 108, fcr: 90, avgTime: '5:20', rank: 16, trend: 'down' as const, status: 'inactive' as const, joinDate: '2024-01-20', email: 'yoon@example.com', phone: '010-8901-2345' },
  { id: 'EMP-006', name: '박지성', team: '상담1팀', position: '사원', consultations: 115, fcr: 91, avgTime: '5:05', rank: 13, trend: 'same' as const, status: 'active' as const, joinDate: '2024-05-20', email: 'parkjs@example.com', phone: '010-0123-4567' },
  { id: 'EMP-007', name: '이강인', team: '상담1팀', position: '사원', consultations: 110, fcr: 89, avgTime: '5:15', rank: 15, trend: 'down' as const, status: 'active' as const, joinDate: '2024-06-01', email: 'leekg@example.com', phone: '010-2345-6780' },
  { id: 'EMP-008', name: '조현우', team: '상담1팀', position: '대리', consultations: 130, fcr: 93, avgTime: '4:40', rank: 6, trend: 'up' as const, status: 'active' as const, joinDate: '2023-10-15', email: 'cho@example.com', phone: '010-3456-7891' },
  { id: 'EMP-009', name: '황희찬', team: '상담1팀', position: '사원', consultations: 105, fcr: 88, avgTime: '5:25', rank: 18, trend: 'down' as const, status: 'active' as const, joinDate: '2024-07-10', email: 'hwang@example.com', phone: '010-4567-8902' },
  { id: 'EMP-010', name: '백승호', team: '상담1팀', position: '사원', consultations: 119, fcr: 92, avgTime: '4:50', rank: 9, trend: 'up' as const, status: 'active' as const, joinDate: '2024-02-20', email: 'baek@example.com', phone: '010-5678-9013' },
  { id: 'EMP-011', name: '김영권', team: '상담1팀', position: '대리', consultations: 125, fcr: 93, avgTime: '4:45', rank: 8, trend: 'up' as const, status: 'active' as const, joinDate: '2023-11-05', email: 'kimyk@example.com', phone: '010-6789-0124' },
  { id: 'EMP-012', name: '정우영', team: '상담1팀', position: '사원', consultations: 113, fcr: 90, avgTime: '5:00', rank: 14, trend: 'same' as const, status: 'active' as const, joinDate: '2024-03-15', email: 'jung@example.com', phone: '010-7890-1235' },
  { id: 'EMP-013', name: '나상호', team: '상담1팀', position: '사원', consultations: 107, fcr: 89, avgTime: '5:18', rank: 17, trend: 'down' as const, status: 'active' as const, joinDate: '2024-04-25', email: 'na@example.com', phone: '010-8901-2346' },
  { id: 'EMP-014', name: '김진수', team: '상담1팀', position: '사원', consultations: 121, fcr: 91, avgTime: '4:52', rank: 12, trend: 'up' as const, status: 'active' as const, joinDate: '2024-01-10', email: 'kimjs@example.com', phone: '010-9012-3457' },
  { id: 'EMP-015', name: '이재성', team: '상담1팀', position: '대리', consultations: 128, fcr: 94, avgTime: '4:38', rank: 5, trend: 'up' as const, status: 'active' as const, joinDate: '2023-09-20', email: 'leejs@example.com', phone: '010-0123-4568' },
  { id: 'EMP-016', name: '황인범', team: '상담1팀', position: '사원', consultations: 102, fcr: 87, avgTime: '5:30', rank: 19, trend: 'down' as const, status: 'active' as const, joinDate: '2024-05-05', email: 'hwangib@example.com', phone: '010-1234-5679' },
  { id: 'EMP-017', name: '권경원', team: '상담1팀', position: '사원', consultations: 116, fcr: 90, avgTime: '5:08', rank: 12, trend: 'same' as const, status: 'active' as const, joinDate: '2024-02-28', email: 'kwon@example.com', phone: '010-2345-6790' },
  { id: 'EMP-018', name: '이영표', team: '상담1팀', position: '과장', consultations: 135, fcr: 95, avgTime: '4:28', rank: 4, trend: 'up' as const, status: 'active' as const, joinDate: '2023-03-12', email: 'leeyp@example.com', phone: '010-3456-7801' },
  
  // 상담2팀 (15명)
  { id: 'EMP-019', name: '이영희', team: '상담2팀', position: '대리', consultations: 138, fcr: 95, avgTime: '4:20', rank: 3, trend: 'same' as const, status: 'active' as const, joinDate: '2023-11-20', email: 'lee@example.com', phone: '010-3456-7890' },
  { id: 'EMP-020', name: '정수진', team: '상담2팀', position: '사원', consultations: 125, fcr: 93, avgTime: '4:45', rank: 8, trend: 'up' as const, status: 'vacation' as const, joinDate: '2024-02-15', email: 'jung2@example.com', phone: '010-5678-9012' },
  { id: 'EMP-021', name: '강민지', team: '상담2팀', position: '대리', consultations: 134, fcr: 94, avgTime: '4:25', rank: 5, trend: 'up' as const, status: 'active' as const, joinDate: '2023-09-12', email: 'kang@example.com', phone: '010-7890-1234' },
  { id: 'EMP-022', name: '김태희', team: '상담2팀', position: '과장', consultations: 122, fcr: 92, avgTime: '4:50', rank: 9, trend: 'up' as const, status: 'active' as const, joinDate: '2023-08-15', email: 'kimth@example.com', phone: '010-9012-3456' },
  { id: 'EMP-023', name: '손흥민', team: '상담2팀', position: '대리', consultations: 132, fcr: 93, avgTime: '4:35', rank: 6, trend: 'up' as const, status: 'active' as const, joinDate: '2023-12-10', email: 'son@example.com', phone: '010-1234-5679' },
  { id: 'EMP-024', name: '박서준', team: '상담2팀', position: '사원', consultations: 117, fcr: 91, avgTime: '4:58', rank: 11, trend: 'same' as const, status: 'active' as const, joinDate: '2024-01-18', email: 'parksj@example.com', phone: '010-2345-6701' },
  { id: 'EMP-025', name: '김수현', team: '상담2팀', position: '사원', consultations: 123, fcr: 92, avgTime: '4:48', rank: 10, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-22', email: 'kimsh@example.com', phone: '010-3456-7812' },
  { id: 'EMP-026', name: '전지현', team: '상담2팀', position: '대리', consultations: 129, fcr: 94, avgTime: '4:42', rank: 7, trend: 'up' as const, status: 'active' as const, joinDate: '2023-10-08', email: 'jeon@example.com', phone: '010-4567-8923' },
  { id: 'EMP-027', name: '송중기', team: '상담2팀', position: '사원', consultations: 111, fcr: 89, avgTime: '5:12', rank: 15, trend: 'down' as const, status: 'active' as const, joinDate: '2024-04-14', email: 'song@example.com', phone: '010-5678-9034' },
  { id: 'EMP-028', name: '이민호', team: '상담2팀', position: '사원', consultations: 114, fcr: 90, avgTime: '5:05', rank: 14, trend: 'same' as const, status: 'active' as const, joinDate: '2024-02-09', email: 'leemh@example.com', phone: '010-6789-0145' },
  { id: 'EMP-029', name: '유재석', team: '상담2팀', position: '대리', consultations: 126, fcr: 93, avgTime: '4:46', rank: 9, trend: 'up' as const, status: 'active' as const, joinDate: '2023-11-25', email: 'yoo@example.com', phone: '010-7890-1256' },
  { id: 'EMP-030', name: '강호동', team: '상담2팀', position: '사원', consultations: 109, fcr: 88, avgTime: '5:22', rank: 16, trend: 'down' as const, status: 'active' as const, joinDate: '2024-05-30', email: 'kanghd@example.com', phone: '010-8901-2367' },
  { id: 'EMP-031', name: '신동엽', team: '상담2팀', position: '사원', consultations: 120, fcr: 91, avgTime: '4:55', rank: 11, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-07', email: 'shin@example.com', phone: '010-9012-3478' },
  { id: 'EMP-032', name: '김희철', team: '상담2팀', position: '사원', consultations: 106, fcr: 87, avgTime: '5:28', rank: 17, trend: 'down' as const, status: 'active' as const, joinDate: '2024-06-15', email: 'kimhc@example.com', phone: '010-0123-4589' },
  { id: 'EMP-033', name: '이수근', team: '상담2팀', position: '사원', consultations: 115, fcr: 90, avgTime: '5:08', rank: 13, trend: 'same' as const, status: 'active' as const, joinDate: '2024-04-20', email: 'leesg@example.com', phone: '010-1234-5690' },

  // 상담3팀 (12명)
  { id: 'EMP-034', name: '최은정', team: '상담3팀', position: '대리', consultations: 140, fcr: 96, avgTime: '4:18', rank: 2, trend: 'up' as const, status: 'active' as const, joinDate: '2023-07-15', email: 'choiej@example.com', phone: '010-2345-6701' },
  { id: 'EMP-035', name: '정민우', team: '상담3팀', position: '사원', consultations: 124, fcr: 92, avgTime: '4:47', rank: 10, trend: 'up' as const, status: 'active' as const, joinDate: '2024-01-25', email: 'jungmw@example.com', phone: '010-3456-7812' },
  { id: 'EMP-036', name: '서지은', team: '상담3팀', position: '사원', consultations: 131, fcr: 94, avgTime: '4:33', rank: 7, trend: 'up' as const, status: 'active' as const, joinDate: '2023-12-05', email: 'seoje@example.com', phone: '010-4567-8923' },
  { id: 'EMP-037', name: '한동훈', team: '상담3팀', position: '대리', consultations: 127, fcr: 93, avgTime: '4:44', rank: 8, trend: 'same' as const, status: 'active' as const, joinDate: '2023-10-20', email: 'handh@example.com', phone: '010-5678-9034' },
  { id: 'EMP-038', name: '안수진', team: '상담3팀', position: '사원', consultations: 118, fcr: 91, avgTime: '4:56', rank: 11, trend: 'up' as const, status: 'active' as const, joinDate: '2024-02-12', email: 'ansj@example.com', phone: '010-6789-0145' },
  { id: 'EMP-039', name: '배지현', team: '상담3팀', position: '사원', consultations: 112, fcr: 89, avgTime: '5:11', rank: 14, trend: 'down' as const, status: 'active' as const, joinDate: '2024-04-08', email: 'baejh@example.com', phone: '010-7890-1256' },
  { id: 'EMP-040', name: '문성민', team: '상담3팀', position: '과장', consultations: 133, fcr: 95, avgTime: '4:30', rank: 6, trend: 'up' as const, status: 'active' as const, joinDate: '2023-06-18', email: 'moonsm@example.com', phone: '010-8901-2367' },
  { id: 'EMP-041', name: '강하늘', team: '상담3팀', position: '사원', consultations: 122, fcr: 92, avgTime: '4:49', rank: 10, trend: 'up' as const, status: 'active' as const, joinDate: '2024-03-11', email: 'kanghn@example.com', phone: '010-9012-3478' },
  { id: 'EMP-042', name: '오수아', team: '상담3팀', position: '사원', consultations: 116, fcr: 90, avgTime: '5:02', rank: 12, trend: 'same' as const, status: 'active' as const, joinDate: '2024-01-30', email: 'ohsa@example.com', phone: '010-0123-4589' },
  { id: 'EMP-043', name: '임윤아', team: '상담3팀', position: '사원', consultations: 108, fcr: 88, avgTime: '5:20', rank: 15, trend: 'down' as const, status: 'active' as const, joinDate: '2024-05-17', email: 'imya@example.com', phone: '010-1234-5690' },
  { id: 'EMP-044', name: '유진희', team: '상담3팀', position: '대리', consultations: 128, fcr: 93, avgTime: '4:41', rank: 8, trend: 'up' as const, status: 'active' as const, joinDate: '2023-09-22', email: 'yujh@example.com', phone: '010-2345-6701' },
  { id: 'EMP-045', name: '김채원', team: '상담3팀', position: '사원', consultations: 110, fcr: 89, avgTime: '5:14', rank: 13, trend: 'down' as const, status: 'active' as const, joinDate: '2024-06-08', email: 'kimcw@example.com', phone: '010-3456-7812' },
];

// ==================== 상담 데이터 ====================
export const consultationsData = [
  { id: 'CS-20250105-1432', agent: '홍길동', customer: '김민수', category: '카드분실', status: '완료', datetime: '2025-01-05 14:32', duration: '05:12', isBestPractice: true, fcr: true, memo: '카드 분실 신고 및 재발급 처리 완료. 고객 만족도 높음' },
  { id: 'CS-20250105-1315', agent: '이영희', customer: '박철수', category: '해외결제', status: '진행중', datetime: '2025-01-05 13:15', duration: '07:45', isBestPractice: false, fcr: false, memo: '해외 결제 차단 해제 요청 처리 중. 추가 서류 대기' },
  { id: 'CS-20250105-1205', agent: '김민수', customer: '최영수', category: '수수료문의', status: '완료', datetime: '2025-01-05 12:05', duration: '04:30', isBestPractice: false, fcr: true, memo: '연회비 수수료 환불 안내 완료' },
  { id: 'CS-20250105-1120', agent: '홍길동', customer: '강민지', category: '카드분실', status: '미완료', datetime: '2025-01-05 11:20', duration: '03:20', isBestPractice: false, fcr: false, memo: '고객 요청으로 보류. 내일 재연락 예정' },
  { id: 'CS-20250105-1045', agent: '김태희', customer: '윤서연', category: '해외결제', status: '완료', datetime: '2025-01-05 10:45', duration: '06:15', isBestPractice: true, fcr: true, memo: '해외 결제 승인 처리 완료. 우수 상담 사례' },
  { id: 'CS-20250105-0950', agent: '이영희', customer: '정수진', category: '기타', status: '완료', datetime: '2025-01-05 09:50', duration: '05:50', isBestPractice: false, fcr: true, memo: '일반 문의 응대 완료' },
  { id: 'CS-20250104-1650', agent: '김민수', customer: '윤서연', category: '카드분실', status: '완료', datetime: '2025-01-04 16:50', duration: '04:15', isBestPractice: false, fcr: true, memo: '카드 재발급 신청 접수 완료' },
  { id: 'CS-20250104-1520', agent: '강민지', customer: '손흥민', category: '프로모션', status: '완료', datetime: '2025-01-04 15:20', duration: '03:45', isBestPractice: false, fcr: true, memo: '신규 프로모션 상세 안내' },
  { id: 'CS-20250104-1340', agent: '박철수', customer: '이강인', category: '수수료문의', status: '완료', datetime: '2025-01-04 13:40', duration: '05:00', isBestPractice: false, fcr: false, memo: '수수료 정책 상세 설명' },
  { id: 'CS-20250104-1115', agent: '정수진', customer: '박지성', category: '해외결제', status: '완료', datetime: '2025-01-04 11:15', duration: '04:50', isBestPractice: false, fcr: true, memo: '해외 사용 설정 완료' },
  { id: 'CS-20250104-1020', agent: '최은정', customer: '조현우', category: '포인트', status: '완료', datetime: '2025-01-04 10:20', duration: '03:30', isBestPractice: false, fcr: true, memo: '포인트 적립 및 사용 안내' },
  { id: 'CS-20250104-0935', agent: '문성민', customer: '황희찬', category: '한도조회', status: '완료', datetime: '2025-01-04 09:35', duration: '04:10', isBestPractice: false, fcr: true, memo: '일시불 한도 조회 및 증액 안내' },
  { id: 'CS-20250103-1710', agent: '손흥민', customer: '백승호', category: '카드분실', status: '완료', datetime: '2025-01-03 17:10', duration: '05:20', isBestPractice: false, fcr: true, memo: '긴급 카드 정지 및 재발급 처리' },
  { id: 'CS-20250103-1545', agent: '서지은', customer: '김영권', category: '프로모션', status: '완료', datetime: '2025-01-03 15:45', duration: '03:55', isBestPractice: false, fcr: true, memo: '이벤트 참여 방법 안내' },
  { id: 'CS-20250103-1420', agent: '전지현', customer: '정우영', category: '해외결제', status: '진행중', datetime: '2025-01-03 14:20', duration: '06:30', isBestPractice: false, fcr: false, memo: '해외 가맹점 결제 오류 조사 중' },
  { id: 'CS-20250103-1310', agent: '조현우', customer: '나상호', category: '포인트', status: '완료', datetime: '2025-01-03 13:10', duration: '04:22', isBestPractice: false, fcr: true, memo: '적립 포인트 사용 가능 가맹점 안내' },
  { id: 'CS-20250103-1155', agent: '이재성', customer: '김진수', category: '한도조회', status: '완료', datetime: '2025-01-03 11:55', duration: '03:48', isBestPractice: false, fcr: true, memo: '카드 한도 증액 신청 접수' },
  { id: 'CS-20250103-1030', agent: '강민지', customer: '황인범', category: '수수료문의', status: '완료', datetime: '2025-01-03 10:30', duration: '05:35', isBestPractice: false, fcr: true, memo: '해외 사용 수수료 정책 설명' },
  { id: 'CS-20250102-1725', agent: '정민우', customer: '권경원', category: '기타', status: '완료', datetime: '2025-01-02 17:25', duration: '04:05', isBestPractice: false, fcr: true, memo: '결제일 변경 요청 처리 완료' },
  { id: 'CS-20250102-1540', agent: '한동훈', customer: '이영표', category: '프로모션', status: '완료', datetime: '2025-01-02 15:40', duration: '03:28', isBestPractice: false, fcr: true, memo: '신년 이벤트 참여 방법 상세 안내' },
  { id: 'CS-20250102-1435', agent: '안수진', customer: '박서준', category: '카드분실', status: '완료', datetime: '2025-01-02 14:35', duration: '05:42', isBestPractice: false, fcr: true, memo: '긴급 카드 정지 및 임시 카드 발급' },
  { id: 'CS-20250102-1320', agent: '배지현', customer: '김수현', category: '해외결제', status: '완료', datetime: '2025-01-02 13:20', duration: '06:18', isBestPractice: false, fcr: false, memo: '해외 결제 실패 원인 분석 및 해결' },
  { id: 'CS-20250102-1205', agent: '강하늘', customer: '송중기', category: '포인트', status: '완료', datetime: '2025-01-02 12:05', duration: '04:12', isBestPractice: false, fcr: true, memo: '포인트 소멸 예정 안내 및 사용 권유' },
  { id: 'CS-20250102-1050', agent: '오수아', customer: '이민호', category: '한도조회', status: '완료', datetime: '2025-01-02 10:50', duration: '03:55', isBestPractice: false, fcr: true, memo: '일시불 한도 확인 및 안내' },
  { id: 'CS-20250102-0935', agent: '임윤아', customer: '유재석', category: '수수료문의', status: '완료', datetime: '2025-01-02 09:35', duration: '05:08', isBestPractice: false, fcr: true, memo: '카드 대금 연체 수수료 안내' },
];

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
    title: 'AI 상담 지원 시스템 업데이트', 
    date: '2025-01-04',
    author: '관리자',
    views: 156,
    pinned: false,
    content: 'AI 상담 지원 시스템이 업데이트 되었습니다.\n\n주요 변경사항:\n1. 실시간 문서 검색 속도 30% 향상\n2. 칸반보드 UI 개선\n3. STT 인식률 향상\n\n업데이트 후 문제 발생 시 IT팀으로 즉시 연락 바랍니다.'
  },
  { 
    id: 4, 
    tag: '이벤트', 
    title: '설날 특별 프로모션 안내', 
    date: '2025-01-02',
    author: '이영희',
    views: 134,
    pinned: false,
    content: '설날 연휴 특별 프로모션 내용입니다.\n\n기간: 1월 20일 ~ 2월 10일\n혜택: 전통시장 결제 시 10% 캐시백\n한도: 월 최대 5만원\n\n명절 관련 문의가 많을 것으로 예상되니 숙지 바랍니다.'
  },
  { 
    id: 5, 
    tag: '시스템', 
    title: '정기 점검 안내 (1월 10일)', 
    date: '2025-01-01',
    author: '관리자',
    views: 98,
    pinned: false,
    content: '정기 시스템 점검이 예정되어 있습니다.\n\n점검 시간: 1월 10일 02:00 ~ 04:00 (2시간)\n영향 범위: 전체 시스템\n대응 방안: 점검 시간 중 상담 불가\n\n점검 시간에는 시스템 이용이 불가하오니 참고 바랍니다.'
  },
  { 
    id: 6, 
    tag: '교육', 
    title: '신규 금융상품 교육 일정 안내', 
    date: '2024-12-28',
    author: '이영희',
    views: 87,
    pinned: false,
    content: '2025년 1월 신규 출시 금융상품에 대한 교육을 진행합니다.\n\n교육 일정: 1월 15일 (수) 14:00~16:00\n장소: 본사 대회의실\n대상: 전체 상담팀\n준비물: 노트북, 필기구\n\n참석 필수이며, 불참 시 팀장에게 사전 보고 바랍니다.'
  },
  { 
    id: 7, 
    tag: '정책', 
    title: '개인정보 보호법 강화 안내', 
    date: '2024-12-25',
    author: '관리자',
    views: 178,
    pinned: false,
    content: '개인정보 보호법이 강화되어 상담 시 주의사항을 안내드립니다.\n\n1. 고객 주민등록번호 전체 수집 금지\n2. 녹취 자료 보관 기간 준수 (6개월)\n3. 개인정보 제3자 제공 동의 필수\n\n위반 시 법적 제재가 있으니 각별히 유의하시기 바랍니다.'
  },
  { 
    id: 8, 
    tag: '이벤트', 
    title: '겨울 여행 특별 캐시백 이벤트', 
    date: '2024-12-20',
    author: '김민수',
    views: 156,
    pinned: false,
    content: '겨울 시즌 여행 관련 특별 캐시백 이벤트를 시작합니다.\n\n기간: 12월 20일 ~ 2월 28일\n혜택: 항공권, 숙박 결제 시 10% 캐시백\n한도: 월 최대 10만원\n조건: 하나카드 전 회원\n\n겨울 여행 시즌을 맞아 많은 문의가 예상되니 상세 내용 숙지 바랍니다.'
  },
  { 
    id: 9, 
    tag: '근무', 
    title: '연말연시 근무 일정 안내', 
    date: '2024-12-18',
    author: '관리자',
    views: 203,
    pinned: false,
    content: '연말연시 근무 일정을 안내드립니다.\n\n12월 31일: 정상 근무 (18시 마감)\n1월 1일: 휴무\n1월 2일: 정상 근무\n\n비상 연락망을 확인하시고 고객 문의 대응에 차질 없도록 준비 바랍니다.'
  },
  { 
    id: 10, 
    tag: '복지', 
    title: '직원 건강검진 실시 안내', 
    date: '2024-12-15',
    author: '인사팀',
    views: 142,
    pinned: false,
    content: '2025년 직원 건강검진을 실시합니다.\n\n기간: 1월 중\n장소: 제휴 병원 (목록 별도 공지)\n예약: 개별 예약 필수\n\n건강검진은 의무사항이며, 미실시 시 복지 포인트가 차감될 수 있습니다.'
  },
];

// ==================== 자주 찾는 문의 키워드 데이터 ====================
export const frequentInquiriesData = [
  { id: 1, keyword: '카드분실', question: '카드를 분실했어요. 어떻게 해야 하나요?', count: 45, trend: 'up' as const },
  { id: 2, keyword: '해외결제', question: '해외에서 카드가 결제되지 않아요', count: 38, trend: 'up' as const },
  { id: 3, keyword: '수수료문의', question: '연회비와 수수료는 얼마인가요?', count: 32, trend: 'down' as const },
  { id: 4, keyword: '포인트', question: '포인트 적립과 사용 방법을 알려주세요', count: 28, trend: 'same' as const },
  { id: 5, keyword: '한도조회', question: '카드 한도를 확인하고 싶어요', count: 24, trend: 'up' as const },
  { id: 6, keyword: '프로모션', question: '진행 중인 이벤트가 있나요?', count: 21, trend: 'up' as const },
];

// ==================== 통일된 스타일 상수 ====================
export const STYLE_CONSTANTS = {
  // 헤더
  headerTitle: 'text-base font-bold text-[#333333]',
  headerContainer: 'bg-white rounded-lg shadow-sm border border-[#E0E0E0] p-3 flex-shrink-0',
  
  // 카드
  cardContainer: 'bg-white rounded-lg shadow-sm border border-[#E0E0E0]',
  cardPadding: 'p-3',
  cardTitle: 'text-sm font-bold text-[#333333]',
  
  // 버튼
  buttonHeight: 'h-8',
  buttonText: 'text-xs',
  buttonPrimary: 'bg-[#0047AB] hover:bg-[#003580]',
  
  // 입력
  inputHeight: 'h-8',
  inputText: 'text-xs',
  inputPadding: 'px-2',
  inputPlaceholder: 'placeholder:text-[10px]',
  
  // 테이블
  tableHeaderText: 'text-[11px] font-semibold text-[#666666]',
  tableCellText: 'text-xs',
  tableRowPadding: 'py-2',
  
  // 간격
  pageGap: 'gap-3',
  pagePadding: 'p-4',
  sectionGap: 'gap-3',
};

// ==================== 교육 시뮬레이션 데이터 ====================
export const simulationsData = [
  // 완료한 시뮬레이션
  { 
    id: 'SIM-001', 
    title: '카드 분실 신고 처리', 
    category: '기초',
    status: 'completed' as const,
    progress: 100,
    score: 95,
    completedDate: '2025-01-05',
    duration: '15분',
    difficulty: 'easy' as const
  },
  { 
    id: 'SIM-002', 
    title: '한도 조정 상담', 
    category: '중급',
    status: 'completed' as const,
    progress: 100,
    score: 88,
    completedDate: '2025-01-06',
    duration: '20분',
    difficulty: 'medium' as const
  },
  { 
    id: 'SIM-003', 
    title: '해외 결제 승인 문의', 
    category: '기초',
    status: 'in-progress' as const,
    progress: 65,
    score: 0,
    completedDate: '',
    duration: '18분',
    difficulty: 'easy' as const
  },
  
  // 추천 시뮬레이션
  { 
    id: 'SIM-004', 
    title: '연체 고객 응대 스킬', 
    category: '고급',
    status: 'recommended' as const,
    progress: 0,
    score: 0,
    completedDate: '',
    duration: '25분',
    difficulty: 'hard' as const,
    recommended: true
  },
  { 
    id: 'SIM-005', 
    title: '부정 사용 의심 케이스', 
    category: '중급',
    status: 'recommended' as const,
    progress: 0,
    score: 0,
    completedDate: '',
    duration: '22분',
    difficulty: 'medium' as const,
    recommended: true
  },
  { 
    id: 'SIM-006', 
    title: '포인트 적립 문의 응대', 
    category: '기초',
    status: 'recommended' as const,
    progress: 0,
    score: 0,
    completedDate: '',
    duration: '12분',
    difficulty: 'easy' as const,
    recommended: true
  }
];