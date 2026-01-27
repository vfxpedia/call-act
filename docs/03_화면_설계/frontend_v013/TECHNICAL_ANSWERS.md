# CALL:ACT 기술 질문 답변

## 1. 키워드 매핑 수정 완료 ✅

**질문:** 지금 문제 되는 부분을 수정해서 전달해주면 안될까요?

**답변:** ✅ **완료했습니다!**
- `/src/app/pages/RealTimeConsultationPage.tsx`의 492-499번 라인을 493-540번 라인으로 확장
- 시나리오 1-6의 모든 키워드 매핑 추가 완료
- 총 47개 키워드 매핑 (기존 6개 → 47개)

---

## 2. 키워드 매핑 vs DB 단어사전

### Q2-1: KEYWORD_MAP_FIX.ts는 프론트단에서 미리 세팅한 값인가요?

**답변:** ✅ **네, 맞습니다.**

현재 구조:
```typescript
// 프론트단에 하드코딩된 키워드 매핑
const keywordMap: Record<string, string[]> = {
  '카드분실': ['카드', '잃어버렸', '분실'],
  '긴급정지': ['정지', '즉시', '긴급'],
  // ... 
};
```

**역할:**
- STT에서 실시간으로 들어오는 대화 텍스트와 시나리오의 키워드를 매칭하기 위한 **보조 매핑 테이블**
- 예: "카드분실" 키워드를 찾기 위해 ["카드", "잃어버렸", "분실"] 중 하나라도 포함되면 감지

### Q2-2: 나중에 DB의 단어사전(keywords_dict.json)을 통해 처리할 수 있나요?

**답변:** ✅ **네, 가능합니다! 오히려 권장됩니다.**

#### 현재 구조 (프론트 하드코딩):
```
STT 텍스트 → keywordMap (하드코딩) → 키워드 감지 → UI 표시
```

#### 권장 구조 (DB 단어사전 활용):

**방법 1: 초기 로딩 시 DB에서 가져오기**
```typescript
// API에서 keywords_dict.json 로드
const loadKeywordDictionary = async () => {
  const response = await fetch('/api/keywords-dictionary');
  const keywordDict = await response.json();
  return keywordDict;
};

useEffect(() => {
  loadKeywordDictionary().then(dict => {
    setKeywordMap(dict); // State로 관리
  });
}, []);
```

**방법 2: 시나리오 선택 시 함께 로드**
```typescript
const handleSelectWaitingCall = async (category: string) => {
  // 시나리오와 키워드 사전을 동시에 로드
  const [scenario, keywordDict] = await Promise.all([
    getScenarioByCategory(category),
    loadKeywordDictionary()
  ]);
  
  setActiveScenario(scenario);
  setKeywordMap(keywordDict);
};
```

**방법 3: 시나리오 데이터에 포함 (추천!)**
```typescript
// scenarios.ts 또는 DB의 시나리오 테이블에 포함
{
  id: 'scenario-1',
  category: '카드분실',
  steps: [...],
  keywordMapping: {  // ⭐ 여기에 포함!
    '카드분실': ['카드', '잃어버렸', '분실'],
    '긴급정지': ['정지', '즉시', '긴급'],
    // ...
  }
}
```

### Q2-3: 속도는 느리지 않을까요?

**답변:** ✅ **전혀 느리지 않습니다!**

#### 성능 분석:

| 방식 | 속도 | 장점 | 단점 |
|------|------|------|------|
| **현재 방식 (하드코딩)** | ⚡ 즉시 (0ms) | 빠름 | 유지보수 어려움, 확장성 낮음 |
| **초기 로딩 (권장)** | ⚡ 빠름 (100-200ms) | 한 번만 로드, 실시간 처리는 동일 | 초기 로딩 시간 필요 |
| **실시간 API 호출** | ❌ 느림 (500ms+) | 항상 최신 데이터 | 매번 네트워크 요청 |

**권장 방식:**
```typescript
// 1. 앱 시작 시 한 번만 로드 (App.tsx 또는 Context)
const KeywordDictionaryContext = createContext();

export const KeywordDictionaryProvider = ({ children }) => {
  const [keywordDict, setKeywordDict] = useState({});
  
  useEffect(() => {
    // 앱 시작 시 한 번만 로드
    fetch('/api/keywords-dictionary')
      .then(res => res.json())
      .then(data => setKeywordDict(data));
  }, []);
  
  return (
    <KeywordDictionaryContext.Provider value={keywordDict}>
      {children}
    </KeywordDictionaryContext.Provider>
  );
};

// 2. 실시간 STT 처리에서는 메모리에 있는 데이터 사용
const RealTimeConsultationPage = () => {
  const keywordMap = useContext(KeywordDictionaryContext); // ⚡ 메모리에서 읽음 (0ms)
  
  // STT 처리 - 매우 빠름!
  const processSTT = (word) => {
    const matched = keywordMap[keyword]?.some(mapped => word.includes(mapped));
  };
};
```

