# Toast 알림 디자인 가이드

## 📐 Toast 색상 및 디자인 기준

### 라이브러리: Sonner
- **출처:** [sonner by Emil Kowalski](https://sonner.emilkowal.ski/)
- **특징:** React용 최신 Toast 라이브러리, shadcn/ui 권장 라이브러리
- **장점:** 
  - 부드러운 애니메이션
  - 자동 스택 관리
  - TypeScript 완벽 지원
  - 접근성 (a11y) 준수

---

## 🎨 Toast 타입별 색상 시스템

### 1. Success (성공)
**색상:**
- 배경: `#10B981` (녹색)
- 아이콘: ✅ (체크 마크)
- 텍스트: 흰색

**사용 시나리오:**
- 저장 완료
- 등록 완료
- 수정 완료
- 삭제 완료

**예시:**
```typescript
showSuccess('저장되었습니다.');
```

---

### 2. Warning (경고)
**색상:**
- 배경: `#F59E0B` (주황색)
- 아이콘: ⚠️ (경고 삼각형)
- 텍스트: 흰색

**사용 시나리오:**
- 유효성 검사 실패
- 중복 작업 시도
- 필수 항목 누락
- 권한 부족

**예시:**
```typescript
showWarning('모든 필수 항목을 입력해주세요.');
```

---

### 3. Error (에러)
**색상:**
- 배경: `#EF4444` (빨간색)
- 아이콘: ❌ (X 마크)
- 텍스트: 흰색

**사용 시나리오:**
- API 요청 실패
- 네트워크 에러
- 데이터 로드 실패
- 시스템 오류

**예시:**
```typescript
showError('저장에 실패했습니다.', '다시 시도해주세요.');
```

---

### 4. Info (정보)
**색상:**
- 배경: `#3B82F6` (파란색)
- 아이콘: ℹ️ (정보 아이콘)
- 텍스트: 흰색

**사용 시나리오:**
- 상태 변경 알림
- 안내 메시지
- 팁/도움말
- 일반 알림

**예시:**
```typescript
showInfo('우수사례에서 제외되었습니다.');
```

---

## 🎯 CALL:ACT 프로젝트 색상 통합

### 기본 색상 시스템
- **Primary Blue:** `#0047AB` (메인 블루)
- **Secondary Yellow:** `#FBBC04` (옐로우)
- **White/Gray:** 화이트/그레이 계열

### Toast에서 활용
Sonner 라이브러리는 자체 색상 시스템을 사용하지만, `richColors` prop을 통해 타입별 색상을 자동 적용합니다.

```tsx
<Toaster 
  position="top-center"
  richColors              // ← 타입별 색상 자동 적용
  closeButton
  duration={3000}
/>
```

---

## 📏 디자인 스펙

### 크기
- **너비:** 최대 356px (반응형)
- **높이:** 자동 (콘텐츠에 따라)
- **패딩:** 16px
- **모서리:** 8px 라운드

### 타이포그래피
- **제목 (message):** 14px, 볼드
- **설명 (description):** 12px, 일반
- **줄 간격:** 1.5

### 애니메이션
- **등장:** 위에서 아래로 슬라이드 + 페이드인 (200ms)
- **사라짐:** 위로 슬라이드 + 페이드아웃 (200ms)
- **easing:** cubic-bezier(0.16, 1, 0.3, 1)

### 위치
- **화면:** 상단 중앙 (`top-center`)
- **마진:** 상단에서 16px
- **스택:** 최대 3개까지 동시 표시

---

## 🔧 기술적 구현

### App.tsx 설정
```tsx
<Toaster 
  position="top-center"    // 위치: 상단 중앙
  richColors               // 타입별 색상 적용
  closeButton              // X 버튼 표시
  duration={3000}          // 3초 후 자동 사라짐
/>
```

### ESC 키로 닫기 (Phase 10-2 추가)
```typescript
useEffect(() => {
  const handleEscKey = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      toast.dismiss(); // 모든 Toast 닫기
    }
  };

  window.addEventListener('keydown', handleEscKey);
  return () => {
    window.removeEventListener('keydown', handleEscKey);
  };
}, []);
```

---

## 🎭 사용자 경험 (UX)

### 타이밍 전략
| 타입 | 지속 시간 | 이유 |
|------|----------|------|
| Success | 2.5초 | 빠르게 확인 후 사라짐 |
| Warning | 3초 | 읽을 시간 제공 |
| Error | 3.5초 | 에러 메시지는 조금 더 오래 |
| Info | 3초 | 표준 시간 |

### 인터랙션
1. **자동 사라짐:** 설정된 시간 후 자동 제거
2. **X 버튼:** 수동으로 즉시 닫기
3. **ESC 키:** 모든 Toast 일괄 닫기 ⭐ 새로 추가!
4. **호버:** 마우스 올리면 자동 사라짐 일시 정지

### 스택 관리
- 최대 3개까지 동시 표시
- 새 Toast는 아래에 쌓임
- 오래된 Toast부터 자동 제거
- 공간 절약을 위해 부드러운 전환

---

## 📱 반응형 디자인

### 데스크톱 (1024px+)
- 너비: 356px (고정)
- 위치: 상단 중앙

### 태블릿 (768px ~ 1023px)
- 너비: 90% (최대 356px)
- 위치: 상단 중앙

### 모바일 (~ 767px)
- 너비: 95% (좌우 마진 최소화)
- 위치: 상단 중앙

---

## 🔍 접근성 (Accessibility)

### ARIA 속성
- `role="status"` (Success, Info)
- `role="alert"` (Warning, Error)
- `aria-live="polite"` (자동 읽기)

### 키보드 지원
- **ESC:** 모든 Toast 닫기 ✅
- **Tab:** 닫기 버튼 포커스
- **Enter/Space:** 포커스된 버튼 클릭

### 스크린 리더
- Toast 내용 자동 읽기
- 타입별 접두사 추가 ("성공:", "경고:", "오류:")

---

## 🎨 디자인 철학

### 1. 최소주의 (Minimalism)
- 필요한 정보만 표시
- 과도한 장식 제거
- 깔끔한 타이포그래피

### 2. 일관성 (Consistency)
- 모든 Toast 동일한 크기/위치
- 타입별 색상만 변경
- 애니메이션 통일

### 3. 사용자 중심 (User-Centric)
- 자동 사라짐 (클릭 불필요)
- 수동 닫기 옵션 (X 버튼)
- ESC 키 지원 (빠른 닫기)

---

## 🆚 기존 alert()와 비교

### alert() (Before)
```
❌ 페이지 전체 블로킹
❌ 브라우저 기본 스타일 (못생김)
❌ 확인 버튼 클릭 강제
❌ 디자인 커스터마이징 불가
❌ 접근성 제한적
```

### Toast (After)
```
✅ 페이지 사용 가능
✅ 모던한 디자인
✅ 자동 사라짐 (선택적 클릭)
✅ 완전한 커스터마이징
✅ 접근성 우수
✅ ESC 키로 빠른 닫기
```

---

## 📚 참고 자료

- [Sonner 공식 문서](https://sonner.emilkowal.ski/)
- [shadcn/ui Toast](https://ui.shadcn.com/docs/components/toast)
- [Material Design - Snackbar](https://m3.material.io/components/snackbar/overview)
- [Apple HIG - Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)

---

**마지막 업데이트:** Phase 10-2  
**ESC 키 지원 추가:** 2025-01-22
