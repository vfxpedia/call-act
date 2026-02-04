# 인입 키워드 표시 타이밍 문제 수정

## 문제 보고

**증상:** 
- 통화 시작 직후 STT에서 "카드분실" 키워드가 아직 감지되지 않았는데
- 인입 키워드 영역에 "카드분실" 태그가 먼저 표시됨

**예상 동작:**
```
통화 시작 → 인입 키워드 비어있음
         → STT 대화에서 "카드" 감지
         → 인입 키워드에 "카드분실" 추가 ✅
```

**실제 동작 (문제):**
```
통화 시작 → 인입 키워드에 "카드분실" 즉시 표시 ❌
         → STT 대화에서 "카드" 감지
         → (이미 표시되어 있음)
```

---

## 원인 분석

### 코드 구조

**두 가지 State:**
1. `incomingKeywords` = 기대되는 키워드 목록 (현재 Step의 모든 키워드)
2. `displayedKeywords` = 실제로 감지된 키워드 (화면에 표시)

**UI 렌더링:**
```typescript
// RealTimeConsultationPage.tsx 라인 1139
{displayedKeywords.slice(0, 3).map((keyword, index) => (
  <span>{keyword}</span>
))}
```

✅ 화면에는 `displayedKeywords`만 표시됨 (정상)

### 문제 발견

**라인 879: 시나리오가 없는 경우**
```typescript
} else {
  // 시나리오가 없는 경우 기본값 (기존 로직)
  setIncomingKeywords(incomingKeywordsByCase[category] || []);
  setDisplayedKeywords(incomingKeywordsByCase[category] || []); // ❌ 문제!
```

**문제점:**
- 시나리오가 로드되지 않은 경우 (또는 로딩 지연)
- `displayedKeywords`를 `incomingKeywordsByCase[category]`로 즉시 채움
- 예: `['카드분실', '분실신고', '재발급']` → 통화 시작 직후 즉시 표시

---

## 수정 내용

### 변경 사항

**파일:** `/src/app/pages/RealTimeConsultationPage.tsx`

**라인 879-880 수정:**

**Before:**
```typescript
setIncomingKeywords(incomingKeywordsByCase[category] || []);
setDisplayedKeywords(incomingKeywordsByCase[category] || []); // ❌ 즉시 표시
```

**After:**
```typescript
setIncomingKeywords(incomingKeywordsByCase[category] || []);
setDisplayedKeywords([]); // ✅ 빈 배열로 시작 - STT에서 실시간 감지
setIsExtractingKeywords(true); // ✅ 키워드 추출 중 상태
```

### 통일된 동작

이제 **모든 경우**에 동일하게 동작합니다:

1. **시나리오가 있는 경우** (라인 863):
   ```typescript
   setDisplayedKeywords([]); // 빈 배열로 시작
   setIsExtractingKeywords(true); // 키워드 추출 중
   ```

2. **시나리오가 없는 경우** (라인 879):
   ```typescript
   setDisplayedKeywords([]); // 빈 배열로 시작
   setIsExtractingKeywords(true); // 키워드 추출 중
   ```

---

## 예외 사항 (정상 동작)

### 수동 Step 전환 시 즉시 표시

다음 경우에는 키워드를 **즉시 전체 표시**하는 것이 정상입니다:

#### 1. 이전 Step으로 드래그 (라인 687)
```typescript
// 이전 Step으로 이동 시 키워드는 즉시 전체 표시 (애니메이션 스킵)
setDisplayedKeywords(prevStepKeywords); // ✅ 정상
setIsExtractingKeywords(false); // ✅ 추출 완료
```

**이유:** 이미 지나간 Step이므로 키워드를 다시 감지할 필요 없음

#### 2. 다음 Step으로 드래그 (라인 701)
```typescript
// 이미 도달한 Step으로 이동하므로 키워드 즉시 전체 표시
setDisplayedKeywords(nextStepKeywords); // ✅ 정상
setIsExtractingKeywords(false); // ✅ 추출 완료
```

**이유:** 이미 도달한 Step (maxReachedStep까지만 이동 가능)이므로 키워드가 이미 감지됨

