# CALL:ACT 페이지별 구현 현황

## 1. 개요

CALL:ACT 시스템의 **실제 구현된 페이지별 상세 현황**을 정리한 문서입니다.

**작성일**: 2025-01-09  
**기준**: mockData.ts 반영 완료 (사원 45명, 상담 데이터 25건)

---

## 2. 공통 데이터 구조 (/src/data/mockData.ts)

### 2.1 사원 데이터 (employeesData)

**총 45명 사원 구성:**
- 상담1팀: 18명
- 상담2팀: 15명
- 상담3팀: 12명

```typescript
interface Employee {
  id: string;              // 'EMP-001'
  name: string;            // '홍길동'
  team: string;            // '상담1팀', '상담2팀', '상담3팀'
  position: string;        // '사원', '대리', '과장'
  consultations: number;   // 상담 건수 (102~145)
  fcr: number;             // FCR 달성률 87~96%
  avgTime: string;         // 평균 처리 시간 '4:15' ~ '5:30'
  rank: number;            // 전체 순위 1~45
  trend: 'up' | 'down' | 'same';  // 추이
  status: 'active' | 'inactive' | 'vacation';
  joinDate: string;        // '2024-01-15'
  email: string;
  phone: string;
}
```

**Top 3 사원:**
1. 🥇 김민수 (상담1팀) - 145건, FCR 96%, 4:15
2. 🥈 최은정 (상담3팀) - 140건, FCR 96%, 4:18
3. 🥉 이영희 (상담2팀) - 138건, FCR 95%, 4:20

---

### 2.2 상담 데이터 (consultationsData)

**총 25건 상담 내역 (2025-01-02 ~ 2025-01-05)**

```typescript
interface Consultation {
  id: string;              // 'CS-20250105-1432'
  agent: string;           // 상담사 이름
  customer: string;        // 고객 이름
  category: string;        // '카드분실', '해외결제', '수수료문의', '프로모션', '포인트', '한도조회', '기타'
  status: string;          // '완료', '진행중', '미완료'
  datetime: string;        // '2025-01-05 14:32'
  duration: string;        // '05:12'
  isBestPractice: boolean; // 우수 사례 여부
  fcr: boolean;            // FCR 달성 여부
  memo: string;            // 상담 내용 요약
}
```

**카테고리 분포:**
- 카드분실: 5건
- 해외결제: 5건
- 수수료문의: 3건
- 프로모션: 3건
- 포인트: 3건
- 한도조회: 3건
- 기타: 3건

**우수 사례 (isBestPractice: true):**
- CS-20250105-1432 (홍길동, 카드분실)
- CS-20250105-1045 (김태희, 해외결제)

---

### 2.3 공지사항 데이터 (noticesData)

**약 15건 공지사항**

```typescript
interface Notice {
  id: number;
  tag: string;     // '긴급', '시스템', '이벤트', '교육', '정책', '근무', '복지'
  title: string;
  date: string;    // '2025-01-05'
  author: string;
  views: number;
  pinned: boolean; // 고정 여부
  content: string;
}
```

**주요 공지:**
- (긴급, 고정) KT 화재로 인한 통신망 장애 대응
- (이벤트, 고정) 하나카드x메가커피 프로모션 안내

---

## 3. 페이지별 구현 현황

### 3.1 LandingPage (랜딩 페이지)

**경로**: `/`  
**접근**: 비로그인 사용자

#### 주요 기능
- 시스템 소개 (Hero Section)
- 핵심 기능 3가지
- 실시간 데모 영상 (예정)
- 로그인 버튼

#### 디자인
- 애플/테슬라급 미니멀 디자인
- 8K 프리미엄 수준
- 색상: #0047AB, #FBBC04, White/Gray

---

### 3.2 LoginPage (로그인 페이지)

**경로**: `/login`  
**접근**: 비로그인 사용자

#### Mock 로그인 정보
```typescript
const mockUsers = [
  { 
    id: 'EMP-001', 
    username: 'admin', 
    password: 'admin123', 
    role: 'admin',
    name: '관리자'
  },
  { 
    id: 'EMP-002', 
    username: 'agent', 
    password: 'agent123', 
    role: 'agent',
    name: '홍길동'
  }
];
```

#### 로그인 후 라우팅
- admin → `/admin/stats` (관리자 통계 대시보드)
- agent → `/dashboard` (상담사 대시보드)

---

### 3.3 DashboardPage (대시보드)

**경로**: `/dashboard`  
**접근**: 상담사 로그인 필요

#### 표시 데이터

**1) 상단 KPI 카드 (4개)**
- 오늘의 상담 건수
- FCR 달성률
- 평균 처리 시간
- 완료된 상담

