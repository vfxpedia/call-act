# 인입 키워드 Sync 문제 해결

## 문제점

**증상:** 실시간 STT 대화에서 키워드가 태깅되는데, '인입 키워드' 영역에 표시되는 타이밍이 늦음 (Sync가 안맞음)

**원인:**
```typescript
// 기존 코드 (라인 586-593)
if (newKeywords.length === 1) {
  setTimeout(() => {              // ❌ 100ms 지연
    setIsKeywordDetected(true);
    setIsExtractingKeywords(false);
    setTimeout(() => {              // ❌ 추가 1200ms 지연
      setShowNextStepCards(true);
    }, 1200);
  }, 100);
}
```

**문제:**
1. 첫 키워드 감지 후 100ms 후에 칸반보드 표시
2. 첫 키워드 감지 후 1300ms(1.3초) 후에 다음 단계 카드 표시
3. STT 대화에서 키워드가 하이라이팅 되는 순간과 인입 키워드에 표시되는 순간 사이에 100ms 간격 발생

## 해결책 ✅

```typescript
// 수정된 코드 (라인 586-592)
if (newKeywords.length === 1) {
  setIsKeywordDetected(true);         // ⚡ 즉시 실행 (지연 제거)
  setIsExtractingKeywords(false);     // ⚡ 즉시 실행 (지연 제거)
  setTimeout(() => {
    setShowNextStepCards(true);
  }, 800);                             // ✅ 800ms로 단축 (1200ms → 800ms)
}
```

**개선 사항:**
1. ✅ 키워드 감지 → 인입 키워드 표시: **0ms** (즉시)
2. ✅ 칸반보드 표시: **0ms** (즉시)
3. ✅ 다음 단계 카드 표시: **800ms** (빠른 전환)

## 타임라인 비교

### 기존:
```
0ms     : STT 대화에서 "카드" 단어 감지 → 하이라이팅
100ms   : 인입 키워드에 "카드분실" 표시 ⬅️ 100ms 지연!
100ms   : 칸반보드 표시
1300ms  : 다음 단계 카드 표시
```

### 수정 후:
```
0ms     : STT 대화에서 "카드" 단어 감지 → 하이라이팅
0ms     : 인입 키워드에 "카드분실" 표시 ⬅️ ⚡ 즉시!
0ms     : 칸반보드 표시
800ms   : 다음 단계 카드 표시
```

## 동작 흐름

```
[사용자] "안녕하세요, 카드를 잃어버렸어요"
    ↓
[STT] 단어 단위로 수신: "안녕하세요," "카드를" "잃어버렸어요"
    ↓
[키워드 감지 (프론트)] "카드" → keywordMap['카드분실'] 매칭 ✓
    ↓
[즉시 실행]
  1. sttTexts에 "카드" 추가 (isKeyword: true로 하이라이팅)
  2. displayedKeywords에 "카드분실" 추가  ⬅️ ⚡ 동시!
  3. setIsKeywordDetected(true) - 칸반보드 표시
  4. setIsExtractingKeywords(false)
    ↓
[800ms 후]
  5. setShowNextStepCards(true) - 다음 단계 카드 표시
```

## 사용자 경험 개선

### Before:
- 대화: "카드를 잃어버렸어요"
- 화면: "카드" 하이라이팅 → [100ms 기다림] → 인입 키워드 표시
- 느낌: 약간 버벅이는 느낌

### After:
- 대화: "카드를 잃어버렸어요"
- 화면: "카드" 하이라이팅 ⚡ 동시에 인입 키워드 표시
- 느낌: 매끄럽고 즉각적인 반응

## 추가 최적화 가능성

만약 더 빠른 반응을 원하신다면:

```typescript
// 옵션 1: 다음 단계 카드도 더 빠르게
setTimeout(() => {
  setShowNextStepCards(true);
}, 500);  // 800ms → 500ms

// 옵션 2: 즉시 표시 (동시에 모두 표시)
setShowNextStepCards(true);  // setTimeout 없이 즉시
```

다만 현재 800ms는 사용자가 "현재 상황 카드"를 먼저 읽고 "다음 단계 카드"를 보는 시간으로 적절합니다.

## 테스트 방법

1. 시나리오 1(카드분실) 선택 후 통화 시작
2. STT 대화: "안녕하세요, 카드를 잃어버렸어요!"
3. "카드" 단어가 하이라이팅 되는 순간 인입 키워드에 "카드분실"이 동시에 표시되는지 확인
4. 다른 키워드들도 즉시 표시되는지 확인

---

**결론:** ✅ **Sync 문제 해결 완료! 키워드 태깅과 인입 키워드 표시가 즉시 동기화됩니다.**
