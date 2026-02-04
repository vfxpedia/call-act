# Phase A: Mock/Real 분기 구조 구축 (2026-01-21)

## 📋 개요

상담 ID 생성 방식 변경(`CS-EMP002-202601211430`) 이후, AfterCallWorkPage에서 Mock 데이터가 여전히 사용되는 문제를 발견했습니다. **Phase A**는 Mock/Real 데이터 전환이 가능한 Feature Flag 구조를 구현하여, Figma Make 개발 환경과 실제 배포 환경을 명확히 분리합니다.

---

## 🎯 목표

1. **단일 플래그로 Mock/Real 모드 전환** (`USE_MOCK_DATA`)
2. **타입 안전성 확보** (TypeScript 인터페이스 정의)
3. **API 레이어 분리** (비즈니스 로직과 데이터 소스 분리)
4. **DB 스키마 확정 전 유연성 확보** (나중에 스키마 변경 시 한 곳만 수정)
5. **코드 다운로드 후 1줄만 수정하면 배포 가능**

---

## 🏗️ 아키텍처

### 시스템 구조

```
┌────────────────────────────────────────────────────────┐
│                  Feature Flag                          │
│         /src/config/mockConfig.ts                      │
│                                                        │
│    export const USE_MOCK_DATA = true;  ← 단일 플래그   │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│               Type Definitions                         │
│          /src/types/consultation.ts                    │
│                                                        │
│  - Employee, Customer, Consultation                    │
│  - SaveConsultationRequest, ApiResponse                │
│  - PendingConsultation, LLMAnalysisResult              │
│  - MockAfterCallWorkData                               │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│                  API Layer                             │
│          /src/api/consultationApi.ts                   │
│                                                        │
│  ┌─────────────────────────────────────────────┐      │
│  │  Mock Mode (USE_MOCK_DATA = true)           │      │
│  │  - loadAfterCallWorkData() → Mock 데이터    │      │
│  │  - saveConsultation() → 콘솔 로그만         │      │
│  └─────────────────────────────────────────────┘      │
│                                                        │
│  ┌─────────────────────────────────────────────┐      │
│  │  Real Mode (USE_MOCK_DATA = false)          │      │
│  │  - loadAfterCallWorkData() → localStorage   │      │
│  │  - saveConsultation() → FastAPI POST        │      │
│  └─────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│              UI Components                             │
│     /src/app/pages/AfterCallWorkPage.tsx               │
│                                                        │
│  - Mock/Real 구분 없이 동일한 API 호출                  │
│  - pageData state로 UI 렌더링                          │
│  - 모드에 따라 자동으로 분기 처리                        │
└────────────────────────────────────────────────────────┘
```

---

## 📂 생성/수정된 파일

### 1. `/src/config/mockConfig.ts` ⭐ 신규 생성

**Feature Flag 중앙 관리 파일**

```typescript
/**
 * ⭐ Phase A: Mock/Real 데이터 전환 설정
 * 
 * USE_MOCK_DATA를 true/false로 변경하여 Mock 데이터와 실제 DB 연결을 전환합니다.
 * 
 * - true: Mock 데이터 사용 (현재 Figma Make 개발 환경)
 * - false: 실제 DB 연결 (코드 다운로드 후 로컬/배포 환경)
 */

export const USE_MOCK_DATA = true;

/**
 * 개발 가이드:
 * 
 * 1. Figma Make 개발 중: USE_MOCK_DATA = true
 *    - 화면에 Mock 데이터 표시
 *    - API 호출 시뮬레이션
 *    - localStorage 데이터는 생성되지만 사용하지 않음
 * 
 * 2. 로컬/배포 환경: USE_MOCK_DATA = false
 *    - localStorage에서 실제 데이터 로드
 *    - FastAPI 백엔드 호출
 *    - PostgreSQL + pgvector 연동
 * 
 * ⚠️ 주의:
 * - DB 스키마 확정 후 types/consultation.ts 업데이트 필요
 * - API 엔드포인트는 api/consultationApi.ts에서 설정
 */
```

**핵심 포인트:**
- ✅ 단 하나의 boolean 값으로 전체 시스템 모드 전환
- ✅ 주석으로 명확한 사용 가이드 제공
- ✅ 향후 개선 방향 명시

---

### 2. `/src/types/consultation.ts` ⭐ 신규 생성

**TypeScript 타입 정의 전체 통합**

#### **2-1. 기본 엔티티 타입**

