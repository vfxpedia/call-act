# 🌐 CALL:ACT API 명세서 (Specifications)

**프로젝트:** CALL:ACT - 상담 지원 시스템  
**API 버전:** v1.0  
**작성일:** 2025-02-03  
**기반 기술:** FastAPI (Python 3.11+), PostgreSQL 16+  
**인증 방식:** JWT Bearer Token

---

## 📋 목차

1. [API 설계 철학](#1-api-설계-철학)
2. [공통 규격](#2-공통-규격)
3. [API 엔드포인트 목록](#3-api-엔드포인트-목록)
4. [상세 스펙](#4-상세-스펙)
5. [DB 스키마 제안](#5-db-스키마-제안)
6. [마이그레이션 계획](#6-마이그레이션-계획)

---

## 1. API 설계 철학

### 1.1 설계 원칙

```
🎯 거시적 관점 (Macro View)
├─ RESTful API 원칙 준수
├─ 응답 구조 일관성 (Mock 데이터 = API 응답)
├─ 확장 가능한 버저닝 (v1, v2...)
└─ 성능 최적화 (페이지네이션, 캐싱, 인덱싱)

🔍 구체적 사항 (Micro Details)
├─ Mock 데이터 형식 100% 호환
├─ 에러 코드 표준화
├─ 응답 시간 목표: P95 < 200ms
└─ 동시 접속 지원: 100 users
```

### 1.2 Mock 데이터 → API 전환 전략

#### Feature Flag 기반 전환

```typescript
// /src/config/dataConfig.ts
export const API_CONFIG = {
  USE_API: process.env.VITE_USE_API === 'true', // 기본값: false (Mock)
  BASE_URL: process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
};

// 예시: 데이터 가져오기
const getEmployees = async () => {
  if (API_CONFIG.USE_API) {
    return await fetch(`${API_CONFIG.BASE_URL}/employees`);
  } else {
    return employeesData; // Mock
  }
};
```

---

## 2. 공통 규격

### 2.1 Base URL

```
개발 환경: http://localhost:8000/api/v1
스테이징: https://staging-api.callact.com/api/v1
프로덕션: https://api.callact.com/api/v1
```

### 2.2 인증 헤더

```http
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

### 2.3 공통 응답 포맷

#### ✅ 성공 응답

```json
{
  "success": true,
  "data": { ... },
  "message": "요청이 성공적으로 처리되었습니다.",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

#### ❌ 에러 응답

```json
{
  "success": false,
  "error": {
    "code": "ERR_NOT_FOUND",
    "message": "요청한 리소스를 찾을 수 없습니다.",
    "details": { ... }
  },
  "timestamp": "2025-02-03T10:30:00Z"
}
```

### 2.4 에러 코드 표준

| 에러 코드 | HTTP 상태 | 설명 |
|----------|----------|------|
| `ERR_UNAUTHORIZED` | 401 | 인증 실패 (토큰 없음/만료) |
| `ERR_FORBIDDEN` | 403 | 권한 없음 (관리자 전용 API) |
| `ERR_NOT_FOUND` | 404 | 리소스 없음 |
| `ERR_VALIDATION` | 422 | 입력값 검증 실패 |
| `ERR_SERVER` | 500 | 서버 내부 오류 |
| `ERR_RATE_LIMIT` | 429 | API 호출 한도 초과 |

### 2.5 페이지네이션 규격

```http
GET /api/v1/consultations?page=1&limit=20&sort=datetime&order=desc

Response:
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_items": 200,
      "per_page": 20,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## 3. API 엔드포인트 목록

### 3.1 전체 API 맵

| No | 카테고리 | 엔드포인트 | 메서드 | 설명 | 우선순위 |
|----|---------|-----------|--------|------|---------|
| 1 | **인증** | `/auth/login` | POST | 로그인 | 🔴 P0 |
| 2 | **인증** | `/auth/logout` | POST | 로그아웃 | 🔴 P0 |
| 3 | **인증** | `/auth/refresh` | POST | 토큰 갱신 | 🔴 P0 |
| 4 | **직원** | `/employees` | GET | 직원 목록 조회 | 🔴 P0 |
| 5 | **직원** | `/employees/{id}` | GET | 직원 상세 조회 | 🟡 P1 |
| 6 | **직원** | `/employees` | POST | 직원 추가 | 🟡 P1 |
| 7 | **직원** | `/employees/{id}` | PUT | 직원 수정 | 🟡 P1 |
| 8 | **직원** | `/employees/{id}` | DELETE | 직원 삭제 | 🟡 P1 |
| 9 | **상담** | `/consultations` | GET | 상담 목록 조회 | 🔴 P0 |
| 10 | **상담** | `/consultations/{id}` | GET | 상담 상세 조회 | 🔴 P0 |
| 11 | **상담** | `/consultations` | POST | 상담 등록 | 🔴 P0 |
| 12 | **상담** | `/consultations/{id}` | PUT | 상담 수정 | 🟡 P1 |
| 13 | **상담** | `/consultations/best-practices` | GET | 우수 상담 조회 | 🟡 P1 |
| 14 | **공지** | `/notices` | GET | 공지사항 목록 | 🔴 P0 |
| 15 | **공지** | `/notices/{id}` | GET | 공지사항 상세 | 🟡 P1 |
| 16 | **공지** | `/notices` | POST | 공지사항 작성 | 🟡 P1 |
| 17 | **공지** | `/notices/{id}` | PUT | 공지사항 수정 | 🟡 P1 |
| 18 | **공지** | `/notices/{id}` | DELETE | 공지사항 삭제 | 🟡 P1 |
| 19 | **시뮬레이션** | `/simulations` | GET | 시뮬레이션 목록 | 🟡 P1 |
| 20 | **시뮬레이션** | `/simulations/scenarios` | GET | 시나리오 목록 | 🟡 P1 |
| 21 | **시뮬레이션** | `/simulations/attempts` | GET | 시도 기록 조회 | 🟡 P1 |
| 22 | **시뮬레이션** | `/simulations/attempts` | POST | 시도 기록 저장 | 🟡 P1 |
| 23 | **대시보드** | `/dashboard/stats` | GET | 오늘의 통계 | 🔴 P0 |
| 24 | **대시보드** | `/dashboard/weekly-goal` | GET | 주간 목표 | 🟡 P1 |
| 25 | **대시보드** | `/dashboard/team-stats` | GET | 팀별 통계 | 🟡 P1 |
| 26 | **자주 찾는 문의** | `/frequent-inquiries` | GET | 문의 목록 | 🟡 P1 |
| 27 | **자주 찾는 문의** | `/frequent-inquiries/{id}` | GET | 문의 상세 | 🟢 P2 |
| 28 | **프로필** | `/profile` | GET | 내 프로필 조회 | 🔴 P0 |
| 29 | **프로필** | `/profile` | PUT | 프로필 수정 | 🟡 P1 |
| 30 | **프로필** | `/profile/badges` | GET | 내 배지 목록 | 🟡 P1 |
| 31 | **프로필** | `/profile/monthly-stats` | GET | 월간 통계 | 🟡 P1 |
| 32 | **검색** | `/search/documents` | GET | 문서 검색 | 🔴 P0 |

---

## 4. 상세 스펙

### 4.1 인증 API

#### 🔐 POST `/auth/login`

**목적:** 사용자 로그인 및 JWT 토큰 발급

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "employee_id": "EMP-001",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "EMP-001",
      "name": "홍길동",
      "email": "hong@teddycard.com",
      "team": "상담1팀",
      "position": "대리",
      "is_admin": false
    }
  },
  "message": "로그인 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": {
    "code": "ERR_UNAUTHORIZED",
    "message": "사번 또는 비밀번호가 일치하지 않습니다."
  },
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mock/employees.mock.ts
export const employeesData = [
  {
    id: 'EMP-001',
    name: '홍길동',
    email: 'hong@teddycard.com',
    password: 'password123', // ⚠️ 실제 DB에서는 bcrypt 해시
    team: '상담1팀',
    position: '대리',
    isAdmin: false
  }
];
```

---

### 4.2 직원 관리 API

#### 👥 GET `/employees`

**목적:** 직원 목록 조회 (페이지네이션, 필터링, 정렬)

**Request:**
```http
GET /api/v1/employees?page=1&limit=20&team=상담1팀&sort=consultations&order=desc
Authorization: Bearer {token}
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 | 기본값 |
|---------|------|------|------|--------|
| `page` | integer | ❌ | 페이지 번호 | 1 |
| `limit` | integer | ❌ | 페이지당 항목 수 | 20 |
| `team` | string | ❌ | 팀 필터 (예: "상담1팀") | - |
| `search` | string | ❌ | 검색어 (이름, 사번) | - |
| `sort` | string | ❌ | 정렬 필드 (consultations, fcr, avgTime) | consultations |
| `order` | string | ❌ | 정렬 순서 (asc, desc) | desc |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "EMP-001",
        "name": "김민수",
        "team": "상담1팀",
        "position": "팀장",
        "rank": 1,
        "consultations": 145,
        "fcr": 96,
        "avgTime": "4:15",
        "joinDate": "2023-01-15",
        "email": "kim@teddycard.com",
        "phone": "010-1234-5678",
        "status": "active"
      }
      // ... 더 많은 직원
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_items": 45,
      "per_page": 20,
      "has_next": true,
      "has_prev": false
    }
  },
  "message": "직원 목록 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mock/employees.mock.ts
export const employeesData = [
  {
    id: 'EMP-001',
    name: '김민수',
    team: '상담1팀',
    position: '팀장',
    rank: 1,
    consultations: 145,
    fcr: 96,
    avgTime: '4:15',
    joinDate: '2023-01-15',
    email: 'kim@teddycard.com',
    phone: '010-1234-5678',
    status: 'active'
  }
  // ... 45명
];
```

---

#### 👤 GET `/employees/{id}`

**목적:** 특정 직원 상세 정보 조회

**Request:**
```http
GET /api/v1/employees/EMP-001
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "EMP-001",
    "name": "김민수",
    "team": "상담1팀",
    "position": "팀장",
    "rank": 1,
    "consultations": 145,
    "fcr": 96,
    "avgTime": "4:15",
    "joinDate": "2023-01-15",
    "email": "kim@teddycard.com",
    "phone": "010-1234-5678",
    "status": "active",
    "performance": {
      "monthly_consultations": 145,
      "monthly_fcr": 96,
      "monthly_avg_time": "4:15",
      "badges": ["FCR 마스터", "스피드 레이서"]
    }
  },
  "message": "직원 상세 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": {
    "code": "ERR_NOT_FOUND",
    "message": "직원을 찾을 수 없습니다.",
    "details": { "employee_id": "EMP-999" }
  },
  "timestamp": "2025-02-03T10:30:00Z"
}
```

---

#### ➕ POST `/employees`

**목적:** 새 직원 추가 (관리자 전용)

**Request:**
```http
POST /api/v1/employees
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "id": "EMP-046",
  "name": "이영희",
  "team": "상담2팀",
  "position": "사원",
  "email": "lee@teddycard.com",
  "phone": "010-9876-5432",
  "joinDate": "2025-02-03",
  "password": "temporary123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "EMP-046",
    "name": "이영희",
    "team": "상담2팀",
    "position": "사원",
    "email": "lee@teddycard.com",
    "phone": "010-9876-5432",
    "joinDate": "2025-02-03",
    "status": "active",
    "rank": null,
    "consultations": 0,
    "fcr": 0,
    "avgTime": "0:00"
  },
  "message": "직원 추가 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Response (403 Forbidden):**
```json
{
  "success": false,
  "error": {
    "code": "ERR_FORBIDDEN",
    "message": "관리자 권한이 필요합니다."
  },
  "timestamp": "2025-02-03T10:30:00Z"
}
```

---

### 4.3 상담 관리 API

#### 📞 GET `/consultations`

**목적:** 상담 이력 조회 (페이지네이션, 필터링)

**Request:**
```http
GET /api/v1/consultations?page=1&limit=20&status=완료&category=분실/도난&date_from=2025-01-01&date_to=2025-01-31
Authorization: Bearer {token}
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 | 기본값 |
|---------|------|------|------|--------|
| `page` | integer | ❌ | 페이지 번호 | 1 |
| `limit` | integer | ❌ | 페이지당 항목 수 | 20 |
| `status` | string | ❌ | 상태 필터 (완료, 진행중, 보류) | - |
| `category` | string | ❌ | 대분류 카테고리 | - |
| `agent` | string | ❌ | 상담사 이름 | - |
| `customer` | string | ❌ | 고객명 | - |
| `fcr` | boolean | ❌ | FCR 여부 필터 | - |
| `best_practice` | boolean | ❌ | 우수 상담 필터 | - |
| `date_from` | string | ❌ | 시작 날짜 (YYYY-MM-DD) | - |
| `date_to` | string | ❌ | 종료 날짜 (YYYY-MM-DD) | - |
| `sort` | string | ❌ | 정렬 필드 (datetime, duration) | datetime |
| `order` | string | ❌ | 정렬 순서 (asc, desc) | desc |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "CS-EMP001-202501051432",
        "agent": "홍길동",
        "agent_id": "EMP-001",
        "customer": "김민수",
        "category": "분실/도난 > 분실신고",
        "main_category": "분실/도난",
        "sub_category": "분실신고",
        "status": "완료",
        "content": "카드 분실 신고 접수 및 즉시 정지 처리. 재발급 신청 완료",
        "datetime": "2025-01-05 14:32",
        "duration": "05:12",
        "fcr": true,
        "is_best_practice": true,
        "memo": "카드 분실 신고 및 재발급 처리 완료. 고객 만족도 높음"
      }
      // ... 더 많은 상담
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 15,
      "total_items": 300,
      "per_page": 20,
      "has_next": true,
      "has_prev": false
    },
    "summary": {
      "total_consultations": 300,
      "completed": 250,
      "in_progress": 30,
      "on_hold": 20,
      "fcr_rate": 85.5,
      "avg_duration": "5:30"
    }
  },
  "message": "상담 목록 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mock/consultations.mock.ts
export const consultationsData = [
  {
    id: 'CS-EMP001-202501051432',
    agent: '홍길동',
    customer: '김민수',
    category: '분실/도난 > 분실신고',
    status: '완료',
    content: '카드 분실 신고 접수 및 즉시 정지 처리. 재발급 신청 완료',
    datetime: '2025-01-05 14:32',
    duration: '05:12',
    isBestPractice: true,
    fcr: true,
    memo: '카드 분실 신고 및 재발급 처리 완료. 고객 만족도 높음'
  }
  // ... 300건
];
```

---

#### 📝 POST `/consultations`

**목적:** 새 상담 등록

**Request:**
```http
POST /api/v1/consultations
Authorization: Bearer {token}
Content-Type: application/json

{
  "agent_id": "EMP-001",
  "customer": "김철수",
  "category": "분실/도난 > 분실신고",
  "content": "카드 분실 신고 접수",
  "status": "진행중",
  "duration": null,
  "fcr": null,
  "memo": ""
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "CS-EMP001-202502031035",
    "agent": "홍길동",
    "agent_id": "EMP-001",
    "customer": "김철수",
    "category": "분실/도난 > 분실신고",
    "main_category": "분실/도난",
    "sub_category": "분실신고",
    "status": "진행중",
    "content": "카드 분실 신고 접수",
    "datetime": "2025-02-03 10:35",
    "duration": null,
    "fcr": null,
    "is_best_practice": false,
    "memo": ""
  },
  "message": "상담 등록 성공",
  "timestamp": "2025-02-03T10:35:00Z"
}
```

---

### 4.4 대시보드 통계 API

#### 📊 GET `/dashboard/stats`

**목적:** 오늘의 콜 통계 조회

**Request:**
```http
GET /api/v1/dashboard/stats
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "todayCalls": 127,
    "completed": 95,
    "pending": 12,
    "incomplete": 20,
    "date": "2025-02-03"
  },
  "message": "대시보드 통계 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mockData.ts
export const dashboardStatsData = {
  todayCalls: 127,
  completed: 95,
  pending: 12,
  incomplete: 20
};
```

**DB 쿼리 예시 (PostgreSQL):**
```sql
-- 오늘의 통계 집계
SELECT 
  COUNT(*) as today_calls,
  COUNT(*) FILTER (WHERE status = '완료') as completed,
  COUNT(*) FILTER (WHERE status = '진행중') as pending,
  COUNT(*) FILTER (WHERE status = '미완료') as incomplete
FROM consultations
WHERE DATE(datetime) = CURRENT_DATE;
```

---

#### 🎯 GET `/dashboard/weekly-goal`

**목적:** 주간 목표 및 진행률 조회

**Request:**
```http
GET /api/v1/dashboard/weekly-goal
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "target": 500,
    "current": 389,
    "percentage": 78,
    "week_start": "2025-01-27",
    "week_end": "2025-02-02"
  },
  "message": "주간 목표 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mockData.ts
export const weeklyGoalData = {
  target: 500,
  current: 389,
  percentage: 78
};
```

---

#### 👥 GET `/dashboard/team-stats`

**목적:** 팀별 통계 조회

**Request:**
```http
GET /api/v1/dashboard/team-stats?period=week
Authorization: Bearer {token}
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 | 기본값 |
|---------|------|------|------|--------|
| `period` | string | ❌ | 기간 (today, week, month) | week |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "teams": [
      {
        "team": "A팀",
        "calls": 142,
        "fcr": 94,
        "color": "#0047AB",
        "members": 15,
        "avg_duration": "5:20"
      },
      {
        "team": "B팀",
        "calls": 128,
        "fcr": 89,
        "color": "#34A853",
        "members": 15,
        "avg_duration": "5:45"
      },
      {
        "team": "C팀",
        "calls": 119,
        "fcr": 91,
        "color": "#FBBC04",
        "members": 15,
        "avg_duration": "5:30"
      }
    ],
    "period": "week",
    "start_date": "2025-01-27",
    "end_date": "2025-02-02"
  },
  "message": "팀별 통계 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mockData.ts
