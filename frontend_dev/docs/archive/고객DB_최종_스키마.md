# 고객 DB 최종 스키마 (Phase 10-4)

## 📋 개요

고객 정보 화면 구성을 위해 `birth_date`와 `address` 필드를 customers 테이블에 추가합니다.

---

## 🗄️ customers 테이블 최종 스키마

```sql
CREATE TABLE customers (
  -- 기본 식별자
  id VARCHAR(50) PRIMARY KEY,           -- 'CUST-TEDDY-00001'

  -- 기본 정보 (실제 데이터 저장, 마스킹은 Frontend에서)
  name VARCHAR(100) NOT NULL,           -- '김민수' (실제 이름)
  phone VARCHAR(20) NOT NULL,           -- '010-1234-5678' (실제 번호)
  
  -- ⭐ Phase 10-4: 추가 필드
  birth_date DATE,                      -- '1982-05-15' (생년월일)
  address TEXT,                         -- '서울시 강남구 테헤란로 123, 5동 301호'
  
  gender VARCHAR(10) DEFAULT 'unknown', -- 'male', 'female', 'unknown'
  age_group VARCHAR(10),                -- '20대', '30대', ... (기존 데이터 활용)
  grade VARCHAR(20) DEFAULT 'GENERAL',  -- 'VIP', 'GOLD', 'SILVER', 'GENERAL'

  -- 카드 정보
  card_type VARCHAR(100),               -- '테디카드 프리미엄'
  card_number_last4 VARCHAR(4),         -- '5678' (마지막 4자리만 저장)
  card_brand VARCHAR(20),               -- 'visa', 'mastercard', 'local'

  -- 고객 특성 태그 (LLM 가이던스용)
  personality_tags TEXT[],              -- ['impatient', 'detailed']
  communication_style JSONB,            -- {"speed": "fast", "tone": "formal"}

  -- 상담 통계
  total_consultations INT DEFAULT 0,
  resolved_first_call INT DEFAULT 0,
  last_consultation_date DATE,

  -- 타임스탬프
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

---

## 📊 필드 설명

### 1. birth_date (생년월일)
- **타입:** `DATE`
- **형식:** `YYYY-MM-DD` (예: `1982-05-15`)
- **필수 여부:** 선택 (NULL 허용)
- **용도:** 
  - 고객 정보 화면 표시
  - 연령대 자동 계산
  - 생일 축하 이벤트

**연령대 계산 로직:**
```sql
SELECT 
  birth_date,
  EXTRACT(YEAR FROM age(birth_date)) AS age,
  CASE 
    WHEN EXTRACT(YEAR FROM age(birth_date)) BETWEEN 10 AND 19 THEN '10대'
    WHEN EXTRACT(YEAR FROM age(birth_date)) BETWEEN 20 AND 29 THEN '20대'
    WHEN EXTRACT(YEAR FROM age(birth_date)) BETWEEN 30 AND 39 THEN '30대'
    WHEN EXTRACT(YEAR FROM age(birth_date)) BETWEEN 40 AND 49 THEN '40대'
    WHEN EXTRACT(YEAR FROM age(birth_date)) BETWEEN 50 AND 59 THEN '50대'
    WHEN EXTRACT(YEAR FROM age(birth_date)) BETWEEN 60 AND 69 THEN '60대'
    WHEN EXTRACT(YEAR FROM age(birth_date)) >= 70 THEN '70대'
    ELSE 'unknown'
  END AS age_group
FROM customers;
```

---

### 2. address (주소)
- **타입:** `TEXT`
- **형식:** 자유 텍스트 (예: `서울시 강남구 테헤란로 123, 5동 301호`)
- **필수 여부:** 선택 (NULL 허용)
- **용도:**
  - 고객 정보 화면 표시
  - 재발급 카드 배송지
  - 지역별 통계 분석

**주소 형식 예시:**
```
서울시 [구] [도로명] [건물번호], [동] [호수]
서울시 강남구 테헤란로 123, 5동 301호
서울시 서초구 반포대로 201, 12동 1502호
서울시 송파구 올림픽로 300, 3동 805호
```

---

## 🎨 프론트엔드 화면 구성

### 고객 정보 카드

```
고객 정보
┌─────────────────────────────────┐
│ 이름:      김*수                 │ ← 마스킹 (클릭 시 실명)
│ 전화:      010-****-5678         │ ← 마스킹 (클릭 시 실명)
│ 생년월일:  1982-05-15           │ ← 새로 추가
│ 주소:      서울시 강남구...     │ ← 새로 추가 (truncate)
└─────────────────────────────────┘
```

### TypeScript 타입 (CustomerInfo)

```typescript
export interface CustomerInfo {
  id: string;
  name: string;
  phone: string;
  
  // ⭐ Phase 10-4: 추가
  birthDate?: string;     // 'YYYY-MM-DD'
  address?: string;       // 전체 주소
  
  cardNumber: string;
  cardType: string;
  grade: string;
  
