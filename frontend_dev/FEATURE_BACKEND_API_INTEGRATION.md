# 🔌 교육 모드 백엔드 API 연동 가이드

## ✅ 변경 사항 요약

### **문제점:**
- ❌ 교육 모드에서 다이렉트 콜 진입 시 프론트엔드 하드코딩된 Mock 데이터 즉시 로드
- ❌ 백엔드 AI TTS, RAG, DB 검색이 개입할 여지 없음
- ❌ 실제 상담 흐름과 다른 경험 제공
- ❌ **교육 모드에서 시나리오 로드 시 자동으로 통화 시작 (Phase 1 완료 로직 오작동)**

### **해결책:**
- ✅ Mock 데이터 연결 완전 제거
- ✅ 백엔드 API 호출 구조 구축
- ✅ Timeline 기반 순차적 표시 시스템 구현
- ✅ Mock API (임시) → 실제 API로 쉽게 교체 가능한 구조
- ✅ **Phase 1 완료 시 자동 통화 시작 로직에 `isGuideModeActive` 조건 추가**

---

## 📊 Before vs After

### **Before (잘못된 구조):**
```
교육 모드 → 다이렉트 콜 클릭
  ↓
handleCallConnect() 호출 (대기콜 함수) ❌
  ↓
scenariosData.ts의 하드코딩된 데이터 즉시 로드
  ↓
고객 정보, 키워드, 정보 카드 즉시 표시 (비현실적)
```

### **After (올바른 구조):**
```
교육 모드 → 다이렉트 콜 클릭
  ↓
handleStartCall() → fetchScenarioData() 호출 ✅
  ↓
빈 화면 표시 (키워드 추출 중...)
  ↓
[Backend API] POST /api/scenarios/:id/start
  ↓
Backend 응답:
  - AI TTS로 생성된 고객 음성 (→ STT 텍스트)
  - 시나리오별 키워드
  - RAG를 통해 DB에서 검색된 정보 카드
  ↓
[Frontend] Timeline 기반 순차적 표시:
  - STT 텍스트 타이핑 효과
  - 키워드 하나씩 애니메이션
  - 정보 카드 순차적 등장 (실제 상담처럼)
```

---

## 🔧 구현된 코드 (Step 1 + Step 4)

### **1. processScenarioTimeline() - 타임라인 처리**

**위치:** `/src/app/pages/RealTimeConsultationPage.tsx` (1248번째 줄)

```typescript
// ⭐ 교육 모드: 시나리오 타임라인 처리
const processScenarioTimeline = (timeline: any[], customerData?: any) => {
  console.log('🎓 시나리오 타임라인 처리 시작:', timeline.length, '개 이벤트');
  
  // ⭐ 고객 정보가 있으면 즉시 설정
  if (customerData) {
    setCustomerInfo(customerData);
    setShowCustomerInfo(true);
    setShowRecentConsultations(true);
    console.log('👤 고객 정보 설정:', customerData.name);
  }
  
  // ⭐ Timeline 이벤트를 순차적으로 실행
  timeline.forEach(event => {
    setTimeout(() => {
      switch (event.type) {
        case 'stt':
          // STT 텍스트 추가
          setSttTexts(prev => [...prev, event.text]);
          console.log('💬 STT 추가:', event.text);
          break;
          
        case 'keyword':
          // 키워드 추가
          setIncomingKeywords(prev => [...prev, event.text]);
          setDisplayedKeywords(prev => [...prev, event.text]);
          setIsKeywordDetected(true);
          console.log('🔑 키워드 추가:', event.text);
          break;
          
        case 'infoCard':
          // 정보 카드 추가
          setCurrentStepCards(prev => [...prev, event.card]);
          console.log('📄 정보 카드 추가:', event.card.title);
          break;
          
        case 'step':
          // Step 전환
          setPreviousStep(currentStep);
          setCurrentStep(event.stepNumber);
          setMaxReachedStep(prev => Math.max(prev, event.stepNumber));
          console.log('📍 Step 전환:', event.stepNumber);
          break;
      }
    }, event.timestamp);
  });
  
  // ⭐ 키워드 추출 완료 (타임라인의 마지막 시간 기준)
  const maxTimestamp = timeline.length > 0 ? Math.max(...timeline.map(e => e.timestamp)) : 0;
  setTimeout(() => {
    setIsExtractingKeywords(false);
    console.log('✅ 키워드 추출 완료');
  }, maxTimestamp + 500);
};
```