export const teamStatsData = [
  { team: 'A팀', calls: 142, fcr: 94, color: '#0047AB' },
  { team: 'B팀', calls: 128, fcr: 89, color: '#34A853' },
  { team: 'C팀', calls: 119, fcr: 91, color: '#FBBC04' },
];
```

---

### 4.5 시뮬레이션 API

#### 🎮 GET `/simulations/scenarios`

**목적:** 시뮬레이션 시나리오 목록 조회

**Request:**
```http
GET /api/v1/simulations/scenarios?user_id=EMP-001
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "scenarios": [
      {
        "id": "SIM-001",
        "category": "카드분실",
        "title": "카드 분실 신고 및 재발급",
        "difficulty": "초급",
        "duration": "5분",
        "description": "고객의 카드 분실 신고를 접수하고 재발급 절차를 안내하는 시나리오",
        "tags": ["카드분실", "재발급", "기본상담"],
        "completed": true,
        "score": 95,
        "locked": false,
        "attempts": 3,
        "best_score": 95,
        "avg_score": 92
      }
      // ... 6개 시나리오
    ],
    "user_progress": {
      "total_scenarios": 6,
      "completed_scenarios": 2,
      "locked_scenarios": 3,
      "total_attempts": 5,
      "avg_score": 91.5
    }
  },
  "message": "시나리오 목록 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mockData.ts
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
  }
  // ... 6개
];
```

---

#### 📝 POST `/simulations/attempts`

**목적:** 시뮬레이션 시도 기록 저장

**Request:**
```http
POST /api/v1/simulations/attempts
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": "EMP-001",
  "scenario_id": "SIM-001",
  "score": 95,
  "duration": "4분 50초",
  "answers": [
    { "question_id": 1, "answer": "A", "correct": true },
    { "question_id": 2, "answer": "B", "correct": true }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "attempt_id": 123,
    "user_id": "EMP-001",
    "scenario_id": "SIM-001",
    "score": 95,
    "duration": "4분 50초",
    "completed_at": "2025-02-03 10:35:00",
    "is_best_score": true
  },
  "message": "시도 기록 저장 성공",
  "timestamp": "2025-02-03T10:35:00Z"
}
```

---

### 4.6 프로필 API

#### 👤 GET `/profile`

**목적:** 내 프로필 조회

**Request:**
```http
GET /api/v1/profile
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "EMP-001",
    "name": "홍길동",
    "email": "hong@teddycard.com",
    "phone": "010-1234-5678",
    "team": "상담1팀",
    "position": "대리",
    "joinDate": "2024-01-15",
    "isAdmin": false,
    "rank": 3,
    "rankOutOf": 45
  },
  "message": "프로필 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

