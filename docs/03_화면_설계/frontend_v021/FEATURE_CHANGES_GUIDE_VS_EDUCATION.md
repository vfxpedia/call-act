# 🎓 가이드 모드 vs 교육 모드 - 기능 변경 완료

## ✅ 변경 사항 요약

### 1. **버튼 이름 변경**
- ❌ 기존: "도움말"
- ✅ 변경: "가이드"
- 📁 파일: 
  - `/src/app/pages/RealTimeConsultationPage.tsx`
  - `/src/app/pages/AfterCallWorkPage.tsx`

### 2. **🚨 CRITICAL FIX: 교육 모드 대기콜 차단**
- ⚠️ **중요:** 차단 로직은 **반드시** 상태 변경(타임스탬프, 대기콜 수 등) 전에 실행되어야 함
- ✅ **효과:** 대기콜 클릭 시 아무 상태 변경 없이 즉시 차단
- 🔒 **방지:** 타임스탬프, 대기콜 수 감소 등 상태 변경 방지

**🐛 버그 수정:**
- 초기 구현에서는 차단 로직이 1786번째 줄(타임스탬프 설정 후)에 위치
- ❌ 문제: 대기콜 클릭 시 타임스탬프, 대기콜 수 감소 등이 먼저 실행됨
- ✅ 해결: 차단 로직을 1650번째 줄(함수 시작 직후)로 이동
- 결과: 교육 모드에서 대기콜 클릭 시 아무 상태 변경 없이 즉시 차단

---

### 3. **🚨 CRITICAL FIX: 교육 모드에서 가이드 자동 활성화 방지**
- ⚠️ **문제:** 교육 모드 진입 시 가이드(말풍선)가 자동으로 활성화되는 버그
- ✅ **해결:** 교육 모드 진입 시 `isGuideModeActive`를 명시적으로 false로 설정
- 📁 **파일:** 
  - `/src/app/pages/RealTimeConsultationPage.tsx` (748번째 줄)
  - `/src/app/pages/AfterCallWorkPage.tsx` (143번째 줄)
  - `/src/app/pages/SimulationPage.tsx` (96, 223번째 줄)

---

### 4. **🚨 CRITICAL FIX: 교육 모드 Mock 데이터 연결 제거 + 백엔드 API 구조 구축**
- ⚠️ **문제:** 교육 모드에서 다이렉트 콜 진입 시 프론트엔드 하드코딩된 Mock 데이터 즉시 로드
- ✅ **해결:** 
  - Mock 데이터 연결 완전 제거 (`handleCallConnect` 호출 제거)
  - 백엔드 API 호출 구조 구축 (`fetchScenarioData` 함수 추가)
  - Timeline 기반 순차적 표시 시스템 구현
  - Mock API (임시) → 실제 API로 쉽게 교체 가능한 구조
- 📁 **파일:** `/src/app/pages/RealTimeConsultationPage.tsx`
  - `processScenarioTimeline()` 추가 (1248줄)
  - `fetchScenarioData()` 추가 (1308줄)  
  - `handleStartCall()` 수정 (1456줄)
- 📖 **상세 문서:** `/FEATURE_BACKEND_API_INTEGRATION.md`

---

### 5. **🚨 CRITICAL FIX: Phase 1 완료 시 자동 통화 시작 버그**
- ⚠️ **문제:** 교육 모드에서 시나리오 로드 시 자동으로 통화가 시작되는 버그
- ✅ **원인:** TutorialGuide onComplete 핸들러에서 `activeScenario`만 체크하고 `isGuideModeActive`를 체크하지 않음
- ✅ **해결:** Phase 1 완료 시 자동 통화 시작 조건에 `isGuideModeActive` 추가
- 📁 **파일:** `/src/app/pages/RealTimeConsultationPage.tsx` (3256줄)
- 📖 **상세 문서:** `/FIX_PHASE1_AUTOCOMPLETE_BUG.md`

---

## 🎯 두 가지 모드 명확한 구분

### **A. [가이드 모드] - UI 학습용**

#### **진입 방법:**
```
헤더 우측 상단 "가이드" 버튼 클릭
```

#### **특징:**
- ✅ **목적:** UI 사용법 학습 (투어 방식)
- ✅ **말풍선 가이드:** 활성화
- ✅ **대기콜 클릭:** 허용 (설명 진행)
- ❌ **다이렉트 콜 클릭:** 차단 (모달 표시)

#### **다이렉트 콜 차단 모달:**
```
제목: 🎓 가이드 모드 안내

내용:
가이드 모드에서는 아래 대기콜 목록에서 하나를 선택해주세요.

💡 다이렉트 콜은 실제 STT와 백엔드 연동으로 진행되어 
   가이드가 제공되지 않습니다.
```

---

### **B. [교육 모드] - 시나리오 연습용**

#### **진입 방법:**
```
교육 시뮬레이션 페이지 → 시나리오 선택 (예: "불만 고객 응대")
```