---

### **2. fetchScenarioData() - Mock API (임시)**

**위치:** `/src/app/pages/RealTimeConsultationPage.tsx` (1308번째 줄)

```typescript
// ⭐ 교육 모드: 시나리오 데이터 로드 (Mock API - 나중에 실제 API로 교체)
const fetchScenarioData = async (scenarioId: string) => {
  console.log('🎓 교육 시나리오 데이터 요청:', scenarioId);
  
  // ⭐ TODO: 실제 백엔드 API로 교체 시 아래 주석 해제하고 Mock 데이터 제거
  /*
  try {
    const response = await fetch(`/api/scenarios/${scenarioId}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenarioId,
        userId: localStorage.getItem('employeeId') || 'EMP-001',
        mode: 'simulation'
      })
    });
    
    const data = await response.json();
    console.log('🎓 시나리오 데이터 수신:', data);
    
    processScenarioTimeline(data.timeline, data.customerInfo);
    
  } catch (error) {
    console.error('❌ 시나리오 데이터 로드 실패:', error);
    toast.error('교육 시나리오를 불러올 수 없습니다.');
  }
  */
  
  // ⭐ Mock 데이터 (임시 - 백엔드 구현 전까지 사용)
  if (!activeScenario) {
    console.error('❌ activeScenario가 없습니다.');
    toast.error('시나리오 정보를 찾을 수 없습니다.');
    return;
  }
  
  console.log('🎓 Mock 시나리오 데이터 생성:', activeScenario.category);
  
  // ⭐ Mock 고객 정보 (실제로는 백엔드에서 AI가 생성)
  const mockCustomerData = {
    id: 'CUST-SIM-001',
    name: '김철수',
    phone: '010-9876-5432',
    birthDate: '1990-05-20',
    address: '서울시 강남구 테헤란로 456',
    cardName: '테디 프리미엄 카드',
    cardNumber: '1234-5678-****-****',
    cardIssueDate: '2023-01-15',
    cardExpiryDate: '2028-01-31',
  };
  
  // ⭐ Mock Timeline (실제로는 백엔드에서 AI TTS + RAG로 생성)
  const step1Data = activeScenario.steps[0];
  const mockTimeline = [
    // STT 텍스트 (AI TTS 시뮬레이션)
    { timestamp: 1000, type: 'stt', text: '안녕하세요.' },
    { timestamp: 2500, type: 'stt', text: step1Data.customerDialog },
    
    // 키워드 추출 (순차적)
    ...step1Data.keywords.map((kw, idx) => ({
      timestamp: 4000 + (idx * 800),
      type: 'keyword',
      text: kw.text
    })),
    
    // 정보 카드 (RAG 검색 결과 시뮬레이션)
    ...step1Data.cards.map((card, idx) => ({
      timestamp: 6000 + (idx * 1200),
      type: 'infoCard',
      card: card
    }))
  ];
  
  console.log('🎓 Mock Timeline 생성 완료:', mockTimeline.length, '개 이벤트');
  
  // ⭐ 타임라인 실행
  processScenarioTimeline(mockTimeline, mockCustomerData);
};
```

---

### **3. handleStartCall() - 교육 모드 분기 처리**

**위치:** `/src/app/pages/RealTimeConsultationPage.tsx` (1456번째 줄)

**변경 전:**
```typescript
// ⭐ 교육 모드: Phase 1 튜토리얼이 진행 중이면 자동 완료 후 대기 콜 자동 선택
if (isSimulationMode && tutorialPhase === 1 && isTutorialActive) {
  // ... 대기콜 자동 선택 로직
  handleCallConnect(activeScenario.category); // ❌ Mock 데이터 즉시 로드!
  return;
}
```

**변경 후:**
```typescript
// ⭐ 교육 모드: 시나리오 데이터 로드 (백엔드 API)
if (isSimulationMode) {
  setIsExtractingKeywords(true);
  console.log('🎓 교육 모드: 다이렉트 콜 시작 (시나리오 데이터 로드)');
  
  // ⭐ 시나리오 ID 가져오기
  const scenarioId = activeScenario?.id || location.state?.scenarioId || 'SIM-001';
  
  // ⭐ 백엔드 API 호출 (현재는 Mock)
  fetchScenarioData(scenarioId);
  return;
}