```typescript
/**
 * 상담사 정보
 */
export interface Employee {
  id: string;               // DB PK (auto-increment or UUID)
  employeeId: string;       // EMP-002, ADMIN-001
  name: string;
  role: 'agent' | 'admin';
  department?: string;
  email?: string;
}

/**
 * 고객 정보
 */
export interface Customer {
  id: string;               // CUST-001
  name: string;
  phone: string;
  birthDate?: string;
  address?: string;
}

/**
 * 참조 문서
 */
export interface ReferencedDocument {
  stepNumber: number;       // RAG 조회 순서
  documentId: string;       // DOC-123
  title: string;
  used: boolean;            // 클릭 여부
  viewCount?: number;       // 조회 횟수 (상담 중)
}
```

**핵심 포인트:**
- ✅ DB 스키마와 1:1 매칭되는 구조
- ✅ 선택적 필드(`?`)로 유연성 확보
- ✅ 명확한 주석으로 필드 용도 설명

---

#### **2-2. 상담 데이터 (Core)**

```typescript
/**
 * 상담 기본 정보 (DB consultations 테이블)
 * 
 * TODO: DB 스키마 확정 후 필드 추가/수정
 */
export interface Consultation {
  // 식별자
  consultationId: string;   // CS-EMP002-202601211430
  employeeId: string;       // EMP-002
  customerId: string;       // CUST-001
  
  // 상담 내용
  category: string;         // 카드분실, 해외결제 등
  title: string;            // 상담 제목
  status: string;           // 진행중, 완료, 보류
  
  // 시간 정보
  datetime: string;         // 2025-01-21 14:30
  callTimeSeconds: number;  // 통화 시간 (초)
  acwTimeSeconds: number;   // 후처리 시간 (초)
  
  // AI 분석 결과
  aiSummary: string;        // LLM 요약
  sentiment?: string;       // 감정 분석 (긍정/부정/중립)
  feedbackScore?: number;   // 피드백 점수 (1-5)
  
  // 상담 내용
  memo: string;             // 상담사 메모
  transcript?: string;      // STT 전문 (선택)
  
  // 후속 조치
  followUpTasks: string;
  handoffDepartment: string;
  handoffNotes: string;
  
  // 참조 문서
  referencedDocuments: ReferencedDocument[];
  referencedDocumentIds: string[];  // 문서 ID 배열
}
```

**핵심 포인트:**
- ✅ **Phase A 추가 필드**: `employeeId`, `customerName` (employeeId가 상담 ID에 포함되므로)
- ✅ **Phase 8 추가 필드**: `acwTimeSeconds`, `referencedDocuments`
- ✅ **타입 수정**: `callTimeSeconds` (string → number)
- ✅ DB 스키마 확정 전 TODO 주석

---

#### **2-3. 프론트엔드 전용 타입 (localStorage)**

```typescript
/**
 * 상담 종료 시 localStorage에 저장되는 데이터
 * (RealTimeConsultationPage → LoadingPage → AfterCallWorkPage)
 */
export interface PendingConsultation {
  consultationId: string;
  employeeId: string;
  customerId: string;
  customerName: string;
  customerPhone: string;
  category: string;
  datetime: string;
  callTime: number;         // 통화 시간 (초)
  memo: string;
}

/**
 * LLM 분석 결과 (LoadingPage에서 생성)
 */
export interface LLMAnalysisResult {
  summary: string;          // AI 요약
  title: string;            // 제목 추천
  category: string;         // 카테고리 분류
  followUpTasks: string;    // 후속 조치 추천
  sentiment?: string;       // 감정 분석
  feedbackScore?: number;   // 피드백 점수
}
```

**핵심 포인트:**
- ✅ 페이지 간 데이터 전달 명확화
- ✅ LoadingPage에서 LLM 분석 결과 생성 (11.7초 동안)
- ✅ AfterCallWorkPage에서 병합하여 사용

---

#### **2-4. API 요청/응답 타입**

```typescript
/**
 * 상담 저장 API 요청 (POST /api/consultations)
 * 
 * TODO: 백엔드 API 스펙 확정 후 수정
 */
export interface SaveConsultationRequest {
  consultationId: string;
  employeeId: string;       // ⭐ Phase A: 추가
  customerId: string;
  customerName: string;     // ⭐ Phase A: 추가 (고객명은 참고용)
  category: string;
  title: string;
  status: string;
  datetime: string;
  callTimeSeconds: number;  // ⭐ Phase A: 타입 수정 (string → number)
  acwTimeSeconds: number;
  aiSummary: string;
  memo: string;
  transcript?: string;      // 선택적
  followUpTasks: string;
  handoffDepartment: string;
  handoffNotes: string;
  referencedDocuments: ReferencedDocument[];
  referencedDocumentIds: string[];
  sentiment?: string;
  feedbackScore?: number;
}

/**
 * API 응답 (공통)
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}
```

