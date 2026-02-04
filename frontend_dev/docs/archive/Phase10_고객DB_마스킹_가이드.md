# Phase 10: 고객 DB 연동 및 마스킹 시스템 구현 가이드

## 📋 개요

Phase 10에서는 백엔드 `customers` 테이블과 연동하기 위한 프론트엔드 인프라를 구축했습니다:

1. **마스킹 유틸리티**: Toss CRM 방식의 실명 노출 (3초)
2. **12개 페르소나**: 백엔드 personality_tags 매핑
3. **Mock 고객 DB**: 백엔드 구현 전까지 사용할 샘플 데이터
4. **Feature Flag 통합**: USE_MOCK_DATA로 Mock/Real 전환

---

## 🎯 핵심 구현 사항

### 1. 마스킹 유틸리티 (`/src/utils/mask.ts`)

#### 함수 목록

```typescript
// 이름 마스킹
maskName('김민수') // → '김*수'
maskName('홍길') // → '홍*'

// 전화번호 마스킹
maskPhone('010-1234-5678') // → '010-****-5678'
maskPhone('01012345678') // → '010****5678'

// 카드번호 마스킹
maskCardNumber('1234-5678-9012-3456') // → '****-****-****-3456'
maskCardNumber('3456') // → '****-****-****-3456'

// 마스킹된 카드번호에서 마지막 4자리 추출
extractLast4Digits('****-****-****-3456') // → '3456'

// 실명 노출 타이머
createUnmaskTimer(3000) // → Promise (3초 후 resolve)

// 마스킹 토글
toggleMask('김민수', true, maskName) // → '김*수'
toggleMask('김민수', false, maskName) // → '김민수'
```

#### 사용 예시

```typescript
import { maskName, maskPhone, maskCardNumber } from '@/utils/mask';

const customer = {
  name: '김민수',
  phone: '010-1234-5678',
  cardNumber: '1234-5678-9012-3456'
};

console.log(maskName(customer.name)); // "김*수"
console.log(maskPhone(customer.phone)); // "010-****-5678"
console.log(maskCardNumber(customer.cardNumber)); // "****-****-****-3456"
```

---

### 2. MaskedText 컴포넌트 (`/src/app/components/ui/MaskedText.tsx`)

#### Props

```typescript
interface MaskedTextProps {
  originalText: string;    // 원본 텍스트 (예: "김민수")
  maskedText: string;      // 마스킹된 텍스트 (예: "김*수")
  type: 'name' | 'phone' | 'cardNumber';
  duration?: number;       // 노출 시간 (ms, 기본 3000)
  className?: string;
  showIcon?: boolean;      // 아이콘 표시 (기본 true)
}
```

#### 사용 예시

```tsx
import { MaskedText } from '@/app/components/ui/MaskedText';
import { maskName } from '@/utils/mask';

<MaskedText
  originalText="김민수"
  maskedText={maskName("김민수")}
  type="name"
  duration={3000}
/>
```

**인터랙션:**
1. 기본: `김*수` + `👁️ 보기` 버튼 표시
2. 클릭: `김민수` (실명) + `👁️‍🗨️ 3초` 카운트다운
3. 3초 후: 자동으로 `김*수` 마스킹 복구

---

### 3. Mock 고객 DB (`/src/data/mockCustomerDB.ts`)

#### 12개 페르소나 구성