#### **특징:**
- ✅ **목적:** 실전 시나리오 연습
- ❌ **말풍선 가이드:** 비활성화
- ❌ **대기콜 클릭:** 차단 (모달 표시)
- ✅ **다이렉트 콜 클릭:** 허용 (교육 시작)

#### **화면 상단 표시:**
```
┌────────────────────────────────────────────────────┐
│  🎓 교육 시나리오 대기중                             │
│  우측 상단 통화 버튼을 클릭하여 교육을 시작하세요      │
└────────────────────────────────────────────────────┘
  (녹색 배경, 애니메이션 효과)
```

#### **대기콜 차단 모달:**
```
제목: 🎓 교육 시나리오 진행 안내

내용:
선택하신 교육 시나리오를 진행하기 위해서는 
우측 상단 통화 버튼을 클릭해주세요.

다이렉트 콜을 잡아서 진행하시면 교육이 바로 시작됩니다.

💪 상담에 최선을 다해주세요!
```

---

## 📊 모드별 비교표

| 구분 | 가이드 모드 | 교육 모드 |
|------|-----------|----------|
| **진입** | 헤더 "가이드" 버튼 | 교육 페이지 → 시나리오 선택 |
| **목적** | UI 학습 (투어) | 시나리오 연습 |
| **상태 표시** | "상담 대기중" (기본) | "🎓 교육 시나리오 대기중" (녹색) |
| **말풍선 가이드** | ✅ 활성화 | ❌ 비활성화 |
| **대기콜 클릭** | ✅ 허용 | ❌ 차단 (모달) |
| **다이렉트 콜 클릭** | ❌ 차단 (모달) | ✅ 허용 |

---

## 🔧 코드 변경 세부사항

### **1. State 추가**
```typescript
// /src/app/pages/RealTimeConsultationPage.tsx

// 기존 (가이드 모드용)
const [showDirectCallBlockModal, setShowDirectCallBlockModal] = useState(false);

// 추가 (교육 모드용)
const [showWaitingCallBlockModal, setShowWaitingCallBlockModal] = useState(false);
```

### **2. 대기콜 클릭 차단 로직**
```typescript
// handleCallConnect 함수 내부 - 🚨 함수 맨 앞으로 이동 (1650번째 줄)

const handleCallConnect = (category: string) => {
  // 1. 통화 중 검증
  if (isCallActive) {
    toast.warning('이미 통화 중입니다.');
    return;
  }
  
  // 2. ⭐🚨 교육 모드(가이드 아닌)일 때 대기콜 차단 (최우선 실행!)
  if (isSimulationMode && !isGuideModeActive) {
    console.log('🚫 교육 모드: 대기콜 차단 → 다이렉트 콜 유도');
    setShowWaitingCallBlockModal(true);
    return; // ✅ 여기서 즉시 종료! 이후 로직 실행 안 됨
  }
  
  // 3. 이하 일반 로직 (타임스탬프, 시나리오 로드 등)
  // ...
}
```

### **3. 다이렉트 콜 차단 로직 (기존 유지)**
```typescript
// handleStartCall 함수 내부

// ⭐🚨 가이드 모드일 때 다이렉트 콜 차단
if (isGuideModeActive && isSimulationMode) {
  console.log('🚫 가이드 모드: 다이렉트 콜 차단 → 대기콜 선택 유도');
  setShowDirectCallBlockModal(true);
  return;
}
```

### **4. 교육 모드 상단 배너**
```typescript
{/* ⭐ 교육 모드(가이드 아닌): "통화 연결중" 표시 */}
{isSimulationMode && !isGuideModeActive && (
  <div className="bg-gradient-to-r from-[#10B981] to-[#059669] ...">
    <div className="flex items-center justify-center gap-3">
      <div className="relative flex items-center justify-center">
        <div className="absolute w-8 h-8 bg-white/30 rounded-full animate-ping"></div>
        <div className="relative w-6 h-6 bg-white rounded-full ...">
          <Phone className="w-3 h-3 text-[#10B981]" />
        </div>
      </div>
      <div className="text-center">
        <h3 className="text-base font-bold text-white mb-1">
          🎓 교육 시나리오 대기중
        </h3>
        <p className="text-xs text-white/90">
          우측 상단 통화 버튼을 클릭하여 교육을 시작하세요
        </p>
      </div>
    </div>
  </div>
)}
```

### **5. 교육 모드 진입 시 가이드 비활성화 (CRITICAL!)**