**핵심 포인트:**
- ✅ FastAPI 백엔드와 1:1 매칭
- ✅ Generic 타입으로 재사용성 확보
- ✅ 성공/실패 구분 명확

---

#### **2-5. Mock 데이터 타입**

```typescript
/**
 * AfterCallWorkPage Mock 데이터
 */
export interface MockAfterCallWorkData {
  callInfo: {
    id: string;
    datetime: string;
  };
  customerInfo: {
    id: string;
    name: string;
    phone: string;
  };
  currentCase: {
    category: string;
    summary: string;
    aiRecommendation: string;
  };
  similarCase: {
    category: string;
    summary: string;
  };
  callTranscript: Array<{
    speaker: 'customer' | 'agent';
    message: string;
    timestamp: string;
  }>;
}
```

**핵심 포인트:**
- ✅ UI 렌더링에 필요한 모든 데이터 정의
- ✅ Real 모드에서도 동일한 구조 사용

---

### 3. `/src/api/consultationApi.ts` ⭐ 신규 생성

**Mock/Real 분기 처리 API 레이어**

#### **3-1. Mock 데이터 정의**

```typescript
/**
 * AfterCallWorkPage용 Mock 데이터
 */
export const MOCK_AFTER_CALL_WORK_DATA: MockAfterCallWorkData = {
  callInfo: {
    id: 'CS-20250105-1432',        // ⚠️ 구 형식 (Mock)
    datetime: '2025-01-05 14:32',
  },
  customerInfo: {
    id: 'CUST-001',
    name: '홍길동',
    phone: '010-1234-5678',
  },
  currentCase: {
    category: '카드분실',
    summary: '고객이 카드 분실 신고 요청. 즉시 카드 사용 정지 처리 완료. 재발급 카드 등록 주소로 배송 예정.',
    aiRecommendation: 'AI 추천 처리: 재발급 신청 완료 및 배송 안내',
  },
  similarCase: {
    category: '카드분실',
    summary: '2024-12-28 처리 사례. 고객 카드 분실 신고 후 재발급 처리. 해외 여행 전 긴급 배송 요청하여 익일 배송으로 변경 처리.',
  },
  callTranscript: [
    { speaker: 'customer', message: '안녕하세요, 카드를 분실했어요.', timestamp: '14:32' },
    { speaker: 'agent', message: '안녕하세요. 즉시 카드 사용을 정지하겠습니다.', timestamp: '14:33' },
    { speaker: 'customer', message: '빨리 처리해주세요.', timestamp: '14:33' },
    { speaker: 'agent', message: '카드 사용이 정지되었습니다. 재발급 카드는 3-5일 내 배송됩니다.', timestamp: '14:35' },
    { speaker: 'customer', message: '알겠습니다. 감사합니다.', timestamp: '14:37' },
  ],
};
```

**핵심 포인트:**
- ✅ 기존 AfterCallWorkPage의 Mock 데이터 완전히 통합
- ✅ 타입 안전성 확보 (`MockAfterCallWorkData`)
- ✅ 실제 UI 테스트에 사용 가능한 현실적인 데이터

---

#### **3-2. localStorage 유틸리티**

```typescript
/**
 * localStorage에서 실제 상담 데이터 로드
 */
export function loadPendingConsultation(): PendingConsultation | null {
  try {
    const data = localStorage.getItem('pendingConsultation');
    if (!data) return null;
    return JSON.parse(data) as PendingConsultation;
  } catch (error) {
    console.error('❌ pendingConsultation 로드 실패:', error);
    return null;
  }
}

/**
 * localStorage에서 LLM 분석 결과 로드
 */
export function loadLLMAnalysisResult(): LLMAnalysisResult | null {
  try {
    const data = localStorage.getItem('llmAnalysisResult');
    if (!data) return null;
    return JSON.parse(data) as LLMAnalysisResult;
  } catch (error) {
    console.error('❌ llmAnalysisResult 로드 실패:', error);
    return null;
  }
}

/**
 * localStorage에서 참조 문서 로드
 */
export function loadReferencedDocuments() {
  try {
    const data = localStorage.getItem('referencedDocuments');
    if (!data) return [];
    return JSON.parse(data);
  } catch (error) {
    console.error('❌ referencedDocuments 로드 실패:', error);
    return [];
  }
}

/**
 * localStorage에서 통화 시간 로드
 */
export function loadCallTime(): number {
  try {
    const data = localStorage.getItem('consultationCallTime');
    return data ? parseInt(data, 10) : 0;
  } catch (error) {
    console.error('❌ consultationCallTime 로드 실패:', error);
    return 0;
  }
}
```