// ⭐ 실제 상담 모드: 다이렉트 인입 시 키워드 추출 중 상태만 표시
if (isDirectIncoming) {
  setIsExtractingKeywords(true);
  console.log('📞 실제 상담: 다이렉트 인입 (백엔드 연동 대기)');
  // TODO: 백엔드 API 연동
}
```

---

## 🎯 백엔드 API 설계 (Step 2)

### **엔드포인트:**
```
POST /api/scenarios/:scenarioId/start
```

### **요청 (Request):**
```json
{
  "scenarioId": "SIM-001",
  "userId": "EMP-001",
  "mode": "simulation"
}
```

### **응답 (Response):**
```json
{
  "scenarioId": "SIM-001",
  "scenarioType": "basic",
  "customerInfo": {
    "id": "CUST-001",
    "name": "김철수",
    "phone": "010-1234-5678",
    "birthDate": "1990-05-20",
    "address": "서울시 강남구 테헤란로 456",
    "cardName": "테디 프리미엄 카드",
    "cardNumber": "1234-5678-****-****",
    "cardIssueDate": "2023-01-15",
    "cardExpiryDate": "2028-01-31"
  },
  "timeline": [
    {
      "timestamp": 1000,
      "type": "stt",
      "text": "안녕하세요"
    },
    {
      "timestamp": 2000,
      "type": "stt",
      "text": "카드를 분실했어요"
    },
    {
      "timestamp": 3000,
      "type": "keyword",
      "text": "카드분실"
    },
    {
      "timestamp": 5000,
      "type": "infoCard",
      "card": {
        "id": "DOC-001",
        "title": "카드 분실 신고 절차",
        "description": "즉시 사용 정지 처리",
        "category": "카드관리",
        "tags": ["긴급", "필수"],
        "content": "1. 즉시 사용 정지\\n2. 재발급 신청\\n3. 배송 추적"
      }
    },
    {
      "timestamp": 8000,
      "type": "step",
      "stepNumber": 2
    }
  ]
}
```

---

## 🔄 백엔드 처리 흐름 (예상)

### **1. 시나리오 데이터 조회**
```python
# FastAPI 예시
@app.post("/api/scenarios/{scenario_id}/start")
async def start_scenario(scenario_id: str, request: ScenarioRequest):
    # DB에서 시나리오 데이터 조회
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="시나리오를 찾을 수 없습니다.")
    
    # ...
```

### **2. AI TTS로 고객 음성 생성 (텍스트)**
```python
# AI TTS (Text-to-Speech) → 실제로는 음성이지만 여기서는 텍스트로 시뮬레이션
customer_dialogs = await ai_tts_service.generate_customer_dialog(
    scenario_id=scenario_id,
    scenario_type=scenario.type,
    personality_traits=scenario.customer_traits
)

# 예: ["안녕하세요", "카드를 분실했어요", "재발급도 해주세요"]
```

### **3. RAG로 정보 카드 검색**
```python
# RAG (Retrieval-Augmented Generation)
keywords = scenario.keywords  # ["카드분실", "재발급"]

info_cards = []
for keyword in keywords:
    # Vector DB 검색
    search_results = await vector_db.search(
        query=keyword,
        top_k=3,
        filters={"category": scenario.category}
    )
    
    # LLM으로 카드 생성
    for result in search_results:
        card = await llm_service.generate_info_card(
            keyword=keyword,
            document=result.content,
            template="consultation_guide"
        )
        info_cards.append(card)
```

### **4. Timeline 구성**
```python
timeline = []

# STT 텍스트 추가
for idx, dialog in enumerate(customer_dialogs):
    timeline.append({
        "timestamp": 1000 + (idx * 1500),
        "type": "stt",
        "text": dialog
    })

# 키워드 추가
for idx, keyword in enumerate(keywords):
    timeline.append({
        "timestamp": 4000 + (idx * 800),
        "type": "keyword",
        "text": keyword
    })

# 정보 카드 추가
for idx, card in enumerate(info_cards):
    timeline.append({
        "timestamp": 6000 + (idx * 1200),
        "type": "infoCard",
        "card": card
    })

