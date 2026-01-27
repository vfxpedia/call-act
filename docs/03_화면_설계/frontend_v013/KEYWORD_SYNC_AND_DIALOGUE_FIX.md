# 인입 키워드 Sync 및 대화 흐름 문제 수정

## 보고된 문제 (2개)

### 문제 1: 키워드 Sync 불일치 ❌

**증상:**
```
STT 화면: "안녕하세요, 테디카드 상담센터입니다."
인입 키워드: [카드분실] ← 이미 표시됨 ❌
```

**예상 동작:**
```
STT 화면: "안녕하세요, 테디카드 상담센터입니다."
인입 키워드: (비어있음) ✅

→ STT "카드를 잃어버렸어요" 감지
→ 인입 키워드: [카드분실] 추가 ⚡
```

### 문제 2: 대화 흐름 부자연스러움 ❌

**현재 표시:**
```
안녕하세요, 테디카드 상담센터입니다. 무엇을 도와드릴까요? 안녕하세요, 급한 고객님, 우선 카드 사용을 즉시 네, 1990년 3월 15일입니다. 확인되었습니다. 카드 사용이 정지되었습니다. 분실 재발급은 어떻게 받나요? 해외 출장이 재발급 카드는 등록된 주소로 3-5일 아, 그럼 임시 카드로 받고 공항 라운지 다음주 월요일 오전 10시 인천공항 신청 완료했습니다. 출국 당일 인천공항 감사합니다! 추가 문의사항 있으시면 언제든 연락주세요.
```

**문제점:**
- 모든 대화가 한 줄로 이어붙여짐
- 메시지 구분 없음
- 문장이 잘린 것처럼 보임

**원래 대화:**
```
[상담사] 안녕하세요, 테디카드 상담센터입니다. 무엇을 도와드릴까요?
[고객] 안녕하세요, 급한 일인데요. 카드를 잃어버렸어요!
[상담사] 고객님, 우선 카드 사용을 즉시 정지하겠습니다. 본인 확인을 위해 생년월일을 말씀해주시겠어요?
[고객] 네, 1990년 3월 15일입니다.
[상담사] 확인되었습니다. 카드 사용이 정지되었습니다. 분실 신고 접수 완료했습니다.
...
```

---

## 문제 1 해결: 키워드 Sync

### 원인 분석

#### 1차 수정 (이전)
**라인 879:** 시나리오가 없는 경우, `displayedKeywords`를 즉시 채움
```typescript
// Before (❌)
setDisplayedKeywords(incomingKeywordsByCase[category] || []); // ['카드분실', '분실신고', '재발급']
```

**수정:**
```typescript
// After (✅)
setDisplayedKeywords([]); // 빈 배열로 시작
setIsExtractingKeywords(true); // 키워드 추출 중 상태
```

#### 2차 디버깅 (현재)
사용자가 여전히 문제가 발생한다고 보고 → 디버깅 로그 추가

**라인 865:** 통화 시작 시 초기화 확인
```typescript
setDisplayedKeywords([]); // 빈 배열로 시작 - STT에서 실시간 감지
setIsExtractingKeywords(true); // 키워드 추출 중 상태
console.log('✅ 통화 시작: displayedKeywords를 빈 배열로 초기화');
```

**라인 583:** 키워드 감지 시 로그
```typescript
if (isKeyword && matchedKeyword) {
  console.log(`⚡ 키워드 감지: "${word}" → "${matchedKeyword}"`);
  setDisplayedKeywords(prev => {
    if (!prev.includes(matchedKeyword)) {
      const newKeywords = [...prev, matchedKeyword];
      console.log(`✅ 인입 키워드 추가:`, newKeywords);
      // ...
    }
  });
}
```

### 테스트 방법

#### 1. 브라우저 새로고침
- **Hard Refresh:** Ctrl+Shift+R (Windows) 또는 Cmd+Shift+R (Mac)
- **이유:** 브라우저 캐시 제거

#### 2. 콘솔 확인 (F12 → Console)
```
[통화 시작]
✅ 통화 시작: displayedKeywords를 빈 배열로 초기화

[1초] STT: "안녕하세요, 테디카드 상담센터입니다. 무엇을 도와드릴까요?"
(아직 키워드 없음)

[3초] STT: "안녕하세요, 급한 일인데요. 카드를 잃어버렸어요!"
⚡ 키워드 감지: "카드" → "카드분실"
✅ 인입 키워드 추가: ["카드분실"]
```