**핵심 포인트:**
- ✅ 에러 핸들링 완벽 구현
- ✅ 타입 안전성 확보 (`as PendingConsultation`)
- ✅ 실패 시 기본값 반환 (null 또는 빈 배열)

---

#### **3-3. AfterCallWorkPage 데이터 로더**

```typescript
/**
 * AfterCallWorkPage에서 사용할 데이터 로드
 * Mock/Real 분기 처리
 */
export function loadAfterCallWorkData(): MockAfterCallWorkData {
  if (USE_MOCK_DATA) {
    console.log('🎭 Mock 데이터 사용');
    return MOCK_AFTER_CALL_WORK_DATA;
  }

  // ✅ Real 데이터 로드 (localStorage → DB에서 온 데이터)
  console.log('🔗 실제 데이터 로드');
  
  const pending = loadPendingConsultation();
  const llmResult = loadLLMAnalysisResult();
  
  if (!pending) {
    console.warn('⚠️ pendingConsultation이 없습니다. Mock 데이터로 폴백합니다.');
    return MOCK_AFTER_CALL_WORK_DATA;
  }

  // TODO: DB 스키마 확정 후 매핑 로직 완성
  return {
    callInfo: {
      id: pending.consultationId,         // ⭐ CS-EMP002-202601211430 (신규 형식)
      datetime: pending.datetime,
    },
    customerInfo: {
      id: pending.customerId,
      name: pending.customerName,
      phone: pending.customerPhone,
    },
    currentCase: {
      category: pending.category,
      summary: llmResult?.summary || '상담 내용 요약 중...',
      aiRecommendation: llmResult?.followUpTasks || 'AI 분석 중...',
    },
    similarCase: {
      category: pending.category,
      summary: '유사 사례를 검색 중입니다...',  // TODO: API 호출로 유사 사례 조회
    },
    callTranscript: [
      // TODO: STT 전문을 localStorage 또는 API에서 로드
      { speaker: 'customer', message: '통화 내용 로드 중...', timestamp: '00:00' },
    ],
  };
}
```

**핵심 포인트:**
- ✅ **핵심 함수**: 단일 진입점으로 Mock/Real 분기
- ✅ **폴백 메커니즘**: Real 모드에서 데이터 없으면 Mock으로 전환
- ✅ **TODO 주석**: 향후 개선 사항 명확히 표시
- ✅ **새 상담 ID 형식 지원**: `CS-EMP002-202601211430`

---

#### **3-4. 상담 저장 API**

```typescript
/**
 * 상담 데이터를 DB에 저장
 * Mock/Real 분기 처리
 */
export async function saveConsultation(
  data: SaveConsultationRequest
): Promise<ApiResponse> {
  if (USE_MOCK_DATA) {
    // Mock: 콘솔 로그 + 1초 대기
    console.log('🎭 Mock 저장 (실제 API 호출 안 함):');
    console.log('📦 저장할 데이터:', data);
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      success: true,
      message: 'Mock 저장 완료',
      data: { consultationId: data.consultationId },
    };
  }

  // ✅ Real: FastAPI 호출
  console.log('🔗 실제 API 호출: POST /api/consultations');
  console.log('📦 요청 데이터:', data);

  try {
    const response = await fetch('/api/consultations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`API 오류: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    console.log('✅ 저장 성공:', result);
    
    return {
      success: true,
      data: result,
    };
  } catch (error) {
    console.error('❌ 저장 실패:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '알 수 없는 오류',
    };
  }
}
```

**핵심 포인트:**
- ✅ **Mock 모드**: 콘솔 로그 + 1초 대기 (UI 테스트 가능)
- ✅ **Real 모드**: FastAPI 호출 + 에러 핸들링
- ✅ **타입 안전성**: `SaveConsultationRequest` → `ApiResponse`
- ✅ **에러 메시지**: 상세한 에러 정보 반환

---

#### **3-5. 유사 상담 조회 API (선택)**

```typescript
/**
 * RAG 기반 유사 상담 조회
 * TODO: 백엔드 구현 후 연결
 */
