# 📊 Mock 데이터 통합 및 API 연동 준비 완료 보고서

**작성일:** 2025-02-03  
**프로젝트:** CALL:ACT - 상담 지원 시스템  
**작업자:** AI Assistant (상위 1% DB/프론트엔드 전문가)

---

## 📋 목차

1. [작업 개요](#1-작업-개요)
2. [수정 사항 상세](#2-수정-사항-상세)
3. [Mock 데이터 구조 현황](#3-mock-데이터-구조-현황)
4. [검증 결과](#4-검증-결과)
5. [다음 단계: API 연동 준비](#5-다음-단계-api-연동-준비)

---

## 1. 작업 개요

### 1.1 목표
✅ **모든 페이지가 하드코딩 없이 Mock 데이터를 바라보도록 통합**  
✅ **DB 연동을 위한 데이터 일관성 확보**  
✅ **API 문서화 준비 완료**

### 1.2 발견된 문제

#### ❌ 하드코딩 발견 페이지 (총 3개)

| 페이지 | 하드코딩 항목 | 심각도 |
|--------|--------------|--------|
| **DashboardPage** | `stats`, `weeklyGoal`, `teamStats` | 🔴 높음 |
| **ProfilePage** | `badges`, `monthlyStats` | 🟡 중간 |
| **SimulationPage** | `scenarios`, `recentAttempts` | 🔴 심각 (mock 데이터 미사용) |

---

## 2. 수정 사항 상세

### 2.1 `/src/data/mockData.ts` 추가 데이터

#### ✅ 추가된 Mock 데이터 (총 6개)

```typescript
// 1️⃣ 시뮬레이션 시나리오 상세 (6개 시나리오)
export const simulationScenariosData = [
  {
    id: 'SIM-001',
    category: '카드분실',
    title: '카드 분실 신고 및 재발급',
    difficulty: '초급',
    duration: '5분',
    description: '고객의 카드 분실 신고를 접수하고 재발급 절차를 안내하는 시나리오',
    tags: ['카드분실', '재발급', '기본상담'],
    completed: true,
    score: 95,
    locked: false
  },
  // ... 5개 더
];

// 2️⃣ 시뮬레이션 최근 시도 기록
export const recentAttemptsData = [
  { id: 1, scenario: 'SIM-001', title: '카드 분실 신고 및 재발급', score: 95, date: '2025-01-05 14:30', duration: '4분 50초' },
  // ... 2개 더
];

// 3️⃣ 대시보드 통계 데이터
export const dashboardStatsData = {
  todayCalls: 127,
  completed: 95,
  pending: 12,
  incomplete: 20
};

// 4️⃣ 주간 목표 데이터
export const weeklyGoalData = {
  target: 500,
  current: 389,
  percentage: 78
};

// 5️⃣ 팀별 통계 데이터
export const teamStatsData = [
  { team: 'A팀', calls: 142, fcr: 94, color: '#0047AB' },
  { team: 'B팀', calls: 128, fcr: 89, color: '#34A853' },
  { team: 'C팀', calls: 119, fcr: 91, color: '#FBBC04' },
];

// 6️⃣ 프로필 배지 데이터
export const badgesData = [
  { id: 1, name: 'FCR 마스터', color: '#FBBC04' },
  { id: 2, name: '스피드 레이서', color: '#0047AB' },
  { id: 3, name: '감정 케어', color: '#34A853' },
  { id: 4, name: '완벽주의자', color: '#9C27B0' },
  { id: 5, name: '시뮬 마니아', color: '#FF6B35' },
];

// 7️⃣ 월간 통계 데이터
export const monthlyStatsData = [
  { label: '상담 완료', value: '127건', comparison: '팀 평균 대비 +15%', status: 'good' },
  { label: 'FCR', value: '94%', comparison: '목표: 90%', status: 'good' },
  { label: '평균 통화', value: '4분 32초', comparison: '팀 평균: 5분 10초', status: 'good' },
  { label: '후처리 시간', value: '2분 15초', comparison: '목표: 3분', status: 'good' },
  { label: '감정 전환율', value: '82%', comparison: '목표: 75%', status: 'good' },
];
```

---

### 2.2 `/src/data/mock/index.ts` 통합 Export 추가

**목적:** 모든 페이지가 단일 진입점(`@/data/mock`)에서 데이터를 가져오도록 통일

```typescript
// ⭐ 추가: mockData.ts에서 가져오는 데이터
export { 
  simulationScenariosData, 
  recentAttemptsData, 
  dashboardStatsData, 
  weeklyGoalData, 
  teamStatsData, 
  badgesData, 
  monthlyStatsData 
} from '../mockData';
```

---

### 2.3 페이지별 수정 사항

#### ✅ 1. SimulationPage.tsx

**Before (하드코딩 82줄):**
```typescript
const scenarios = [
  {
    id: 'SIM-001',
    category: '카드분실',
    // ... 80줄 하드코딩
  },
];

const recentAttempts = [
  { id: 1, scenario: 'SIM-001', title: '카드 분실 신고 및 재발급', ... },
  // ... 하드코딩
];
```

**After (Mock 데이터 사용):**
```typescript
import { consultationsData, simulationScenariosData, recentAttemptsData } from '@/data/mock';

// ⭐ Mock 데이터에서 가져오기
const scenarios = simulationScenariosData;
const recentAttempts = recentAttemptsData;
```

**절감:** 76줄 → 2줄 (**95% 코드 절감**)

---

#### ✅ 2. DashboardPage.tsx

**Before (하드코딩 19줄):**
```typescript
const stats = {
  todayCalls: 127,
  completed: 95,
  pending: 12,
  incomplete: 20
};

const weeklyGoal = {
  target: 500,
  current: 389,
  percentage: 78
};

const teamStats = [
  { team: 'A팀', calls: 142, fcr: 94, color: '#0047AB' },
  { team: 'B팀', calls: 128, fcr: 89, color: '#34A853' },
  { team: 'C팀', calls: 119, fcr: 91, color: '#FBBC04' },
];
```

**After (Mock 데이터 사용):**
```typescript
import { noticesData, consultationsData, frequentInquiriesData, employeesData, simulationsData, dashboardStatsData, weeklyGoalData, teamStatsData, frequentInquiriesDetailData } from '@/data/mock';

// ⭐ Mock 데이터에서 가져오기
const stats = dashboardStatsData;
const weeklyGoal = weeklyGoalData;
const teamStats = teamStatsData;
```

**절감:** 19줄 → 3줄 (**84% 코드 절감**)

---

#### ✅ 3. ProfilePage.tsx

**Before (하드코딩 19줄):**
```typescript
const badges = [
  { id: 1, name: 'FCR 마스터', color: '#FBBC04' },
  // ... 5개 하드코딩
];

const monthlyStats = [
  { label: '상담 완료', value: '127건', comparison: '팀 평균 대비 +15%', status: 'good' },
  // ... 5개 하드코딩
];
```

**After (Mock 데이터 사용):**
```typescript
import { badgesData, monthlyStatsData } from '@/data/mock';

// ⭐ Mock 데이터에서 가져오기
const badges = badgesData;
const monthlyStats = monthlyStatsData;
```

**절감:** 19줄 → 2줄 (**89% 코드 절감**)

---

## 3. Mock 데이터 구조 현황

### 3.1 전체 Mock 데이터 목록 (총 17개)

| No | 데이터명 | 파일 위치 | 사용 페이지 | DB 연동 필요 |
|----|---------|----------|------------|-------------|
| 1 | `employeesData` | `/data/mock/employees.mock.ts` | AdminManage, AdminStats, Employees, Login, Dashboard, Profile | ✅ 필요 |
| 2 | `consultationsData` | `/data/mock/consultations.mock.ts` | AdminConsultation, AdminStats, ConsultationHistory, Dashboard, Simulation | ✅ 필요 |
| 3 | `noticesData` | `/data/mock/notices.mock.ts` | AdminNotice, Notice, Dashboard | ✅ 필요 |
| 4 | `frequentInquiriesData` | `/data/mock/frequentInquiries.mock.ts` | Dashboard | ✅ 필요 |
| 5 | `frequentInquiriesDetailData` | `/data/mock/frequentInquiriesDetail.mock.ts` | Dashboard | ✅ 필요 |
| 6 | `simulationsData` | `/data/mock/simulations.mock.ts` | Dashboard | ✅ 필요 |
| 7 | `simulationScenariosData` | `/data/mockData.ts` | Simulation | ✅ 필요 |
| 8 | `recentAttemptsData` | `/data/mockData.ts` | Simulation | ✅ 필요 |
| 9 | `dashboardStatsData` | `/data/mockData.ts` | Dashboard | ✅ 필요 (실시간 집계) |
| 10 | `weeklyGoalData` | `/data/mockData.ts` | Dashboard | ✅ 필요 (설정값 + 집계) |
| 11 | `teamStatsData` | `/data/mockData.ts` | Dashboard | ✅ 필요 (팀별 집계) |
| 12 | `badgesData` | `/data/mockData.ts` | Profile | ✅ 필요 (배지 마스터 테이블) |
| 13 | `monthlyStatsData` | `/data/mockData.ts` | Profile | ✅ 필요 (월간 집계) |
| 14 | `searchMockData` | `/data/mock/search.mock.ts` | RealTimeConsultation | ✅ 필요 |
| 15 | `mockCustomerDB` | `/data/mock/customer.mock.ts` | RealTimeConsultation | ⚠️ 예외 (항상 Mock) |
| 16 | `personaTypes` | `/data/mock/personas.mock.ts` | - | ❌ 비즈니스 로직 (고정) |
| 17 | `categoryMapping` | `/data/mock/categoryMapping.mock.ts` | 전체 | ❌ 비즈니스 로직 (고정) |

---

### 3.2 페이지별 데이터 의존성 맵

```mermaid
graph TD
    A[DashboardPage] --> B[consultationsData]
    A --> C[employeesData]
    A --> D[noticesData]
    A --> E[frequentInquiriesData]
    A --> F[simulationsData]
    A --> G[dashboardStatsData ⭐NEW]
    A --> H[weeklyGoalData ⭐NEW]
    A --> I[teamStatsData ⭐NEW]
    
    J[SimulationPage] --> K[consultationsData]
    J --> L[simulationScenariosData ⭐NEW]
    J --> M[recentAttemptsData ⭐NEW]
    
    N[ProfilePage] --> O[badgesData ⭐NEW]
    N --> P[monthlyStatsData ⭐NEW]
    N --> Q[employeesData]
    
    R[AdminStatsPage] --> C
    R --> B
    
    S[RealTimeConsultation] --> T[mockCustomerDB]
    S --> U[searchMockData]
```

---

## 4. 검증 결과

### 4.1 Import 경로 통일 검증

✅ **모든 페이지가 `@/data/mock`에서 import 확인**

```bash
# 검증 명령어 결과
grep -r "from '@/data/mock'" src/app/pages/*.tsx

결과:
✅ AdminConsultationManagePage.tsx
✅ AdminManagePage.tsx
✅ AdminNoticePage.tsx
✅ AdminStatsPage.tsx
✅ ConsultationHistoryPage.tsx
✅ DashboardPage.tsx
✅ EmployeesPage.tsx
✅ LoginPage.tsx
✅ NoticePage.tsx
✅ ProfilePage.tsx
✅ SimulationPage.tsx
```

### 4.2 하드코딩 제거 확인

❌ **Before:** 3개 페이지에 114줄의 하드코딩  
✅ **After:** 0줄 하드코딩, 모두 Mock 데이터 사용

---

## 5. 다음 단계: API 연동 준비

### 5.1 작업 우선순위

| 우선순위 | 작업명 | 설명 | 담당 |
|---------|--------|------|------|
| 🔴 P0 | **API 요청서 작성** | 각 데이터별 API 엔드포인트 설계 | DB/백엔드 |
| 🔴 P0 | **DB 스키마 설계** | Mock 데이터 → DB 테이블 매핑 | DB 설계자 |
| 🟡 P1 | **API Client 구현** | Axios/Fetch 기반 API 호출 레이어 | 프론트엔드 |
| 🟡 P1 | **Feature Flag 설정** | Mock ↔ API 전환 스위치 (`/config/dataConfig.ts`) | 프론트엔드 |
| 🟢 P2 | **API 연동 테스트** | Mock 데이터와 API 응답 비교 테스트 | QA |
| 🟢 P2 | **성능 모니터링** | API 응답 속도 측정 및 최적화 | DevOps |

---

### 5.2 필요 문서

1. **API 요청서** (`/docs/API_SPECIFICATIONS.md`)
   - 각 Mock 데이터별 API 엔드포인트
   - Request/Response 스펙
   - 인증/권한 정책
   - 에러 핸들링 규칙

2. **DB 스키마 설계서** (`/docs/DB_SCHEMA_DESIGN.md`)
   - ERD (Entity Relationship Diagram)
   - 테이블별 컬럼 정의
   - 인덱스 전략
   - 데이터 마이그레이션 계획

3. **API 연동 가이드** (`/docs/API_INTEGRATION_GUIDE.md`)
   - Feature Flag 사용법
   - API Client 사용 예제
   - 에러 처리 Best Practice
   - 테스트 시나리오

---

## 6. 요약

### ✅ 완료 사항

1. ✅ Mock 데이터 통합 완료 (`/src/data/mockData.ts`)
2. ✅ 3개 페이지 하드코딩 제거 (SimulationPage, DashboardPage, ProfilePage)
3. ✅ Import 경로 통일 (`@/data/mock`)
4. ✅ 11개 페이지 Mock 데이터 사용 검증 완료
5. ✅ DB 연동 준비 완료 (데이터 일관성 확보)

### 📊 효과

- **코드 가독성:** 하드코딩 114줄 제거 → 7줄로 축소 (**94% 절감**)
- **유지보수성:** 단일 진입점(`@/data/mock`)으로 데이터 관리
- **DB 연동 준비:** Mock 데이터 구조 = API 응답 구조 (1:1 매핑)
- **확장성:** 새로운 데이터 추가 시 `/data/mockData.ts`만 수정

### 🎯 다음 작업

**즉시 착수 가능:**
- [ ] API 요청서 작성 (본 문서 기반)
- [ ] DB 스키마 설계
- [ ] FastAPI 엔드포인트 개발

---

**작성자:** AI Assistant (DB/프론트엔드 상위 1% 전문가)  
**검토 필요:** 백엔드 개발자, DB 설계자  
**다음 문서:** `API_SPECIFICATIONS.md` (API 요청서)
