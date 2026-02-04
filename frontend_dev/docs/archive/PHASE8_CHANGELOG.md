# Phase 8 변경 사항 기록 (Changelog)

## 📋 개요
Phase 8에서는 후처리 페이지에 참조 문서 섹션 추가 및 피드백 모달을 구현합니다.

---

## 🎯 Phase 8-1: 참조 문서 섹션 추가 (2026-01-20) ✅ 완료

### 개요
상담 중 페이지(RealTimeConsultationPage)에서 표시된 문서를 Step별로 추적하고, 후처리 페이지(AfterCallWorkPage)의 좌측에 참조 문서 섹션을 추가했습니다. 각 인입케이스별로 다른 참조 문서가 저장되며, 문서 클릭 시 DocumentDetailModal로 전체 약관을 확인할 수 있습니다.

### ✅ 인입케이스별 참조 문서 검증 완료

**카드분실 시나리오 (총 6개 문서):**
- **Step 1 (2개)** - currentSituationCards만
  1. `card-1-1-1`: 카드 즉시 사용 정지
  2. `card-1-1-2`: 분실 신고 접수 완료

- **Step 2 (2개)** - currentSituationCards만
  3. `card-1-2-1`: 해외 출장 긴급 대응
  4. `card-1-2-2`: 공항 라운지 임시 카드

- **Step 3 (2개)** - currentSituationCards만 (예시)
  5. `card-1-3-1`: (Step 3 문서 1)
  6. `card-1-3-2`: (Step 3 문서 2)

✅ scenarios.ts와 실제 저장되는 문서 ID 일치 확인 완료  
✅ **nextStepCards (다음 예상 정보) 제외 완료** - currentSituationCards (현재 상황 관련 정보)만 저장

---

### 🐛 버그 수정 (2026-01-20)

#### 이슈 1: 12개 문서가 표시됨 (예상: 6개)

**문제:**
- RealTimeConsultationPage의 `handleConfirmEndCall`에서 `currentSituationCards` + `nextStepCards` 모두 저장 중
- 결과: 카드분실 시나리오에서 12개 문서가 표시됨 (Step1 4개 + Step2 4개 + ...)

**원인:**
```typescript
// ❌ 잘못된 코드
stepData.currentSituationCards.forEach(card => { ... }); // 현재 상황 카드
stepData.nextStepCards.forEach(card => { ... });         // 다음 예상 카드 (불필요)
```

**해결:**
```typescript
// ✅ 수정된 코드
stepData.currentSituationCards.forEach(card => { ... }); // 현재 상황 카드만
// nextStepCards 제거
```

**수정 파일:**
- `/src/app/pages/RealTimeConsultationPage.tsx` - `handleConfirmEndCall` 함수

---

#### 이슈 2: 클릭 추적 기능 미구현

**문제:**
- 상담 중 문서 "자세히 보기" 클릭 시 추적되지 않음
- 후처리 페이지에서 클릭한 문서가 리스트 상단에 표시되지 않음

**해결:**
1. **RealTimeConsultationPage: 클릭 추적 로직 추가**
   ```typescript
   // ⭐ 문서 클릭 핸들러
   const handleCardClick = (card: ScenarioCard) => {
     setSelectedDetailCard(card);
     
     // localStorage에서 클릭된 문서 ID 목록 가져오기
     const clickedDocsStr = localStorage.getItem('clickedDocuments');
     let clickedDocs: string[] = [];
     
     if (clickedDocsStr) {
       try {
         clickedDocs = JSON.parse(clickedDocsStr);
       } catch (error) {
         console.error('클릭된 문서 파싱 오류:', error);
       }
     }
     
     // 중복 제거하고 맨 앞에 추가
     clickedDocs = clickedDocs.filter(id => id !== card.id);
     clickedDocs.unshift(card.id);
     
     // localStorage에 저장
     localStorage.setItem('clickedDocuments', JSON.stringify(clickedDocs));
   };
   ```

2. **버튼 클릭 핸들러 변경**
   ```typescript
   // ❌ 이전
   onClick={() => setSelectedDetailCard(card)}
   
   // ✅ 변경
   onClick={() => handleCardClick(card)}
   ```

3. **통화 시작 시 초기화**
   ```typescript
   const handleStartCall = () => {
     // 상태 초기화
     setIsKeywordDetected(false);
     setShowNextStepCards(false);
     setIsCallActive(true);
     setCallTime(0);
     
     // ⭐ 큐 초기화
     wordQueueRef.current = [];
     isProcessingQueueRef.current = false;
     
     // ⭐ Phase 8-1: Step1의 카드 ID 저장 (통화 시작 시)
     if (activeScenario && activeScenario.steps.length > 0) {
       const step1Data = activeScenario.steps[0];
       const cardIds = [
         ...step1Data.currentSituationCards.map(card => card.id),
         ...step1Data.nextStepCards.map(card => card.id)
       ];
       setReferencedDocuments({
         step1: cardIds,
         step2: [],
         step3: []
       });
     }
     
     // ⭐ Phase 8-1: 클릭된 문서 목록 초기화
     localStorage.removeItem('clickedDocuments');
   };
   ```