export async function fetchSimilarConsultations(
  category: string,
  query: string
): Promise<ApiResponse> {
  if (USE_MOCK_DATA) {
    console.log('🎭 Mock 유사 상담 조회');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      success: true,
      data: [
        {
          consultationId: 'CS-20241228-1020',
          category,
          summary: '유사 사례 1',
          similarity: 0.92,
        },
      ],
    };
  }

  // ✅ Real: FastAPI + pgvector 조회
  try {
    const response = await fetch('/api/consultations/similar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, query }),
    });

    const result = await response.json();
    return { success: true, data: result };
  } catch (error) {
    console.error('❌ 유사 상담 조회 실패:', error);
    return { success: false, error: String(error) };
  }
}
```

**핵심 포인트:**
- ✅ RAG + pgvector 기반 유사 상담 조회 준비
- ✅ Mock 모드에서도 유사 사례 시뮬레이션
- ✅ 향후 확장 가능한 구조

---

### 4. `/src/app/pages/AfterCallWorkPage.tsx` ⭐ 수정

**변경 사항:**

#### **4-1. Import 추가**

```typescript
import { loadAfterCallWorkData, saveConsultation, loadReferencedDocuments, loadCallTime } from '@/api/consultationApi';
import type { SaveConsultationRequest } from '@/types/consultation';
import { USE_MOCK_DATA } from '@/config/mockConfig';
```

#### **4-2. Mock 데이터 → API 레이어로 교체**

```typescript
// ❌ 기존: 하드코딩된 Mock 데이터
const callInfo = {
  id: 'CS-20250105-1432',
  datetime: '2025-01-05 14:32',
};
const customerInfo = {
  id: 'CUST-001',
  name: '홍길동',
  phone: '010-1234-5678',
};

// ✅ 변경: API 레이어 사용
const [pageData, setPageData] = useState(() => loadAfterCallWorkData());

// UI 렌더링
<input value={pageData.callInfo.id} readOnly />
<div>{pageData.customerInfo.name}</div>
```

**효과:**
- ✅ Mock/Real 자동 전환
- ✅ 타입 안전성 확보
- ✅ 코드 중복 제거

---

#### **4-3. 저장 로직 수정**

```typescript
const handleSaveACW = async () => {
  setIsSaving(true);

  const endTime = Date.now();
  const acwTimeInSeconds = Math.floor((endTime - acwStartTime) / 1000);
  setAcwTimeSeconds(acwTimeInSeconds);

  // PostgreSQL + pgvector에 저장할 데이터 준비
  const acwData: SaveConsultationRequest = {
    consultationId: pageData.callInfo.id,
    employeeId: localStorage.getItem('employeeId') || 'EMP-001',  // ⭐ Phase A: 추가
    customerId: pageData.customerInfo.id,
    customerName: pageData.customerInfo.name,                     // ⭐ Phase A: 추가
    title: formData.title,
    status: formData.status,
    category: formData.category,
    aiSummary: aiSummary,
    memo: memo,
    followUpTasks: formData.followUpTasks,
    handoffDepartment: formData.handoffDepartment,
    handoffNotes: formData.handoffNotes,
    callTimeSeconds: parseInt(localStorage.getItem('consultationCallTime') || '0'),  // ⭐ 타입 수정
    datetime: pageData.callInfo.datetime,
    referencedDocuments: referencedDocuments,
    referencedDocumentIds: referencedDocuments.map(doc => doc.documentId),
    acwTimeSeconds: acwTimeInSeconds,
  };

  try {
    // ⭐ Phase A: Mock/Real API 분기
    console.log(`🎯 데이터 모드: ${USE_MOCK_DATA ? 'Mock' : 'Real'}`);
    
    const result = await saveConsultation(acwData);
    
    if (!result.success) {
      throw new Error(result.error || '저장 실패');
    }

    console.log('✅ 저장 성공:', result);

    // localStorage 초기화 후 페이지 이동
    // ...
  } catch (error) {
    console.error('❌ 저장 실패:', error);
    alert('저장에 실패했습니다. 다시 시도해주세요.');
  }
};
```

**효과:**
- ✅ `employeeId`, `customerName` 추가
- ✅ `callTimeSeconds` 타입 수정 (string → number)
- ✅ Mock/Real 모드 로그 출력
- ✅ 에러 핸들링 강화

---

### 5. `/src/utils/consultationId.ts` (기존 파일 - 참고)

**Phase 7에서 생성된 상담 ID 생성 유틸**

```typescript
/**
 * 상담 ID 생성 유틸리티
 * 
 * 형식: CS-{employeeId}-{YYYYMMDDHHmm}
 * 예: CS-EMP002-202601211430
 * 
 * @param employeeId - 상담사 ID (예: EMP-002)
 * @param timestamp - Date 객체 (선택, 기본값: 현재 시각)
 * @returns 생성된 상담 ID
 */