return {
    "scenarioId": scenario_id,
    "customerInfo": customer_info,
    "timeline": timeline
}
```

---

## 🚀 실제 API 연동 방법 (Step 3)

### **프론트엔드 수정 (아주 간단!):**

**1. fetchScenarioData() 함수에서 주석 해제:**

```typescript
// ⭐ 현재 Mock 부분 주석 처리
/*
// ⭐ Mock 데이터 (임시 - 백엔드 구현 전까지 사용)
const mockCustomerData = { ... };
const mockTimeline = [ ... ];
processScenarioTimeline(mockTimeline, mockCustomerData);
*/

// ⭐ 실제 API 호출 주석 해제
try {
  const response = await fetch(`/api/scenarios/${scenarioId}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenarioId,
      userId: localStorage.getItem('employeeId') || 'EMP-001',
      mode: 'simulation'
    })
  });
  
  const data = await response.json();
  console.log('🎓 시나리오 데이터 수신:', data);
  
  processScenarioTimeline(data.timeline, data.customerInfo);
  
} catch (error) {
  console.error('❌ 시나리오 데이터 로드 실패:', error);
  toast.error('교육 시나리오를 불러올 수 없습니다.');
}
```

**끝!** 나머지 코드는 전혀 수정할 필요 없습니다.

---

## 📊 Timeline 이벤트 타입

| Type | 설명 | 필수 필드 | 예시 |
|------|------|----------|------|
| **stt** | STT 텍스트 | `text` | `{ timestamp: 1000, type: 'stt', text: '안녕하세요' }` |
| **keyword** | 키워드 | `text` | `{ timestamp: 3000, type: 'keyword', text: '카드분실' }` |
| **infoCard** | 정보 카드 | `card` | `{ timestamp: 5000, type: 'infoCard', card: {...} }` |
| **step** | Step 전환 | `stepNumber` | `{ timestamp: 8000, type: 'step', stepNumber: 2 }` |

---

## 🧪 테스트 시나리오

### **Mock API 테스트 (현재):**
1. ✅ 교육 페이지 → "불만 고객 응대" 선택
2. ✅ "시작하기" 클릭 → 상담 페이지 이동
3. ✅ 녹색 배너 확인: "🎓 교육 시나리오 대기중"
4. ✅ 통화 버튼 클릭
5. ✅ "키워드 추출 중..." 표시 확인
6. ✅ 1초 후: STT 텍스트 "안녕하세요" 표시
7. ✅ 2.5초 후: 고객 대화 표시
8. ✅ 4초 후: 첫 번째 키워드 표시
9. ✅ 6초 후: 첫 번째 정보 카드 표시
10. ✅ 순차적 애니메이션 확인

### **실제 API 테스트 (나중):**
1. ⏳ 백엔드 서버 실행
2. ⏳ fetchScenarioData() 주석 해제
3. ⏳ API 응답 확인
4. ⏳ Timeline 정상 작동 확인

---

## 📝 주요 변경 파일

1. ✅ `/src/app/pages/RealTimeConsultationPage.tsx`
   - `processScenarioTimeline()` 추가 (1248줄)
   - `fetchScenarioData()` 추가 (1308줄)
   - `handleStartCall()` 수정 (1456줄)

---

## 🎯 다음 단계

### **즉시 가능:**
- ✅ Mock API로 교육 모드 테스트
- ✅ Timeline 애니메이션 확인
- ✅ 실제 상담 모드와 비교

### **백엔드 팀 협업 필요:**
- ⏳ API 엔드포인트 구현 (`POST /api/scenarios/:id/start`)
- ⏳ AI TTS 연동 (고객 음성 → 텍스트)
- ⏳ RAG 시스템 연동 (키워드 → 정보 카드)
- ⏳ Vector DB 검색 최적화

### **프론트엔드 추가 개선:**
- ⏳ 로딩 상태 개선 (스켈레톤 UI)
- ⏳ 에러 핸들링 강화
- ⏳ Timeline 재생 속도 조절 (빠르기/느리기)
- ⏳ Step 2, 3 자동 전환 로직 추가

---

**✅ Step 1 (Mock 데이터 제거) + Step 4 (Mock API 구현) 완료!**
**🎯 이제 백엔드 팀과 Step 2, 3 진행 가능!**