  // ... 기타 필드
}
```

---

## 🔐 개인정보 보호

### 마스킹 정책

| 필드 | 저장 형식 | 화면 표시 (기본) | 클릭 시 |
|------|----------|----------------|---------|
| name | 김민수 (실제) | 김*수 (마스킹) | 김민수 (3초) |
| phone | 010-1234-5678 | 010-****-5678 | 010-1234-5678 (3초) |
| birth_date | 1982-05-15 | 1982-05-15 | - (마스킹 불필요) |
| address | 서울시 강남구... | 서울시 강남구... (truncate) | - (마스킹 불필요) |

**마스킹 대상:**
- ✅ name (이름)
- ✅ phone (전화번호)

**마스킹 불필요:**
- ❌ birth_date (생년월일) - 일반 정보
- ❌ address (주소) - truncate로 긴 주소만 처리

---

## 📝 Mock 데이터 예시

```typescript
// /src/data/mockCustomerDB.ts
export const MOCK_CUSTOMER_DB: CustomerInfo[] = [
  {
    id: 'CUST-TEDDY-00001',
    name: '김민수',
    phone: '010-1234-5678',
    birthDate: '1982-05-15',
    address: '서울시 강남구 테헤란로 123, 5동 301호',
    cardNumber: '1234-5678-9012-3456',
    cardType: '테디카드 스탠다드',
    grade: 'GENERAL',
    gender: 'male',
    ageGroup: '40대',
    age: 42,
    personalityTags: ['normal', 'polite'],
    communicationStyle: { speed: 'moderate', tone: 'neutral' },
    totalConsultations: 3,
    lastConsultationDate: '2024-12-15',
  },
  // ... 추가 고객 데이터
];
```

---

## 🚀 API 응답 형식

### GET /api/v1/customers/{customer_id}

**응답:**
```json
{
  "id": "CUST-TEDDY-00001",
  "name": "김민수",
  "phone": "010-1234-5678",
  "birthDate": "1982-05-15",
  "address": "서울시 강남구 테헤란로 123, 5동 301호",
  "cardNumber": "1234-5678-9012-3456",
  "cardType": "테디카드 스탠다드",
  "grade": "GENERAL",
  "gender": "male",
  "ageGroup": "40대",
  "personalityTags": ["normal", "polite"],
  "communicationStyle": {
    "speed": "moderate",
    "tone": "neutral"
  },
  "totalConsultations": 3,
  "lastConsultationDate": "2024-12-15"
}
```

---

## 📊 데이터 생성 전략

### 2,500명 고객 데이터 생성 시

#### 1. birth_date 생성
```python
import random
from datetime import date, timedelta

def generate_birth_date(age_group: str) -> date:
    """연령대 기반 생년월일 생성"""
    current_year = 2025
    
    age_ranges = {
        '10대': (10, 19),
        '20대': (20, 29),
        '30대': (30, 39),
        '40대': (40, 49),
        '50대': (50, 59),
        '60대': (60, 69),
        '70대': (70, 79),
    }
    
    min_age, max_age = age_ranges.get(age_group, (30, 39))
    age = random.randint(min_age, max_age)
    birth_year = current_year - age
    
    # 랜덤 월/일 생성
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # 간단하게 28일까지만
    
    return date(birth_year, month, day)
```

#### 2. address 생성
```python
import random

SEOUL_DISTRICTS = [
    '강남구', '서초구', '송파구', '강동구', '마포구',
    '용산구', '영등포구', '구로구', '양천구', '강서구',
    '관악구', '동작구', '금천구', '성동구', '광진구',
    '중랑구', '동대문구', '성북구', '강북구', '도봉구',
    '노원구', '은평구', '서대문구', '종로구', '중구',
]

def generate_address() -> str:
    """랜덤 주소 생성"""
    district = random.choice(SEOUL_DISTRICTS)
    street_num = random.randint(1, 500)
    dong = random.randint(1, 20)
    ho = random.randint(101, 3005)
    
    return f"서울시 {district} 테헤란로 {street_num}, {dong}동 {ho}호"
```

---

## ✅ 체크리스트

### 프론트엔드 (완료)
- [x] CustomerInfo 타입에 birthDate, address 추가
- [x] 고객 정보 UI에 생년월일, 주소 표시
- [x] Mock 데이터에 샘플 추가 (일부)
- [x] 문서 작성

### 백엔드 (구현 필요)
- [ ] customers 테이블에 birth_date, address 컬럼 추가
- [ ] 2,500명 Mock 데이터 생성 시 birth_date, address 포함
- [ ] API 응답에 birthDate, address 포함
- [ ] 연령대 자동 계산 로직 구현 (선택)

---

## 🎯 마이그레이션 (기존 데이터가 있는 경우)

```sql
-- 컬럼 추가
ALTER TABLE customers 
ADD COLUMN birth_date DATE,
ADD COLUMN address TEXT;

-- 기존 고객 데이터에 더미 데이터 추가 (선택)
UPDATE customers
SET 
  birth_date = (
    CASE age_group
      WHEN '20대' THEN DATE '2000-01-01' + (random() * 3650)::int
      WHEN '30대' THEN DATE '1990-01-01' + (random() * 3650)::int
      WHEN '40대' THEN DATE '1980-01-01' + (random() * 3650)::int
      WHEN '50대' THEN DATE '1970-01-01' + (random() * 3650)::int
      WHEN '60대' THEN DATE '1960-01-01' + (random() * 3650)::int
      ELSE DATE '1985-01-01'
    END
  ),
  address = '서울시 강남구 테헤란로 ' || (random() * 500)::int || ', ' || 
            (random() * 20)::int || '동 ' || (random() * 3000 + 100)::int || '호'
WHERE birth_date IS NULL OR address IS NULL;
```

---

**마지막 업데이트:** Phase 10-4  
**상태:** birth_date, address 필드 추가 완료 ✅