4. **AfterCallWorkPage: 클릭된 문서 우선순위 정렬**
   ```typescript
   // ⭐ 클릭된 문서 우선순위 정렬
   const clickedDocsStr = localStorage.getItem('clickedDocuments');
   let clickedDocs: string[] = [];
   
   if (clickedDocsStr) {
     try {
       clickedDocs = JSON.parse(clickedDocsStr);
     } catch (error) {
       console.error('클릭된 문서 파싱 오류:', error);
     }
   }
   
   // 클릭된 문서를 우선순위로 정렬
   const sortedDocs = docs.sort((a: any, b: any) => {
     const aIndex = clickedDocs.indexOf(a.documentId);
     const bIndex = clickedDocs.indexOf(b.documentId);
     
     // 둘 다 클릭되지 않음 → 원래 순서 유지
     if (aIndex === -1 && bIndex === -1) return 0;
     // a만 클릭됨 → a를 앞으로
     if (aIndex !== -1 && bIndex === -1) return -1;
     // b만 클릭됨 → b를 앞으로
     if (aIndex === -1 && bIndex !== -1) return 1;
     // 둘 다 클릭됨 → 클릭 순서대로
     return aIndex - bIndex;
   });
   
   setReferencedDocuments(sortedDocs);
   ```

**수정 파일:**
- `/src/app/pages/RealTimeConsultationPage.tsx` - 클릭 추적 로직 추가
- `/src/app/pages/AfterCallWorkPage.tsx` - 클릭 우선순위 정렬

**동작 순서:**
1. 상담 중 페이지에서 "자세히 보기" 클릭
2. localStorage에 문서 ID 저장 (클릭 순서대로)
3. 통화 종료 → 후처리 페이지 이동
4. 후처리 페이지에서 참조 문서 불러오기
5. 클릭된 문서를 리스트 상단에 표시
6. 저장 완료 → localStorage 초기화

---

#### 이슈 3: 세션 초기화 문제 ⭐ 신규 (2026-01-20 수정)

**문제:**
- **대기콜 잡기** 클릭 시 localStorage 초기화가 안 됨
- 이전 상담의 클릭 기록(`clickedDocuments`)이 새 상담에 영향을 줌
- 캐시 초기화(Ctrl+Shift+R) 없이 새 상담 시작 시 이전 문서가 상위에 표시됨

**원인:**
```typescript
// ❌ 문제: handleCallConnect에서 초기화 없음
const handleCallConnect = (category: string) => {
  // localStorage 초기화 없음!
  // 상태 초기화만 있음
  setDisplayedKeywords([]);
  setIncomingKeywords([]);
  // ...
}
```

**해결:**
```typescript
// ✅ 해결: 대기콜 잡기 시 즉시 localStorage 초기화
const handleCallConnect = (category: string) => {
  if (isCallActive) {
    alert('이미 통화 중입니다.');
    return;
  }

  // ⭐ Phase 8-1: 새 상담 시작 시 localStorage 초기화 (클릭 추적 등)
  localStorage.removeItem('clickedDocuments');
  localStorage.removeItem('currentConsultationMemo');
  localStorage.removeItem('consultationCallTime');
  localStorage.removeItem('referencedDocuments');
  localStorage.removeItem('currentScenarioCategory');
  
  console.log('🔄 새 상담 시작: localStorage 초기화 완료');

  // 상태 초기화...
  setDisplayedKeywords([]);
  // ...
}
```

**수정 파일:**
- `/src/app/pages/RealTimeConsultationPage.tsx` - `handleCallConnect` 함수

**동작 순서:**
1. **대기콜 잡기** 클릭
2. localStorage 전체 초기화 (즉시)
3. 콘솔에 `🔄 새 상담 시작: localStorage 초기화 완료` 출력
4. 상담 진행
5. 통화 종료 → 후처리 페이지
6. **새 상담의 클릭 기록만 표시** ✅

**테스트 방법:**
1. 카드분실 상담 → "해외 출장 긴급 대응" 클릭 → 후처리 완료
2. 다시 카드분실 상담 → 아무 문서도 클릭 안 함 → 후처리 페이지 확인
3. **"해외 출장 긴급 대응"이 표시되지 않아야 함** ✅

---

### 🎨 UI 개선 사항 (2026-01-20 추가)