**2) 실시간 상담 현황**
- 진행 중인 상담 목록 (Mock)
- 대기 중인 상담 알림

**3) 최근 상담 내역**
- consultationsData에서 최근 5건 표시
- 상태별 색상 구분 (완료: 녹색, 진행중: 노랑, 미완료: 빨강)

**4) 공지사항**
- noticesData에서 pinned: true 우선 표시
- 최대 5건 표시

**5) 금주의 이슈**
- Mock 데이터 (예정: AI 트렌드 분석)

**6) 우수사원 사례집**
- consultationsData에서 isBestPractice: true 필터링
- 상담 ID, 상담사, 카테고리 표시

---

### 3.4 RealTimeConsultationPage (실시간 상담 페이지)

**경로**: `/consultation/realtime`  
**접근**: 상담사 로그인 필요

#### 핵심 기능: 칸반보드 시스템

**좌측: 고객 정보 + 최근 상담 내역**
```typescript
const customerInfo = {
  id: 'CUST-001',
  name: '홍길동',
  phone: '010-1234-5678',
  birthDate: '1985-03-15',
  address: '서울시 강남구 테헤란로 123'
};

const recentConsultations = [
  { id: 1, title: '카드 재발급 문의', date: '2025-01-03 10:30', category: '카드분실', status: '완료' }
];
```

**중앙: 칸반보드 (2개 컬럼)**

1. **현재 상황** - currentSituationCards (2개 카드)
2. **다음 단계** - nextStepCards (2개 카드)

**칸반보드 카드 구조 (DetailCard)**
```typescript
interface DetailCard {
  id: number;
  title: string;              // '카드 분실 신고 처리 절차'
  keywords: string[];         // ['#분실신고', '#즉시정지', '#재발급']
  content: string;            // 간단한 설명
  
  // ⭐ 상담사 핵심 정보
  systemPath: string;         // '고객관리 > 카드관리 > 분실신고 > 즉시정지'
  requiredChecks: string[];   // 필수 확인 사항 (4개)
  exceptions: string[];       // 예외 케이스 (3개)
  regulation: string;         // '카드업무 취급요령 제34조'
  detailContent: string;      // 약관 전문 (전체 조문)
  
  time?: string;              // '처리 시간: 약 3-5분'
  note?: string;              // '분실 신고 후 72시간 내 부정 사용 보상 가능'
}
```

**칸반보드 카드 표시 정보 우선순위:**
1. 🖥️ systemPath (시스템 처리 경로) - 배경색 강조
2. ✅ requiredChecks (필수 확인 사항) - 최소 3개 표시
3. ⚠️ exceptions (예외 사항) - 최소 2개 표시, 빨간색
4. 📋 title + content (제목 + 설명)
5. 🏷️ keywords (키워드)

**[상세보기] 모달:**
- 전체 systemPath
- 전체 requiredChecks
- 전체 exceptions
- regulation (약관 제목)
- detailContent (약관 전문)

**우측: AI 검색 어시스턴트**
- 상담사 질문 입력
- AI 답변 표시 (Mock)
- 과거 대화 히스토리

**하단: 통화 제어**
- ☎️ 통화 시작/종료 버튼
- ⏱️ 통화 시간 타이머
- 💾 임시 저장 버튼

**STT 키워드 영역**
- 실시간 키워드 표시 (Mock: ['카드분실', '해외결제', '수수료문의'])

---

### 3.5 AfterCallWorkPage (후처리 페이지)

**경로**: `/consultation/aftercall`  
**접근**: 상담사 로그인 필요

#### 레이아웃 (3컬럼)

**좌측: 현재 케이스 + 유사 사례**
```typescript
const currentCase = {
  category: '카드분실',
  summary: '고객이 카드 분실 신고 요청. 즉시 카드 사용 정지 처리 완료. 재발급 카드 등록 주소로 배송 예정.',
  aiRecommendation: 'AI 추천 처리: 재발급 신청 완료 및 배송 안내'
};

const similarCase = {
  category: '카드분실',
  summary: '2024-12-28 처리 사례. 고객 카드 분실 신고 후 재발급 처리. 해외 여행 전 긴급 배송 요청하여 익일 배송으로 변경 처리.',
  aiRecommendation: '긴급 배송 옵션 제안 권장',
  outcome: '성공'
};
```

**중앙: AI 상담 요약**
```typescript
const aiSummary = `문의사항: 고객이 카드를 분실하여 즉시 사용 정지 및 재발급 요청

처리 결과: 카드 사용 즉시 정지 처리 완료. 재발급 카드 신청 접수하였으며, 등록된 주소(서울시 강남구 테헤란로 123)로 3-5일 내 배송 예정. 고객에게 배송 추적 안내 완료.`;
```

