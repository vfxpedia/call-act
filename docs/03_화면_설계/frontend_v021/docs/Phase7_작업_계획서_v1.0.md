# Phase 7: 기능 개선 및 확장 작업 계획서

## 문서 정보

| 항목 | 내용 |
|------|------|
| **문서명** | CALL:ACT Phase 7 기능 개선 및 확장 작업 계획서 |
| **버전** | 1.0 |
| **작성일** | 2026-01-19 |
| **예상 기간** | 3주 (2026-01-20 ~ 2026-02-07) |

---

## 목차

1. [작업 개요](#1-작업-개요)
2. [작업 우선순위](#2-작업-우선순위)
3. [작업별 상세 계획](#3-작업별-상세-계획)
4. [일정 계획](#4-일정-계획)
5. [데이터베이스 스키마 변경](#5-데이터베이스-스키마-변경)
6. [API 명세 추가/변경](#6-api-명세-추가변경)
7. [리스크 및 이슈](#7-리스크-및-이슈)

---

## 1. 작업 개요

### 1.1 목표

Phase 6에서 완성한 MVP를 바탕으로, **실무 적용 가능한 수준**으로 시스템을 확장하고 개선합니다.

### 1.2 주요 작업 영역

| 영역 | 작업 수 | 우선순위 |
|------|--------|---------|
| **공통 UI/UX 개선** | 2개 | P0 (최우선) |
| **상담 내역 페이지** | 1개 | P1 (높음) |
| **상담 중 페이지** | 4개 | P0 (최우선) |
| **상담 후처리 페이지** | 6개 | P0 (최우선) |
| **교육 시뮬레이션 페이지** | 전체 구현 | P2 (중간) |
| **데이터 정합성 확보** | 5개 | P1 (높음) |

---

## 2. 작업 우선순위

### 2.1 우선순위 기준

| 우선순위 | 설명 | 기준 |
|---------|------|------|
| **P0 (최우선)** | 즉시 착수, 핵심 기능 | 실무 적용 필수, 사용자 경험 직접 영향 |
| **P1 (높음)** | 1주 내 완료 | 시스템 안정성, 데이터 정합성 |
| **P2 (중간)** | 2주 내 완료 | 추가 기능, 교육/관리 |
| **P3 (낮음)** | 여유 있을 때 | 부가 기능, 최적화 |

### 2.2 작업 순서 (Phase별)

#### Phase 7-1: 핵심 기능 개선 (1주차, 2026-01-20 ~ 2026-01-24)
1. ✅ **[P0] 공통 UI/UX 개선** (1일)
   - 모달/팝업 ESC 키 닫기
   - 팝업 중앙 정렬
   
2. ✅ **[P0] 상담 중 페이지 핵심 개선** (3일)
   - 인입케이스 8개로 확대
   - 상담 시작 시 DB 즉시 저장
   - AI 검색 어시스턴트 칸반보드 연동
   
3. ✅ **[P0] 상담 후처리 페이지 개선** (3일)
   - 참조 문서 섹션 추가
   - 상담 피드백 모달 분리
   - LLM 자동 후처리 문서 생성 연동

#### Phase 7-2: 데이터 정합성 및 부가 기능 (2주차, 2026-01-27 ~ 2026-01-31)
4. ✅ **[P1] 상담 내역 페이지 개선** (1일)
   - 엑셀 다운로드 기능
   
5. ✅ **[P1] 데이터 정합성 확보** (2일)
   - employees 데이터 개선
   - notices 데이터 검증
   - view count 기능 구현
   
6. ✅ **[P1] 평가 시스템 구축** (2일)
   - 평가 항목 및 점수 계산 로직
   - 오각형 평가 모델 구현

#### Phase 7-3: 교육 시뮬레이션 (3주차, 2026-02-03 ~ 2026-02-07)
7. ✅ **[P2] 교육 시뮬레이션 페이지 구축** (5일)
   - 페이지 구현
   - 교육 DB 구축
   - AI TTS 연동
   - 우수 사례 기반 시나리오 생성

---

## 3. 작업별 상세 계획

---

## 3.0 공통 UI/UX 개선

### 3.0.1 모달/팝업 ESC 키 닫기

**목표**: 모든 모달/팝업에서 ESC 키로 닫기 가능

**영향 범위**:
- 공지사항 상세 모달
- 상담 상세 모달
- 직원 추가/수정 모달
- 카드 "자세히 보기" 모달
- 상담 피드백 모달
- 교육 시뮬레이션 피드백 모달

**구현 방안**:

```tsx
// /src/app/components/modals/BaseModal.tsx (새로 생성)
import { useEffect } from 'react';
import { X } from 'lucide-react';

interface BaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  showCloseButton?: boolean;
  className?: string;
}

export const BaseModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  showCloseButton = true,
  className = 'w-[600px]' 
}: BaseModalProps) => {
  // ESC 키 이벤트 리스너
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

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose} // 배경 클릭 시 닫기
    >
      <div 
        className={`bg-white rounded-lg ${className} max-h-[80vh] overflow-y-auto shadow-2xl`}
        onClick={(e) => e.stopPropagation()} // 모달 내부 클릭 시 전파 중지
      >
        {/* 헤더 */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-6 border-b border-[#E0E0E0]">
            {title && <h2 className="text-lg font-bold text-[#333333]">{title}</h2>}
            {showCloseButton && (
              <button 
                onClick={onClose}
                className="hover:bg-[#F5F5F5] p-1 rounded transition-colors"
                aria-label="닫기"
              >
                <X className="w-5 h-5 text-[#666666]" />
              </button>
            )}
          </div>
        )}
        
        {/* 본문 */}
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
};
```

**적용 예시**:

```tsx
// 기존 모달을 BaseModal로 교체
<BaseModal
  isOpen={isDetailModalOpen}
  onClose={() => setIsDetailModalOpen(false)}
  title="공지사항 상세"
>
  {/* 모달 내용 */}
</BaseModal>
```

**체크리스트**:
- [ ] BaseModal 컴포넌트 생성
- [ ] 모든 기존 모달을 BaseModal로 교체
  - [ ] AnnouncementModal
  - [ ] ConsultationDetailModal
  - [ ] AddEmployeeModal
  - [ ] EditEmployeeModal
  - [ ] ChangePasswordModal
  - [ ] 카드 상세 모달 (RealTimeConsultationPage)
- [ ] ESC 키 동작 테스트
- [ ] 배경 클릭 닫기 테스트

---

### 3.0.2 팝업 중앙 정렬

**목표**: 모든 팝업이 화면 중앙에 정확히 위치

**현재 문제**:
- 일부 모달이 화면 상단에 치우쳐 있음
- 스크롤 위치에 따라 모달 위치가 달라짐

**해결 방안**:

```css
/* BaseModal에 이미 적용됨 */
.modal-overlay {
  position: fixed;
  inset: 0; /* top: 0; right: 0; bottom: 0; left: 0; */
  display: flex;
  align-items: center; /* 세로 중앙 */
  justify-content: center; /* 가로 중앙 */
  z-index: 50;
}
```

**체크 대상 페이지**:
- [ ] 공지사항 페이지 (공지 작성/수정 모달)
- [ ] 직원 관리 페이지 (사원 추가/수정 모달)
- [ ] 상담 내역 페이지 (상담 상세 모달)
- [ ] 실시간 상담 페이지 (카드 상세 모달)
- [ ] 상담 후처리 페이지 (피드백 모달)
- [ ] 교육 시뮬레이션 페이지 (피드백 모달)

**일정**: 1일 (2026-01-20)

---

## 3.1 상담 내역 페이지 (`/history`)

### 3.1.1 엑셀 다운로드 기능

**목표**: 상담 내역을 엑셀 파일로 다운로드

**라이브러리**: `xlsx` (설치 필요)

```bash
npm install xlsx
npm install --save-dev @types/xlsx
```

**구현 방안**:

```tsx
// /src/app/pages/ConsultationHistoryPage.tsx

import * as XLSX from 'xlsx';

// 엑셀 다운로드 함수
const handleExcelDownload = () => {
  // 1. 데이터 준비 (현재 필터링된 데이터)
  const excelData = filteredConsultations.map((item, index) => ({
    '번호': index + 1,
    '상담 ID': item.id,
    '고객명': item.customerName,
    '전화번호': item.customerPhone,
    '카테고리': item.category,
    '상담사': item.agentName,
    '상담 일시': item.date,
    '통화 시간': item.duration,
    '상태': item.status,
    '요약': item.summary
  }));

  // 2. 워크시트 생성
  const worksheet = XLSX.utils.json_to_sheet(excelData);

  // 3. 컬럼 너비 설정
  worksheet['!cols'] = [
    { wch: 5 },  // 번호
    { wch: 20 }, // 상담 ID
    { wch: 10 }, // 고객명
    { wch: 15 }, // 전화번호
    { wch: 12 }, // 카테고리
    { wch: 10 }, // 상담사
    { wch: 18 }, // 상담 일시
    { wch: 10 }, // 통화 시간
    { wch: 8 },  // 상태
    { wch: 50 }  // 요약
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
  toast.success(`상담 내역이 다운로드되었습니다. (${fileName})`);
};

// UI
<button
  onClick={handleExcelDownload}
  className="flex items-center gap-2 px-4 py-2 bg-[#34A853] text-white rounded-lg hover:bg-[#2D9A4C] transition-colors"
>
  <Download className="w-4 h-4" />
  엑셀 다운로드
</button>
```

**파일명 형식**:
```
상담내역_20260120_143052.xlsx
```

**체크리스트**:
- [ ] xlsx 라이브러리 설치
- [ ] 엑셀 다운로드 함수 구현
- [ ] 버튼 UI 추가
- [ ] 필터링된 데이터만 다운로드되는지 확인
- [ ] 컬럼 너비 최적화
- [ ] 한글 파일명 인코딩 테스트 (특수문자 포함)

**일정**: 0.5일 (2026-01-27)

---

## 3.2 상담 중 페이지 (`/consultation`)

### 3.2.1 인입케이스 8개로 확대

**현재**: 6개 카테고리
- 카드분실, 해외결제, 수수료문의, 한도증액, 연체문의, 기타문의

**변경**: 8개 카테고리
- **분실/도난**, **한도**, **결제/승인**, **이용내역**, **수수료/연체**, **포인트/혜택**, **정부지원**, **기타**

**구현 방안**:

```tsx
// /src/data/mockData.ts

// ⭐ 대기 콜 현황 (8개 카테고리로 확대)
const getInitialWaitingCalls = () => [
  { category: '분실/도난', count: 3, waitTimeSeconds: 155, priority: 'urgent' as const },
  { category: '한도', count: 2, waitTimeSeconds: 115, priority: 'normal' as const },
  { category: '결제/승인', count: 2, waitTimeSeconds: 80, priority: 'normal' as const },
  { category: '이용내역', count: 1, waitTimeSeconds: 45, priority: 'normal' as const },
  { category: '수수료/연체', count: 1, waitTimeSeconds: 190, priority: 'urgent' as const },
  { category: '포인트/혜택', count: 2, waitTimeSeconds: 95, priority: 'normal' as const },
  { category: '정부지원', count: 1, waitTimeSeconds: 60, priority: 'normal' as const },
  { category: '기타', count: 1, waitTimeSeconds: 30, priority: 'normal' as const },
];

// ⭐ 인입 케이스별 키워드 매핑 (8개)
const incomingKeywordsByCase: Record<string, string[]> = {
  '분실/도난': ['카드분실', '분실신고', '도난', '긴급정지', '재발급'],
  '한도': ['한도증액', '한도조회', '신용한도', '이용한도', '한도변경'],
  '결제/승인': ['결제', '승인', '결제거절', '승인오류', '결제취소'],
  '이용내역': ['이용내역', '거래내역', '사용내역', '명세서', '청구서'],
  '수수료/연체': ['수수료', '연회비', '이자', '연체', '납부'],
  '포인트/혜택': ['포인트', '마일리지', '적립', '혜택', '캐시백'],
  '정부지원': ['K-패스', '청년도약', '정부지원', '국가지원', '정책카드'],
  '기타': ['기타문의', '일반상담', '안내'],
};
```

**대기콜 UI 수정** (8개 카드가 들어가도록 레이아웃 조정):

```tsx
// 2열 그리드 → 4열 그리드로 변경
<div className="grid grid-cols-4 gap-3">
  {waitingCalls.map((call) => (
    <div
      key={call.category}
      className={`bg-white rounded-lg border-2 p-3 cursor-pointer hover:shadow-lg transition-all ${
        call.priority === 'urgent' 
          ? 'border-[#EA4335]/40 hover:border-[#EA4335]' 
          : 'border-[#E0E0E0] hover:border-[#0047AB]/40'
      }`}
      onClick={() => handleCallStart(call.category)}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-[#666666]">{call.category}</span>
        {call.priority === 'urgent' && (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#EA4335] text-white">
            긴급
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-[#0047AB] mb-1">{call.count}명</div>
      <div className="text-[11px] text-[#999999]">
        평균 대기: {formatTime(call.waitTimeSeconds)}
      </div>
    </div>
  ))}
</div>
```

**체크리스트**:
- [ ] mockData.ts에서 카테고리 8개로 확대
- [ ] 키워드 매핑 업데이트
- [ ] UI 레이아웃 조정 (4열 그리드)
- [ ] scenarios.ts에서 시나리오 카테고리 업데이트
- [ ] 상담 후처리 페이지에서 카테고리 선택 옵션 업데이트

**일정**: 0.5일 (2026-01-20)

---

### 3.2.2 상담 시작 시 DB 즉시 저장

**목표**: 통화 시작 버튼 클릭 시 즉시 DB에 상담 기록 생성

**현재 문제**:
- 상담 종료 후에만 DB 저장
- 상담 중 시스템 오류 시 데이터 유실 위험

**해결 방안**:

**1. 상담 ID 생성 규칙**:
```
CS-YYYYMMDD-HHMM
예: CS-20260120-1432
```

**2. 통화 시작 시 저장할 데이터**:

```typescript
// /src/types/consultation.ts
interface ConsultationRecord {
  id: string;                    // 'CS-20260120-1432'
  customerId: string;             // 'CUST-001'
  customerName: string;           // '홍길동'
  customerPhone: string;          // '010-1234-5678'
  agentId: string;                // 'EMP-2024-001'
  agentName: string;              // '김현우'
  startTime: string;              // '2026-01-20T14:32:15+09:00' (ISO 8601)
  endTime: string | null;         // null (통화 중)
  status: 'in_progress' | 'completed' | 'incomplete';  // 'in_progress'
  category: string;               // '분실/도난' (인입케이스)
  subcategories: string[];        // [] (나중에 후처리에서 추가)
  summary: string | null;         // null (나중에 LLM이 생성)
  transcript: string;             // '' (STT 누적)
  referenceDocs: string[];        // [] (칸반보드에 표시된 문서 ID)
  memo: string;                   // '' (상담 메모)
  createdAt: string;              // 생성 시각
  updatedAt: string;              // 마지막 업데이트 시각
}
```

**3. 구현 코드**:

```tsx
// /src/app/pages/RealTimeConsultationPage.tsx

const handleCallStart = async (category: string) => {
  try {
    // 1. 상담 ID 생성
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, ''); // YYYYMMDD
    const timeStr = now.toTimeString().slice(0, 5).replace(/:/g, '');  // HHMM
    const consultationId = `CS-${dateStr}-${timeStr}`;
    
    // 2. 상담 기록 생성
    const consultationRecord: ConsultationRecord = {
      id: consultationId,
      customerId: customer.id,
      customerName: customer.name,
      customerPhone: customer.phone,
      agentId: currentUser.id,
      agentName: currentUser.name,
      startTime: now.toISOString(),
      endTime: null,
      status: 'in_progress',
      category: category,
      subcategories: [],
      summary: null,
      transcript: '',
      referenceDocs: [],
      memo: '',
      createdAt: now.toISOString(),
      updatedAt: now.toISOString()
    };
    
    // 3. DB 저장 (API 호출)
    const response = await fetch('/api/consultations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(consultationRecord)
    });
    
    if (!response.ok) {
      throw new Error('상담 기록 생성 실패');
    }
    
    // 4. 상태 업데이트
    setCurrentConsultationId(consultationId);
    setIsCallActive(true);
    setCurrentCase(category);
    
    // 5. STT 시작
    startSTT(consultationId);
    
    // 6. 시뮬레이션 시작 (mockData 사용 시)
    const scenario = getScenarioByCategory(category);
    setActiveScenario(scenario);
    simulateDialogue(scenario);
    
    toast.success('상담이 시작되었습니다.');
    
  } catch (error) {
    console.error('상담 시작 오류:', error);
    toast.error('상담 시작에 실패했습니다.');
  }
};

// STT 텍스트 수신 시 transcript 업데이트 (실시간 저장)
const updateTranscript = async (newText: string) => {
  try {
    const response = await fetch(`/api/consultations/${currentConsultationId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        transcript: currentTranscript + '\n' + newText,
        updatedAt: new Date().toISOString()
      })
    });
    
    if (!response.ok) {
      console.error('transcript 업데이트 실패');
    }
  } catch (error) {
    console.error('transcript 업데이트 오류:', error);
  }
};

// 칸반보드 카드 추가 시 referenceDocs 업데이트
const addReferenceDoc = async (docId: string) => {
  try {
    const response = await fetch(`/api/consultations/${currentConsultationId}/reference-docs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        docId: docId,
        addedAt: new Date().toISOString()
      })
    });
    
    if (!response.ok) {
      console.error('참조 문서 추가 실패');
    }
  } catch (error) {
    console.error('참조 문서 추가 오류:', error);
  }
};
```

**4. 백엔드 API**:

```python
# FastAPI 예시
@app.post("/api/consultations")
async def create_consultation(
    consultation: ConsultationRecord,
    current_user: User = Depends(get_current_user)
):
    """상담 기록 생성 (통화 시작 시)"""
    
    # DB 저장
    result = await db.consultations.insert_one(consultation.dict())
    
    return {"id": consultation.id, "message": "상담 기록이 생성되었습니다."}

@app.patch("/api/consultations/{consultation_id}")
async def update_consultation(
    consultation_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user)
):
    """상담 기록 업데이트 (실시간)"""
    
    update_data['updatedAt'] = datetime.now().isoformat()
    
    await db.consultations.update_one(
        {"id": consultation_id},
        {"$set": update_data}
    )
    
    return {"message": "상담 기록이 업데이트되었습니다."}
```

**체크리스트**:
- [ ] ConsultationRecord 타입 정의
- [ ] 상담 ID 생성 함수
- [ ] 통화 시작 시 DB 저장 API 호출
- [ ] STT transcript 실시간 업데이트
- [ ] 참조 문서 추가 API 구현
- [ ] 에러 핸들링 (네트워크 오류 등)
- [ ] 상담 중 페이지 새로고침 시 복구 로직

**일정**: 1일 (2026-01-21)

---

### 3.2.3 AI 검색 어시스턴트 칸반보드 연동

**목표**: AI 검색 어시스턴트로 검색한 결과를 칸반보드에 표시

**현재 상황**:
- AI 검색 어시스턴트는 텍스트 답변만 제공
- 칸반보드는 STT 키워드 기반으로만 표시

**개선 방안**:
- 사용자가 검색한 쿼리 → RAG 검색 → 결과를 칸반보드에 추가
- 태그 색상 구분: **STT 자동 (파란색)** vs **사용자 검색 (초록색)**

**구현 코드**:

```tsx
// /src/app/pages/RealTimeConsultationPage.tsx

// 사용자 검색 상태
const [userSearchQuery, setUserSearchQuery] = useState('');
const [userSearchResults, setUserSearchResults] = useState<ScenarioCard[]>([]);

// AI 검색 어시스턴트에서 검색 실행
const handleUserSearch = async () => {
  if (!userSearchQuery.trim()) {
    toast.error('검색어를 입력해주세요.');
    return;
  }
  
  try {
    // 1. RAG 검색 API 호출
    const response = await fetch('/api/rag/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        query: userSearchQuery,
        keywords: [], // 사용자 직접 검색이므로 키워드 비워둠
        consultationId: currentConsultationId,
        searchType: 'user_query' // 검색 타입 구분
      })
    });
    
    if (!response.ok) {
      throw new Error('검색 실패');
    }
    
    const data = await response.json();
    const searchCards: ScenarioCard[] = data.cards.map((card: any) => ({
      ...card,
      searchType: 'user_query', // ⭐ 사용자 검색으로 태그
      searchQuery: userSearchQuery // 검색어 저장
    }));
    
    // 2. 검색 결과를 칸반보드에 추가
    setUserSearchResults(searchCards);
    
    // 3. 참조 문서에 추가
    for (const card of searchCards) {
      await addReferenceDoc(card.id);
    }
    
    // 4. 성공 메시지
    toast.success(`${searchCards.length}개의 문서를 찾았습니다.`);
    
    // 5. 검색어 초기화
    setUserSearchQuery('');
    
  } catch (error) {
    console.error('검색 오류:', error);
    toast.error('검색에 실패했습니다.');
  }
};

// 칸반보드 렌더링 (STT 자동 + 사용자 검색 통합)
const renderKanbanBoard = () => {
  // STT 자동 카드
  const sttCards = activeScenario?.steps[currentStep - 1]?.currentSituationCards || [];
  
  // 사용자 검색 카드
  const userCards = userSearchResults;
  
  // 통합
  const allCards = [...sttCards, ...userCards];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {allCards.map((card) => (
        <div
          key={card.id}
          className="bg-gradient-to-br from-white to-[#F8FBFF] border-2 border-[#0047AB]/20 rounded-lg p-5"
        >
          {/* 태그 (STT 자동 vs 사용자 검색) */}
          <div className="flex items-center justify-between mb-2">
            <span 
              className={`text-[9px] px-1.5 py-0.5 rounded font-medium ${
                card.searchType === 'user_query'
                  ? 'bg-[#34A853] text-white' // 초록색 (사용자 검색)
                  : 'bg-[#0047AB] text-white' // 파란색 (STT 자동)
              }`}
            >
              {card.searchType === 'user_query' ? '키워드검색' : `Step ${currentStep}`}
            </span>
            
            {card.searchType === 'user_query' && (
              <span className="text-[10px] text-[#999999]">
                검색어: "{card.searchQuery}"
              </span>
            )}
          </div>
          
          {/* 카드 내용 (기존과 동일) */}
          <h3 className="text-base font-bold text-[#0047AB] mb-2.5">{card.title}</h3>
          {/* ... */}
        </div>
      ))}
    </div>
  );
};
```

**UI 예시**:

```
┌──────────────────┐ ┌──────────────────┐
│ Step 1           │ │ Step 1           │
│ 카드 즉시 정지   │ │ 분실 신고 접수   │
│ (STT 자동)       │ │ (STT 자동)       │
└──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ 키워드검색       │ │ 키워드검색       │
│ 해외 긴급 재발급 │ │ 임시 카드 발급   │
│ (사용자 검색)    │ │ (사용자 검색)    │
│ 검색어: "해외..." │ │ 검색어: "해외..." │
└──────────────────┘ └──────────────────┘
```

**체크리스트**:
- [ ] AI 검색 어시스턴트 UI에 검색 버튼 추가
- [ ] 검색 API 호출 함수 구현
- [ ] 검색 결과를 칸반보드에 추가하는 로직
- [ ] 태그 색상 구분 (파란색 vs 초록색)
- [ ] 검색어 표시
- [ ] 참조 문서 자동 추가

**일정**: 1일 (2026-01-22)

---

### 3.2.4 통화 중 페이지 전환 제한 또는 백그라운드 처리

**목표**: 상담 중 다른 페이지로 이동해도 상담이 백그라운드에서 계속 진행

**옵션 1: 페이지 전환 제한 (권장하지 않음)**

```tsx
// 통화 중 페이지 이동 시 경고
useEffect(() => {
  if (!isCallActive) return;
  
  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    e.preventDefault();
    e.returnValue = '상담이 진행 중입니다. 페이지를 벗어나시겠습니까?';
  };
  
  window.addEventListener('beforeunload', handleBeforeUnload);
  
  return () => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
  };
}, [isCallActive]);
```

**옵션 2: 백그라운드 처리 (권장 ✅)**

**개념**:
- 상담 상태를 전역 Context에 저장
- 다른 페이지로 이동해도 상담 상태 유지
- Header에 "상담 중" 표시 및 복귀 버튼 제공

**구현 코드**:

```tsx
// /src/app/contexts/ConsultationContext.tsx (새로 생성)
import { createContext, useContext, useState, ReactNode } from 'react';

interface ConsultationContextType {
  isCallActive: boolean;
  currentConsultationId: string | null;
  currentCase: string;
  startConsultation: (id: string, category: string) => void;
  endConsultation: () => void;
}

const ConsultationContext = createContext<ConsultationContextType | undefined>(undefined);

export const ConsultationProvider = ({ children }: { children: ReactNode }) => {
  const [isCallActive, setIsCallActive] = useState(false);
  const [currentConsultationId, setCurrentConsultationId] = useState<string | null>(null);
  const [currentCase, setCurrentCase] = useState('');

  const startConsultation = (id: string, category: string) => {
    setIsCallActive(true);
    setCurrentConsultationId(id);
    setCurrentCase(category);
  };

  const endConsultation = () => {
    setIsCallActive(false);
    setCurrentConsultationId(null);
    setCurrentCase('');
  };

  return (
    <ConsultationContext.Provider value={{
      isCallActive,
      currentConsultationId,
      currentCase,
      startConsultation,
      endConsultation
    }}>
      {children}
    </ConsultationContext.Provider>
  );
};

export const useConsultation = () => {
  const context = useContext(ConsultationContext);
  if (!context) {
    throw new Error('useConsultation must be used within ConsultationProvider');
  }
  return context;
};
```

**Header에 상담 중 표시**:

```tsx
// /src/app/components/layout/Header.tsx

import { useConsultation } from '@/app/contexts/ConsultationContext';
import { Phone } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Header = () => {
  const { isCallActive, currentCase } = useConsultation();
  const navigate = useNavigate();

  return (
    <header className="...">
      {/* 왼쪽: 로고 + 페이지명 */}
      <div className="flex items-center gap-4">
        {/* ... */}
      </div>
      
      {/* 중앙: 상담 중 표시 */}
      {isCallActive && (
        <div 
          className="flex items-center gap-2 px-4 py-2 bg-[#EA4335] text-white rounded-lg cursor-pointer animate-pulse"
          onClick={() => navigate('/consultation')}
        >
          <Phone className="w-4 h-4" />
          <span className="text-sm font-medium">상담 중 ({currentCase})</span>
          <span className="text-xs">클릭하여 복귀</span>
        </div>
      )}
      
      {/* 오른쪽: 알림 + 프로필 */}
      <div className="flex items-center gap-4">
        {/* ... */}
      </div>
    </header>
  );
};
```

**App.tsx에 Provider 추가**:

```tsx
// /src/app/App.tsx

import { ConsultationProvider } from './contexts/ConsultationContext';

function App() {
  return (
    <ConsultationProvider>
      <Router>
        {/* ... */}
      </Router>
    </ConsultationProvider>
  );
}
```

**체크리스트**:
- [ ] ConsultationContext 생성
- [ ] Header에 상담 중 표시 추가
- [ ] 상담 중 페이지에서 Context 연동
- [ ] 다른 페이지로 이동 후 복귀 시 상담 상태 복원
- [ ] STT가 백그라운드에서 계속 동작하는지 확인

**일정**: 1일 (2026-01-23)

---

## 3.3 상담 후처리 페이지 (`/aftercall`)

### 3.3.1 참조 문서 섹션 추가

**목표**: 상담 중 표시된 정보 카드를 "참조 문서"로 정리하여 표시

**위치**: 좌측 하단 (상담 전문 아래)

**UI 디자인**:

```tsx
// /src/app/pages/AfterCallWorkPage.tsx

<div className="bg-white rounded-lg border-2 border-[#E0E0E0] p-6 mb-6">
  <h2 className="text-base font-bold text-[#333333] mb-4 flex items-center gap-2">
    <FileText className="w-5 h-5 text-[#0047AB]" />
    참조 문서
  </h2>
  
  {referenceDocs.length === 0 ? (
    <div className="text-center text-[#999999] text-sm py-4">
      상담 중 참조한 문서가 없습니다.
    </div>
  ) : (
    <div className="space-y-2">
      {referenceDocs.map((doc, index) => (
        <div 
          key={doc.id}
          className="flex items-center justify-between p-3 bg-[#F8FBFF] rounded-lg hover:bg-[#E8F1FC] transition-colors group"
        >
          <div className="flex items-center gap-3 flex-1">
            <span className="text-xs font-medium text-[#0047AB]">
              {index + 1}
            </span>
            <div className="flex-1">
              <div className="text-sm font-medium text-[#333333]">
                {doc.title}
              </div>
              <div className="text-xs text-[#999999] mt-0.5">
                {doc.systemPath}
              </div>
            </div>
          </div>
          
          {/* 삭제 버튼 */}
          <button
            onClick={() => handleRemoveReferenceDoc(doc.id)}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[#EA4335]/10 rounded"
            title="문서 삭제"
          >
            <Trash2 className="w-4 h-4 text-[#EA4335]" />
          </button>
        </div>
      ))}
    </div>
  )}
  
  <div className="mt-4 text-xs text-[#999999]">
    💡 참조 문서는 상담 내역에 함께 저장됩니다. 불필요한 문서는 삭제할 수 있습니다.
  </div>
</div>
```

**데이터 가져오기**:

```tsx
// 상담 기록에서 참조 문서 가져오기
useEffect(() => {
  const fetchReferenceDocs = async () => {
    try {
      const response = await fetch(`/api/consultations/${consultationId}/reference-docs`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('참조 문서 조회 실패');
      }
      
      const data = await response.json();
      
      // AI가 필터링한 관련 문서만 가져오기
      const filteredDocs = await filterRelevantDocs(data.docs, transcript);
      
      setReferenceDocs(filteredDocs);
      
    } catch (error) {
      console.error('참조 문서 조회 오류:', error);
    }
  };
  
  fetchReferenceDocs();
}, [consultationId]);

// AI가 관련 문서만 필터링
const filterRelevantDocs = async (allDocs: ScenarioCard[], transcript: string) => {
  try {
    const response = await fetch('/api/ai/filter-relevant-docs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        documents: allDocs,
        transcript: transcript
      })
    });
    
    if (!response.ok) {
      throw new Error('문서 필터링 실패');
    }
    
    const data = await response.json();
    return data.filteredDocs;
    
  } catch (error) {
    console.error('문서 필터링 오류:', error);
    return allDocs; // 오류 시 전체 반환
  }
};

// 참조 문서 삭제
const handleRemoveReferenceDoc = async (docId: string) => {
  try {
    const response = await fetch(`/api/consultations/${consultationId}/reference-docs/${docId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error('문서 삭제 실패');
    }
    
    // 상태 업데이트
    setReferenceDocs(prev => prev.filter(doc => doc.id !== docId));
    
    toast.success('참조 문서가 삭제되었습니다.');
    
  } catch (error) {
    console.error('문서 삭제 오류:', error);
    toast.error('문서 삭제에 실패했습니다.');
  }
};
```

**백엔드 API**:

```python
# FastAPI 예시
@app.get("/api/consultations/{consultation_id}/reference-docs")
async def get_reference_docs(
    consultation_id: str,
    current_user: User = Depends(get_current_user)
):
    """참조 문서 조회"""
    
    # DB에서 참조 문서 ID 가져오기
    consultation = await db.consultations.find_one({"id": consultation_id})
    doc_ids = consultation.get("referenceDocs", [])
    
    # 문서 상세 정보 가져오기
    docs = []
    for doc_id in doc_ids:
        # 3개 DB에서 검색
        doc = await get_document_by_id(doc_id)
        if doc:
            docs.append(doc)
    
    return {"docs": docs}

@app.post("/api/ai/filter-relevant-docs")
async def filter_relevant_docs(
    request: FilterRequest,
    current_user: User = Depends(get_current_user)
):
    """AI가 상담 내용과 관련있는 문서만 필터링"""
    
    # LLM 프롬프트
    prompt = f"""
다음 상담 전문을 읽고, 제공된 문서 중 실제로 상담에서 참조된 문서만 선택하세요.

상담 전문:
{request.transcript}

문서 목록:
{json.dumps([doc.dict() for doc in request.documents], ensure_ascii=False)}

다음 단계 예상 정보 카드는 제외하세요.
실제로 상담사가 참조한 것으로 판단되는 문서의 ID만 리스트로 반환하세요.
"""
    
    # LLM 호출
    response = await llm.generate(prompt)
    filtered_doc_ids = json.loads(response.text)
    
    # 필터링된 문서 반환
    filtered_docs = [doc for doc in request.documents if doc.id in filtered_doc_ids]
    
    return {"filteredDocs": filtered_docs}
```

**체크리스트**:
- [ ] 참조 문서 섹션 UI 구현
- [ ] 참조 문서 조회 API 호출
- [ ] AI 문서 필터링 API 구현
- [ ] 문서 삭제 기능
- [ ] 삭제 시 상담 기록 업데이트
- [ ] 빈 상태 처리

**일정**: 1일 (2026-01-24)

---

### 3.3.2 상담 피드백 모달 분리

**목표**: "후처리 완료 및 저장" 클릭 시 피드백을 모달로 표시

**현재 문제**:
- 상담 피드백이 페이지에 항상 표시되어 공간 차지
- 후처리 작업 흐름이 명확하지 않음

**개선 방안**:
- 상담 피드백 섹션 제거
- "후처리 완료 및 저장" 클릭 시 모달로 피드백 표시
- 실제 상담 vs 교육 시뮬레이션에 따라 다른 피드백

**구현 코드**:

```tsx
// /src/app/components/modals/ConsultationFeedbackModal.tsx (새로 생성)

import { BaseModal } from './BaseModal';
import { CheckCircle, XCircle, TrendingUp, TrendingDown } from 'lucide-react';

interface FeedbackScore {
  category: string;
  score: number;
  weight: number;
  feedback: string;
}

interface ConsultationFeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  isSimulation: boolean; // 교육 시뮬레이션 여부
  feedbackData: {
    totalScore: number;
    scores: FeedbackScore[];
    overallFeedback: string;
  };
  onSkip?: () => void; // 실제 상담일 때만
}

export const ConsultationFeedbackModal = ({
  isOpen,
  onClose,
  isSimulation,
  feedbackData,
  onSkip
}: ConsultationFeedbackModalProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-[#34A853]';
    if (score >= 70) return 'text-[#FBBC04]';
    return 'text-[#EA4335]';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 90) return <CheckCircle className="w-5 h-5 text-[#34A853]" />;
    if (score >= 70) return <TrendingUp className="w-5 h-5 text-[#FBBC04]" />;
    return <XCircle className="w-5 h-5 text-[#EA4335]" />;
  };

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      title={isSimulation ? "교육 시뮬레이션 피드백" : "상담 피드백"}
      className="w-[700px]"
    >
      <div className="space-y-6">
        {/* 총점 */}
        <div className="bg-gradient-to-br from-[#E8F1FC] to-white rounded-lg p-6 text-center">
          <div className="text-sm text-[#666666] mb-2">
            {isSimulation ? '교육 평가 점수' : '상담 품질 점수'}
          </div>
          <div className={`text-5xl font-bold ${getScoreColor(feedbackData.totalScore)}`}>
            {feedbackData.totalScore}점
          </div>
          <div className="text-xs text-[#999999] mt-2">
            (100점 만점)
          </div>
        </div>

        {/* 항목별 점수 */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-[#333333]">항목별 평가</h3>
          
          {feedbackData.scores.map((item, index) => (
            <div key={index} className="bg-[#F8FBFF] rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getScoreIcon(item.score)}
                  <span className="text-sm font-medium text-[#333333]">
                    {item.category}
                  </span>
                  <span className="text-xs text-[#999999]">
                    (가중치 {item.weight}%)
                  </span>
                </div>
                <span className={`text-lg font-bold ${getScoreColor(item.score)}`}>
                  {item.score}점
                </span>
              </div>
              
              {/* 진행바 */}
              <div className="w-full bg-[#E0E0E0] rounded-full h-2 mb-2">
                <div 
                  className={`h-2 rounded-full ${
                    item.score >= 90 ? 'bg-[#34A853]' : 
                    item.score >= 70 ? 'bg-[#FBBC04]' : 
                    'bg-[#EA4335]'
                  }`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
              
              <div className="text-xs text-[#666666]">
                {item.feedback}
              </div>
            </div>
          ))}
        </div>

        {/* 오각형 평가 모델 (기업 매뉴얼 준수) */}
        <div className="bg-[#F8FBFF] rounded-lg p-4">
          <h3 className="text-sm font-bold text-[#333333] mb-3">
            기업 매뉴얼 준수 평가 (오각형 모델)
          </h3>
          
          {/* 오각형 차트 자리 (추후 구현) */}
          <div className="h-48 bg-white rounded flex items-center justify-center">
            <div className="text-center text-[#999999]">
              <div className="text-sm">오각형 차트</div>
              <div className="text-xs">(차트 라이브러리로 구현 예정)</div>
            </div>
          </div>
        </div>

        {/* AI 종합 피드백 */}
        <div className="bg-white border-2 border-[#0047AB]/20 rounded-lg p-4">
          <h3 className="text-sm font-bold text-[#0047AB] mb-2 flex items-center gap-2">
            <Bot className="w-4 h-4" />
            AI 종합 피드백
          </h3>
          <p className="text-sm text-[#666666] leading-relaxed">
            {feedbackData.overallFeedback}
          </p>
        </div>

        {/* 버튼 */}
        <div className="flex gap-2">
          {!isSimulation && onSkip && (
            <button
              onClick={onSkip}
              className="flex-1 px-4 py-3 bg-[#F5F5F5] text-[#666666] rounded-lg hover:bg-[#E0E0E0] transition-colors text-sm"
            >
              [x] 피드백 건너뛰고 업무 집중하기
            </button>
          )}
          
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-[#0047AB] text-white rounded-lg hover:bg-[#003580] transition-colors text-sm font-medium"
          >
            {isSimulation ? '확인' : '확인 후 돌아가기'}
          </button>
        </div>
      </div>
    </BaseModal>
  );
};
```

**AfterCallWorkPage에서 사용**:

```tsx
// /src/app/pages/AfterCallWorkPage.tsx

const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
const [feedbackData, setFeedbackData] = useState<any>(null);

// "후처리 완료 및 저장" 버튼 클릭
const handleComplete = async () => {
  try {
    // 1. 상담 후처리 데이터 저장
    const response = await fetch(`/api/consultations/${consultationId}/complete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        summary: aiSummary,
        categories: selectedCategories,
        status: selectedStatus,
        memo: memo,
        referenceDocs: referenceDocs.map(doc => doc.id)
      })
    });
    
    if (!response.ok) {
      throw new Error('저장 실패');
    }
    
    // 2. 피드백 생성 (AI)
    const feedbackResponse = await fetch('/api/ai/generate-feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        consultationId: consultationId,
        isSimulation: isSimulation
      })
    });
    
    if (!feedbackResponse.ok) {
      throw new Error('피드백 생성 실패');
    }
    
    const feedback = await feedbackResponse.json();
    setFeedbackData(feedback);
    
    // 3. 피드백 모달 표시
    setIsFeedbackModalOpen(true);
    
  } catch (error) {
    console.error('완료 처리 오류:', error);
    toast.error('완료 처리에 실패했습니다.');
  }
};

// 피드백 건너뛰기 (실제 상담만)
const handleSkipFeedback = () => {
  setIsFeedbackModalOpen(false);
  navigate('/consultation');
  toast.success('상담이 완료되었습니다.');
};

// 피드백 확인 후 돌아가기
const handleCloseFeedback = () => {
  setIsFeedbackModalOpen(false);
  
  if (isSimulation) {
    // 교육 시뮬레이션: 시뮬레이션 페이지로
    navigate('/simulation');
  } else {
    // 실제 상담: 상담 중 페이지로
    navigate('/consultation');
  }
  
  toast.success('상담이 완료되었습니다.');
};

return (
  <div>
    {/* 기존 UI */}
    
    {/* 피드백 모달 */}
    <ConsultationFeedbackModal
      isOpen={isFeedbackModalOpen}
      onClose={handleCloseFeedback}
      isSimulation={isSimulation}
      feedbackData={feedbackData}
      onSkip={!isSimulation ? handleSkipFeedback : undefined}
    />
  </div>
);
```

**체크리스트**:
- [ ] ConsultationFeedbackModal 컴포넌트 생성
- [ ] 피드백 생성 API 구현 (백엔드)
- [ ] 실제 상담 vs 교육 시뮬레이션 분기 처리
- [ ] 오각형 차트 구현 (recharts 라이브러리)
- [ ] "피드백 건너뛰기" 버튼 조건부 표시
- [ ] 모달 닫기 후 페이지 이동

**일정**: 1일 (2026-01-27)

---

### 3.3.3 평가 항목 및 점수 계산 로직

**평가 항목**:

| 항목 | 실제 상담 가중치 | 교육 시뮬레이션 가중치 | 설명 |
|------|----------------|---------------------|------|
| **후처리 시간** | 20% | 20% | 상담 종료 후 후처리 완료까지 소요 시간 |
| **고객 감사 표현** | 10% | 10% | 상담 종료 시 고객의 감사 표현 비율 |
| **고객 감정 전환** | 20% | 0% | 부정 → 중립 → 긍정 전환 여부 (TTS 한계로 시뮬레이션 제외) |
| **기업 매뉴얼 준수** | 50% | 70% | 오각형 평가 모델 (5가지 항목) |

**백엔드 점수 계산 로직**:

```python
# /backend/ai/feedback_generator.py

from typing import Dict, List
import asyncio

class FeedbackGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def generate_feedback(
        self, 
        consultation_id: str,
        is_simulation: bool
    ) -> Dict:
        """상담 피드백 생성"""
        
        # 1. 상담 데이터 가져오기
        consultation = await get_consultation(consultation_id)
        
        # 2. 각 항목 점수 계산
        afterwork_score = await self._calculate_afterwork_time_score(consultation)
        gratitude_score = await self._calculate_gratitude_score(consultation)
        emotion_score = await self._calculate_emotion_score(consultation) if not is_simulation else 0
        manual_score = await self._calculate_manual_compliance_score(consultation)
        
        # 3. 가중치 적용
        if is_simulation:
            weights = {
                'afterwork': 0.20,
                'gratitude': 0.10,
                'emotion': 0.00,
                'manual': 0.70
            }
        else:
            weights = {
                'afterwork': 0.20,
                'gratitude': 0.10,
                'emotion': 0.20,
                'manual': 0.50
            }
        
        total_score = (
            afterwork_score * weights['afterwork'] +
            gratitude_score * weights['gratitude'] +
            emotion_score * weights['emotion'] +
            manual_score * weights['manual']
        )
        
        # 4. 항목별 피드백 생성
        scores = [
            {
                'category': '후처리 시간',
                'score': afterwork_score,
                'weight': int(weights['afterwork'] * 100),
                'feedback': await self._generate_afterwork_feedback(afterwork_score)
            },
            {
                'category': '고객 감사 표현',
                'score': gratitude_score,
                'weight': int(weights['gratitude'] * 100),
                'feedback': await self._generate_gratitude_feedback(gratitude_score)
            },
        ]
        
        if not is_simulation:
            scores.append({
                'category': '고객 감정 전환',
                'score': emotion_score,
                'weight': int(weights['emotion'] * 100),
                'feedback': await self._generate_emotion_feedback(emotion_score)
            })
        
        scores.append({
            'category': '기업 매뉴얼 준수',
            'score': manual_score,
            'weight': int(weights['manual'] * 100),
            'feedback': await self._generate_manual_feedback(manual_score)
        })
        
        # 5. 종합 피드백 생성
        overall_feedback = await self._generate_overall_feedback(
            total_score, 
            scores, 
            consultation
        )
        
        return {
            'totalScore': round(total_score, 1),
            'scores': scores,
            'overallFeedback': overall_feedback
        }
    
    async def _calculate_afterwork_time_score(self, consultation: Dict) -> float:
        """후처리 시간 점수 계산"""
        
        # 상담 종료 시간 ~ 후처리 완료 시간
        end_time = datetime.fromisoformat(consultation['endTime'])
        complete_time = datetime.fromisoformat(consultation['completedAt'])
        
        afterwork_minutes = (complete_time - end_time).total_seconds() / 60
        
        # 5분 이하: 100점
        # 10분: 80점
        # 15분: 60점
        # 20분 이상: 40점
        if afterwork_minutes <= 5:
            return 100.0
        elif afterwork_minutes <= 10:
            return 100 - (afterwork_minutes - 5) * 4  # 80점
        elif afterwork_minutes <= 15:
            return 80 - (afterwork_minutes - 10) * 4  # 60점
        elif afterwork_minutes <= 20:
            return 60 - (afterwork_minutes - 15) * 4  # 40점
        else:
            return 40.0
    
    async def _calculate_gratitude_score(self, consultation: Dict) -> float:
        """고객 감사 표현 점수 계산"""
        
        transcript = consultation['transcript']
        
        # LLM으로 감사 표현 감지
        prompt = f"""
다음 상담 전문에서 고객의 감사 표현을 감지하세요.

상담 전문:
{transcript}

고객이 "감사합니다", "고맙습니다", "수고하셨습니다" 등의 표현을 사용했다면 True,
그렇지 않다면 False를 반환하세요.

JSON 형식으로 반환:
{{"hasGratitude": true/false, "gratitudeExpressions": ["감사합니다", ...]}}
"""
        
        response = await self.llm.generate(prompt)
        result = json.loads(response.text)
        
        if result['hasGratitude']:
            # 감사 표현 횟수에 따라 점수
            count = len(result['gratitudeExpressions'])
            if count >= 3:
                return 100.0
            elif count == 2:
                return 85.0
            else:
                return 70.0
        else:
            return 50.0
    
    async def _calculate_emotion_score(self, consultation: Dict) -> float:
        """고객 감정 전환 점수 계산"""
        
        transcript = consultation['transcript']
        
        # LLM으로 감정 변화 분석
        prompt = f"""
다음 상담 전문에서 고객의 감정 변화를 분석하세요.

상담 전문:
{transcript}

상담 초반, 중반, 후반의 고객 감정을 "부정", "중립", "긍정"으로 분류하세요.

JSON 형식으로 반환:
{{
    "initial": "부정/중립/긍정",
    "middle": "부정/중립/긍정",
    "final": "부정/중립/긍정",
    "emotionFlow": "부정→중립→긍정"
}}
"""
        
        response = await self.llm.generate(prompt)
        result = json.loads(response.text)
        
        # 감정 전환 패턴 점수화
        flow = result['emotionFlow']
        
        if flow == '부정→중립→긍정' or flow == '부정→긍정':
            return 100.0
        elif flow == '중립→긍정' or flow == '부정→중립':
            return 80.0
        elif result['final'] == '긍정':
            return 70.0
        elif result['final'] == '중립':
            return 60.0
        else:
            return 40.0
    
    async def _calculate_manual_compliance_score(self, consultation: Dict) -> float:
        """기업 매뉴얼 준수 점수 계산 (오각형 모델)"""
        
        transcript = consultation['transcript']
        reference_docs = consultation['referenceDocs']
        
        # 5가지 평가 항목
        criteria = [
            '정확한 정보 제공',
            '친절한 응대',
            '절차 준수',
            '문제 해결 능력',
            '후속 조치 안내'
        ]
        
        # LLM으로 각 항목 평가
        prompt = f"""
다음 상담 전문을 기업 매뉴얼 준수 관점에서 평가하세요.

상담 전문:
{transcript}

참조 문서:
{json.dumps(reference_docs, ensure_ascii=False)}

다음 5가지 항목을 각각 100점 만점으로 평가하세요:
1. 정확한 정보 제공: 고객에게 정확하고 완전한 정보를 제공했는가?
2. 친절한 응대: 고객에게 친절하고 공손한 태도로 응대했는가?
3. 절차 준수: 회사의 표준 절차와 규정을 준수했는가?
4. 문제 해결 능력: 고객의 문제를 효과적으로 해결했는가?
5. 후속 조치 안내: 필요한 후속 조치를 명확히 안내했는가?

JSON 형식으로 반환:
{{
    "정확한 정보 제공": 85,
    "친절한 응대": 92,
    "절차 준수": 88,
    "문제 해결 능력": 90,
    "후속 조치 안내": 87,
    "평균": 88.4,
    "세부 피드백": {{
        "정확한 정보 제공": "고객에게 카드 재발급 절차를 정확히 안내했습니다...",
        ...
    }}
}}
"""
        
        response = await self.llm.generate(prompt)
        result = json.loads(response.text)
        
        return result['평균']
    
    async def _generate_overall_feedback(
        self, 
        total_score: float,
        scores: List[Dict],
        consultation: Dict
    ) -> str:
        """종합 피드백 생성"""
        
        prompt = f"""
다음 상담 평가 결과를 바탕으로 종합 피드백을 생성하세요.

총점: {total_score}점

항목별 점수:
{json.dumps(scores, ensure_ascii=False)}

상담 전문:
{consultation['transcript']}

200자 이내로 상담사의 강점과 개선점을 요약하여 피드백을 작성하세요.
긍정적이고 건설적인 톤으로 작성하세요.
"""
        
        response = await self.llm.generate(prompt)
        return response.text
```

**체크리스트**:
- [ ] 백엔드 피드백 생성 로직 구현
- [ ] 각 항목별 점수 계산 함수
- [ ] 가중치 적용 (실제 vs 시뮬레이션)
- [ ] 오각형 모델 계산 (5가지 항목)
- [ ] 종합 피드백 생성 (LLM)
- [ ] API 엔드포인트 추가

**일정**: 2일 (2026-01-28 ~ 2026-01-29)

---

(계속됩니다...)
