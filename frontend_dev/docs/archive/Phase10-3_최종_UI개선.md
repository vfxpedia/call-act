# Phase 10-3: 최종 UI 개선

## 📋 개요

사용자 피드백을 반영하여 최종 UI/UX를 개선했습니다.

---

## ✅ 1. 고객 정보 UI 개선

### 변경 사항

#### ❌ 생년 필드 제거
**이유:** 백엔드 customers 테이블에 birth_date 필드가 없음

**Before:**
```
┌─────────────────────────┐
│ 고객 정보                │
├─────────────────────────┤
│ 이름: 김*수              │
│ 전화: 010-****-5678      │
│ 생년: 1985-03-15  ← 제거│
│ 주소: 서울시 강남구...  │
└─────────────────────────┘
```

**After:**
```
고객 정보
┌─────────────────────────┐
│ 이름: 김*수              │
│ 전화: 010-****-5678      │
│ 주소: 서울시 강남구...  │
└─────────────────────────┘
```

---

#### ✅ 타이틀을 카드 밖으로 이동

**이유:** 고객 특성 가이드, 최근 상담 내역과 UI 통일성

**Before:**
```
┌─────────────────────────┐
│ 고객 정보                │ ← 카드 안
├─────────────────────────┤
│ 이름: 김*수              │
│ ...                     │
└─────────────────────────┘
```

**After:**
```
고객 정보                    ← 카드 밖
┌─────────────────────────┐
│ 이름: 김*수              │
│ ...                     │
└─────────────────────────┘

고객 특성 가이드              ← 카드 밖 (통일)
┌─────────────────────────┐
│ 태그들...               │
└─────────────────────────┘

최근 상담 내역               ← 카드 밖 (통일)
┌─────────────────────────┐
│ 상담 목록...            │
└─────────────────────────┘
```

---

#### ✅ 개행 방지 (inline-flex)

**문제:** 전화번호 마스킹 클릭 시 "3s" 카운트다운이 다음 줄로 넘어감

**Before:**
```
전화: 010-****-5678
      3s              ← 개행 발생!
```

**After:**
```
전화: 010-1234-5678 3s  ← 한 줄에 표시
```

**기술적 해결:**
```tsx
<span className="inline-flex items-center gap-0.5">
  <span>{isRevealed ? originalText : maskedText}</span>
  {isRevealed && <span className="shrink-0">{remainingTime}s</span>}
</span>
```

---

## 🎨 2. Toast 색상 시스템 개선

### CALL:ACT 톤과 맞춤

**Before (Sonner 기본):**
- Success: 녹색 `#10B981`
- Warning: 주황색 `#F59E0B`
- Error: 빨간색 `#EF4444`
- Info: 파란색 `#3B82F6`

**After (CALL:ACT 통합):**
| 타입 | 배경 | 텍스트 | 테두리 | CALL:ACT 색상 활용 |
|------|------|--------|--------|-------------------|
| **Success** | `#F0F9FF` (연한 블루) | `#0047AB` (메인 블루) | `#0047AB/20` | ✅ 블루 계열 |
| **Warning** | `#FFFBEB` (연한 노랑) | `#D97706` | `#FBBC04/30` | ✅ 옐로우 계열 |
| **Error** | `#FEF2F2` (연한 빨강) | `#DC2626` | `#DC2626/20` | 🔴 에러 전용 |
| **Info** | `#F0F9FF` (연한 블루) | `#0047AB` (메인 블루) | `#0047AB/20` | ✅ 블루 계열 |

### 색상 전략

1. **Success & Info:** CALL:ACT 메인 블루 `#0047AB` 사용
2. **Warning:** CALL:ACT 서브 옐로우 `#FBBC04` 계열
3. **Error:** 빨간색 유지 (에러는 빨간색이 직관적)

### 통일성

- 배경: 모두 연한 톤 (시각적 부담 감소)
- 텍스트: 진한 컬러 (가독성 확보)
- 테두리: 투명도 적용 (부드러운 느낌)

---

## 📊 최종 UI 비교

### 고객 정보 카드 (Before vs After)

**Before (Phase 10-2):**
```
┌─────────────────────────────────┐
│ 고객 정보                        │
├─────────────────────────────────┤
│ ID:      CUST-001               │ ← 불필요
│ 이름:    김*수                   │
│ 전화:    010-****-5678           │
│ 생년:    1985-03-15              │ ← DB에 없음
│ 주소:    서울시 강남구...       │
└─────────────────────────────────┘
```

**After (Phase 10-3):**
```
고객 정보                            ← 타이틀 밖으로
┌─────────────────────────────────┐
│ 이름: 김*수 3s                   │ ← 개행 없음
│ 전화: 010-1234-5678 2s           │
│ 주소: 서울시 강남구...          │
└─────────────────────────────────┘
```

---

## 🚀 구현 코드

### 1. InlineMaskedText 개행 방지

```tsx
// /src/app/components/ui/MaskedText.tsx
<span
  className="inline-flex items-center gap-0.5"  // ← inline-flex로 변경
>
  <span>{isRevealed ? originalText : maskedText}</span>
  {isRevealed && (
    <span className="shrink-0">{remainingTime}s</span>  // ← shrink-0
  )}
</span>
```