#### **A. RealTimeConsultationPage.tsx (748번째 줄)**
```typescript
// ⭐ 교육 모드 진입 시 튜토리얼 완료 상태 초기화
useEffect(() => {
  if (isSimulationMode) {
    console.log('🎓 교육 모드 진입 → 튜토리얼 완료 상태 초기화');
    localStorage.removeItem('tutorial-phase1-completed');
    localStorage.removeItem('tutorial-phase2-completed');
    localStorage.removeItem('tutorial-completed');
    
    // ⭐🚨 교육 모드에서는 가이드 모드를 비활성화
    console.log('🎓 교육 모드 진입 → 가이드 모드 비활성화');
    localStorage.removeItem('isGuideModeActive');
    setIsGuideModeActive(false);
    setIsTutorialActive(false);
  }
}, [isSimulationMode]);
```

#### **B. AfterCallWorkPage.tsx (143번째 줄)**
```typescript
// ⭐ 교육 모드 진입 시 튜토리얼 완료 상태 초기화
useEffect(() => {
  if (isSimulationMode) {
    console.log('🎓 [후처리] 교육 모드 진입 → Phase 3 튜토리얼 완료 상태 초기화');
    localStorage.removeItem('tutorial-phase3-completed');
    
    // ⭐🚨 교육 모드에서는 가이드 모드를 비활성화
    console.log('🎓 [후처리] 교육 모드 진입 → 가이드 모드 비활성화');
    localStorage.removeItem('isGuideModeActive');
    setIsGuideModeActive(false);
    setIsTutorialActive(false);
  }
}, [isSimulationMode]);
```

#### **C. SimulationPage.tsx - 기본 교육 시작 (96번째 줄)**
```typescript
const handleStartSimulation = (scenarioId: string) => {
  sessionStorage.setItem('simulationMode', 'true');
  sessionStorage.setItem('educationType', 'basic');
  
  // ⭐🚨 가이드 모드 비활성화 (교육 모드와 분리)
  localStorage.removeItem('isGuideModeActive');
  
  navigate('/consultation/live', { 
    state: { 
      mode: 'simulation',
      educationType: 'basic',
      scenarioId 
    } 
  });
};
```

#### **D. SimulationPage.tsx - 고급 교육 시작 (223번째 줄)**
```typescript
onClick={() => {
  sessionStorage.setItem('simulationMode', 'true');
  sessionStorage.setItem('educationType', 'advanced');
  
  // ⭐🚨 가이드 모드 비활성화 (교육 모드와 분리)
  localStorage.removeItem('isGuideModeActive');
  
  localStorage.setItem('simulationCase', JSON.stringify(consultation));
  navigate('/consultation/live', {
    state: {
      mode: 'simulation',
      educationType: 'advanced',
      scenarioId: consultation.id
    }
  });
}}
```

---

## 🎬 사용 시나리오

### **시나리오 1: 가이드 모드 (UI 학습)**

```
1. 상담 중 페이지 진입
2. 헤더 우측 "가이드" 버튼 클릭
3. 말풍선 가이드 시작 (Phase 1)
4. "대기콜 목록" 설명 → 대기콜 클릭 가능
5. 대기콜 선택 → Phase 2 가이드 진행
6. 통화 버튼 클릭 시도 → ❌ 차단 모달 표시
```

### **시나리오 2: 교육 모드 (시나리오 연습)**

```
1. 교육 시뮬레이션 페이지 진입
2. 시나리오 선택 (예: "불만 고객 응대")
3. 상담 중 페이지로 자동 이동
4. 녹색 배너 표시: "🎓 교육 시나리오 대기중"
5. 대기콜 클릭 시도 → ❌ 차단 모달 표시
6. 우측 상단 통화 버튼 클릭 → ✅ 교육 시작
7. 시나리오 데이터로 상담 진행
```

---

## 🧪 테스트 체크리스트

### **가이드 모드**
- [ ] "가이드" 버튼이 헤더에 표시되는가?
- [ ] 클릭 시 Phase 1 말풍선이 나타나는가?
- [ ] 대기콜 클릭 시 Phase 2로 전환되는가?
- [ ] 통화 버튼 클릭 시 차단 모달이 나타나는가?

### **교육 모드**
- [ ] 시나리오 선택 후 녹색 배너가 표시되는가?
- [ ] **🚨 CRITICAL:** 교육 모드 진입 시 말풍선 가이드가 자동으로 나타나지 않는가?
- [ ] 대기콜 클릭 시 차단 모달이 나타나는가?
- [ ] **🚨 CRITICAL:** 대기콜 클릭 시 대기콜 수가 감소하지 않는가?
- [ ] **🚨 CRITICAL:** 대기콜 클릭 시 통화 연결이 되지 않는가?
- [ ] 통화 버튼 클릭 시 교육이 시작되는가?
- [ ] 통화 중에 말풍선 가이드가 표시되지 않는가?

---

## 📝 추가 개선 사항 (향후)

- [ ] 교육 모드 배너 디자인 A/B 테스트
- [ ] 모달 메시지 사용자 피드백 수집
- [ ] 통화 버튼에 "교육 시작" 텍스트 동적 변경 고려

---

**✅ 모든 기능 변경이 완료되었습니다!**
다음 단계: 해상도 최적화 진행