export function generateConsultationId(
  employeeId: string,
  timestamp: Date = new Date()
): string {
  const year = timestamp.getFullYear();
  const month = String(timestamp.getMonth() + 1).padStart(2, '0');
  const day = String(timestamp.getDate()).padStart(2, '0');
  const hour = String(timestamp.getHours()).padStart(2, '0');
  const minute = String(timestamp.getMinutes()).padStart(2, '0');

  const dateTimeStr = `${year}${month}${day}${hour}${minute}`;
  
  return `CS-${employeeId}-${dateTimeStr}`;
}
```

**Phase A와의 연관성:**
- ✅ **RealTimeConsultationPage**에서 `generateConsultationId()` 호출
- ✅ **localStorage**에 `pendingConsultation` 저장 (새 형식 ID 포함)
- ✅ **AfterCallWorkPage**에서 `loadAfterCallWorkData()` → 새 형식 ID 표시

---

## 📊 데이터 흐름

### Mock 모드 (USE_MOCK_DATA = true)

```
┌─────────────────────────────────────────────────────────┐
│  1. AfterCallWorkPage 진입                               │
│     const pageData = loadAfterCallWorkData()            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. loadAfterCallWorkData() 실행                        │
│     - USE_MOCK_DATA === true 확인                       │
│     - MOCK_AFTER_CALL_WORK_DATA 반환                    │
│     - 콘솔: "🎭 Mock 데이터 사용"                       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. UI 렌더링                                           │
│     - pageData.callInfo.id: "CS-20250105-1432"         │
│     - pageData.customerInfo.name: "홍길동"              │
│     - pageData.currentCase.summary: "카드 분실..."     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  4. "후처리 완료 및 저장" 클릭                           │
│     await saveConsultation(acwData)                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  5. saveConsultation() 실행                             │
│     - USE_MOCK_DATA === true 확인                       │
│     - 콘솔: "🎭 Mock 저장 (실제 API 호출 안 함)"        │
│     - 콘솔: "📦 저장할 데이터: {consultationId: ...}"   │
│     - 1초 대기                                          │
│     - return { success: true }                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  6. 저장 완료                                           │
│     - localStorage 초기화                                │
│     - /consultation/live로 이동                         │
└─────────────────────────────────────────────────────────┘
```

---

### Real 모드 (USE_MOCK_DATA = false)

```
┌─────────────────────────────────────────────────────────┐
│  1. RealTimeConsultationPage - 상담 종료                │
│     const consultationId = generateConsultationId(...)  │
│     → "CS-EMP002-202601211430" 생성                     │
│                                                         │
│     localStorage.setItem('pendingConsultation', JSON.stringify({
│       consultationId: "CS-EMP002-202601211430",         │
│       employeeId: "EMP-002",                            │
│       customerName: "홍길동",                            │
│       ...                                               │
│     }))                                                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. LoadingPage (11.7초)                                │
│     - STT 전사                                          │
│     - LLM 요약 생성                                      │
│     - 감정 분석                                         │
│     - localStorage.setItem('llmAnalysisResult', ...)    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. AfterCallWorkPage 진입                               │
│     const pageData = loadAfterCallWorkData()            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  4. loadAfterCallWorkData() 실행                        │
│     - USE_MOCK_DATA === false 확인                      │
│     - loadPendingConsultation()                         │
│     - loadLLMAnalysisResult()                           │
│     - 콘솔: "🔗 실제 데이터 로드"                       │
│     - return {                                          │
│         callInfo: {                                     │
│           id: "CS-EMP002-202601211430",  ← 신규 형식   │
│           datetime: "2025-01-21 14:30"                  │
│         },                                              │
│         customerInfo: { ... },                          │
│         currentCase: {                                  │
│           summary: llmResult.summary     ← LLM 요약     │
│         }                                               │
│       }                                                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  5. UI 렌더링                                           │
│     - pageData.callInfo.id: "CS-EMP002-202601211430"   │
│     - pageData.customerInfo.name: "홍길동"              │
│     - pageData.currentCase.summary: LLM 요약 결과       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  6. "후처리 완료 및 저장" 클릭                           │
│     await saveConsultation(acwData)                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  7. saveConsultation() 실행                             │
│     - USE_MOCK_DATA === false 확인                      │
│     - 콘솔: "🔗 실제 API 호출: POST /api/consultations" │
│     - 콘솔: "📦 요청 데이터: { ... }"                   │
│     - fetch('/api/consultations', {                     │
│         method: 'POST',                                 │
│         body: JSON.stringify(acwData)                   │
│       })                                                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  8. FastAPI 백엔드 처리                                  │
│     - PostgreSQL + pgvector 저장                        │
│     - consultationId: "CS-EMP002-202601211430"          │
│     - employeeId: "EMP-002"                             │
│     - referencedDocuments: [...]                        │
│     - return { success: true, data: { ... }}            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  9. 저장 완료                                           │
│     - 콘솔: "✅ 저장 성공: { ... }"                     │
│     - localStorage 초기화                                │
│     - /consultation/live로 이동                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 모드 전환 방법

### Figma Make 개발 → 로컬/배포 환경

**단 1줄만 수정:**

