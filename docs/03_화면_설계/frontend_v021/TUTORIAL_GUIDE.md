# 📖 튜토리얼 말풍선 위치 조정 가이드

## 🎯 개요

CALL:ACT 시스템의 튜토리얼 말풍선 위치는 **설정 파일 기반**으로 관리됩니다.
- ✅ 2K (1920×1080) 기준 설계
- ✅ 4K (3840×2160)까지 자동 스케일링
- ✅ 중앙 관리로 유지보수 용이

---

## 📁 파일 구조

```
/src
├── config/
│   └── tutorialConfig.ts      ⭐ 여기서만 위치 수정!
├── data/
│   └── tutorialSteps.ts        (화살표 방향만 수정)
└── app/components/tutorial/
    └── TutorialGuide.tsx       (건드리지 마세요)
```

---

## ✏️ 1. 말풍선 위치 조정 방법

### 📍 기본 조정 (가장 간단)

**파일:** `/src/config/tutorialConfig.ts`

```typescript
export const tutorialOffsets: Record<string, TooltipOffset> = {
  'scenario-selector': {
    offsetY: -80,              // 🎯 변경: -80 → -100 (더 위로)
    offsetX: 0,                // 🎯 변경: 0 → 50 (오른쪽으로)
    useTargetSize: false,
    scaleWithViewport: true,
  },
}
```

### 📊 offsetY/offsetX 값의 의미

| 축 | 양수 (+) | 음수 (-) | 예시 |
|----|---------|---------|------|
| **Y축** | 아래로 이동 ↓ | 위로 이동 ↑ | `offsetY: -100` = 타겟 100px 위 |
| **X축** | 오른쪽 이동 → | 왼쪽 이동 ← | `offsetX: 50` = 타겟 50px 오른쪽 |

---

## 🎛️ 2. 고급 설정

### useTargetSize (타겟 크기 기반 계산)

```typescript
'stt-area': {
  offsetY: 40,               // 타겟 높이 + 40px
  useTargetSize: true,       // ✅ 타겟 크기에 따라 자동 조정
  scaleWithViewport: true,
},
```

**동작:**
- `offsetY: 40` + `useTargetSize: true` → **타겟 높이 + 40px** 아래에 배치
- 타겟이 커지면 말풍선도 자동으로 멀어짐

### scaleWithViewport (4K 자동 스케일링)

```typescript
'call-action-button': {
  offsetY: 0,
  offsetX: 100,
  scaleWithViewport: true,   // ✅ 4K에서 자동 확대
},
```

**동작:**
- 1920×1080 (2K): `offsetX = 100px`
- 3840×2160 (4K): `offsetX = 200px` (자동 2배)
- 1366×768 (HD): `offsetX = 71px` (자동 0.71배)

### 최소/최대 값 제한

```typescript
'scenario-selector': {
  offsetY: -80,
  minOffset: 20,            // 최소 20px 거리 유지
  maxOffset: 150,           // 최대 150px 제한
  scaleWithViewport: true,
},
```

---

## 🎨 3. 화살표 방향 변경

**파일:** `/src/data/tutorialSteps.ts`

```typescript
{
  id: 'step-customer-info',
  targetId: 'customer-info-card',
  title: '고객 정보 카드',
  description: '...',
  position: 'right',  // ⭐ 변경: 'top' | 'bottom' | 'left' | 'right'
}
```

---

## 📐 4. 해상도별 테스트 방법

### Chrome DevTools 사용

1. `F12` → DevTools 열기
2. `Ctrl + Shift + M` → 반응형 모드
3. 해상도 선택:
   - 1366×768 (HD)
   - 1920×1080 (2K) ⭐ 기준
   - 2560×1440 (QHD)
   - 3840×2160 (4K)

### 권장 테스트 시나리오

```
✅ 1920×1080 (기준) → 말풍선이 정확한 위치에 있는지 확인
✅ 3840×2160 (4K)   → 말풍선이 자동으로 2배 확대되었는지 확인
✅ 1366×768 (HD)    → 말풍선이 화면을 벗어나지 않는지 확인
```

---

## 🛠️ 5. 실전 예시

### 예시 1: 대기콜 목록 말풍선을 더 위로 올리기

**현재 (80px 위):**
```typescript
'scenario-selector': {
  offsetY: -80,
}
```

**변경 (120px 위):**
```typescript
'scenario-selector': {
  offsetY: -120,
}
```

### 예시 2: 통화 버튼 말풍선을 왼쪽에 배치