**우측: 상담 전문 + 감정 분석 + 피드백**
```typescript
const callTranscript = [
  { speaker: 'customer', message: '안녕하세요, 카드를 분실했어요.', timestamp: '14:32' },
  { speaker: 'agent', message: '안녕하세요. 즉시 카드 사용을 정지하겠습니다.', timestamp: '14:33' }
];

// 감정 분석
const emotions = {
  start: '부정적',
  middle: '중립',
  end: '긍정적',
  qualityScore: '상'
};

// 피드백 점수
const feedback = {
  processingTime: 85,
  gratitude: 75,
  emotionShift: 88,
  manualCompliance: 92
};
```

**하단: 후처리 양식**
- 제목, 상태, 카테고리
- 후속 일정
- 이관 부서/사항
- 상담사 메모
- 💾 저장 버튼

---

### 3.6 ConsultationHistoryPage (상담 내역)

**경로**: `/consultation/history`  
**접근**: 상담사 로그인 필요

#### 상단: 검색/필터
- 검색: 고객명, 상담 ID
- 필터: 상태 (전체/완료/진행중/미완료)
- 필터: 카테고리 (전체/카드분실/해외결제/...)
- 기간: 날짜 범위

#### 테이블 (consultationsData 표시)
- ID
- 상담사
- 고객
- 카테고리
- 상태 (완료: 녹색, 진행중: 노랑, 미완료: 빨강)
- 일시
- 통화 시간
- FCR (✅/❌)
- 상세보기 버튼

#### 상세보기 모달 (ConsultationDetailModal)
- 고객 정보 (Mock)
- 상담 시간
- 녹취록 재생 (Mock)
- AI 요약
- 상담 전문
- FCR 달성 여부

---

### 3.7 ProfilePage (프로필)

**경로**: `/profile`  
**접근**: 로그인 필요

#### 표시 정보 (Mock)
```typescript
const currentAgent = {
  id: 'EMP-002',
  name: '홍길동',
  team: '상담1팀',
  position: '대리',
  email: 'hong@example.com',
  phone: '010-1234-5678',
  joinDate: '2024-01-15',
  consultations: 127,
  fcr: 94,
  avgTime: '4:32',
  rank: 7
};

const badges = [
  { name: 'FCR 마스터', icon: '🏆', color: '#FBBC04' },
  { name: '신속 처리왕', icon: '⚡', color: '#34A853' }
];
```

#### 개인 성과 통계
- 오늘의 상담 건수
- FCR 달성률
- 평균 처리 시간
- 전체 순위

---

### 3.8 EmployeesPage (사원 목록)

**경로**: `/employees`  
**접근**: 로그인 필요

#### 상단: Top 3 카드 + 검색
- 🥇 🥈 🥉 Top 3 사원 카드 (메달 색상 구분)
- 검색 박스 (사원명, 사번, 팀)

#### 필터
- 팀: 전체/상담1팀/상담2팀/상담3팀
- 직급: 전체/사원/대리/과장

#### 테이블 (employeesData 표시)
- 순위 (1~3위는 🏆 아이콘)
- 사번
- 이름
- 소속
- 직급 (배지)
- 상담 건수
- FCR (색상: 95%↑ 녹색, 90~95% 노랑, 90%↓ 빨강)
- 평균 시간
- 추이 (▲▼―)

#### 페이지네이션
- 동적 계산 (화면 높이에 따라 자동 조정)
- 현재 페이지 / 전체 페이지
- 페이지 이동 입력

**⚠️ 알려진 이슈:**
- 순위 표시 오류 (1234556667 등) → 수정 예정
- 해상도 하드코딩 문제 (5K에서 아래 반 이상 빔) → 수정 예정

---

### 3.9 NoticePage (공지사항)

**경로**: `/notice`  
**접근**: 로그인 필요

#### 표시 데이터 (noticesData)
- 총 15건 공지사항
- 고정 공지 (pinned: true) 상단 표시
- 태그별 색상 구분:
  - 긴급: 빨강
  - 시스템: 노랑
  - 이벤트: 파랑
  - 교육: 보라
  - 정책: 청록
  - 근무: 주황
  - 복지: 하늘

#### 공지 카드
- 📌 고정 아이콘 (pinned)
- 태그 배지
- 제목
- 내용 미리보기 (2줄)
- 작성자, 조회수, 날짜

---

### 3.10 SimulationPage (시뮬레이션)

**경로**: `/simulation`  
**접근**: 로그인 필요

#### 상단 배너
- 완료한 시나리오: 3개
- 평균 점수: 92점
- 총 시도 횟수: 5회
- 이용 가능: 8개