| ID | 페르소나 | personalityTags | traits (UI 표시) | 비율 |
|----|---------|----------------|-----------------|------|
| N1 | 일반친절형 | `['normal', 'polite']` | `['일반 고객', '친절한 성향']` | 25% |
| N2 | 조용한내성형 | `['quiet', 'reserved']` | `['조용한 성향', '내성적']` | 15% |
| N3 | 실용주의형 | `['practical', 'efficient']` | `['실용주의', '효율 중시', '목적 지향적']` | 12% |
| N4 | 친화적수다형 | `['friendly', 'talkative']` | `['친화적', '수다형', '대화 선호']` | 8% |
| S1 | 급한성격형 | `['impatient', 'direct', 'busy']` | `['급한 성향', '빠른 답변 선호', '바쁨']` | 8% |
| S2 | 꼼꼼상세형 | `['detailed', 'analytical']` | `['꼼꼼한 성향', '상세한 설명 필요', '분석적']` | 6% |
| S3 | 감정호소형 | `['emotional', 'expressive']` | `['감정 호소형', '공감 필요', '표현적']` | 5% |
| S4 | 시니어친화형 | `['elderly', 'patient', 'needs_repetition']` | `['시니어', '천천히 설명 필요', '반복 안내 필요']` | 8% |
| S5 | 디지털네이티브 | `['tech_savvy', 'self_service']` | `['디지털 네이티브', '기술 친화적', '셀프서비스 선호']` | 5% |
| S6 | VIP고객형 | `['high_value', 'premium', 'loyal']` | `['VIP 고객', '프리미엄 서비스 기대', '충성 고객']` | 3% |
| S7 | 반복민원형 | `['frequent_caller', 'frustrated']` | `['반복 민원', '좌절감', '이전 이력 확인 필요']` | 3% |
| S8 | 불만항의형 | `['complaining', 'demanding']` | `['불만 항의', '요구사항 많음', '까다로움']` | 2% |

#### 샘플 데이터

```typescript
import { MOCK_CUSTOMER_DB, getCustomerById } from '@/data/mockCustomerDB';

// 고객 조회
const customer = getCustomerById('CUST-TEDDY-00001');
console.log(customer);
// {
//   id: 'CUST-TEDDY-00001',
//   name: '김민수',
//   phone: '010-1234-5678',
//   cardNumber: '1234-5678-9012-3456',
//   cardType: '테디카드 스탠다드',
//   grade: 'GENERAL',
//   personalityTags: ['normal', 'polite'],
//   traits: ['일반 고객', '친절한 성향'],
//   preferredStyle: '일반적인 응대로 친절하게 안내하세요...',
//   gender: 'male',
//   ageGroup: '40대',
//   age: 42,
//   totalConsultations: 3,
//   lastConsultationDate: '2024-12-15',
// }
```

---

### 4. Customer API (`/src/api/customerApi.ts`)

#### Feature Flag 통합

```typescript
import { USE_MOCK_DATA } from '@/config/mockConfig';
```

**동작 방식:**
- `USE_MOCK_DATA = true`: Mock 고객 DB 사용 (현재)
- `USE_MOCK_DATA = false`: FastAPI 백엔드 호출 (백엔드 구현 완료 후)

#### API 함수 목록

```typescript
// 1. 고객 정보 조회
fetchCustomerInfo(customerId: string): Promise<CustomerInfo | null>

// 2. 고객 목록 조회 (페이지네이션)
fetchCustomerList(page: number, limit: number): Promise<{
  customers: CustomerInfo[];
  total: number;
  page: number;
  limit: number;
}>

// 3. 고객 정보 업데이트
updateCustomerInfo(customerId: string, updates: Partial<CustomerInfo>): Promise<boolean>

// 4. LLM 가이드 생성 요청
fetchCustomerLLMGuide(customerId: string): Promise<string | null>
```

#### 사용 예시

```typescript
import { fetchCustomerInfo, fetchCustomerLLMGuide } from '@/api/customerApi';

// 고객 정보 조회
const customer = await fetchCustomerInfo('CUST-TEDDY-00001');
console.log(customer);

// LLM 가이드 조회
const guide = await fetchCustomerLLMGuide('CUST-TEDDY-00001');
console.log(guide);
// "일반적인 응대로 친절하게 안내하세요. 표준 매뉴얼대로 진행하시면 됩니다."
```

---

### 5. CustomerInfo 타입 확장 (`/src/data/scenarios.ts`)

#### 추가된 필드