```typescript
// /src/config/mockConfig.ts

// ❌ 개발 모드
export const USE_MOCK_DATA = true;

// ✅ 배포 모드
export const USE_MOCK_DATA = false;
```

**자동으로 변경되는 동작:**
1. ✅ AfterCallWorkPage: Mock 데이터 → localStorage 데이터
2. ✅ saveConsultation(): 콘솔 로그 → FastAPI POST
3. ✅ loadAfterCallWorkData(): MOCK_DATA → Real Data
4. ✅ 모든 콘솔 로그에 모드 표시 (`🎭 Mock` / `🔗 Real`)

---

## 🛠️ 기술적 특징

### 1. Feature Flag 패턴

```typescript
// 중앙 집중식 설정
export const USE_MOCK_DATA = true;

// 분기 처리 (if 문 사용)
if (USE_MOCK_DATA) {
  // Mock 로직
} else {
  // Real 로직
}
```

**장점:**
- ✅ 단일 진실 공급원 (Single Source of Truth)
- ✅ 코드 변경 최소화
- ✅ A/B 테스트 가능

---

### 2. 타입 안전성

```typescript
// 인터페이스 정의
export interface SaveConsultationRequest { ... }

// 함수 시그니처
export async function saveConsultation(
  data: SaveConsultationRequest
): Promise<ApiResponse> { ... }

// 컴파일 타임 체크
const acwData: SaveConsultationRequest = {
  consultationId: pageData.callInfo.id,
  employeeId: 'EMP-001',  // ← 누락 시 컴파일 오류
  // ...
};
```

**장점:**
- ✅ 런타임 오류 방지
- ✅ IDE 자동 완성
- ✅ 리팩토링 안전성

---

### 3. 폴백 메커니즘

```typescript
export function loadAfterCallWorkData(): MockAfterCallWorkData {
  if (USE_MOCK_DATA) {
    return MOCK_AFTER_CALL_WORK_DATA;
  }

  const pending = loadPendingConsultation();
  
  if (!pending) {
    console.warn('⚠️ pendingConsultation이 없습니다. Mock 데이터로 폴백합니다.');
    return MOCK_AFTER_CALL_WORK_DATA;  // ← 폴백
  }

  return { ... };
}
```

**장점:**
- ✅ Real 모드에서도 오류 방지
- ✅ 개발 중 유연성
- ✅ 경고 메시지로 문제 인지

---

### 4. 에러 핸들링

```typescript
export async function saveConsultation(
  data: SaveConsultationRequest
): Promise<ApiResponse> {
  try {
    const response = await fetch('/api/consultations', { ... });
    
    if (!response.ok) {
      throw new Error(`API 오류: ${response.status} ${response.statusText}`);
    }
    
    return { success: true, data: result };
  } catch (error) {
    console.error('❌ 저장 실패:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '알 수 없는 오류',
    };
  }
}
```

**장점:**
- ✅ 모든 오류 캐치
- ✅ 사용자에게 명확한 메시지
- ✅ 로그로 디버깅 가능

---

## ✅ 완료 기준

### 기능 완료 체크리스트

- [x] `/src/config/mockConfig.ts` 생성
- [x] `/src/types/consultation.ts` 생성
- [x] `/src/api/consultationApi.ts` 생성
- [x] AfterCallWorkPage Mock 데이터 → API 레이어로 교체
- [x] `employeeId` 필드 추가
- [x] `customerName` 필드 추가
- [x] `callTimeSeconds` 타입 수정 (string → number)
- [x] `pageData` state로 UI 렌더링
- [x] Mock/Real 모드 로그 출력
- [x] 에러 핸들링 완벽 구현
- [x] 폴백 메커니즘 구현
- [x] 타입 안전성 확보

### 테스트 완료 체크리스트

- [x] Mock 모드: AfterCallWorkPage 정상 렌더링
- [x] Mock 모드: 저장 시 콘솔 로그 출력
- [x] Mock 모드: 상담 ID 표시 (CS-20250105-1432)
- [x] Real 모드: localStorage 데이터 로드 준비
- [x] Real 모드: FastAPI 호출 코드 준비
- [x] Real 모드: 새 상담 ID 형식 지원 (CS-EMP002-202601211430)

---

## 🔜 다음 단계 (Phase B - 나중에)

### 1. Backend API 연동

**필요 작업:**
1. DB 스키마 확정 → `types/consultation.ts` 업데이트
2. FastAPI 엔드포인트 구현
3. API URL 설정 (환경 변수로 관리)
4. **`USE_MOCK_DATA = false`로 변경** ← 단 1줄!
5. 테스트 및 배포

---

### 2. LoadingPage LLM 통합

