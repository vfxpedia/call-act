# 07. MockData 구조

> **mockData.ts 파일의 데이터 구조 및 화면 연동 상세**

## 목차
- [1. MockData 개요](#1-mockdata-개요)
- [2. 데이터 구조 상세](#2-데이터-구조-상세)
- [3. 화면 연동](#3-화면-연동)
- [4. LocalStorage 활용](#4-localstorage-활용)
- [5. DB 전환 가이드](#5-db-전환-가이드)

---

## 1. MockData 개요

### 1.1 파일 정보

| 항목 | 값 |
|------|-----|
| **파일 경로** | `/src/data/mockData.ts` |
| **파일 크기** | 약 2,500줄 |
| **데이터 개수** | 200+ 건 |
| **용도** | MVP 개발용 Mock 데이터 |

### 1.2 포함 데이터

```typescript
// mockData.ts 구조
export const noticesData = [...];           // 공지사항 (15개)
export const consultationsData = [...];     // 상담 이력 (100+개)
export const frequentInquiriesData = [...]; // 자주 찾는 문의 (5개)
export const employeesData = [...];         // 사원 데이터 (45명)
export const dashboardStats = {...};        // 대시보드 통계
export const cardData = [...];              // 카드 정보
```

### 1.3 데이터 흐름

```
mockData.ts
    ↓
LocalStorage (App.tsx에서 초기화)
    ↓
각 페이지에서 읽기/쓰기
    ↓
화면 렌더링
```

---

## 2. 데이터 구조 상세

### 2.1 noticesData (공지사항)

**개수**: 15개  
**타입**: Array<Notice>

```typescript
interface Notice {
  id: number;                    // 공지사항 ID
  tag: string;                   // 태그 (긴급, 이벤트, 시스템, 교육, 정책, 근무, 복지)
  title: string;                 // 제목
  date: string;                  // 작성일 (YYYY-MM-DD)
  author: string;                // 작성자
  views: number;                 // 조회수
  pinned: boolean;               // 상단 고정 여부
  content: string;               // 내용 (상세)
}
```

**샘플 데이터**:
```typescript
{
  id: 1,
  tag: '긴급',
  title: 'KT 화재로 인한 통신망 장애 대응',
  date: '2025-01-05',
  author: '관리자',
  views: 245,
  pinned: true,
  content: 'KT 아현지사 화재로 인한 통신망 장애가 발생했습니다...'
}
```

**태그별 분포**:
| 태그 | 개수 | 예시 |
|------|------|------|
| 긴급 | 1 | KT 화재 대응 |
| 이벤트 | 3 | 메가커피 프로모션, 우수 상담사 시상식 |
| 시스템 | 2 | 신규 상담 시스템 업데이트 |
| 교육 | 3 | 신규 입사자 온보딩, FCR 워크샵 |
| 정책 | 2 | 카드 분실 프로세스 변경 |
| 근무 | 2 | 설 연휴 근무, 재택근무 확대 |
| 복지 | 2 | 건강검진, 카페테리아 메뉴 개편 |

**사용 화면**:
- NoticePage (공지사항 목록)
- AdminNoticePage (관리자 공지 관리)
- DashboardPage (최근 공지사항 위젯)

---

### 2.2 consultationsData (상담 이력)

**개수**: 100+ 개  
**타입**: Array<Consultation>

```typescript
interface Consultation {
  id: string;                    // 상담 ID (예: CS-20250105-1432)
  agent: string;                 // 상담사명
  customer: string;              // 고객명
  category: string;              // 카테고리 (카드분실, 해외결제, 포인트 등)
  status: string;                // 상태 (완료, 진행중, 미완료)
  content: string;               // 상담 내용 요약
  datetime: string;              // 상담 일시 (YYYY-MM-DD HH:mm)
  duration: string;              // 상담 시간 (MM:SS)
  isBestPractice: boolean;       // 우수 상담 여부
  fcr: boolean;                  // FCR 달성 여부
  memo: string;                  // 상담사 메모
}
```

**샘플 데이터**:
```typescript
{
  id: 'CS-20250105-1432',
  agent: '홍길동',
  customer: '김민수',
  category: '카드분실',
  status: '완료',
  content: '카드 분실 신고 접수 및 즉시 정지 처리. 재발급 신청 완료',
  datetime: '2025-01-05 14:32',
  duration: '05:12',
  isBestPractice: true,
  fcr: true,
  memo: '카드 분실 신고 및 재발급 처리 완료. 고객 만족도 높음'
}
```

**카테고리별 분포**:
| 카테고리 | 개수 | 비율 |
|----------|------|------|
| 카드분실 | 25 | 25% |
| 해외결제 | 20 | 20% |
| 포인트 | 15 | 15% |
| 수수료문의 | 12 | 12% |
| 한도조회 | 10 | 10% |
| 프로모션 | 10 | 10% |
| 기타 | 8 | 8% |

**상태별 분포**:
| 상태 | 개수 | 비율 |
|------|------|------|
| 완료 | 92 | 92% |
| 진행중 | 5 | 5% |
| 미완료 | 3 | 3% |

**FCR 달성률**: 85% (85건/100건)

**사용 화면**:
- ConsultationHistoryPage (상담 이력 조회)
- DashboardPage (최근 상담 위젯)
- AdminConsultationManagePage (관리자 상담 관리)

---

### 2.3 frequentInquiriesData (자주 찾는 문의)

**개수**: 5개  
**타입**: Array<FrequentInquiry>

```typescript
interface FrequentInquiry {
  id: number;                    // ID
  keyword: string;               // 키워드
  question: string;              // 질문
  count: number;                 // 문의 건수
  trend: 'up' | 'down' | 'same'; // 추세
}
```

**데이터**:
```typescript
[
  { id: 1, keyword: '카드 분실', question: '카드를 분실했어요. 어떻게 해야 하나요?', count: 45, trend: 'up' },
  { id: 2, keyword: '해외 결제', question: '해외에서 카드가 안 됩니다.', count: 38, trend: 'up' },
  { id: 3, keyword: '포인트 적립', question: '포인트가 적립 안 됐어요.', count: 32, trend: 'same' },
  { id: 4, keyword: '연회비 환불', question: '연회비 환불 받을 수 있나요?', count: 28, trend: 'down' },
  { id: 5, keyword: '한도 증액', question: '신용한도를 올리고 싶어요.', count: 25, trend: 'up' }
]
```

**사용 화면**:
- DashboardPage (자주 찾는 문의 위젯)

---

### 2.4 employeesData (사원 데이터)

**개수**: 45명 (상담1팀 18명, 상담2팀 15명, 상담3팀 12명)  
**타입**: Array<Employee>

```typescript
interface Employee {
  id: string;                    // 사원 ID (예: EMP-001)
  name: string;                  // 이름
  team: string;                  // 팀 (상담1팀, 상담2팀, 상담3팀)
  position: string;              // 직급 (사원, 대리, 과장, 차장, 부장)
  consultations: number;         // 상담 건수
  fcr: number;                   // FCR 달성률 (%)
  avgTime: string;               // 평균 상담 시간 (M:SS)
  rank: number;                  // 순위 (1~45)
  trend: 'up' | 'down' | 'same'; // 추세
  status: 'active' | 'inactive' | 'vacation'; // 상태
  joinDate: string;              // 입사일 (YYYY-MM-DD)
  email: string;                 // 이메일
  phone: string;                 // 전화번호
}
```

**샘플 데이터**:
```typescript
{
  id: 'EMP-002',
  name: '김민수',
  team: '상담1팀',
  position: '사원',
  consultations: 145,
  fcr: 96,
  avgTime: '4:15',
  rank: 1,
  trend: 'up',
  status: 'active',
  joinDate: '2024-03-01',
  email: 'kim@teddycard.com',
  phone: '010-2345-6789'
}
```

**순위 기준** (우선순위):
1. **상담 건수** (consultations) - 높은 순
2. **FCR 달성률** (fcr) - 높은 순
3. **평균 상담 시간** (avgTime) - 빠른 순

**TOP 10 상담사**:
| 순위 | 이름 | 팀 | 상담 건수 | FCR | 평균 시간 |
|------|------|-----|-----------|-----|-----------|
| 🥇 1위 | 김민수 | 상담1팀 | 145 | 96% | 4:15 |
| 🥈 2위 | 최은정 | 상담3팀 | 140 | 96% | 4:18 |
| 🥉 3위 | 이영희 | 상담2팀 | 138 | 95% | 4:20 |
| 4위 | 이영표 | 상담1팀 | 135 | 95% | 4:28 |
| 5위 | 강민지 | 상담2팀 | 134 | 94% | 4:25 |
| 6위 | 문성민 | 상담3팀 | 133 | 95% | 4:30 |
| 7위 | 손흥민 | 상담2팀 | 132 | 93% | 4:35 |
| 8위 | 서지은 | 상담3팀 | 131 | 94% | 4:33 |
| 9위 | 조현우 | 상담1팀 | 130 | 93% | 4:40 |
| 10위 | 전지현 | 상담2팀 | 129 | 94% | 4:42 |

**팀별 인원 분포**:
| 팀 | 인원 | 비율 |
|------|------|------|
| 상담1팀 | 18명 | 40% |
| 상담2팀 | 15명 | 33% |
| 상담3팀 | 12명 | 27% |

**직급별 분포**:
| 직급 | 인원 | 비율 |
|------|------|------|
| 사원 | 20명 | 44% |
| 대리 | 20명 | 44% |
| 과장 | 5명 | 11% |

**사용 화면**:
- EmployeesPage (사원 관리)
- DashboardPage (우수 상담사 위젯)
- AdminManagePage (관리자 사원 관리)
- ProfilePage (프로필 조회)

---

### 2.5 dashboardStats (대시보드 통계)

**타입**: Object

```typescript
interface DashboardStats {
  todayConsultations: number;      // 금일 상담 건수
  avgConsultationTime: string;     // 평균 상담 시간
  fcrRate: number;                 // FCR 달성률 (%)
  ongoingConsultations: number;    // 진행 중 상담 건수
}
```

**데이터**:
```typescript
export const dashboardStats = {
  todayConsultations: 127,
  avgConsultationTime: '4:35',
  fcrRate: 89,
  ongoingConsultations: 12
};
```

**사용 화면**:
- DashboardPage (통계 카드 위젯)

---

### 2.6 cardData (카드 정보)

**개수**: 다수  
**타입**: Array<CardInfo>

```typescript
interface CardInfo {
  cardNumber: string;              // 카드 번호 (마스킹)
  cardType: string;                // 카드 종류
  issuedDate: string;              // 발급일
  expiryDate: string;              // 만료일
  status: string;                  // 상태 (정상, 정지, 만료)
}
```

**사용 화면**:
- RealTimeConsultationPage (고객 카드 정보 조회)
- AfterCallWorkPage (카드 정보 표시)

---

## 3. 화면 연동

### 3.1 데이터 흐름 다이어그램

```
App.tsx (초기화)
    ↓
localStorage.setItem('employees', JSON.stringify(employeesData))
localStorage.setItem('notices', JSON.stringify(noticesData))
    ↓
각 페이지 컴포넌트
    ↓
const employees = JSON.parse(localStorage.getItem('employees') || '[]')
    ↓
화면 렌더링
```

### 3.2 화면별 사용 데이터

#### 3.2.1 DashboardPage

**사용 데이터**:
- `dashboardStats` → 통계 카드 (금일 상담, FCR 등)
- `consultationsData` → 최근 상담 이력 (최근 5건)
- `employeesData` → 우수 상담사 (Top 5)
- `noticesData` → 최근 공지사항 (최근 3건)
- `frequentInquiriesData` → 자주 찾는 문의 (전체)

**코드 예시**:
```typescript
// DashboardPage.tsx
const [stats, setStats] = useState(dashboardStats);
const [recentConsultations, setRecentConsultations] = useState(
  consultationsData.slice(0, 5)
);
const [topAgents, setTopAgents] = useState(
  employeesData.slice(0, 5)
);
```

#### 3.2.2 ConsultationHistoryPage

**사용 데이터**:
- `consultationsData` → 전체 상담 이력

**기능**:
- 페이지네이션 (10건씩)
- 필터링 (카테고리, 상태, 날짜)
- 검색 (상담 ID, 고객명)

**코드 예시**:
```typescript
// ConsultationHistoryPage.tsx
const [consultations, setConsultations] = useState(
  JSON.parse(localStorage.getItem('consultations') || '[]')
);

// 필터링
const filtered = consultations.filter(c => 
  c.category === selectedCategory || selectedCategory === '전체'
);
```

#### 3.2.3 EmployeesPage

**사용 데이터**:
- `employeesData` → 전체 사원 데이터

**기능**:
- 사원 추가 (AddEmployeeModal)
- 사원 수정 (EditEmployeeModal)
- 사원 삭제
- 검색 (이름, 팀, 직급)

**코드 예시**:
```typescript
// EmployeesPage.tsx
const [employees, setEmployees] = useState(
  JSON.parse(localStorage.getItem('employees') || '[]')
);

// 사원 추가
const handleAddEmployee = (newEmployee: Employee) => {
  const updated = [...employees, newEmployee];
  setEmployees(updated);
  localStorage.setItem('employees', JSON.stringify(updated));
};
```

#### 3.2.4 NoticePage

**사용 데이터**:
- `noticesData` → 전체 공지사항

**기능**:
- 페이지네이션 (10건씩)
- 필터링 (태그)
- 검색 (제목, 내용)
- 조회수 증가

**코드 예시**:
```typescript
// NoticePage.tsx
const [notices, setNotices] = useState(
  JSON.parse(localStorage.getItem('notices') || '[]')
);

// 조회수 증가
const handleViewNotice = (id: number) => {
  const updated = notices.map(n => 
    n.id === id ? { ...n, views: n.views + 1 } : n
  );
  setNotices(updated);
  localStorage.setItem('notices', JSON.stringify(updated));
};
```

---

## 4. LocalStorage 활용

### 4.1 초기화 (App.tsx)

```typescript
// App.tsx
useEffect(() => {
  const savedEmployees = localStorage.getItem('employees');
  if (!savedEmployees) {
    // 초기 데이터가 없으면 mockData 저장
    localStorage.setItem('employees', JSON.stringify(employeesData));
    console.log('✅ Initial employee data loaded to LocalStorage');
  }
}, []);
```

### 4.2 데이터 읽기

```typescript
// 데이터 읽기 (기본값 포함)
const employees = JSON.parse(
  localStorage.getItem('employees') || '[]'
);

// 안전한 읽기 (try-catch)
let employees = [];
try {
  employees = JSON.parse(localStorage.getItem('employees') || '[]');
} catch (error) {
  console.error('Failed to parse employees data', error);
  employees = employeesData; // Fallback to mockData
}
```

### 4.3 데이터 쓰기

```typescript
// 데이터 쓰기
const updatedEmployees = [...employees, newEmployee];
localStorage.setItem('employees', JSON.stringify(updatedEmployees));

// 상태 동기화
setEmployees(updatedEmployees);
```

### 4.4 데이터 삭제

```typescript
// 특정 키 삭제
localStorage.removeItem('employees');

// 전체 삭제 (주의!)
localStorage.clear();
```

### 4.5 LocalStorage 키 목록

| 키 | 데이터 | 크기 (예상) |
|-----|--------|-------------|
| `user` | 로그인 사용자 정보 | 1KB |
| `employees` | 사원 데이터 (45명) | 20KB |
| `notices` | 공지사항 (15개) | 10KB |
| `consultations` | 상담 이력 (100+개) | 50KB |
| **합계** | - | **약 80KB** |

**⚠️ 주의**: LocalStorage 용량 제한은 브라우저마다 다르지만 일반적으로 **5-10MB**입니다.

---

## 5. DB 전환 가이드

### 5.1 전환 전략

#### 5.1.1 단계적 전환 (권장)

```
Phase 1: DB 설정 및 스키마 생성
    ↓
Phase 2: 초기 데이터 마이그레이션 (mockData → DB)
    ↓
Phase 3: API 엔드포인트 개발
    ↓
Phase 4: 프론트엔드 API 통합 (LocalStorage → API)
    ↓
Phase 5: 테스트 및 검증
```

#### 5.1.2 Dual Mode 운영 (개발 중)

```typescript
// config.ts
export const USE_API = process.env.VITE_USE_API === 'true';

// 데이터 가져오기
const getEmployees = async () => {
  if (USE_API) {
    // API 호출
    const response = await fetch('/api/employees');
    return await response.json();
  } else {
    // LocalStorage 사용
    return JSON.parse(localStorage.getItem('employees') || '[]');
  }
};
```

### 5.2 마이그레이션 스크립트

#### 5.2.1 Python 스크립트

```python
# migrate_mockdata.py
import json
import psycopg2
from datetime import datetime

# DB 연결
conn = psycopg2.connect(
    host="localhost",
    database="callact_db",
    user="postgres",
    password="password"
)
cur = conn.cursor()

# mockData.json 읽기 (TypeScript → JSON 변환 필요)
with open('mockData.json') as f:
    data = json.load(f)

# 사원 데이터 삽입
for emp in data['employees']:
    cur.execute("""
        INSERT INTO users (id, name, email, team, position, phone, join_date, total_consultations, fcr_rate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        emp['id'],
        emp['name'],
        f"{emp['email']}",
        emp['team'],
        emp['position'],
        emp['phone'],
        emp['joinDate'],
        emp['consultations'],
        emp['fcr']
    ))

conn.commit()
print(f"✅ Inserted {len(data['employees'])} employees")
```

#### 5.2.2 SQL 직접 삽입

```sql
-- 사원 데이터 삽입
INSERT INTO users (id, name, email, team, position, phone, join_date, total_consultations, fcr_rate) VALUES
('EMP-001', '홍길동', 'hong@teddycard.com', '상담1팀', '대리', '010-1234-5678', '2024-01-15', 127, 94),
('EMP-002', '김민수', 'kim@teddycard.com', '상담1팀', '사원', '010-2345-6789', '2024-03-01', 145, 96),
-- ... (나머지 43명)
;

-- 공지사항 삽입
INSERT INTO notices (id, title, content, tag, author, views, is_pinned, created_at) VALUES
(1, 'KT 화재로 인한 통신망 장애 대응', '...', '긴급', '관리자', 245, TRUE, '2025-01-05'),
-- ... (나머지 14개)
;
```

### 5.3 API 통합

#### 5.3.1 API 서비스 레이어

```typescript
// services/employeeService.ts
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const employeeService = {
  // 전체 사원 조회
  async getAll() {
    const response = await axios.get(`${API_URL}/api/employees`);
    return response.data;
  },
  
  // 사원 추가
  async create(employee: Employee) {
    const response = await axios.post(`${API_URL}/api/employees`, employee);
    return response.data;
  },
  
  // 사원 수정
  async update(id: string, employee: Partial<Employee>) {
    const response = await axios.put(`${API_URL}/api/employees/${id}`, employee);
    return response.data;
  },
  
  // 사원 삭제
  async delete(id: string) {
    await axios.delete(`${API_URL}/api/employees/${id}`);
  }
};
```

#### 5.3.2 페이지에서 사용

```typescript
// EmployeesPage.tsx
import { employeeService } from '@/services/employeeService';

const EmployeesPage = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadEmployees();
  }, []);
  
  const loadEmployees = async () => {
    try {
      setLoading(true);
      const data = await employeeService.getAll();
      setEmployees(data);
    } catch (error) {
      console.error('Failed to load employees', error);
      toast.error('사원 데이터를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddEmployee = async (newEmployee: Employee) => {
    try {
      await employeeService.create(newEmployee);
      toast.success('사원이 추가되었습니다');
      loadEmployees(); // 목록 새로고침
    } catch (error) {
      toast.error('사원 추가에 실패했습니다');
    }
  };
  
  return (
    // UI 렌더링
  );
};
```

### 5.4 전환 체크리스트

#### 5.4.1 백엔드

- [ ] PostgreSQL DB 생성 및 스키마 설정
- [ ] pgvector 확장 설치
- [ ] FastAPI 프로젝트 초기화
- [ ] SQLAlchemy 모델 정의
- [ ] API 엔드포인트 개발
- [ ] mockData → DB 마이그레이션
- [ ] API 테스트 (Postman, Swagger)

#### 5.4.2 프론트엔드

- [ ] Axios 또는 Fetch 라이브러리 설정
- [ ] API 서비스 레이어 생성
- [ ] 환경 변수 설정 (VITE_API_URL)
- [ ] LocalStorage → API 전환
- [ ] 에러 핸들링 추가
- [ ] 로딩 상태 UI 추가
- [ ] 통합 테스트

---

**이전 문서**: [06_데이터베이스_설계.md](./06_데이터베이스_설계.md)  
**다음 문서**: [08_시나리오_데이터.md](./08_시나리오_데이터.md)