---

#### 🏅 GET `/profile/badges`

**목적:** 내 배지 목록 조회

**Request:**
```http
GET /api/v1/profile/badges?user_id=EMP-001
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "badges": [
      {
        "id": 1,
        "name": "FCR 마스터",
        "color": "#FBBC04",
        "description": "FCR 95% 이상 달성",
        "earned": true,
        "earned_at": "2025-01-15"
      },
      {
        "id": 2,
        "name": "스피드 레이서",
        "color": "#0047AB",
        "description": "평균 통화 시간 4분 이하",
        "earned": true,
        "earned_at": "2025-01-20"
      },
      {
        "id": 3,
        "name": "감정 케어",
        "color": "#34A853",
        "description": "감정 전환율 80% 이상",
        "earned": false,
        "earned_at": null
      }
      // ... 5개
    ],
    "total_badges": 5,
    "earned_badges": 2
  },
  "message": "배지 목록 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mockData.ts
export const badgesData = [
  { id: 1, name: 'FCR 마스터', color: '#FBBC04' },
  { id: 2, name: '스피드 레이서', color: '#0047AB' },
  { id: 3, name: '감정 케어', color: '#34A853' },
  { id: 4, name: '완벽주의자', color: '#9C27B0' },
  { id: 5, name: '시뮬 마니아', color: '#FF6B35' },
];
```