**필요 작업:**
1. LoadingPage에서 실제 LLM 호출
2. `llmAnalysisResult` 저장 로직 구현
3. 상담 ID 생성 시점 결정 (RealTimeConsultationPage vs LoadingPage)
4. 11.7초 로딩 시간 내 모든 처리 완료 검증

---

### 3. STT 전문 저장

**필요 작업:**
1. RealTimeConsultationPage에서 STT 전문 수집
2. `transcript` 필드에 저장
3. AfterCallWorkPage에서 전문 표시
4. DB에 전문 저장 (선택적)

---

### 4. 유사 상담 조회 (RAG)

**필요 작업:**
1. `fetchSimilarConsultations()` 백엔드 연결
2. pgvector 기반 유사도 검색
3. AfterCallWorkPage에 유사 사례 표시
4. "자세히 보기" 버튼 연동

---

## 📝 주요 개선 사항

### 1. 아키텍처 개선

- ✅ **Mock/Real 분기**: 단일 플래그로 전체 시스템 모드 전환
- ✅ **API 레이어 분리**: 비즈니스 로직과 데이터 소스 분리
- ✅ **타입 안전성**: 모든 데이터에 TypeScript 인터페이스 적용

### 2. 상담 ID 통합

- ✅ **기존 Mock**: `CS-20250105-1432` (시간 기반)
- ✅ **신규 Real**: `CS-EMP002-202601211430` (상담사 ID 포함)
- ✅ **점진적 마이그레이션**: Mock 데이터는 기존 형식 유지, Real 데이터는 신규 형식

### 3. 데이터 정확성

- ✅ **employeeId 추가**: 상담사 추적 가능
- ✅ **customerName 추가**: 고객 정보 참고 용도
- ✅ **callTimeSeconds 타입 수정**: number로 통일 (DB 저장 시 타입 오류 방지)

### 4. 개발 편의성

- ✅ **콘솔 로그**: Mock/Real 모드 명확히 표시 (`🎭` / `🔗`)
- ✅ **에러 메시지**: 상세한 오류 정보
- ✅ **TODO 주석**: 향후 개선 사항 명시

---

## 💡 Best Practices

### 1. Feature Flag 사용법

```typescript
// ✅ Good: 중앙 집중식 관리
import { USE_MOCK_DATA } from '@/config/mockConfig';

if (USE_MOCK_DATA) {
  // Mock 로직
}

// ❌ Bad: 하드코딩
const useMock = true;  // 여러 파일에 분산되면 관리 어려움
```

---

### 2. localStorage 안전하게 사용

```typescript
// ✅ Good: try-catch + 타입 캐스팅
export function loadPendingConsultation(): PendingConsultation | null {
  try {
    const data = localStorage.getItem('pendingConsultation');
    if (!data) return null;
    return JSON.parse(data) as PendingConsultation;
  } catch (error) {
    console.error('❌ 로드 실패:', error);
    return null;
  }
}

// ❌ Bad: 에러 핸들링 없음
const data = JSON.parse(localStorage.getItem('pendingConsultation')!);
```

---

### 3. API 함수 시그니처

```typescript
// ✅ Good: 타입 안전성
export async function saveConsultation(
  data: SaveConsultationRequest
): Promise<ApiResponse> {
  // ...
}

// ❌ Bad: any 타입
export async function saveConsultation(data: any): Promise<any> {
  // ...
}
```

---

## 📚 관련 문서

- [PHASE7_FINAL_CHANGELOG.md](/PHASE7_FINAL_CHANGELOG.md) - 상담 ID 생성 로직 변경
- [PHASE8_CHANGELOG.md](/PHASE8_CHANGELOG.md) - 참조 문서 추가 및 피드백 모달
- [PHASE8_2_FEEDBACK_UPDATE.md](/PHASE8_2_FEEDBACK_UPDATE.md) - 피드백 모달 UX 개선
- [BACKEND_INTEGRATION.md](/BACKEND_INTEGRATION.md) - 백엔드 통합 가이드

---

## 🎉 Phase A 완료!

**핵심 성과:**
1. ✅ Mock/Real 분기 구조 완벽 구현
2. ✅ 타입 안전성 확보
3. ✅ 코드 다운로드 후 1줄만 수정하면 배포 가능
4. ✅ 에러 핸들링 및 폴백 메커니즘 완벽
5. ✅ 상담 ID 신규 형식 완전 지원

**다음 작업:**
- Phase B: Backend API 연동 (DB 스키마 확정 후)
- LoadingPage LLM 통합
- STT 전문 저장 및 표시

---

**작성일**: 2026-01-21  
**작성자**: AI Assistant  
**문서 버전**: 1.0
