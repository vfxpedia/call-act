# Toast 알림 시스템 적용 페이지 목록

## 📋 전체 적용 현황 (13개)

### ✅ 1. RealTimeConsultationPage.tsx
**위치:** `/src/app/pages/RealTimeConsultationPage.tsx`

**적용 위치:**
```typescript
Line 1041: handleCallConnect 함수
```

**변경 내역:**
```typescript
// Before
alert('이미 통화 중입니다.');

// After
toast.warning('이미 통화 중입니다.', {
  description: '현재 통화를 종료한 후 다시 시도해주세요.',
  duration: 2000,
});
```

**Toast 타입:** `warning`  
**테스트 방법:** 통화 중일 때 다른 인입콜 클릭

---

### ✅ 2. AfterCallWorkPage.tsx
**위치:** `/src/app/pages/AfterCallWorkPage.tsx`

**적용 위치:**
```typescript
Line 306: saveConsultation catch 블록
```

**변경 내역:**
```typescript
// Before
alert('저장에 실패했습니다. 다시 시도해주세요.');

// After
toast.error('저장에 실패했습니다.', {
  description: '다시 시도해주세요.',
  duration: 3000,
});
```

**Toast 타입:** `error`  
**테스트 방법:** 후처리 페이지에서 저장 실패 시나리오

---

### ✅ 3. ProfilePage.tsx
**위치:** `/src/app/pages/ProfilePage.tsx`

**적용 위치:**
```typescript
Line 105: handleSave 함수 (성공)
Line 107: handleSave catch 블록 (실패)
```

**변경 내역:**
```typescript
// Before
alert('저장되었습니다.');

// After
showSuccess('저장되었습니다.');

// 에러 처리 추가
showError('저장에 실패했습니다.');
```

**Toast 타입:** `success`, `error`  
**테스트 방법:** 프로필 페이지에서 정보 수정 후 저장

---

### ✅ 4. AdminConsultationManagePage.tsx
**위치:** `/src/app/pages/AdminConsultationManagePage.tsx`

**적용 위치 (2곳):**
```typescript
Line 133: toggleBestPractice 함수
Line 147: handleBulkBestPractice 함수
```

**변경 내역:**
```typescript
// Before (Line 133)
alert(
  consultations.find(c => c.id === id)?.isBestPractice
    ? '우수사례에서 제외되었습니다.'
    : '교육 시뮬레이션 자료로 등록되었습니다!'
);

// After
const consultation = consultations.find(c => c.id === id);
if (consultation?.isBestPractice) {
  showInfo('우수사례에서 제외되었습니다.');
} else {
  showSuccess('교육 시뮬레이션 자료로 등록되었습니다!');
}

// Before (Line 147)
alert(`${selectedRows.length}개의 상담이 교육 시뮬레이션 자료로 등록되었습니다!`);

// After
showSuccess(`${selectedRows.length}개의 상담이 교육 시뮬레이션 자료로 등록되었습니다!`);
```

**Toast 타입:** `success`, `info`  
**테스트 방법:** 
- 관리자 상담 관리 페이지
- 별 아이콘 클릭 (개별)
- 체크박스 선택 후 일괄 등록

---

### ✅ 5. AdminNoticeCreatePage.tsx
**위치:** `/src/app/pages/AdminNoticeCreatePage.tsx`

**적용 위치 (2곳):**
```typescript
Line 24: 유효성 검사
Line 62: 등록 성공
```

**변경 내역:**
```typescript
// Before (Line 24)
alert('제목과 내용을 입력해주세요.');

// After
showWarning('제목과 내용을 입력해주세요.');

// Before (Line 62)
alert('공지사항이 등록되었습니다.');

// After
showSuccess('공지사항이 등록되었습니다.');
```

**Toast 타입:** `warning`, `success`  
**테스트 방법:**
- 관리자 공지사항 생성 페이지
- 빈 폼 제출 (경고)
- 정상 제출 (성공)

---

### ✅ 6. AdminNoticeEditPage.tsx
**위치:** `/src/app/pages/AdminNoticeEditPage.tsx`

**적용 위치 (3곳):**
```typescript
Line 39: 공지사항 못 찾음
Line 53: 유효성 검사
Line 90: 수정 성공
```

**변경 내역:**
```typescript
// Before (Line 39)
alert('공지사항을 찾을 수 없습니다.');

// After
showError('공지사항을 찾을 수 없습니다.');

// Before (Line 53)
alert('제목과 내용을 입력해주세요.');

// After
showWarning('제목과 내용을 입력해주세요.');

// Before (Line 90)
alert('공지사항이 수정되었습니다.');

// After
showSuccess('공지사항이 수정되었습니다.');
```

**Toast 타입:** `error`, `warning`, `success`  
**테스트 방법:**
- 관리자 공지사항 수정 페이지
- 잘못된 ID로 접근 (에러)
- 빈 폼 제출 (경고)
- 정상 수정 (성공)

---

### ✅ 7. AddEmployeeModal.tsx
**위치:** `/src/app/components/modals/AddEmployeeModal.tsx`

**적용 위치:**
```typescript
Line 69: handleSubmit 유효성 검사
```

**변경 내역:**
```typescript
// Before
alert('모든 필수 항목을 입력해주세요.');

// After
import('@/utils/toast').then(({ showWarning }) => {
  showWarning('모든 필수 항목을 입력해주세요.');
});
```