**현재 (오른쪽):**
```typescript
'call-action-button': {
  offsetX: 100,  // 오른쪽
}
```

**변경 (왼쪽):**
```typescript
'call-action-button': {
  offsetX: -100,  // 왼쪽으로 변경
}
```

**+ 화살표 방향도 변경:**
```typescript
// /src/data/tutorialSteps.ts
{
  id: 'step-direct-call-info',
  targetId: 'call-action-button',
  position: 'right',  // 'left' → 'right'로 변경
}
```

### 예시 3: 카드 영역 말풍선을 타겟에 더 가깝게

**현재 (타겟 + 60px):**
```typescript
'next-cards-area': {
  offsetY: 60,
  useTargetSize: true,
}
```

**변경 (타겟 + 30px):**
```typescript
'next-cards-area': {
  offsetY: 30,  // 60 → 30으로 줄임
  useTargetSize: true,
}
```

---

## 🚨 6. 문제 해결

### 말풍선이 화면 밖으로 나갑니다

**원인:** offsetY/X 값이 너무 큽니다.

**해결:**
```typescript
'target-id': {
  offsetY: -500,  // ❌ 너무 큼
  offsetY: -100,  // ✅ 적절
  maxOffset: 150, // ✅ 최대값 제한 추가
}
```

### 4K에서 위치가 이상합니다

**원인:** `scaleWithViewport`가 꺼져 있습니다.

**해결:**
```typescript
'target-id': {
  offsetY: -80,
  scaleWithViewport: false,  // ❌
  scaleWithViewport: true,   // ✅
}
```

### 타겟이 커지면 말풍선이 겹칩니다

**원인:** `useTargetSize`가 꺼져 있습니다.

**해결:**
```typescript
'stt-area': {
  offsetY: 40,
  useTargetSize: false,  // ❌ 고정 픽셀
  useTargetSize: true,   // ✅ 타겟 크기 기반
}
```

---

## 📋 7. 전체 targetId 목록

### Phase 1: 대기 중
- `scenario-selector` - 대기콜 목록
- `call-action-button` - 통화 버튼

### Phase 2: 통화 중
- `customer-info-card` - 고객 정보
- `stt-area` - STT 영역
- `keyword-area` - 키워드 영역
- `current-cards-area` - 현재 카드
- `next-cards-area` - 다음 카드
- `ai-search-area` - AI 검색
- `memo-area` - 메모
- `end-call-button` - 통화 종료

### Phase 3: 후처리
- `acw-transcript` - 상담 전문
- `acw-docs` - 참조 문서
- `acw-current-case` - 현재 케이스
- `acw-similar-cases` - 유사 사례
- `acw-document-area` - 후처리 문서
- `acw-memo-area` - 메모
- `acw-save-button` - 저장 버튼

---

## ✅ 8. 체크리스트

말풍선 위치를 수정할 때 확인하세요:

```
✅ /src/config/tutorialConfig.ts 파일만 수정했나요?
✅ offsetY/X의 부호(+/-)를 올바르게 사용했나요?
✅ 화살표 방향(position)도 함께 확인했나요?
✅ 1920×1080에서 테스트했나요?
✅ 4K (3840×2160)에서도 확인했나요?
✅ scaleWithViewport가 활성화되어 있나요?
```

---

## 🎓 9. 권장 워크플로우

```
1️⃣ /src/config/tutorialConfig.ts 열기
2️⃣ 수정할 targetId 찾기
3️⃣ offsetY/X 값 변경
4️⃣ 저장 및 브라우저 새로고침
5️⃣ 1920×1080에서 테스트
6️⃣ 4K로 전환하여 재확인
7️⃣ 필요시 /src/data/tutorialSteps.ts에서 position 변경
```

---

## 📞 추가 도움

더 복잡한 조정이 필요하거나 새로운 단계를 추가하려면:
1. `/src/config/tutorialConfig.ts`에 새 targetId 설정 추가
2. `/src/data/tutorialSteps.ts`에 새 단계 추가
3. 해당 페이지에 `id="your-target-id"` 속성 추가

**예시:**
```typescript
// 1. tutorialConfig.ts
'new-feature-button': {
  offsetY: -50,
  offsetX: 0,
  scaleWithViewport: true,
}

// 2. tutorialSteps.ts
{
  id: 'step-new-feature',
  targetId: 'new-feature-button',
  title: '새 기능',
  description: '...',
  position: 'bottom',
}

// 3. YourPage.tsx
<button id="new-feature-button">새 기능</button>
```