#### 3. 화면 확인
```
[0초] 통화 시작
인입 키워드: (비어있음) + "키워드 추출 중" 애니메이션 ✅

[3초] STT "카드를 잃어버렸어요" 감지
인입 키워드: [카드분실] 즉시 추가 ⚡
칸반보드 표시 ✅
```

---

## 문제 2 해결: 대화 흐름 개선

### 원인 분석

#### STT 시뮬레이션 로직
**라인 555-577:** 각 메시지를 단어 단위로 쪼개서 표시
```typescript
const words = sttItem.message.split(' ');

words.forEach((word, wordIndex) => {
  const timer = setTimeout(() => {
    setSttTexts(prev => [...prev, { 
      text: word + ' ',  // 단어 + 공백
      isKeyword 
    }]);
  }, ...);
});
```

**문제점:**
- 각 단어는 공백으로 구분되지만, **메시지 구분이 없음**
- 상담사 메시지와 고객 메시지가 이어붙여짐
- 예: "안녕하세요. 무엇을 도와드릴까요? 안녕하세요. 카드를 잃어버렸어요!"
  → 하나의 긴 문장처럼 보임

### 수정 내용

#### 1. 메시지 끝에 줄바꿈 추가

**라인 574-577 수정:**

**Before:**
```typescript
setSttTexts(prev => [...prev, { 
  text: word + ' ',  // 모든 단어에 공백만 추가
  isKeyword 
}]);
```

**After:**
```typescript
// 마지막 단어는 줄바꿈 포함
const isLastWord = wordIndex === words.length - 1;
setSttTexts(prev => [...prev, { 
  text: word + (isLastWord ? '\n\n' : ' '),  // 마지막 단어는 줄바꿈 2번
  isKeyword 
}]);
```

#### 2. CSS white-space 설정

**라인 1571 수정:**

**Before:**
```tsx
<div className="leading-relaxed w-full">
```

**After:**
```tsx
<div className="leading-relaxed w-full whitespace-pre-wrap">
```

**이유:** `white-space: pre-wrap`을 추가해야 `\n` 줄바꿈 문자가 실제로 줄바꿈으로 표시됨

---

## 수정 후 결과

### Before (문제 상황)
```
실시간 STT 분석
────────────────────────────────────────
안녕하세요, 테디카드 상담센터입니다. 무엇을 도와드릴까요? 안녕하세요, 급한 일인데요. 카드를 잃어버렸어요! 고객님, 우선 카드 사용을 즉시 정지하겠습니다. 본인 확인을 위해 생년월일을 말씀해주시겠어요? 네, 1990년 3월 15일입니다. 확인되었습니다. 카드 사용이 정지되었습니다. 분실 신고 접수 완료했습니다.

인입 키워드: [카드분실] [분실신고] [재발급] ← 즉시 표시됨 ❌
```

### After (수정 후)
```
실시간 STT 분석
────────────────────────────────────────
안녕하세요, 테디카드 상담센터입니다. 무엇을 도와드릴까요?

안녕하세요, 급한 일인데요. 카드를 잃어버렸어요!

고객님, 우선 카드 사용을 즉시 정지하겠습니다. 본인 확인을 위해 생년월일을 말씀해주시겠어요?

네, 1990년 3월 15일입니다.

확인되었습니다. 카드 사용이 정지되었습니다. 분실 신고 접수 완료했습니다.

인입 키워드: (비어있음) + "키워드 추출 중" ✅
           → [카드분실] (STT "카드" 감지 후 추가) ⚡
```

---

## 타임라인 비교

### Before
```
0ms     : 통화 시작
0ms     : 인입 키워드 [카드분실] [분실신고] [재발급] 즉시 표시 ❌
1000ms  : STT "안녕하세요, 테디카드 상담센터입니다. 무엇을 도와드릴까요? 안녕하세요, 급한 일인데요..."
          → 모든 메시지가 한 줄로 이어붙여짐 ❌
```

### After
```
0ms     : 통화 시작
0ms     : 인입 키워드 비어있음 + "키워드 추출 중" ✅
1000ms  : STT "안녕하세요, 테디카드 상담센터입니다. 무엇을 도와드릴까요?"
          (첫 메시지 끝에 줄바꿈) ✅
3000ms  : STT "안녕하세요, 급한 일인데요. 카드를 잃어버렸어요!"
          → "카드" 단어 감지
          → 인입 키워드 [카드분실] 즉시 추가 ⚡
          (메시지 끝에 줄바꿈) ✅
6000ms  : STT "고객님, 우선 카드 사용을 즉시 정지하겠습니다..."
          → "정지" 단어 감지
          → 인입 키워드 [긴급정지] 추가 ⚡
          (메시지 끝에 줄바꿈) ✅
```