**변경 내용:**
1. **폰트 크기 통일**
   - "상담 전문"과 "참조 문서" 제목을 동일한 스타일로 변경
   - `text-xs font-bold text-[#333333]` → 일관성 있는 UI

2. **높이 조정**
   - "상담 전문" 높이: 180px → 200px (20px 증가)
   - 두 섹션 간 균등한 비율 유지

3. **삭제 기능 추가 ⭐ 신규**
   - 각 문서 우측에 삭제 아이콘 (Trash2) 추가
   - 클릭 시 삭제 확인 모달 표시
   - 모달 메시지: "해당 참조 문서를 저장하지 않겠습니까?"
   - 확인 시 문서 제외 + 토스트 알림

4. **삭제 확인 모달**
   - 가운데 팝업 형식
   - 문서 제목 표시
   - "취소" / "제외" 버튼

5. **삭제 성공 피드백**
   - 토스트 메시지: "참조 문서가 제외되었습니다."
   - 3초 후 자동 사라짐
   - 화면 상단 중앙에 표시

---

### 1. `/src/app/pages/RealTimeConsultationPage.tsx` ⭐ 수정

**변경 내용:**
- ⭐ **참조 문서 추적 state 추가**: Step별로 표시된 카드 ID 저장
- ⭐ **Step 전환 시 카드 ID 자동 저장**: Step1 → Step2 → Step3 전환 시마다 해당 Step의 카드 ID 수집
- ⭐ **통화 종료 시 localStorage 저장**: 참조 문서 데이터를 localStorage에 저장하여 ACW 페이지로 전달

**추가된 state:**
```typescript
// ⭐ Phase 8-1: 참조 문서 추적 (Step별로 표시된 카드 ID 저장)
const [referencedDocuments, setReferencedDocuments] = useState<{
  step1: string[];
  step2: string[];
  step3: string[];
}>({ step1: [], step2: [], step3: [] });
```

**Step 전환 시 카드 ID 저장 (STT 키워드 감지):**
```typescript
// ⭐ 다음 Step의 키워드가 감지되면 Step 전환
if (nextStepKeywords.includes(wordObj.matchedKeyword)) {
  const nextStep = currentStep + 1;
  setPreviousStep(currentStep);
  setCurrentStep(nextStep);
  setMaxReachedStep(nextStep);
  // ...
  
  // ⭐ Phase 8-1: 참조 문서 추적 - 새 Step 진입 시 해당 Step의 카드 ID 저장
  if (nextStepData) {
    const stepKey = `step${nextStep}` as 'step1' | 'step2' | 'step3';
    const cardIds = [
      ...nextStepData.currentSituationCards.map(card => card.id),
      ...nextStepData.nextStepCards.map(card => card.id)
    ];
    setReferencedDocuments(prev => ({
      ...prev,
      [stepKey]: cardIds
    }));
  }
  
  setTimeout(() => {
    setShowNextStepCards(true);
  }, 800);
}
```

**통화 시작 시 Step1 카드 ID 저장:**
```typescript
const handleStartCall = () => {
  // 상태 초기화
  setIsKeywordDetected(false);
  setShowNextStepCards(false);
  setIsCallActive(true);
  setCallTime(0);
  
  // ⭐ 큐 초기화
  wordQueueRef.current = [];
  isProcessingQueueRef.current = false;
  
  // ⭐ Phase 8-1: Step1의 카드 ID 저장 (통화 시작 시)
  if (activeScenario && activeScenario.steps.length > 0) {
    const step1Data = activeScenario.steps[0];
    const cardIds = [
      ...step1Data.currentSituationCards.map(card => card.id),
      ...step1Data.nextStepCards.map(card => card.id)
    ];
    setReferencedDocuments({
      step1: cardIds,
      step2: [],
      step3: []
    });
  }
  
  // ⭐ Phase 8-1: 클릭된 문서 목록 초기화
  localStorage.removeItem('clickedDocuments');
};
```

**통화 종료 시 localStorage 저장 (이미 구현됨):**
```typescript
const handleConfirmEndCall = () => {
  // 메모를 localStorage에 저장하고 후처리로 이동
  if (memo.trim()) {
    localStorage.setItem('currentConsultationMemo', memo);
  }
  localStorage.setItem('consultationCallTime', callTime.toString());
  
  // ⭐ Phase 8-1: 참조 문서 저장
  if (activeScenario) {
    const referencedDocs: Array<{
      stepNumber: number;
      documentId: string;
      title: string;
      used: boolean;
    }> = [];
    
    // 각 Step별로 표시된 모든 카드 저장 (최대 도달한 Step까지)
    for (let i = 0; i < maxReachedStep; i++) {
      const stepData = activeScenario.steps[i];
      if (stepData) {
        // currentSituationCards
        stepData.currentSituationCards.forEach(card => {
          referencedDocs.push({
            stepNumber: stepData.stepNumber,
            documentId: card.id,
            title: card.title,
            used: true  // 표시된 카드는 모두 사용된 것으로 간주
          });
        });
        
        // nextStepCards 제거
        // stepData.nextStepCards.forEach(card => {
        //   referencedDocs.push({
        //     stepNumber: stepData.stepNumber,
        //     documentId: card.id,
        //     title: card.title,
        //     used: true
        //   });
        // });
      }
    }
    
    localStorage.setItem('referencedDocuments', JSON.stringify(referencedDocs));
    localStorage.setItem('currentScenarioCategory', activeScenario.category);
  }
  
  setIsCallActive(false);
  setIsEndCallModalOpen(false);
  
  // ⭐ 큐 초기화
  wordQueueRef.current = [];
  isProcessingQueueRef.current = false;
  
  navigate('/acw');
};
```

**데이터 구조:**
```typescript
// localStorage에 저장되는 참조 문서 데이터
[
  {
    stepNumber: 1,
    documentId: 'card-1-1-1',
    title: '카드 즉시 사용 정지',
    used: true
  },
  {
    stepNumber: 1,
    documentId: 'card-1-1-2',
    title: '분실 신고 접수 완료',
    used: true
  },
  {
    stepNumber: 2,
    documentId: 'card-1-2-1',
    title: '해외 출장 긴급 대응',
    used: true
  },
  // ...
]
```

---

### 2. `/src/app/pages/AfterCallWorkPage.tsx` ⭐ 수정

**변경 내용:**
- ⭐ **참조 문서 섹션 UI 추가**: 좌측에 "📄 참조 문서" 섹션 표시 (접었다 폈다 기능 제거)
- ⭐ **Step별 그룹화 제거**: 평평한 리스트 형식으로 표시
- ⭐ **상담 피드백 섹션 제거**: 기존 피드백 섹션 완전히 삭제 (Phase 8-2에서 모달로 재구현 예정)
- ⭐ **DocumentDetailModal 연결**: 문서 클릭 시 전체 약관 표시
- ⭐ **저장 데이터에 참조 문서 포함**: acwData에 referencedDocuments 추가
- ⭐ **FileText 아이콘 import**: lucide-react에서 FileText 아이콘 추가

**추가된 import:**
```typescript
import { Save, FileText, Trash2 } from 'lucide-react';
import DocumentDetailModal from '../components/modals/DocumentDetailModal';
import DeleteDocumentModal from '../components/modals/DeleteDocumentModal';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
```

**추가된 state (이미 구현됨):**
```typescript
// ⭐ Phase 8-1: 참조 문서 상태
const [referencedDocuments, setReferencedDocuments] = useState<Array<{
  stepNumber: number;
  documentId: string;
  title: string;
  used: boolean;
}>>([]);
const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
const [isDocumentModalOpen, setIsDocumentModalOpen] = useState(false);
const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
const [documentToDelete, setDocumentToDelete] = useState<{
  stepNumber: number;
  documentId: string;
  title: string;
  used: boolean;
} | null>(null);
```

**localStorage에서 참조 문서 불러오기 (이미 구현됨):**
```typescript
// 페이지 로드 시 localStorage에서 메모 및 참조 문서 불러오기
useEffect(() => {
  const savedMemo = localStorage.getItem('currentConsultationMemo');
  const callTime = localStorage.getItem('consultationCallTime');
  
  if (savedMemo) {
    setMemo(savedMemo);
  }
  
  // 통화 시간이 있으면 콘솔에 표시 (나중에 UI에 추가 가능)
  if (callTime) {
    console.log('통화 시간:', callTime, '초');
  }
  
  // ⭐ Phase 8-1: 참조 문서 불러오기
  const savedReferencedDocs = localStorage.getItem('referencedDocuments');
  if (savedReferencedDocs) {
    try {
      const docs = JSON.parse(savedReferencedDocs);
      setReferencedDocuments(docs);
    } catch (error) {
      console.error('참조 문서 파싱 오류:', error);
    }
  }
}, []);
```

**저장 데이터에 참조 문서 추가:**
```typescript
// PostgreSQL + pgvector에 저장할 데이터 준비
const acwData = {
  consultationId: callInfo.id,
  customerId: customerInfo.id,
  title: formData.title,
  status: formData.status,
  category: formData.category,
  aiSummary: aiSummary,
  memo: memo,
  followUpTasks: formData.followUpTasks,
  handoffDepartment: formData.handoffDepartment,
  handoffNotes: formData.handoffNotes,
  callTime: localStorage.getItem('consultationCallTime'),
  datetime: callInfo.datetime,
  // ⭐ Phase 8-1: 참조 문서 추가
  referencedDocuments: referencedDocuments,
  referencedDocumentIds: referencedDocuments.map(doc => doc.documentId), // 문서 ID만 추출
};
```

**localStorage 초기화:**
```typescript
// localStorage 완전히 clear
localStorage.removeItem('currentConsultationMemo');
localStorage.removeItem('consultationCallTime');
localStorage.removeItem('referencedDocuments'); // ⭐ Phase 8-1: 참조 문서도 삭제
localStorage.removeItem('currentScenarioCategory');
```

**참조 문서 섹션 UI (이미 구현됨):**
```typescript
{/* ⭐ Phase 8-1: 참조 문서 섹션 */}
{referencedDocuments.length > 0 && (
  <div className="mb-3">
    <h4 className="text-xs font-bold text-[#333333]">
      📄 참조 문서 ({referencedDocuments.length}개)
    </h4>
    <div className="pt-2">
      {/* 평평한 리스트 형식 */}
      {referencedDocuments.map((doc) => (
        <div
          key={doc.documentId}
          className="flex items-start gap-2 p-2 rounded bg-[#FAFAFA] hover:bg-[#E8F1FC] cursor-pointer transition-colors border border-[#E0E0E0]"
          onClick={() => {
            setSelectedDocumentId(doc.documentId);
            setIsDocumentModalOpen(true);
          }}
        >
          <FileText className="w-3.5 h-3.5 text-[#0047AB] flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-xs text-[#333333] leading-relaxed">
              {doc.title}
            </p>
          </div>
          {doc.used && (
            <span className="text-[#34A853] text-xs flex-shrink-0">✓</span>
          )}
          {/* ⭐ 삭제 아이콘 추가 */}
          <Trash2
            className="w-3.5 h-3.5 text-[#FF5733] flex-shrink-0 mt-0.5 cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              setDocumentToDelete(doc);
              setIsDeleteModalOpen(true);
            }}
          />
        </div>
      ))}
    </div>
  </div>
)}
```

**DocumentDetailModal 렌더링:**
```typescript
{/* ⭐ Phase 8-1: 문서 상세 모달 */}
{isDocumentModalOpen && selectedDocumentId && (
  <DocumentDetailModal
    isOpen={isDocumentModalOpen}
    onClose={() => {
      setIsDocumentModalOpen(false);
      setSelectedDocumentId(null);
    }}
    documentId={selectedDocumentId}
  />
)}
```

**DeleteDocumentModal 렌더링:**
```typescript
{/* ⭐ Phase 8-1: 문서 삭제 모달 */}
{isDeleteModalOpen && documentToDelete && (
  <DeleteDocumentModal
    isOpen={isDeleteModalOpen}
    onClose={() => {
      setIsDeleteModalOpen(false);
      setDocumentToDelete(null);
    }}
    document={documentToDelete}
    onDelete={() => {
      // 문서 삭제 로직
      const updatedDocs = referencedDocuments.filter(doc => doc.documentId !== documentToDelete.documentId);
      setReferencedDocuments(updatedDocs);
      localStorage.setItem('referencedDocuments', JSON.stringify(updatedDocs));
      setIsDeleteModalOpen(false);
      setDocumentToDelete(null);
      toast.success('참조 문서가 제외되었습니다.', {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "light",
      });
    }}
  />
)}
```

**UI 구조:**
```
좌측 (30%)
├── 상담 전문 (기존)
├── 📄 참조 문서 (신규) ⭐
│   ├── 카드 즉시 사용 정지 ✓
│   ├── 분실 신고 접수 완료 ✓
│   ├── 재발급 카드 신청 ✓
│   ├── 자동이체 재등록 안내 ✓
│   ├── 해외 출장 긴급 대응 ✓
│   ├── 공항 라운지 임시 카드 ✓
└── 후처리 양식 (기존)

우측 (70%)
└── 후처리 양식 (기존)
```

---

## 🎯 Phase 8-2: 피드백 모달 (2026-01-20) ✅ 완료

### 개요
"후처리 완료 및 저장" 버튼 클릭 시 피드백 모달을 표시하여 상담 품질을 평가합니다. AI 분석 기반으로 매뉴얼 준수, 고객 감사 표현, 후처리 시간, 감정 전환을 종합 평가하며, "오늘 하루 보지 않기" 기능으로 상담사가 업무에 집중할 수 있도록 합니다.

### 🎨 UI 개선 (2026-01-20 업데이트) ⭐

**변경 사항:**
- **컴팩트한 2열 레이아웃**으로 재설계
- 스크롤 없이 한 화면에 모든 정보 표시
- 오각형 차트를 좌측에 크게 배치 (280px)
- 4개 주요 점수를 우측에 간결하게 표시
- 상세 점수(9개 항목)는 접었다 폈다 가능
- **후처리 시간 자동 계산 및 실시간 표시** ⭐⭐⭐

**최종 레이아웃:**
```
┌──────────────────────────────────────────────────────┐
│ 🎯 상담 품질 피드백    90 / 100점 (우수)              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─── 좌측: 오각형 차트 ───┐  ┌─── 우측: 점수 ──┐  │
│  │                         │  │                  │  │
│  │   ⭐⭐⭐⭐⭐            │  │ 1. 매뉴얼 45/50  │  │
│  │   (매뉴얼 준수)          │  │    ━━━━━ 90%   │  │
│  │                         │  │                  │  │
│  │   도입부, 응대, 설명,    │  │ 2. 감사 10/10   │  │
│  │   적극성, 정확성         │  │    ━━━━━ 100%  │  │
│  │                         │  │                  │  │
│  │   (280px 높이)          │  │ 3. 후처리 20/20 │  │
│  │                         │  │    ━━━━━ 100%  │  │
│  │                         │  │    • 2분 15초 소요 ⭐│
│  │                         │  │                  │  │
│  │                         │  │ 4. 감정 15/20   │  │
│  │                         │  │    ━━━━━ 75%   │  │
│  └─────────────────────────┘  └──────────────────┘  │
│                                                      │
│  감정 변화: 😠 부정 → 😐 중립 → 😊 긍정              │
│                                                      │
│  ⚠️ 개선 필요: 고객확인 시 정보 누출 (-5점)          │
│                                                      │
│  [▶ 매뉴얼 상세 점수 보기] (9개 항목)                │
│                                                      │
│  ☑️ 오늘 하루 보지 않기                              │
│         [닫기]        [확인]                         │
└──────────────────────────────────────────────────────┘
```

### ⏱️ 후처리 시간 자동 측정 (2026-01-20 추가) ⭐⭐⭐

**구현 내용:**
1. **페이지 진입 시 시작 시간 기록**
   ```typescript
   // AfterCallWorkPage.tsx - useEffect
   const startTime = Date.now();
   setAcwStartTime(startTime);
   ```

2. **피드백 모달 열릴 때 실시간 계산**
   ```typescript
   const getCurrentAcwTime = () => {
     const currentTime = Date.now();
     return Math.floor((currentTime - acwStartTime) / 1000);
   };
   ```

3. **점수 자동 계산 (3분 기준)**
   ```typescript
   // FeedbackModal.tsx - calculateAcwScore
   if (seconds <= 180) return 20;  // 3분 이내 만점
   if (seconds <= 210) return 18;  // 3.5분
   if (seconds <= 240) return 16;  // 4분
   if (seconds <= 270) return 14;  // 4.5분
   if (seconds <= 300) return 12;  // 5분
   return 10;                       // 5분 초과
   ```

4. **실시간 표시**
   - "3. 후처리 시간" 카드에 실제 소요 시간 표시
   - 예: `100% • 2분 15초 소요`
   - 총점에 자동 반영

**측정 로직:**
- ✅ AfterCallWorkPage 진입 시점 = 시작
- ✅ "저장" 버튼 클릭 = 종료
- ✅ 피드백 모달에서는 현재 진행 중인 시간 실시간 표시
- ✅ acwData에 `acwTimeSeconds` 포함하여 DB 저장

**테스트 방법:**
1. 후처리 페이지 진입
2. 30초~1분 대기
3. "후처리 완료 및 저장" 클릭
4. 피드백 모달에서 "3. 후처리 시간"에 실제 시간 표시 확인
5. 콘솔에 `📊 후처리 소요 시간: 45초 (0분 45초)` 출력 확인

---

#### 1. `/src/data/feedbackRules.ts` ⭐ 신규 생성

**피드백 평가 룰 데이터 파일**

**1) 매뉴얼 준수 평가 룰 (50점)**
- 오각형 모델 (5개 대분류)
  - 도입부: 첫/끝인사, 고객확인
  - 응대: 호응어, 사과/대기표현
  - 설명: 커뮤니케이션, 알기 쉬운 설명
  - 적극성: 적극성, 언어표현
  - 정확성: 정확한 업무처리

**2) 고객 감사 표현 평가 룰 (10점)**
```typescript
export const gratitudeKeywords = [
  '덕분에 해결됐네요',
  '정말 친절하시네요',
  '설명이 명확해요',
  '감사합니다',
  '감사해요',
  '고맙습니다',
  // ...
];

export function calculateGratitudeScore(gratitudeCount: number): number {
  if (gratitudeCount === 0) return 0;
  if (gratitudeCount === 1) return 5;
  return 10; // 2회 이상
}
```

**3) 후처리 시간 평가 룰 (20점)**
```typescript
export const acwTimeStandard = {
  minIdeal: 45, // 초
  maxIdeal: 90, // 초
  minGood: 30,
  maxGood: 120,
};

export function calculateAcwTimeScore(acwTimeSeconds: number): number {
  // 이상적인 범위 (45~90초): 20점
  // 양호한 범위 (30~120초): 15점
  // 너무 빠름 (30초 미만): 10점
  // 너무 느림 (120초 이상): 5점
}
```

**4) 감정 전환 평가 룰 (20점)**
```typescript
export function calculateEmotionTransitionScore(emotion: EmotionAnalysis): number {
  // 초반 → 중반 감정 변화
  // 중반 → 후반 감정 변화
  
  // 점수 기준:
  // 부정 → 중립: +5점
  // 부정 → 긍정: +10점
  // 중립 → 긍정: +10점
  // 같은 감정 유지: +3점
  // 부정으로 전환: 0점
}
```

**5) Mock 피드백 데이터**
```typescript
export const mockFeedbackData = {
  total: 90, // 총점
  manualCompliance: 45, // 매뉴얼 준수
  customerGratitude: 10, // 고객 감사 표현
  acwTime: 20, // 후처리 시간
  emotionTransition: 15, // 감정 전환
  
  emotion: {
    early: 'negative', // 초반: 부정
    middle: 'neutral', // 중반: 중립
    late: 'positive', // 후반: 긍정
  },
  
  gratitudeCount: 2, // "감사합니다" 2회
  acwTimeSeconds: 65, // 65초 (이상적 범위)
  
  manualDetails: {
    greeting: 0, // 첫/끝인사
    customerCheck: -5, // 고객확인 (정보 누출)
    empathy: 0,
    apology: 0,
    communication: 0,
    explanation: 0,
    proactiveness: 0,
    language: 0,
    accuracy: 0,
  },
};
```

---

#### 2. `/src/app/components/modals/FeedbackModal.tsx` ⭐ 신규 생성

**피드백 모달 컴포넌트**

**UI 구조:**
```
┌─────────────────────────────────────────────┐
│ 🎯 상담 품질 피드백                          │
│ AI 분석 기반 상담 품질 평가                  │
├─────────────────────────────────────────────┤
│                                             │
│  총점: 90 / 100점                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━ 90%             │
│                                             │
│  ┌─── 1. 매뉴얼 준수 (45 / 50점) ────┐     │
│  │  ⭐⭐⭐⭐⭐ (오각형 차트)           │     │
│  │                                    │     │
│  │  ✅ 첫/끝인사: 0점                │     │
│  │  ⚠️  고객확인: -5점 (정보 누출)   │     │
│  │  ✅ 호응어: 0점                   │     │
│  │  ✅ 사과/대기표현: 0점            │     │
│  │  ✅ 커뮤니케이션: 0점             │     │
│  │  ✅ 알기 쉬운 설명: 0점           │     │
│  │  ✅ 적극성: 0점                   │     │
│  │  ✅ 언어표현: 0점                 │     │
│  │  ✅ 정확한 업무처리: 0점          │     │
│  └────────────────────────────────────┘     │
│                                             │
│  ┌─── 2. 고객 감사 표현 (10 / 10점) ─┐     │
│  │  "감사합니다" 2회 감지             │     │
│  └────────────────────────────────────┘     │
│                                             │
│  ┌─── 3. 후처리 시간 (20 / 20점) ────┐     │
│  │  65초 (이상적 범위: 45~90초)       │     │
│  │  ━━━━━━━━━━━━━━━ 72%              │     │
│  └────────────────────────────────────┘     │
│                                             │
│  ┌─── 4. 고객 감정 전환 (15 / 20점) ─┐     │
│  │  😠 초반: 부정적                   │     │
│  │  😐 중반: 중립                     │     │
│  │  😊 후반: 긍정적                   │     │
│  │                                    │     │
│  │  • 부정 → 중립 (+5점)              │     │
│  │  • 중립 → 긍정 (+10점)             │     │
│  │  총 +15점 획득                     │     │
│  └────────────────────────────────────┘     │
│                                             │
│  ☑️ 오늘 하루 피드백 보지 않고               │
│     업무 집중하기                           │
│                                             │
│         [닫기]        [확인]                │
└─────────────────────────────────────────────┘
```

**주요 기능:**

1. **오각형 그래프 (Radar Chart)**
   - recharts 라이브러리 사용
   - 5개 항목 시각화 (도입부, 응대, 설명, 적극성, 정확성)
   ```typescript
   <RadarChart data={radarData}>
     <PolarGrid stroke="#E0E0E0" />
     <PolarAngleAxis dataKey="category" />
     <PolarRadiusAxis angle={90} domain={[0, 10]} />
     <Radar dataKey="score" stroke="#0047AB" fill="#0047AB" fillOpacity={0.6} />
   </RadarChart>
   ```

2. **감정 분석 시각화**
   ```typescript
   const emotionEmoji = {
     negative: '😠',
     neutral: '😐',
     positive: '😊',
   };
   
   const emotionColor = {
     negative: '#EA4335',
     neutral: '#666666',
     positive: '#34A853',
   };
   ```

3. **"오늘 하루 보지 않기" 기능**
   ```typescript
   const handleConfirm = () => {
     if (dontShowToday) {
       const today = new Date().toDateString();
       localStorage.setItem('feedbackDontShowUntil', today);
     }
     onConfirm();
   };
   ```

4. **ESC 키 닫기**
   - ESC 키로 모달 닫기 가능
   - body 스크롤 잠금

---

#### 3. `/src/app/pages/AfterCallWorkPage.tsx` ⭐ 수정

**변경 내용:**

1. **FeedbackModal import 추가**
   ```typescript
   import FeedbackModal from '../components/modals/FeedbackModal';
   ```

2. **피드백 모달 state 추가**
   ```typescript
   const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
   ```

3. **"후처리 완료 및 저장" 버튼 클릭 로직 변경**
   ```typescript
   // ⭐ Phase 8-2: "후처리 완료 및 저장" 버튼 클릭 핸들러
   const handleSaveButtonClick = () => {
     // "오늘 하루 보지 않기" 설정 확인
     const feedbackDontShowUntil = localStorage.getItem('feedbackDontShowUntil');
     const today = new Date().toDateString();
     
     // 오늘은 피드백을 보지 않기로 설정되어 있으면 바로 저장
     if (feedbackDontShowUntil === today) {
       handleSaveACW();
     } else {
       // 피드백 모달 표시
       setIsFeedbackModalOpen(true);
     }
   };
   ```

4. **피드백 모달 "확인" 클릭 핸들러**
   ```typescript
   // ⭐ Phase 8-2: 피드백 모달에서 "확인" 클릭 시 실제 저장
   const handleFeedbackConfirm = () => {
     setIsFeedbackModalOpen(false);
     handleSaveACW();
   };
   ```

5. **피드백 모달 렌더링**
   ```typescript
   {/* ⭐ Phase 8-2: 피드백 모달 */}
   {isFeedbackModalOpen && (
     <FeedbackModal
       isOpen={isFeedbackModalOpen}
       onClose={() => setIsFeedbackModalOpen(false)}
       onConfirm={handleFeedbackConfirm}
     />
   )}
   ```

**기존 저장 로직 보존:**
- `handleSaveACW()` 함수는 그대로 유지
- 피드백 모달은 선택적으로 표시
- "오늘 하루 보지 않기" 체크 시 다음날까지 모달 표시 안 함

---

### 📊 데이터 흐름

```
[후처리 페이지]
1. "후처리 완료 및 저장" 클릭
   ↓
2. localStorage 확인: feedbackDontShowUntil === today?
   - Yes → 피드백 모달 건너뛰고 바로 저장
   - No → 피드백 모달 표시
   ↓
3. 피드백 모달 표시
   - 총점 (90/100점)
   - 오각형 그래프 (매뉴얼 준수)
   - 감정 분석 (😠 → 😐 → 😊)
   - 상세 점수
   ↓
4. "오늘 하루 보지 않기" 체크?
   - Yes → localStorage.setItem('feedbackDontShowUntil', today)
   - No → (체크 안 함)
   ↓
5. "확인" 클릭
   ↓
6. 모달 닫기 → handleSaveACW() 실행
   ↓
7. PostgreSQL 저장 → 상담 중 페이지로 이동
```

---

### ✅ 완료 기준

- [x] feedbackRules.ts 생성 완료
- [x] FeedbackModal.tsx 생성 완료
- [x] AfterCallWorkPage.tsx 연결 완료
- [x] 오각형 그래프 표시 (recharts)
- [x] 감정 분석 표시 (초반/중반/후반)
- [x] 총점 계산 (100점 만점)
- [x] "오늘 하루 보지 않기" 기능
- [x] ESC 키로 모달 닫기
- [x] 기존 저장 로직 보존

---

### 🔍 테스트 항목

- [ ] "후처리 완료 및 저장" 클릭 시 피드백 모달 표시
- [ ] 오각형 그래프 정상 렌더링
- [ ] 감정 분석 이모지 표시
- [ ] 총점 프로그레스 바 애니메이션
- [ ] "오늘 하루 보지 않기" 체크 후 확인
- [ ] 다음 상담에서 피드백 모달 안 뜸 (오늘 하루 동안)
- [ ] 다음날 피드백 모달 다시 표시
- [ ] ESC 키로 모달 닫기
- [ ] "닫기" 버튼 클릭 시 저장 안 됨
- [ ] "확인" 버튼 클릭 시 저장됨

---

**Phase 8-2 완료!** 🎉

---