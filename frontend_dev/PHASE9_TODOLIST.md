# Phase 9 작업 목록 (TodoList)

## 📋 개요
Phase 9에서는 시나리오 확장 및 칸반보드 UI/UX 최적화를 진행합니다.

---

## 🎯 작업 1: 시나리오 확장 (3개 추가)

### 현재 상태
- ✅ 시나리오 5개 완성: 카드분실, 해외결제, 수수료문의, 한도증액, 연체문의
- ⚠️ 대기콜 8개 vs 시나리오 6개 불일치
- ❌ scenario6: category가 '기타문의'로 되어 있음 (내용은 결제일 변경)
- ❌ 포인트혜택: 시나리오 없음
- ❌ 일반문의: 시나리오 없음

### 작업 내용

#### 1.1 scenario6 수정 (결제일 변경)
**파일:** `/src/data/scenarios.ts`

**수정 내용:**
```typescript
// ❌ 현재
const scenario6: Scenario = {
  id: 'scenario-6',
  category: '기타문의', // 잘못됨
  // ...
};

// ✅ 수정
const scenario6: Scenario = {
  id: 'scenario-6',
  category: '결제일변경', // ⭐ 이것만 수정
  // 나머지 내용은 이미 결제일 변경으로 잘 되어 있음
  // ...
};
```

**작업 시간:** 1분  
**영향 범위:** scenarios.ts만 (기존 코드 안전)

---

#### 1.2 scenario7 추가 (포인트혜택)
**파일:** `/src/data/scenarios.ts`

**필요 구성 요소:**
1. **고객 정보**
   - 이름, 전화번호, 카드번호, 카드 등급
   - 포인트 잔액, 마일리지 정보

2. **최근 상담 이력**
   - 포인트 관련 이전 문의 내역

3. **STT 대화 내용**
   - 상담사 인사 → 고객 포인트 조회 요청
   - 포인트 잔액 안내
   - 포인트 사용 방법 문의
   - 적립 혜택 안내
   - 상담 종료

4. **키워드**
   - Step 1: 포인트, 조회, 잔액
   - Step 2: 사용, 적립, 혜택
   - Step 3: 마일리지, 환전, 사용처

5. **정보 카드 (currentSituationCards + nextStepCards)**
   - Step 1 (현재): 포인트 잔액 조회, 사용 가능 내역
   - Step 1 (다음): 포인트 사용 방법, 적립 혜택
   - Step 2 (현재): 마일리지 환전, 제휴 혜택
   - Step 2 (다음): 이벤트 포인트, 추가 적립 안내

6. **fullText (약관 형식)**
   - 각 카드마다 상세한 약관 형식 내용 (최소 20줄 이상)

**작업 시간:** 30분  
**예상 코드량:** 약 500줄

---

#### 1.3 scenario8 추가 (일반문의)
**파일:** `/src/data/scenarios.ts`

**필요 구성 요소:**
1. **고객 정보**
   - 이름, 전화번호
   - 카드 미발급 고객 (신규 고객)

2. **최근 상담 이력**
   - 없음 (신규 고객)

3. **STT 대화 내용**
   - 상담사 인사 → 고객 카드 발급 문의
   - 카드 종류 안내
   - 신청 방법 안내
   - 앱 다운로드 안내
   - 상담 종료

4. **키워드**
   - Step 1: 카드발급, 신청, 안내
   - Step 2: 앱다운로드, 본인인증, 심사
   - Step 3: 배송, 활성화, 사용방법

5. **정보 카드 (currentSituationCards + nextStepCards)**
   - Step 1 (현재): 카드 종류 안내, 발급 조건
   - Step 1 (다음): 신청 방법, 필요 서류
   - Step 2 (현재): 앱 다운로드, 본인인증
   - Step 2 (다음): 심사 기준, 소요 시간

6. **fullText (약관 형식)**
   - 각 카드마다 상세한 약관 형식 내용 (최소 20줄 이상)

**작업 시간:** 30분  
**예상 코드량:** 약 500줄

---

#### 1.4 Export 업데이트
```typescript
export const scenarios: Scenario[] = [
  scenario1,
  scenario2,
  scenario3,
  scenario4,
  scenario5,
  scenario6, // 수정됨 (category: '결제일변경')
  scenario7, // ⭐ 추가 (포인트혜택)
  scenario8, // ⭐ 추가 (일반문의)
];
```