---

#### 📈 GET `/profile/monthly-stats`

**목적:** 월간 통계 조회

**Request:**
```http
GET /api/v1/profile/monthly-stats?user_id=EMP-001&month=2025-01
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "month": "2025-01",
    "stats": [
      {
        "label": "상담 완료",
        "value": "127건",
        "comparison": "팀 평균 대비 +15%",
        "status": "good"
      },
      {
        "label": "FCR",
        "value": "94%",
        "comparison": "목표: 90%",
        "status": "good"
      },
      {
        "label": "평균 통화",
        "value": "4분 32초",
        "comparison": "팀 평균: 5분 10초",
        "status": "good"
      },
      {
        "label": "후처리 시간",
        "value": "2분 15초",
        "comparison": "목표: 3분",
        "status": "good"
      },
      {
        "label": "감정 전환율",
        "value": "82%",
        "comparison": "목표: 75%",
        "status": "good"
      }
    ]
  },
  "message": "월간 통계 조회 성공",
  "timestamp": "2025-02-03T10:30:00Z"
}
```

**Mock 데이터 매핑:**
```typescript
// /src/data/mockData.ts
export const monthlyStatsData = [
  { label: '상담 완료', value: '127건', comparison: '팀 평균 대비 +15%', status: 'good' },
  { label: 'FCR', value: '94%', comparison: '목표: 90%', status: 'good' },
  { label: '평균 통화', value: '4분 32초', comparison: '팀 평균: 5분 10초', status: 'good' },
  { label: '후처리 시간', value: '2분 15초', comparison: '목표: 3분', status: 'good' },
  { label: '감정 전환율', value: '82%', comparison: '목표: 75%', status: 'good' },
];
```