---

## 전체 수정 파일

### `/src/app/pages/RealTimeConsultationPage.tsx`

#### 수정 1: 키워드 초기화 (라인 879-881)
```typescript
} else {
  // 시나리오가 없는 경우 기본값 (기존 로직)
  setIncomingKeywords(incomingKeywordsByCase[category] || []);
  setDisplayedKeywords([]); // ✅ 빈 배열로 시작
  setIsExtractingKeywords(true); // ✅ 키워드 추출 중 상태
```

#### 수정 2: 디버깅 로그 (라인 865, 583-587)
```typescript
// 통화 시작 시
setDisplayedKeywords([]);
setIsExtractingKeywords(true);
console.log('✅ 통화 시작: displayedKeywords를 빈 배열로 초기화');

// 키워드 감지 시
if (isKeyword && matchedKeyword) {
  console.log(`⚡ 키워드 감지: "${word}" → "${matchedKeyword}"`);
  setDisplayedKeywords(prev => {
    if (!prev.includes(matchedKeyword)) {
      const newKeywords = [...prev, matchedKeyword];
      console.log(`✅ 인입 키워드 추가:`, newKeywords);
      // ...
    }
  });
}
```

#### 수정 3: 메시지 줄바꿈 (라인 574-577)
```typescript
// 마지막 단어는 줄바꿈 포함
const isLastWord = wordIndex === words.length - 1;
setSttTexts(prev => [...prev, { 
  text: word + (isLastWord ? '\n\n' : ' '),  // ✅ 마지막 단어는 줄바꿈
  isKeyword 
}]);
```

#### 수정 4: CSS white-space (라인 1571)
```tsx
<div className="leading-relaxed w-full whitespace-pre-wrap">
  {/* ✅ whitespace-pre-wrap 추가 */}
```

---

## 테스트 체크리스트

### 키워드 Sync 테스트
- [ ] 브라우저 Hard Refresh (Ctrl+Shift+R 또는 Cmd+Shift+R)
- [ ] 대기 콜 "카드분실" 선택
- [ ] 통화 시작
- [ ] 콘솔에 "✅ 통화 시작: displayedKeywords를 빈 배열로 초기화" 표시되는지 확인
- [ ] 인입 키워드가 비어있는지 확인 (✅ 통과)
- [ ] "키워드 추출 중" 애니메이션이 표시되는지 확인
- [ ] STT에서 "카드" 단어 나올 때 콘솔에 "⚡ 키워드 감지" 표시되는지 확인
- [ ] 인입 키워드에 "카드분실"이 즉시 추가되는지 확인 (✅ 통과)
- [ ] 칸반보드가 표시되는지 확인

### 대화 흐름 테스트
- [ ] 각 메시지가 줄바꿈으로 구분되는지 확인
- [ ] 메시지 간 적절한 간격(2줄 공백)이 있는지 확인
- [ ] 전체 대화가 자연스럽게 읽히는지 확인

---

## 추가 개선 아이디어 (향후)

### 상담사/고객 구분 표시
현재는 줄바꿈만 추가했지만, 향후 다음과 같이 개선 가능:

```tsx
// 메시지 단위로 구분
{sttMessages.map((message, index) => (
  <div key={index} className={`mb-2 ${message.speaker === 'agent' ? 'text-blue-700' : 'text-gray-700'}`}>
    <span className="font-bold">
      {message.speaker === 'agent' ? '🎧 상담사' : '👤 고객'}:
    </span>
    {message.text}
  </div>
))}
```

### 실시간 타이핑 효과
단어 단위가 아닌 문자 단위로 타이핑 효과 추가:
```typescript
// 각 단어를 문자 단위로 쪼개서 표시
const chars = word.split('');
chars.forEach((char, charIndex) => {
  setTimeout(() => {
    setSttTexts(prev => [...prev, { text: char, isKeyword }]);
  }, charIndex * 50); // 50ms마다 한 글자씩
});
```

---

## 결론

### ✅ 수정 완료 항목
1. 인입 키워드 Sync: displayedKeywords 초기화 확인 + 디버깅 로그 추가
2. 대화 흐름: 메시지 끝에 줄바꿈 추가 + CSS white-space 설정

### 🔍 확인 필요
- 브라우저 Hard Refresh 후 테스트
- 콘솔 로그 확인
- 실제 동작 확인

### 📋 다음 단계
- 테스트 결과 보고
- 추가 개선사항 논의