```typescript
export interface CustomerInfo {
  // 기존 필드
  id: string;
  name: string;
  phone: string;
  cardNumber: string;
  cardType: string;
  grade: string;
  traits?: string[];
  age?: number;
  preferredStyle?: string;

  // ⭐ Phase 10: 신규 필드
  personalityTags?: string[];           // 백엔드 personality_tags (12개 페르소나)
  communicationStyle?: {                // 백엔드 communication_style
    speed?: 'fast' | 'moderate' | 'slow';
    tone?: 'formal' | 'neutral' | 'casual' | 'warm' | 'empathetic';
  };
  gender?: 'male' | 'female' | 'unknown'; // 성별
  ageGroup?: string;                    // 연령대 ('20대', '30대', ...)
  totalConsultations?: number;          // 총 상담 횟수
  lastConsultationDate?: string;        // 마지막 상담 일자
}
```

---

## 🚀 실제 사용 가이드

### 시나리오 1: 상담 중 페이지에서 고객 정보 표시

**RealTimeConsultationPage.tsx** (이미 적용 완료)

```tsx
import { maskName, maskPhone } from '@/utils/mask';
import { MaskedText } from '@/app/components/ui/MaskedText';

// 고객 정보 표시
<div className="space-y-1.5 text-[11px] text-[#666666]">
  <div className="flex items-center">
    <span className="font-medium text-[#333333] w-20">이름:</span>
    <MaskedText
      originalText={customerInfo.name}
      maskedText={maskName(customerInfo.name)}
      type="name"
      duration={3000}
    />
  </div>
  <div className="flex items-center">
    <span className="font-medium text-[#333333] w-20">전화:</span>
    <MaskedText
      originalText={customerInfo.phone}
      maskedText={maskPhone(customerInfo.phone)}
      type="phone"
      duration={3000}
    />
  </div>
</div>
```

**결과:**
- 기본: `김*수` + `👁️ 보기`
- 클릭 시: `김민수` (3초 동안 표시)
- 자동 마스킹 복구

---

### 시나리오 2: 백엔드 API 연동 (백엔드 구현 완료 후)

**Step 1: mockConfig.ts 수정**

```typescript
// /src/config/mockConfig.ts
export const USE_MOCK_DATA = false; // Mock → Real 전환
```

**Step 2: 백엔드 API 엔드포인트 확인**

```
GET /api/v1/customers/{customer_id}
```

**Step 3: API 응답 형식 (백엔드 팀 제공)**

```json
{
  "id": "CUST-TEDDY-00001",
  "name": "김민수",
  "phone": "010-1234-5678",
  "cardNumber": "1234-5678-9012-3456",
  "cardType": "테디카드 스탠다드",
  "grade": "GENERAL",
  "personalityTags": ["normal", "polite"],
  "communicationStyle": {
    "speed": "moderate",
    "tone": "neutral"
  },
  "gender": "male",
  "ageGroup": "40대",
  "totalConsultations": 3,
  "lastConsultationDate": "2024-12-15"
}
```

**Step 4: 프론트엔드에서 호출**

```typescript
import { fetchCustomerInfo } from '@/api/customerApi';

// USE_MOCK_DATA = false이면 자동으로 백엔드 호출
const customer = await fetchCustomerInfo('CUST-TEDDY-00001');
```

---

### 시나리오 3: 고객 특성 태그 표시

**이미 구현 완료** (Phase 9-2)

```tsx
import { getTraitColor } from '@/utils/customerTraitGuide';

{activeScenario.customer.traits?.map((trait, index) => {
  const colors = getTraitColor(trait);
  return (
    <span
      key={index}
      className="px-2 py-0.5 rounded text-[10px] font-medium"
      style={{ 
        backgroundColor: colors.bg,
        color: colors.text
      }}
    >
      {trait}
    </span>
  );
})}
```

**결과:**
- `일반 고객` (그레이)
- `VIP 고객` (블루)
- `급한 성향` (연한 블루)

---

## 📊 백엔드 연동 체크리스트

### ✅ 프론트엔드 준비 완료 (Phase 10)

- [x] 마스킹 유틸리티 (`mask.ts`)
- [x] MaskedText 컴포넌트 (실명 노출 3초)
- [x] 12개 페르소나 Mock 데이터
- [x] Customer API Feature Flag 통합
- [x] CustomerInfo 타입 확장
- [x] 고객 특성 태그 색상 매핑 (12개 페르소나)

### ⏳ 백엔드 구현 대기 중