**Toast 타입:** `warning`  
**테스트 방법:** 직원 추가 모달에서 필수 항목 미입력 후 제출

---

### ✅ 8. EditEmployeeModal.tsx
**위치:** `/src/app/components/modals/EditEmployeeModal.tsx`

**적용 위치:**
```typescript
Line 60: handleSubmit 유효성 검사
```

**변경 내역:**
```typescript
// Before
alert('모든 필수 항목을 입력해주세요.');

// After
import('@/utils/toast').then(({ showWarning }) => {
  showWarning('모든 필수 항목을 입력해주세요.');
});
```

**Toast 타입:** `warning`  
**테스트 방법:** 직원 수정 모달에서 필수 항목 삭제 후 제출

---

### ✅ 9. ChangePasswordModal.tsx
**위치:** `/src/app/components/modals/ChangePasswordModal.tsx`

**적용 위치:**
```typescript
Line 59: handleSubmit 성공
```

**변경 내역:**
```typescript
// Before
alert('비밀번호가 변경되었습니다.\n※ 현재 베타 버전에서는 비밀번호 변경 기능이 제한됩니다.');

// After
import('@/utils/toast').then(({ showSuccess }) => {
  showSuccess('비밀번호가 변경되었습니다.', '※ 현재 베타 버전에서는 비밀번호 변경 기능이 제한됩니다.');
});
```

**Toast 타입:** `success`  
**테스트 방법:** 비밀번호 변경 모달에서 변경 완료

---

## 📊 Toast 타입별 통계

| Toast 타입 | 사용 횟수 | 주요 용도 |
|-----------|----------|----------|
| `success` | 6개 | 저장/등록/수정 완료 |
| `warning` | 5개 | 유효성 검사 실패, 중복 작업 |
| `error` | 2개 | 저장 실패, 데이터 없음 |
| `info` | 1개 | 상태 변경 알림 |
| **합계** | **14개** | - |

---

## 🧪 테스트 체크리스트

### 1. 실시간 상담 페이지
- [ ] 통화 중일 때 다른 콜 클릭 → 경고 Toast

### 2. 후처리 페이지
- [ ] 저장 실패 시 → 에러 Toast

### 3. 프로필 페이지
- [ ] 정보 저장 성공 → 성공 Toast
- [ ] 저장 실패 → 에러 Toast

### 4. 관리자 - 상담 관리
- [ ] 우수사례 등록 → 성공 Toast
- [ ] 우수사례 제외 → 정보 Toast
- [ ] 일괄 등록 → 성공 Toast

### 5. 관리자 - 공지사항 생성
- [ ] 빈 폼 제출 → 경고 Toast
- [ ] 등록 성공 → 성공 Toast

### 6. 관리자 - 공지사항 수정
- [ ] 잘못된 ID → 에러 Toast
- [ ] 빈 폼 제출 → 경고 Toast
- [ ] 수정 성공 → 성공 Toast

### 7. 직원 관리 모달
- [ ] 필수 항목 미입력 (추가) → 경고 Toast
- [ ] 필수 항목 미입력 (수정) → 경고 Toast

### 8. 비밀번호 변경 모달
- [ ] 변경 성공 → 성공 Toast

---

## 🎨 Toast 설정 (App.tsx)

```tsx
<Toaster 
  position="top-center"    // 화면 상단 중앙
  richColors               // 타입별 색상 적용
  closeButton              // X 버튼 표시
  duration={3000}          // 3초 후 자동 사라짐
/>
```

---

## 📁 관련 파일

### 핵심 파일
- `/src/utils/toast.ts` - Toast 헬퍼 함수
- `/src/app/App.tsx` - Toaster 컴포넌트 설정
- `/src/app/components/ui/sonner.tsx` - Toast UI 컴포넌트

### 수정된 페이지 (9개)
1. `/src/app/pages/RealTimeConsultationPage.tsx`
2. `/src/app/pages/AfterCallWorkPage.tsx`
3. `/src/app/pages/ProfilePage.tsx`
4. `/src/app/pages/AdminConsultationManagePage.tsx`
5. `/src/app/pages/AdminNoticeCreatePage.tsx`
6. `/src/app/pages/AdminNoticeEditPage.tsx`
7. `/src/app/components/modals/AddEmployeeModal.tsx`
8. `/src/app/components/modals/EditEmployeeModal.tsx`
9. `/src/app/components/modals/ChangePasswordModal.tsx`

---

## 🔍 확인 방법

### 1. 브라우저 개발자 도구
```javascript
// Console에서 직접 테스트
import { showSuccess } from './src/utils/toast';
showSuccess('테스트 메시지');
```

### 2. 페이지별 실제 동작 테스트
각 페이지에서 해당 액션을 수행하면 Toast 알림이 화면 상단 중앙에 표시됩니다.

### 3. Toast 표시 위치 확인
- 화면 상단 중앙 (헤더 아래)
- 여러 Toast가 겹칠 경우 아래로 쌓임
- 최대 3개까지 동시 표시

---

## ✅ 완료 사항

- [x] 전체 13개 alert() → Toast 대체
- [x] 4가지 Toast 타입 활용 (success, warning, error, info)
- [x] App.tsx에 Toaster 설정
- [x] 모든 페이지 import 추가
- [x] 테스트 체크리스트 작성

---

**마지막 업데이트:** Phase 10-2 완료