#### 3. Progress bar 클릭 (라인 731)
```typescript
setDisplayedKeywords(targetStepKeywords); // ✅ 정상
setIsExtractingKeywords(false); // ✅ 추출 완료
```

**이유:** 수동 이동이므로 즉시 표시

---

## 수정 후 동작 흐름

### 통화 시작 시

```
1. 대기 콜 "카드분실" 선택
   ↓
2. handleSelectWaitingCall('카드분실') 실행
   ↓
3. setDisplayedKeywords([]) - 빈 배열로 초기화 ✅
   setIsExtractingKeywords(true) - 키워드 추출 중 표시 ✅
   ↓
4. UI: "인입 키워드" 영역 비어있음 + "키워드 추출 중" 애니메이션 ✅
   ↓
5. STT 대화 시작: "안녕하세요, 카드를 잃어버렸어요"
   ↓
6. "카드" 단어 감지
   ↓
7. setDisplayedKeywords(['카드분실']) - 즉시 추가 ⚡
   ↓
8. UI: "인입 키워드" 영역에 "카드분실" 표시 ✅
   ↓
9. 칸반보드 표시 + 다음 단계 카드 표시
```

### 타임라인

```
0ms     : 통화 시작
0ms     : 인입 키워드 비어있음 ✅
0ms     : "키워드 추출 중" 표시 ✅
3000ms  : STT "안녕하세요" → 키워드 아님
3200ms  : STT "카드를" → 키워드 감지!
3200ms  : 인입 키워드에 "카드분실" 추가 ⚡
3200ms  : 칸반보드 표시
4000ms  : 다음 단계 카드 표시
```

---

## UI 표시 상태

### 통화 전
```
┌──────────────────────────────┐
│   실시간 상담 분석            │
├──────────────────────────────┤
│ 통화가 시작되면 실시간으로   │
│ STT 분석이 진행됩니다.       │
└──────────────────────────────┘
```

### 통화 시작 직후 (수정 후)
```
┌──────────────────────────────┐
│   실시간 상담 분석            │
├──────────────────────────────┤
│ 인입 키워드                   │
│ ● ● ● 키워드 추출 중          │  ✅ 빈 상태 + 로딩 애니메이션
│ (비어있음)                    │
└──────────────────────────────┘
```

### STT 키워드 감지 후
```
┌──────────────────────────────┐
│   실시간 상담 분석            │
├──────────────────────────────┤
│ 인입 키워드                   │
│ [카드분실] [긴급정지]        │  ✅ 실시간 감지된 키워드만 표시
└──────────────────────────────┘
```

---

## 테스트 시나리오

### 테스트 1: 카드분실 (시나리오 1)
1. 대기 콜 "카드분실" 선택
2. 통화 시작 버튼 클릭
3. ✅ 인입 키워드 비어있음 확인
4. ✅ "키워드 추출 중" 애니메이션 확인
5. STT 대화 시작
6. ✅ "카드" 단어 나오는 순간 "카드분실" 키워드 즉시 표시
7. ✅ 칸반보드 표시

### 테스트 2: 해외결제 (시나리오 2)
1. 대기 콜 "해외결제" 선택
2. 통화 시작
3. ✅ 인입 키워드 비어있음
4. STT "해외" 감지
5. ✅ "해외결제" 키워드 즉시 표시

### 테스트 3: 수동 Step 전환
1. 시나리오 1 통화 중
2. Step 2로 자동 전환
3. 드래그로 Step 1로 복귀
4. ✅ 인입 키워드 즉시 전체 표시 (정상 - 이미 지나간 Step)

---

## 결론

✅ **수정 완료!**

**변경 사항:**
- 라인 879-880: `setDisplayedKeywords([])`로 빈 배열 시작
- 라인 881: `setIsExtractingKeywords(true)` 추가

**결과:**
- 통화 시작 시 인입 키워드 비어있음 ✅
- STT에서 키워드 감지 시 즉시 표시 ✅
- 완벽한 Sync! ✅

**다음 단계:**
- 브라우저에서 테스트하여 정상 동작 확인
- 모든 시나리오(1-6)에서 동일하게 동작하는지 확인