- [ ] `customers` 테이블 생성 (DDL 실행)
- [ ] 2,500명 고객 데이터 생성 (12개 페르소나 분포)
- [ ] 6,533개 상담 데이터 customer_id 재배정
- [ ] FCR 계산 및 통계 업데이트
- [ ] GET /api/v1/customers/{customer_id} 엔드포인트
- [ ] LLM 기반 상담 가이드 생성 API

---

## 🎨 UI/UX 개선 사항

### 마스킹 텍스트 디자인

**기본 상태:**
```
이름: 김*수 [👁️ 보기]
```

**클릭 후 (3초 동안):**
```
이름: 김민수 [👁️‍🗨️ 3초]
```

**색상:**
- 마스킹: `#333333` (기본 텍스트)
- 언마스킹: `#0047AB` (블루)
- 버튼: `#F5F5F5` (그레이) → `#E8F1FC` (블루, 활성화)

---

## 🔒 보안 고려 사항

### 1. 마스킹 처리 위치

✅ **Frontend에서 마스킹** (Toss CRM 방식)
- DB: 실제 데이터 저장
- API 응답: 실제 데이터 전송
- Frontend: 화면 표시 시 마스킹

❌ **Backend에서 마스킹하지 않는 이유:**
- Frontend에서 실명 노출 기능 구현 필요
- 상담사 권한 확인 후 실명 노출 가능

### 2. 실명 노출 시간 제한

- **기본 3초**: 업계 표준 (Toss, 카카오뱅크)
- **자동 마스킹**: 3초 후 자동 복구
- **재클릭 가능**: 필요 시 다시 클릭하여 노출

### 3. 개인정보 보호법 준수

- **저장**: 암호화된 DB (백엔드 책임)
- **전송**: HTTPS 필수
- **표시**: 마스킹 기본 + 실명 노출 로그 기록 (향후 구현)

---

## 📝 다음 단계 (Phase 11)

### 백엔드 구현 완료 후 작업

1. **Feature Flag 전환**
   ```typescript
   export const USE_MOCK_DATA = false;
   ```

2. **API 엔드포인트 테스트**
   - GET /api/v1/customers/{customer_id}
   - PATCH /api/v1/customers/{customer_id}
   - GET /api/v1/customers (페이지네이션)

3. **LLM 가이드 통합**
   - 실시간 고객 특성 분석
   - 상담 가이드 자동 생성

4. **FCR 통계 표시**
   - 고객별 FCR 비율
   - 상담 이력 하이라이트

5. **재방문 고객 알림**
   - 7일 이내 재문의 고객 하이라이트
   - 이전 상담 이력 자동 로드

---

## 🐛 트러블슈팅

### Q1: 마스킹이 작동하지 않아요

**A:** CustomerInfo 타입에 name, phone이 올바르게 전달되는지 확인하세요.

```typescript
console.log(customerInfo); // { name: '김민수', phone: '010-1234-5678' }
console.log(maskName(customerInfo.name)); // "김*수"
```

### Q2: MaskedText 클릭해도 실명이 안 보여요

**A:** originalText와 maskedText가 제대로 전달되는지 확인하세요.

```tsx
<MaskedText
  originalText="김민수" // 원본 (필수)
  maskedText="김*수"   // 마스킹 (필수)
  type="name"
/>
```

### Q3: Mock 데이터가 안 나와요

**A:** mockConfig.ts 확인

```typescript
export const USE_MOCK_DATA = true; // false면 백엔드 호출 시도
```

### Q4: 백엔드 API 호출 시 CORS 에러

**A:** FastAPI CORS 설정 확인 (백엔드 팀)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 참고 자료

- **백엔드 설계 문서**: `customers` 테이블 구조
- **12개 페르소나**: 백엔드 팀 제공 personality_tags 매핑
- **Toss CRM 방식**: Frontend 마스킹 + 실명 노출 (3-5초)
- **FCR 계산**: 7일 이내 동일 카테고리 재문의 여부

---

## 💬 문의

프론트엔드 구현 완료! 백엔드 팀과 협업하여 다음 단계를 진행하세요.

**Phase 10 완료 ✅**