#### 시나리오 카테고리
- 전체
- 기본 상담
- 민원 대응
- 긴급 상황
- 고급 스킬

#### 시나리오 카드 (Mock 8개)
- 제목
- 난이도 (초급/중급/고급)
- 예상 시간
- 태그
- 완료 여부 (✅ 완료, 🔒 잠김)
- 최고 점수

#### 최근 시도 내역
- 시나리오명
- 점수
- 시도 날짜

---

### 3.11 AdminStatsPage (관리자 통계)

**경로**: `/admin/stats`  
**접근**: 관리자 로그인 필요

#### 총괄 현황 (상단)
- 총 상담 건수 (오늘)
- 총 상담사 수
- 평균 FCR
- 평균 처리 시간

#### 주간 상담 추이 (차트)
- 최근 7일 상담 건수 바 차트
- 일자별 FCR 표시
- Hover 시 상세 정보

---

### 3.12 AdminConsultationManagePage (상담 관리)

**경로**: `/admin/consultations`  
**접근**: 관리자 로그인 필요

#### 기능
- 전체 상담 내역 조회 (consultationsData)
- 검색/필터 (상담사, 고객, 카테고리, 상태)
- 상세보기 모달
- 통계 집계

---

### 3.13 AdminManagePage (사원 관리)

**경로**: `/admin/manage`  
**접근**: 관리자 로그인 필요

#### 기능
- employeesData 테이블 표시
- 검색/필터 (팀, 직급, 상태)
- 사원 상세보기

**⚠️ 미구현 기능:**
- 권한 부여/해제
- 관리자 등록/해제
- 사원 추가
- 사원 삭제
- 사원 정보 수정

---

### 3.14 AdminNoticePage (공지사항 관리)

**경로**: `/admin/notice`  
**접근**: 관리자 로그인 필요

#### 기능
- noticesData 관리
- 공지 추가/수정/삭제 (예정)
- 고정 설정

---

## 4. 공통 컴포넌트

### 4.1 MainLayout
- Header (상단 바)
- Sidebar (좌측 사이드바)
- 메인 컨텐츠 영역

### 4.2 Header
- 로고
- 페이지 제목
- 공지사항 알림 (🔔)
- 프로필 아이콘

### 4.3 Sidebar
- 접기/펼치기 기능
- 메뉴 아이템 (역할별 표시)
  - 상담사: 대시보드, 실시간상담, 후처리, 상담내역, 프로필, 사원목록, 공지사항, 시뮬레이션
  - 관리자: 통계, 상담관리, 사원관리, 공지관리

### 4.4 ConsultationDetailModal
- 상담 상세 정보 모달
- 고객 정보, 상담 시간, 녹취록, AI 요약

### 4.5 AnnouncementModal
- 공지사항 상세 모달

---

## 5. 스타일링 가이드

### 5.1 색상 체계
- **Primary Blue**: #0047AB (메인 색상)
- **Yellow**: #FBBC04 (강조, 경고)
- **Success Green**: #34A853
- **Error Red**: #EA4335
- **Background**: #F5F5F5
- **Text**: #333333 (메인), #666666 (보조), #999999 (비활성)

### 5.2 텍스트 크기 표준
| 요소 | 크기 |
|---|---|
| 테이블 헤더/바디 | text-xs (12px) ~ text-[13px] |
| 라벨/부가정보 | text-[11px] |
| 배지/태그 | text-[11px] |
| 카드 제목 | text-base (16px) |
| 본문 | text-xs (12px) |
| 최소 크기 | text-[10px] (타임스탬프) |

### 5.3 반응형
- 기본: Desktop 1920x1080
- 목표: 4K~5K 해상도 대응 (진행 중)

---

## 6. 알려진 이슈 및 개선 사항

### 6.1 미구현 기능
- [ ] 사원 관리 페이지 CRUD 기능
- [ ] 공지사항 관리 페이지 CRUD 기능
- [ ] 실제 STT 연동
- [ ] 실제 RAG 검색 연동
- [ ] 실제 AI 어시스턴트 연동

### 6.2 버그
- [ ] 사원 목록 순위 표시 오류 (1234556667)
- [ ] 5K 해상도에서 빈 공간 발생 (하드코딩 문제)

### 6.3 개선 예정
- [ ] 칸반보드 정보 우선순위 재배치
- [ ] 대시보드 정보 최적화
- [ ] 해상도별 동적 레이아웃

---

## 7. 업데이트 이력

| 날짜 | 내용 |
|------|------|
| 2025-01-09 | 페이지별 구현 현황 문서 작성 (mockData 반영) |
| 2025-01-09 | 텍스트 크기 표준화 완료 (전체 페이지) |