---

### 2. 고객 정보 레이아웃

```tsx
// /src/app/pages/RealTimeConsultationPage.tsx
<div className="flex-shrink-0 animate-[slideInFromTop_0.5s_ease-out] mb-3">
  {/* 타이틀 밖으로 */}
  <h3 className="text-xs font-bold text-[#333333] mb-2">고객 정보</h3>
  
  {/* 카드 */}
  <div className="bg-white rounded-lg border border-[#E0E0E0] p-2.5">
    <div className="space-y-1 text-[11px]">
      <div className="flex items-center gap-1">
        <span className="font-medium text-[#333333] w-10 shrink-0">이름:</span>
        <InlineMaskedText ... />
      </div>
      <div className="flex items-center gap-1">
        <span className="font-medium text-[#333333] w-10 shrink-0">전화:</span>
        <InlineMaskedText ... />
      </div>
      <div className="flex items-center gap-1">
        <span className="font-medium text-[#333333] w-10 shrink-0">주소:</span>
        <span className="text-[#666666] truncate">...</span>
      </div>
    </div>
  </div>
</div>
```

**주요 변경:**
- `w-10` (40px) - 라벨 너비 고정
- `shrink-0` - 라벨이 줄어들지 않음
- `gap-1` - 라벨과 값 사이 간격
- 생년 필드 제거

---

### 3. Toast 색상 커스터마이징

```tsx
// /src/app/components/ui/sonner.tsx
<Sonner
  toastOptions={{
    classNames: {
      // Success: CALL:ACT 블루
      success: 'group-[.toast]:bg-[#F0F9FF] group-[.toast]:text-[#0047AB] group-[.toast]:border-[#0047AB]/20',
      
      // Warning: CALL:ACT 옐로우
      warning: 'group-[.toast]:bg-[#FFFBEB] group-[.toast]:text-[#D97706] group-[.toast]:border-[#FBBC04]/30',
      
      // Error: 빨간색 (에러 전용)
      error: 'group-[.toast]:bg-[#FEF2F2] group-[.toast]:text-[#DC2626] group-[.toast]:border-[#DC2626]/20',
      
      // Info: CALL:ACT 블루
      info: 'group-[.toast]:bg-[#F0F9FF] group-[.toast]:text-[#0047AB] group-[.toast]:border-[#0047AB]/20',
    },
  }}
/>
```

---

## 🎯 개선 효과

### 1. UI 통일성 ✅
- 고객 정보, 고객 특성 가이드, 최근 상담 내역 모두 동일한 구조
- 타이틀이 카드 밖에 위치
- 카드는 내용만 담음

### 2. 정보 정확성 ✅
- DB에 없는 생년 필드 제거
- 실제 데이터와 일치

### 3. UX 개선 ✅
- 개행 방지로 한 줄에 모든 정보 표시
- 마스킹 클릭 시 자연스러운 카운트다운

### 4. 디자인 통일 ✅
- Toast 색상이 CALL:ACT 시스템 톤과 조화
- 블루/옐로우 중심의 일관된 색상 사용

---

## 📝 고객 DB 필드 (최종)

### customers 테이블 (Phase 10)
```sql
CREATE TABLE customers (
  id VARCHAR(50) PRIMARY KEY,           -- 'CUST-TEDDY-00001'
  name VARCHAR(100) NOT NULL,           -- '김민수'
  phone VARCHAR(20) NOT NULL,           -- '010-1234-5678'
  -- ❌ birth_date 필드 없음
  gender VARCHAR(10),                   -- 'male', 'female', 'unknown'
  age_group VARCHAR(10),                -- '20대', '30대', ...
  grade VARCHAR(20),                    -- 'VIP', 'GOLD', 'SILVER', 'GENERAL'
  card_type VARCHAR(100),
  card_number_last4 VARCHAR(4),
  personality_tags TEXT[],              -- 12개 페르소나
  communication_style JSONB,
  total_consultations INT DEFAULT 0,
  resolved_first_call INT DEFAULT 0,
  last_consultation_date DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

**프론트엔드에서 제거할 필드:**
- ❌ `birthDate` (DB에 없음)

**유지할 필드:**
- ✅ `name` (마스킹)
- ✅ `phone` (마스킹)
- ✅ `address` (주소는 별도 테이블일 수도 있음 - 추후 확인)

---

## ✅ 완료 체크리스트

- [x] 생년 필드 제거
- [x] 타이틀 카드 밖으로 이동
- [x] 개행 방지 (inline-flex)
- [x] Toast 색상 CALL:ACT 톤 통합
- [x] UI 통일성 확보

---

## 🔍 추가 확인 필요

### 주소 필드
**질문:** 백엔드 customers 테이블에 주소(address) 필드가 있나요?

**현재:**
- 프론트엔드에서 표시 중: `customerInfo.address`
- Mock 데이터: `'서울시 강남구 테헤란로 123'`

**확인 필요:**
- customers 테이블에 address 필드 존재 여부
- 없다면 별도 addresses 테이블인지
- 없다면 프론트엔드에서도 제거해야 함

---

**마지막 업데이트:** Phase 10-3  
**상태:** 최종 UI 개선 완료 ✅