**총 작업 시간:** 약 1시간  
**영향 범위:** scenarios.ts만 (기존 1~5 시나리오 절대 수정 안 함)

---

## 🎨 작업 2: 칸반보드 UI/UX 최적화

### 현재 문제점
1. ⚠️ **화면을 줄이면 카드가 칸반보드를 벗어남**
   - 일부 카드가 보이지 않음
   - 스크롤이 생기지 않거나 UX가 불편함

2. ⚠️ **반응형 레이아웃 최적화 부족**
   - 폰트 크기가 화면 크기에 따라 조정되지 않음
   - 카드 크기가 고정되어 있어 작은 화면에서 잘림

3. ⚠️ **현재 2x2 그리드가 보이긴 하지만 최적화되지 않음**
   - 화면 크기별로 레이아웃이 자연스럽게 변하지 않음

### 작업 내용

#### 2.1 칸반보드 컨테이너 최적화
**파일:** `/src/app/pages/RealTimeConsultationPage.tsx`

**수정 전:**
```tsx
<div className="flex flex-col gap-3">
  {/* 카드들 */}
</div>
```

**수정 후:**
```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-3 h-full overflow-y-auto">
  {/* 카드들 */}
</div>
```

**변경 사항:**
- `flex flex-col` → `grid grid-cols-1 lg:grid-cols-2`
- `h-full overflow-y-auto` 추가 (스크롤 보장)
- 모바일: 1열 (카드 세로 배치)
- 데스크톱 (lg 이상): 2열 (2x2 그리드)

---

#### 2.2 카드 크기 반응형 최적화
**파일:** `/src/app/pages/RealTimeConsultationPage.tsx`

**수정 전:**
```tsx
<div className="bg-white rounded-lg shadow-lg p-4">
  <h3 className="text-sm font-bold">{card.title}</h3>
  <p className="text-xs">{card.content}</p>
</div>
```

**수정 후:**
```tsx
<div className="bg-white rounded-lg shadow-lg p-3 lg:p-4 min-h-[200px] max-h-[400px] flex flex-col">
  <h3 className="text-xs lg:text-sm font-bold">{card.title}</h3>
  <p className="text-[10px] lg:text-xs flex-1 overflow-y-auto">{card.content}</p>
</div>
```

**변경 사항:**
- `min-h-[200px] max-h-[400px]`: 카드 높이 제한
- `flex flex-col`: 내부 콘텐츠 flex 레이아웃
- `flex-1 overflow-y-auto`: 내용이 길면 스크롤
- 폰트 크기 반응형:
  - 모바일: `text-xs` (12px), `text-[10px]` (10px)
  - 데스크톱: `text-sm` (14px), `text-xs` (12px)

---

#### 2.3 칸반보드 전체 영역 최적화
**파일:** `/src/app/pages/RealTimeConsultationPage.tsx`

**수정 전:**
```tsx
<div className="flex-1 overflow-y-auto p-4">
  {/* 칸반보드 */}
</div>
```

**수정 후:**
```tsx
<div className="flex-1 overflow-hidden p-3 lg:p-4">
  <div className="h-full overflow-y-auto">
    {/* 칸반보드 */}
  </div>
</div>
```

**변경 사항:**
- 외부: `overflow-hidden` (전체 영역 제한)
- 내부: `h-full overflow-y-auto` (스크롤 보장)
- 패딩 반응형: `p-3 lg:p-4`

---

#### 2.4 Step 진행바 최적화
**파일:** `/src/app/pages/RealTimeConsultationPage.tsx`

**수정 전:**
```tsx
<div className="text-xs">Step {currentStep} / 3</div>
```

**수정 후:**
```tsx
<div className="text-[10px] lg:text-xs">Step {currentStep} / 3</div>
```

**변경 사항:**
- 폰트 크기 반응형

---

#### 2.5 "자세히 보기" 버튼 최적화
**파일:** `/src/app/pages/RealTimeConsultationPage.tsx`

**수정 전:**
```tsx
<button className="w-full mt-1.5 px-2.5 py-1.5 bg-[#0047AB] text-white rounded text-[11px]">
  자세히 보기 (약관 전문)
</button>
```