**결론:** 초기 로딩 시 한 번만 DB에서 가져오고, 실시간 처리는 메모리에서 처리하면 **0ms로 동일하게 빠름!**

---

## 3. 대화 태깅이 프론트단에서 처리되는가?

**답변:** ✅ **네, 현재는 100% 프론트단에서 처리됩니다.**

### 현재 처리 흐름:

```
1. STT 텍스트 수신 (시뮬레이션: activeScenario.sttDialogue)
   ↓
2. 단어 단위로 쪼개기 (word.split(' '))
   ↓
3. 키워드 매칭 (프론트단 - RealTimeConsultationPage.tsx 라인 522-528)
   ↓
4. isKeyword = true/false 판정
   ↓
5. UI에 하이라이팅 표시
```

### 코드 위치:
```typescript
// RealTimeConsultationPage.tsx 라인 522-528
currentKeywords.forEach(kw => {
  const mappedWords = keywordMap[kw] || [kw];
  if (mappedWords.some(mapped => word.includes(mapped))) {
    isKeyword = true;  // ⭐ 프론트단에서 판정
    matchedKeyword = kw;
  }
});
```

### 실제 운영 환경 권장 구조:

#### 옵션 1: 프론트단 처리 (현재 방식) - **권장!**
```
STT 음성 → FastAPI (STT 변환) → WebSocket → React
                                              ↓
                                    키워드 매칭 (프론트)
                                              ↓
                                          UI 표시
```
**장점:**
- ⚡ 매우 빠른 응답 (0-10ms)
- 서버 부하 없음
- 실시간성 보장

**단점:**
- 키워드 사전이 클 경우 메모리 사용량 증가 (하지만 일반적으로 문제 없음)

#### 옵션 2: 백엔드 처리
```
STT 음성 → FastAPI (STT 변환 + 키워드 추출) → WebSocket → React → UI 표시
```
**장점:**
- 복잡한 NLP 처리 가능
- 키워드 사전 관리 용이

**단점:**
- 네트워크 지연 (50-100ms 추가)
- 서버 부하 증가

#### 옵션 3: 하이브리드 (추천!)
```
STT 음성 → FastAPI (STT 변환) → WebSocket → React
                ↓                                ↓
        키워드 후처리 (비동기)        실시간 키워드 매칭 (프론트)
                ↓                                ↓
        DB 저장 + 분석                    UI 즉시 표시
```

**장점:**
- 실시간성 보장 (프론트단 즉시 처리)
- 정확도 향상 (백엔드에서 재검증 및 개선)
- 데이터 축적 (분석 및 학습 가능)

---

## 4. 인입 키워드 Sync 문제

### Q4: 실시간 대화에서 태그되어 나오면 '인입 키워드' 하위에 하나씩 보여지는데 지금 Sync가 안맞습니다. 대화에서 키워드 태깅 되는 순간 뜨면 좋을 것 같은데 구현하기 어려운가요?

**답변:** ✅ **이미 구현되어 있어야 합니다! Sync 문제를 확인하겠습니다.**

### 현재 구현된 로직:

```typescript
// RealTimeConsultationPage.tsx 라인 536-558
// ⭐ 키워드가 감지되면 인입 키워드에 추가
if (isKeyword && matchedKeyword) {
  setDisplayedKeywords(prev => {
    if (!prev.includes(matchedKeyword)) {
      const newKeywords = [...prev, matchedKeyword];
      
      // 첫 번째 키워드가 추가되면 칸반보드 표시
      if (newKeywords.length === 1) {
        setTimeout(() => {
          setIsKeywordDetected(true);  // ⭐ 칸반보드 표시
          setIsExtractingKeywords(false);
          setTimeout(() => {
            setShowNextStepCards(true);
          }, 1200);
        }, 100);  // ⚠️ 문제: 100ms 지연!
      }
      
      return newKeywords;
    }
    return prev;
  });
}
```

### 발견된 Sync 문제:

1. **100ms 지연** (라인 544): 첫 키워드 감지 후 100ms 후에 칸반보드 표시
2. **1200ms 지연** (라인 548): 첫 키워드 감지 후 1200ms(1.2초) 후에 다음 단계 카드 표시

### 해결책:

