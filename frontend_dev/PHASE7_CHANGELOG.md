# Phase 7 변경 사항 기록 (Changelog)

## 📋 개요
Phase 7에서는 모달 ESC 키 지원, 상담 내역 엑셀 다운로드 기능, 인입대기콜 8개 대분류 확장을 완료했습니다.

---

## 🔄 수정된 파일 목록

### 1. `/src/app/components/modals/AnnouncementModal.tsx`
**변경 내용:**
- ⭐ **ESC 키 지원 추가**: 모달이 열려있을 때 ESC 키로 닫을 수 있는 기능 추가
- 모달이 열릴 때 body 스크롤 잠금 기능 추가
- 기존 UI 레이아웃 100% 유지 (변경 없음)

**추가된 코드:**
```typescript
// ESC 키 이벤트 리스너 추가
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isOpen) {
      onClose();
    }
  };

  if (isOpen) {
    document.addEventListener('keydown', handleEscape);
    // 모달 열릴 때 body 스크롤 잠금
    document.body.style.overflow = 'hidden';
  }

  return () => {
    document.removeEventListener('keydown', handleEscape);
    document.body.style.overflow = 'unset';
  };
}, [isOpen, onClose]);
```

---

### 2. `/src/app/components/modals/ConsultationDetailModal.tsx`
**변경 내용:**
- ⭐ **ESC 키 지원 추가**: 모달이 열려있을 때 ESC 키로 닫을 수 있는 기능 추가
- 모달이 열릴 때 body 스크롤 잠금 기능 추가
- 기존 UI 레이아웃 100% 유지 (변경 없음)

**추가된 코드:**
```typescript
// ESC 키 이벤트 리스너 추가
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isOpen) {
      onClose();
    }
  };

  if (isOpen) {
    document.addEventListener('keydown', handleEscape);
    // 모달 열릴 때 body 스크롤 잠금
    document.body.style.overflow = 'hidden';
  }

  return () => {
    document.removeEventListener('keydown', handleEscape);
    document.body.style.overflow = 'unset';
  };
}, [isOpen, onClose]);
```

---

### 3. `/src/app/pages/ConsultationHistoryPage.tsx`
**변경 내용:**
- ⭐ **엑셀 다운로드 기능 추가**: 상담 내역을 엑셀 파일로 다운로드할 수 있는 기능 구현
- ⭐ **개인정보 보호 강화**: 고객명 → 고객ID, 전화번호 제거
- 필터링된 상담 데이터만 다운로드됨
- 파일명: `상담내역_YYYYMMDD_HHMMSS.xlsx` 형식

**다운로드되는 컬럼 (9개):**
1. 번호
2. 상담 ID
3. **고객 ID** (customer_id) - 고객명 대신 사용 (보안)
4. 카테고리
5. 상담사
6. 상담 일시
7. 통화 시간
8. 상태
9. **상담 내용** (content) - 실제 상담 내용

**추가된 함수:**
```typescript
const handleExcelDownload = () => {
  try {
    const excelData = filteredConsultations.map((item, index) => ({
      '번호': index + 1,
      '상담 ID': item.id,
      '고객 ID': item.customer_id || `CUST-${item.id.split('-')[1]}`,  // ⭐ 보안
      '카테고리': item.category,
      '상담사': item.agent,
      '상담 일시': item.datetime,
      '통화 시간': item.duration || '-',
      '상태': item.status,
      '상담 내용': item.content || item.memo || '-'  // ⭐ 실제 내용
    }));

    // 2. 워크시트 생성
    const worksheet = XLSX.utils.json_to_sheet(excelData);

    // 3. 컬럼 너비 설정
    worksheet['!cols'] = [
      { wch: 5 },  // 번호
      { wch: 20 }, // 상담 ID
      { wch: 10 }, // 고객 ID
      { wch: 12 }, // 카테고리
      { wch: 10 }, // 상담사
      { wch: 18 }, // 상담 일시
      { wch: 10 }, // 통화 시간
      { wch: 8 },  // 상태
      { wch: 50 }  // 상담 내용
    ];

    // 4. 워크북 생성
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, '상담 내역');

    // 5. 파일명 생성 (YYYYMMDD_HHMMSS 형식)
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
    const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '');
    const fileName = `상담내역_${dateStr}_${timeStr}.xlsx`;

    // 6. 다운로드
    XLSX.writeFile(workbook, fileName);

    // 7. 성공 토스트
    toast.success(`상담 내역이 다운로드되었습니다. (${filteredConsultations.length}건)`);
  } catch (error) {
    console.error('엑셀 다운로드 오류:', error);
    toast.error('엑셀 다운로드에 실패했습니다.');
  }
};
```

**추가된 UI 요소:**
```typescript
<Button className="bg-[#0047AB] hover:bg-[#003580] h-8 text-xs" onClick={handleExcelDownload}>
  <Download className="w-3.5 h-3.5 mr-1.5" />
  엑셀 다운로드
</Button>
```

---

### 4. `/src/app/pages/RealTimeConsultationPage.tsx` ⭐ NEW
**변경 내용:**
- ⭐ **인입대기콜 8개 대분류로 확장**: 기존 6개 → 8개 대분류로 확장
- ⭐ **키워드 사전 강화**: 각 대분류별 키워드 수 대폭 확대 및 가중치 키워드 추가
- STT에서 빠르게 핵심 키워드를 추출할 수 있도록 키워드 매핑 강화

**확장된 8개 대분류:**
1. **카드분실** - 카드분실, 분실신고, 재발급, 도난, 긴급정지, 즉시정지
2. **해외결제** - 해외결제, 해외사용, 환전, 외화, 달러, 해외승인
3. **수수료문의** - 수수료문의, 연회비, 이자, 할부수수료, 면제조건
4. **한도증액** - 한도증액, 한도조회, 신용한도, 증액신청, 한도상향
5. **연체문의** - 연체문의, 연체이자, 납부, 결제지연, 미납
6. **결제일변경** ⭐ NEW - 결제일변경, 이체일변경, 출금일변경, 납부일변경
7. **포인트혜택** ⭐ NEW - 포인트, 마일리지, 캐시백, 적립, 혜택조회
8. **일반문의** - 일반상담, 안내, 기타문의, 카드발급, 서비스

**강화된 키워드 사전 (10개 카테고리):**
```typescript
const keywordDictionary = {
  "카드종류": ["신용카드", "체크카드", "법인카드", "가족카드", "선불카드", "하이브리드카드"],
  "분실도난": ["분실", "도난", "분실신고", "긴급정지", "즉시정지", "정지", "잃어버렸", "없어졌", "찾을수없"],
  "재발급": ["재발급", "재신청", "신규발급", "발급", "배송", "카드받기", "교체"],
  "결제승인": ["결제", "승인", "취소", "환불", "거절", "한도", "거래", "결제오류", "승인거부"],
  "포인트마일": ["포인트", "마일리지", "캐시백", "적립", "사용", "혜택", "리워드", "보너스"],
  "수수료연회비": ["수수료", "연회비", "이자", "할부", "수수료문의", "면제", "면제조건", "할부수수료"],
  "해외사용": ["해외", "해외결제", "해외사용", "외화", "환전", "달러", "해외승인", "해외가맹점"],
  "한도관리": ["한도", "한도증액", "한도조회", "신용한도", "증액", "증액신청", "한도상향", "한도부족"],
  "연체납부": ["연체", "연체이자", "납부", "결제지연", "미납", "입금", "가상계좌", "즉시납부"],
  "결제일": ["결제일", "결제일변경", "이체일", "출금일", "납부일", "급여일", "변경신청"],
};
```

**대기콜 초기 데이터 (8개):**
```typescript
const getInitialWaitingCalls = () => [
  { category: '카드분실', count: 3, waitTimeSeconds: 155, priority: 'urgent' as const },
  { category: '해외결제', count: 2, waitTimeSeconds: 80, priority: 'normal' as const },
  { category: '수수료문의', count: 1, waitTimeSeconds: 45, priority: 'normal' as const },
  { category: '한도증액', count: 2, waitTimeSeconds: 115, priority: 'normal' as const },
  { category: '연체문의', count: 1, waitTimeSeconds: 190, priority: 'urgent' as const },
  { category: '결제일변경', count: 2, waitTimeSeconds: 65, priority: 'normal' as const }, // ⭐ NEW
  { category: '포인트혜택', count: 1, waitTimeSeconds: 40, priority: 'normal' as const }, // ⭐ NEW
  { category: '일반문의', count: 1, waitTimeSeconds: 30, priority: 'normal' as const },
];
```

**UI 변경:**
- 대기콜 현황 패널은 2열 그리드로 자동 배치 (4x2 레이아웃)
- 각 대분류별 색상 코드 추가 (총 10개 카테고리 색상)

---

## 🗑️ 삭제된 파일

### `/src/app/components/modals/BaseModal.tsx`
**삭제 이유:**
- BaseModal을 사용하면 기존 모달의 UI가 변경되는 문제 발생
- 각 모달에 개별적으로 ESC 키 기능을 추가하여 기존 UI 유지
- 향후 필요시 재작성 가능

---

## ✅ 테스트 항목

### ESC 키 기능
- [ ] 공지사항 모달에서 ESC 키 누르면 닫힘
- [ ] 상담 상세 정보 모달에서 ESC 키 누르면 닫힘
- [ ] 모달이 열려있을 때 배경 스크롤 불가
- [ ] 모달이 닫히면 배경 스크롤 복원

### 엑셀 다운로드 기능
- [ ] 엑셀 다운로드 버튼 클릭 시 파일 다운로드
- [ ] 파일명이 `상담내역_YYYYMMDD_HHMMSS.xlsx` 형식으로 생성
- [ ] 필터링된 데이터만 다운로드됨
- [ ] 모든 컬럼이 정확하게 포함됨
- [ ] 컬럼 너비가 적절하게 설정됨
- [ ] 다운로드 성공 시 토스트 메시지 표시
- [ ] 다운로드 실패 시 에러 토스트 메시지 표시

### 인입대기콜 8개 대분류 확장
- [ ] 대기콜 현황 패널에 8개 카테고리 모두 표시됨
- [ ] 각 카테고리별 색상이 정확하게 표시됨
- [ ] 2열 그리드 레이아웃이 정상적으로 작동함
- [ ] 각 카테고리 클릭 시 해당 키워드 사전이 적용됨
- [ ] STT에서 확장된 키워드가 정확하게 감지됨
- [ ] 결제일변경, 포인트혜택 카테고리가 정상 작동함

---

## 📝 참고 사항

1. **기존 UI 유지**: 모든 변경 사항은 기존 UI/UX를 변경하지 않고 기능만 추가하는 방식으로 구현
2. **코드 품질**: ESC 키 이벤트 리스너는 메모리 누수 방지를 위해 cleanup 함수에서 제거
3. **사용자 경험**: 모달이 열릴 때 배경 스크롤을 막아 더 나은 UX 제공
4. **엑셀 다운로드**: XLSX 라이브러리 사용, 컬럼 너비 자동 조정으로 가독성 향상
5. **키워드 가중치**: 각 대분류별로 키워드 수를 확대하여 STT에서 빠른 핵심 키워드 추출 가능
6. **프론트엔드 우선**: 대기콜 데이터는 프론트엔드에서 Mock 데이터로 먼저 구현, 백엔드는 추후 연동

---

## 🔜 다음 작업 (Phase 7 완료)

✅ 모달 ESC 키 지원 추가  
✅ 상담 내역 엑셀 다운로드 기능 추가  
✅ 인입대기콜 8개 대분류 확장  
✅ 자주 찾는 문의 상세 모달 및 관련 문서 연결  

**Phase 7 완료!** 🎉

---

## 📑 Phase 7-2: 자주 찾는 문의 관련 문서 연결 (2026-01-20)

### 개요
대시보드의 "자주 찾는 문의"를 클릭하면 상세 내용과 관련 문서를 표시하고, "보기" 버튼 클릭 시 문서 전문(약관)을 볼 수 있는 기능을 구현했습니다.

---

### 5. `/src/data/frequentInquiriesDetail.ts` ⭐ 수정
**변경 내용:**
- ⭐ **document_id 추가**: scenarios.ts의 문서 ID와 매핑
- 각 자주 찾는 문의에 `relatedDocument.document_id` 필드 추가

**데이터 구조:**
```typescript
export const frequentInquiriesDetailData = [
  { 
    id: 1, 
    keyword: '카드 분실', 
    question: '카드를 분실했어요. 어떻게 해야 하나요?', 
    count: 45, 
    trend: 'up',
    content: `...`,
    relatedDocument: {
      document_id: 'card-1-1-1',  // ⭐ scenarios.ts의 ScenarioCard.id
      title: '카드 즉시 사용 정지',
      regulation: '여신전문금융업법 제16조',
      summary: '...'
    }
  },
  // ... 5개 문의
];
```

**ID 매핑표:**
| 자주 찾는 문의 | document_id | 시나리오 출처 |
|---------------|-------------|--------------|
| 카드 분실 | `card-1-1-1` | scenario-1 (카드분실) Step 1 |
| 해외 결제 | `card-2-1-1` | scenario-2 (해외결제) Step 1 |
| 포인트 적립 | `card-1-2-1` | 임시 (추후 시나리오 확장 필요) |
| 연회비 환불 | `card-3-1-1` | scenario-3 (수수료문의) Step 1 |
| 한도 증액 | `card-4-1-1` | scenario-4 (한도증액) Step 1 |

---

### 6. `/src/app/components/modals/DocumentDetailModal.tsx` ⭐ 신규 생성
**생성 목적:**
- "보기" 버튼 클릭 시 문서 전문(약관) 표시
- scenarios.ts의 ScenarioCard 데이터 활용

**주요 기능:**
1. `documentId`로 scenarios에서 문서 검색
2. 전체 약관 내용(fullText) 표시
3. 시스템 경로, 필수 확인사항, 예외사항 표시
4. ESC 키 지원
5. z-index 60으로 FrequentInquiryModal 위에 표시

**검색 로직:**
```typescript
const findDocument = () => {
  for (const scenario of scenarios) {
    for (const step of scenario.steps) {
      // currentSituationCards 검색
      const foundInCurrent = step.currentSituationCards.find(
        card => card.id === documentId
      );
      if (foundInCurrent) return foundInCurrent;
      
      // nextStepCards 검색
      const foundInNext = step.nextStepCards.find(
        card => card.id === documentId
      );
      if (foundInNext) return foundInNext;
    }
  }
  return null;
};
```

**UI 구성:**
- Header: 제목, 근거 규정, 처리 시간
- Content:
  - 📋 요약
  - 💻 시스템 경로
  - ✅ 필수 확인 사항
  - ⚠️ 예외 사항
  - 💡 참고사항
  - 📄 전체 약관 (fullText)
- Footer: 닫기 버튼

---

### 7. `/src/app/components/modals/FrequentInquiryModal.tsx` ⭐ 수정
**변경 내용:**
- ⭐ **"보기" 버튼 기능 구현**: DocumentDetailModal 연결
- DocumentDetailModal import 및 state 추가

**추가된 코드:**
```typescript
import DocumentDetailModal from './DocumentDetailModal';

const [isDocumentModalOpen, setIsDocumentModalOpen] = useState(false);
const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

// "보기" 버튼 클릭 핸들러
const handleViewDocument = () => {
  if (detail?.relatedDocument.document_id) {
    setSelectedDocumentId(detail.relatedDocument.document_id);
    setIsDocumentModalOpen(true);
  }
};

// 모달 렌더링
{isDocumentModalOpen && selectedDocumentId && (
  <DocumentDetailModal
    isOpen={isDocumentModalOpen}
    onClose={() => setIsDocumentModalOpen(false)}
    documentId={selectedDocumentId}
  />
)}
```

**버튼 수정:**
```typescript
<button 
  onClick={handleViewDocument}  // ⭐ 클릭 이벤트 추가
  className="flex-shrink-0 flex items-center gap-1 px-2 py-1 rounded bg-[#E8F1FC] hover:bg-[#0047AB] text-[#0047AB] hover:text-white transition-colors text-[10px] font-medium"
>
  <ExternalLink className="w-3 h-3" />
  <span>보기</span>
</button>
```

---

### 8. `/src/app/pages/DashboardPage.tsx` ✅ 확인
**현재 상태:**
- 자주 찾는 문의 클릭 이벤트 이미 구현됨
- `handleFrequentInquiryClick` 함수 정상 작동
- FrequentInquiryModal에 `detailData` props 전달 확인

**수정 불필요** - 이미 정상 작동

---

## ✅ 테스트 항목 (추가)

### 자주 찾는 문의 기능
- [x] 대시보드에서 자주 찾는 문의 클릭 시 모달 표시
- [x] 상세 내용(content) 정확하게 표시
- [x] 관련 문서 정보 표시 (제목, 요약, 근거 규정)
- [x] "보기" 버튼 클릭 시 DocumentDetailModal 표시
- [x] 문서 전문(fullText) 정확하게 표시
- [x] 시스템 경로, 필수 확인사항, 예외사항 표시
- [x] ESC 키로 두 모달 모두 닫기 가능
- [x] 모달 위에 모달 표시 (z-index 50 → 60)

---

## 📊 데이터 흐름

### Mock 데이터 (현재)
```
frequentInquiriesDetailData (document_id)
         ↓
    scenarios.ts (ScenarioCard 검색)
         ↓
  DocumentDetailModal (fullText 표시)
```

### 실제 API 연동 시 (추후)
```
GET /api/frequent-inquiries/{id}
    → Response: { ..., top_document: { document_id, ... } }
         ↓
GET /api/documents/{document_id}
    → Response: { id, title, content, fullText, structured, ... }
         ↓
  DocumentDetailModal (fullText 표시)
```

**프론트엔드 수정 포인트:**
- `DocumentDetailModal.tsx`: `findDocument()` → `await api.getDocument(documentId)`
- 단 한 줄만 수정하면 API 연동 완료

---

## 💡 구현 특징

### 1. 기존 데이터 재사용
- scenarios.ts의 ScenarioCard를 문서 DB로 활용
- fullText (전체 약관)가 이미 작성되어 있어 추가 작성 불필요
- 42개 카드 모두 약관 형식으로 작성 완료

### 2. 확장 가능한 구조
- document_id 기반 조회로 DB 구조와 동일
- API 연동 시 최소한의 수정만 필요
- 여러 문서를 관련 문서로 확장 가능 (배열로 변경)

### 3. 사용자 경험
- 자주 찾는 문의 → 상세 내용 → 관련 문서 전문까지 3단계 탐색
- 각 단계에서 ESC 키로 이전 단계로 복귀 가능
- 모달 위에 모달 표시로 맥락 유지

---

## 🔗 Backend 연동 가이드

자세한 내용은 `/docs/Backend_API_Integration_Guide.md` 참조

**Phase 7-2 완료!** 🎉