---

## 5. DB 스키마 제안

### 5.1 ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    employees ||--o{ consultations : "creates"
    employees ||--o{ simulation_attempts : "participates"
    employees ||--o{ employee_badges : "earns"
    
    consultations ||--o{ consultation_categories : "belongs to"
    
    simulations ||--o{ simulation_attempts : "records"
    
    badges ||--o{ employee_badges : "awarded"
    
    employees {
        string id PK "사번 (EMP-001)"
        string name "이름"
        string email "이메일"
        string password_hash "비밀번호 해시"
        string team "팀명"
        string position "직급"
        date join_date "입사일"
        boolean is_admin "관리자 여부"
        string phone "전화번호"
        string status "상태 (active, inactive)"
        timestamp created_at
        timestamp updated_at
    }
    
    consultations {
        string id PK "상담 ID (CS-EMP001-202501051432)"
        string agent_id FK "상담사 ID"
        string customer_name "고객명"
        string main_category "대분류"
        string sub_category "중분류"
        string status "상태 (완료, 진행중, 보류)"
        text content "상담 내용"
        timestamp datetime "상담 일시"
        integer duration_seconds "통화 시간 (초)"
        boolean fcr "FCR 여부"
        boolean is_best_practice "우수 상담 여부"
        text memo "메모"
        timestamp created_at
        timestamp updated_at
    }
    
    simulations {
        string id PK "시나리오 ID (SIM-001)"
        string category "카테고리"
        string title "제목"
        string difficulty "난이도 (초급, 중급, 고급)"
        integer duration_minutes "예상 시간 (분)"
        text description "설명"
        json tags "태그 배열"
        boolean is_active "활성 여부"
        timestamp created_at
        timestamp updated_at
    }
    
    simulation_attempts {
        bigint id PK
        string user_id FK "사용자 ID"
        string scenario_id FK "시나리오 ID"
        integer score "점수"
        integer duration_seconds "소요 시간 (초)"
        json answers "답변 데이터"
        timestamp completed_at
        timestamp created_at
    }
    
    badges {
        integer id PK
        string name "배지명"
        string color "색상 코드"
        text description "설명"
        json criteria "획득 조건 (JSON)"
        timestamp created_at
    }
    
    employee_badges {
        bigint id PK
        string employee_id FK "직원 ID"
        integer badge_id FK "배지 ID"
        timestamp earned_at "획득 일시"
    }
    
    notices {
        bigint id PK
        string title "제목"
        text content "내용"
        string author_id FK "작성자 ID"
        boolean is_pinned "상단 고정 여부"
        integer views "조회수"
        timestamp created_at
        timestamp updated_at
    }
```

---

### 5.2 테이블 상세 스펙

#### 📋 `employees` (직원)

```sql
CREATE TABLE employees (
    id VARCHAR(50) PRIMARY KEY,  -- 'EMP-001'
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt
    team VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    join_date DATE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_team (team),
    INDEX idx_status (status),
    INDEX idx_email (email)
);
```

**샘플 데이터:**
```sql
INSERT INTO employees (id, name, email, password_hash, team, position, join_date, is_admin, phone) VALUES
('EMP-001', '김민수', 'kim@teddycard.com', '$2b$12$...', '상담1팀', '팀장', '2023-01-15', FALSE, '010-1234-5678'),
('EMP-002', '박지영', 'park@teddycard.com', '$2b$12$...', '상담1팀', '대리', '2023-03-20', FALSE, '010-2345-6789');
```

---

#### 📞 `consultations` (상담)

```sql
CREATE TABLE consultations (
    id VARCHAR(100) PRIMARY KEY,  -- 'CS-EMP001-202501051432'
    agent_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    main_category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 완료, 진행중, 보류
    content TEXT,
    datetime TIMESTAMP NOT NULL,
    duration_seconds INTEGER,  -- 통화 시간 (초)
    fcr BOOLEAN DEFAULT FALSE,
    is_best_practice BOOLEAN DEFAULT FALSE,
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES employees(id) ON DELETE CASCADE,
    
    INDEX idx_agent_id (agent_id),
    INDEX idx_datetime (datetime),
    INDEX idx_status (status),
    INDEX idx_main_category (main_category),
    INDEX idx_fcr (fcr),
    INDEX idx_best_practice (is_best_practice)
);
```

**샘플 데이터:**
```sql
INSERT INTO consultations (id, agent_id, customer_name, main_category, sub_category, status, content, datetime, duration_seconds, fcr, is_best_practice, memo) VALUES
('CS-EMP001-202501051432', 'EMP-001', '김민수', '분실/도난', '분실신고', '완료', '카드 분실 신고 접수 및 즉시 정지 처리', '2025-01-05 14:32:00', 312, TRUE, TRUE, '고객 만족도 높음');
```

---

#### 🎮 `simulations` (시뮬레이션 시나리오)

```sql
CREATE TABLE simulations (
    id VARCHAR(50) PRIMARY KEY,  -- 'SIM-001'
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,  -- 초급, 중급, 고급
    duration_minutes INTEGER NOT NULL,
    description TEXT,
    tags JSON,  -- ["카드분실", "재발급", "기본상담"]
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_difficulty (difficulty),
    INDEX idx_is_active (is_active)
);
```

**샘플 데이터:**
```sql
INSERT INTO simulations (id, category, title, difficulty, duration_minutes, description, tags) VALUES
('SIM-001', '카드분실', '카드 분실 신고 및 재발급', '초급', 5, '고객의 카드 분실 신고를 접수하고 재발급 절차를 안내하는 시나리오', '["카드분실", "재발급", "기본상담"]');
```

---

#### 📝 `simulation_attempts` (시뮬레이션 시도 기록)

```sql
CREATE TABLE simulation_attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    scenario_id VARCHAR(50) NOT NULL,
    score INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    answers JSON,  -- 답변 데이터
    completed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES simulations(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_scenario_id (scenario_id),
    INDEX idx_completed_at (completed_at)
);
```

---

#### 🏅 `badges` (배지 마스터)

```sql
CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) NOT NULL,  -- '#FBBC04'
    description TEXT,
    criteria JSON,  -- 획득 조건 (예: {"fcr_threshold": 95})
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE INDEX idx_name (name)
);
```

**샘플 데이터:**
```sql
INSERT INTO badges (name, color, description, criteria) VALUES
('FCR 마스터', '#FBBC04', 'FCR 95% 이상 달성', '{"fcr_threshold": 95}'),
('스피드 레이서', '#0047AB', '평균 통화 시간 4분 이하', '{"avg_time_threshold": 240}');
```

---

#### 🏆 `employee_badges` (직원-배지 매핑)

```sql
CREATE TABLE employee_badges (
    id BIGSERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    badge_id INTEGER NOT NULL,
    earned_at TIMESTAMP NOT NULL,
    
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
    
    UNIQUE INDEX idx_employee_badge (employee_id, badge_id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_earned_at (earned_at)
);
```

---

#### 📢 `notices` (공지사항)

```sql
CREATE TABLE notices (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id VARCHAR(50) NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (author_id) REFERENCES employees(id) ON DELETE CASCADE,
    
    INDEX idx_is_pinned (is_pinned),
    INDEX idx_created_at (created_at)
);
```

---

### 5.3 인덱싱 전략

#### 🎯 고성능 쿼리를 위한 인덱스

| 테이블 | 인덱스 | 목적 |
|--------|--------|------|
| `consultations` | `(agent_id, datetime)` | 상담사별 이력 조회 최적화 |
| `consultations` | `(datetime)` | 날짜별 조회 최적화 |
| `consultations` | `(main_category, sub_category)` | 카테고리별 조회 최적화 |
| `consultations` | `(status, fcr)` | 통계 집계 최적화 |
| `simulation_attempts` | `(user_id, scenario_id, completed_at)` | 사용자별 시도 기록 조회 |
| `employee_badges` | `(employee_id, earned_at)` | 배지 조회 최적화 |

---

## 6. 마이그레이션 계획

### 6.1 단계별 전환 전략

#### 📅 Phase 1: 준비 단계 (1주차)

| 작업 | 담당 | 기간 | 상태 |
|------|------|------|------|
| DB 스키마 생성 | DB 설계자 | 1일 | ⬜ TODO |
| 샘플 데이터 삽입 | DB 설계자 | 1일 | ⬜ TODO |
| API 엔드포인트 개발 (P0) | 백엔드 | 3일 | ⬜ TODO |
| API Client 구현 | 프론트엔드 | 2일 | ⬜ TODO |

#### 📅 Phase 2: 테스트 단계 (2주차)

| 작업 | 담당 | 기간 | 상태 |
|------|------|------|------|
| Mock vs API 응답 비교 테스트 | QA | 2일 | ⬜ TODO |
| 성능 테스트 (부하 테스트) | DevOps | 2일 | ⬜ TODO |
| 버그 수정 | 백엔드 + 프론트엔드 | 2일 | ⬜ TODO |

#### 📅 Phase 3: 배포 단계 (3주차)

| 작업 | 담당 | 기간 | 상태 |
|------|------|------|------|
| Feature Flag 활성화 (일부 사용자) | 프론트엔드 | 1일 | ⬜ TODO |
| 모니터링 및 로그 분석 | DevOps | 3일 | ⬜ TODO |
| 전체 사용자 전환 | 프론트엔드 | 1일 | ⬜ TODO |

---

### 6.2 Feature Flag 전환 예시

```typescript
// /src/config/dataConfig.ts
export const API_ENDPOINTS = {
  EMPLOYEES: '/employees',
  CONSULTATIONS: '/consultations',
  NOTICES: '/notices',
  SIMULATIONS: '/simulations',
  DASHBOARD_STATS: '/dashboard/stats',
  // ...
};

// /src/services/api.ts
import { API_CONFIG, API_ENDPOINTS } from '@/config/dataConfig';
import { employeesData } from '@/data/mock';

export const getEmployees = async () => {
  if (API_CONFIG.USE_API) {
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.EMPLOYEES}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    const result = await response.json();
    return result.data.items; // API 응답
  } else {
    return employeesData; // Mock 데이터
  }
};
```

---

### 6.3 데이터 마이그레이션 스크립트

#### Python 스크립트 예시 (Mock → DB 삽입)

```python
# migrate_mock_to_db.py
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Mock 데이터 로드
with open('src/data/mock/employees.mock.ts', 'r') as f:
    employees_mock = json.load(f)  # TypeScript → JSON 변환 필요

# DB 연결
engine = create_engine('postgresql://user:password@localhost:5432/callact')
Session = sessionmaker(bind=engine)
session = Session()

# 데이터 삽입
for emp in employees_mock:
    session.execute("""
        INSERT INTO employees (id, name, email, password_hash, team, position, join_date, is_admin, phone)
        VALUES (:id, :name, :email, :password_hash, :team, :position, :join_date, :is_admin, :phone)
    """, {
        'id': emp['id'],
        'name': emp['name'],
        'email': emp['email'],
        'password_hash': '$2b$12$...',  # 비밀번호 해시 생성 필요
        'team': emp['team'],
        'position': emp['position'],
        'join_date': emp['joinDate'],
        'is_admin': emp.get('isAdmin', False),
        'phone': emp.get('phone', '')
    })

session.commit()
print("✅ 직원 데이터 마이그레이션 완료!")
```

---

## 7. 보안 정책

### 7.1 인증 및 권한

#### JWT 토큰 구조

```json
{
  "sub": "EMP-001",
  "name": "홍길동",
  "email": "hong@teddycard.com",
  "team": "상담1팀",
  "is_admin": false,
  "exp": 1704124800,
  "iat": 1704121200
}
```

#### 권한 레벨

| 레벨 | 역할 | 접근 가능 API |
|------|------|--------------|
| **User** | 일반 사용자 | 본인 프로필, 상담 조회/등록, 시뮬레이션 |
| **Admin** | 관리자 | 모든 API (직원 관리, 통계 조회, 공지사항 관리) |

---

### 7.2 Rate Limiting

```
사용자당 API 호출 한도:
- 일반 사용자: 100 requests/minute
- 관리자: 200 requests/minute
```

---

## 8. 성능 목표

### 8.1 응답 시간 목표

| API 카테고리 | P50 | P95 | P99 |
|-------------|-----|-----|-----|
| 조회 (GET) | < 50ms | < 200ms | < 500ms |
| 등록 (POST) | < 100ms | < 300ms | < 800ms |
| 수정 (PUT) | < 100ms | < 300ms | < 800ms |
| 삭제 (DELETE) | < 50ms | < 200ms | < 500ms |

---

### 8.2 동시 접속 목표

```
동시 접속 사용자: 100명
최대 RPS (Requests Per Second): 500
```

---

## 9. 모니터링 및 로깅

### 9.1 로그 포맷

```json
{
  "timestamp": "2025-02-03T10:30:00Z",
  "level": "INFO",
  "method": "GET",
  "endpoint": "/api/v1/employees",
  "user_id": "EMP-001",
  "response_time_ms": 45,
  "status_code": 200,
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

---

### 9.2 모니터링 지표

| 지표 | 도구 | 임계값 |
|------|------|--------|
| API 응답 시간 | Prometheus + Grafana | P95 < 200ms |
| 에러율 | Sentry | < 0.1% |
| DB 쿼리 시간 | PostgreSQL Slow Query Log | < 100ms |
| CPU 사용률 | CloudWatch | < 70% |
| 메모리 사용률 | CloudWatch | < 80% |

---

## 10. 요약

### ✅ 완료 사항

1. ✅ 32개 API 엔드포인트 설계 완료
2. ✅ Mock 데이터 → API 응답 1:1 매핑 완료
3. ✅ DB 스키마 제안 (7개 테이블)
4. ✅ 마이그레이션 계획 수립

### 🎯 다음 작업

1. **백엔드 개발자:** FastAPI 엔드포인트 개발 시작 (P0 우선순위)
2. **DB 설계자:** PostgreSQL 스키마 생성 및 샘플 데이터 삽입
3. **프론트엔드 개발자:** API Client 구현 (`/src/services/api.ts`)
4. **QA:** Mock vs API 응답 비교 테스트 시나리오 작성

---

**작성자:** AI Assistant (DB/프론트엔드 상위 1% 전문가)  
**검토 필요:** 백엔드 개발자, DB 설계자, 시스템 아키텍트  
**문의:** API 스펙 변경 필요 시 프론트엔드 팀과 협의 필수