**수정 후:**
```tsx
<button className="w-full mt-1.5 px-2 lg:px-2.5 py-1 lg:py-1.5 bg-[#0047AB] text-white rounded text-[10px] lg:text-[11px]">
  자세히 보기
</button>
```

**변경 사항:**
- 패딩 반응형: `px-2 lg:px-2.5`
- 폰트 크기 반응형: `text-[10px] lg:text-[11px]`
- 버튼 텍스트 간결화 (모바일에서 긴 텍스트 방지)

---

### UI/UX 최적화 원칙

#### ✅ 반응형 브레이크포인트
```
- sm (640px): 모바일
- md (768px): 태블릿
- lg (1024px): 데스크톱
- xl (1280px): 큰 데스크톱
```

#### ✅ 폰트 크기 가이드
```
모바일 → 데스크톱
text-[10px] → text-xs (12px)
text-xs (12px) → text-sm (14px)
text-sm (14px) → text-base (16px)
```

#### ✅ 패딩/마진 가이드
```
모바일 → 데스크톱
p-2 → p-3 → p-4
gap-2 → gap-3 → gap-4
```

#### ✅ 카드 높이 제한
```
min-h-[200px]: 최소 높이 보장
max-h-[400px]: 최대 높이 제한
overflow-y-auto: 내용이 길면 스크롤
```

---

## ⚠️ 주의사항

### 기존 코드 보호
1. **절대 수정하지 않는 파일**
   - `/src/data/mockData.ts`
   - 기존 시나리오 1~5 (scenarios.ts 내부)
   - 모든 컴포넌트 기능 로직

2. **수정 가능한 부분**
   - scenarios.ts: scenario6 category + scenario7, 8 추가
   - RealTimeConsultationPage.tsx: CSS 클래스만 수정 (기능 로직 건드리지 않음)

3. **테스트 필수**
   - 각 시나리오별로 통화 → 참조 문서 확인
   - 화면 크기 조정하며 카드 레이아웃 확인
   - 모바일/태블릿/데스크톱 모두 테스트

---

## 📊 작업 우선순위

```
Priority 1: Phase 8-2 (피드백 모달) ⭐ 지금 진행
   ↓
Priority 2: Phase 9-1 (시나리오 확장)
   - scenario6 수정
   - scenario7 추가 (포인트혜택)
   - scenario8 추가 (일반문의)
   ↓
Priority 3: Phase 9-2 (칸반보드 UI/UX 최적화)
   - 그리드 레이아웃
   - 반응형 폰트
   - 스크롤 최적화
```

---

## ✅ 완료 기준

### Phase 9-1: 시나리오 확장
- [ ] scenario6 category 수정 완료
- [ ] scenario7 (포인트혜택) 추가 완료
- [ ] scenario8 (일반문의) 추가 완료
- [ ] 각 시나리오별 통화 테스트 완료
- [ ] 참조 문서 6개씩 정확히 저장되는지 확인

### Phase 9-2: 칸반보드 UI/UX 최적화
- [ ] 2x2 그리드 레이아웃 적용
- [ ] 화면 크기별 반응형 테스트 (모바일/태블릿/데스크톱)
- [ ] 카드가 칸반보드 영역을 벗어나지 않는지 확인
- [ ] 스크롤이 자연스럽게 작동하는지 확인
- [ ] 폰트 크기가 화면 크기에 맞게 조정되는지 확인
- [ ] "자세히 보기" 버튼이 잘 보이는지 확인

---

## 💡 참고사항

### 좋은 웹사이트의 UI/UX 원칙
1. **반응형 디자인**: 모든 화면 크기에서 최적화
2. **가독성**: 폰트 크기가 화면에 맞게 조정
3. **여백**: 적절한 패딩/마진으로 답답하지 않게
4. **스크롤**: 내용이 길어도 자연스럽게 스크롤
5. **일관성**: 모든 페이지에서 동일한 디자인 패턴

### 테디카드 시스템에 적용
- ✅ HD에서 4K까지 대응
- ✅ 블루(#0047AB), 옐로우(#FBBC04), 화이트/그레이 3색 통일
- ✅ 카드 크기, 폰트 크기 반응형
- ✅ 스크롤 자연스럽게 작동
- ✅ 버튼, 아이콘 크기 최적화

---

**Phase 9 TodoList 작성 완료!** 📝  
**다음 작업: Phase 8-2 (피드백 모달) 구현** 🚀
