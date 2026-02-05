# CALL:ACT RAG API 응답 스키마 (Phase 2 업데이트)

## 📌 개요

CALL:ACT 시스템은 RAG(Retrieval-Augmented Generation) 기반으로 실시간 상담 시나리오 카드를 생성합니다.  
**Phase 2**에서 `documentType` 필드가 추가되어 문서 타입별 렌더링이 가능해졌습니다.

---

## 📋 ScenarioCard 인터페이스

### TypeScript 타입 정의

```typescript
export type DocumentType = 'terms' | 'product-spec' | 'analysis-report' | 'guide' | 'general';

export interface ScenarioCard {
  id: string;                      // 카드 고유 ID (예: "card-6-1-1")
  title: string;                   // 카드 제목
  keywords: string[];              // 태그 배열 (예: ["보유카드", "포인트형", "혜택"])
  content: string;                 // 카드 간단 설명 (description)
  systemPath: string;              // 시스템 경로 (예: "카드관리 > 혜택조회 > 보유카드")
  requiredChecks: string[];        // 필수 확인 사항
  exceptions: string[];            // 예외 사항
  time: string;                    // 소요 시간
  note: string;                    // 메모
  regulation: string;              // 관련 규정/법령
  fullText: string;                // 전체 문서 내용 (자세히 보기 시 표시)
  
  // 하이브리드 카드 속성
  type?: 'text' | 'product-info'; // UI 렌더링 방식 (기본: 'text')
  attributes?: Array<{             // product-info 타입일 때만 사용
    label: string;
    value: string;
    highlight?: boolean;           // 강조 표시 여부
  }>;
  
  // ⭐ Phase 2: 문서 타입 추가
  documentType?: DocumentType;     // 문서 타입 (선택 필드)
}
```

---

## 📂 DocumentType 정의

### 1. `terms` - 법적 약관, 규정 전문
**용도**: 카드 이용약관, 법령 조항 등  
**특징**: 조항 번호, 법적 문구, 상세한 조건  
**예시**:
```
제34조 (카드의 분실신고 및 재발급)

① 회원은 카드를 분실한 경우 즉시 회사에 신고하여야 하며...
② 회사는 회원의 분실신고 접수 시점 이후 발생한 제3자의 부정사용...
```

---

### 2. `product-spec` - 상품 사양서, 카드 정보, 혜택 명세
**용도**: 카드 상품설명서, 혜택 정보  
**특징**: 연회비, 적립률, 혜택 항목 등 구조화된 상품 정보  
**예시**:
```
【테디 포인트 플러스 카드 상품설명서】

제1조 (카드 개요)
본 카드는 다양한 가맹점에서 포인트를 적립하여 현금처럼 사용할 수 있는...

제2조 (연회비)
본 카드의 연회비는 10,000원입니다.
- 전년도 이용실적 50만원 이상 시 연회비 면제

제3조 (포인트 적립)
1. 기본 적립률: 이용금액의 1.0% (1,000원당 10포인트)
2. 특별 적립:
   - 온라인 쇼핑몰: 3.0% 적립
   - 카페/베이커리: 3.0% 적립
```

**주의**: `product-spec`은 주로 `type: "product-info"`와 함께 사용되며, `attributes` 그리드가 표시됩니다.

---

### 3. `analysis-report` - 비교 분석, 시뮬레이션 결과, 데이터 리포트
**용도**: 고객 소비 패턴 분석, 카드 혜택 비교, 자격 조회 결과  
**특징**: 표/차트 형식, 수치 비교, AI 인사이트  
**예시**:
```
【고객 소비 패턴 분석 보고서】

■ 분석 기간: 2024년 10월 ~ 2024년 12월 (최근 3개월)
■ 분석 대상: 강민지 고객님 (CUST-TEDDY-00006)

【1. 월별 이용 현황】
- 2024년 10월: 1,250,000원 (국내 75% / 해외 25%)
- 2024년 11월: 1,480,000원 (국내 60% / 해외 40%)

【2. 카테고리별 지출 비중】
1. 여행/항공: 42% (1,911,000원) ⬆️ 전분기 대비 +40%
2. 숙박: 18% (819,000원)
```

---

### 4. `guide` - 절차 안내, 사용 가이드, FAQ
**용도**: 카드 발급 절차, 바우처 사용 방법, 조회 안내  
**특징**: Step-by-step 가이드, 실무 진행 절차, 조회 방법  
**예시**:
```
【국민행복카드 바우처 이용 안내】

【1. 바우처 사용 가능처】

✅ 산부인과·조산원
┌────────────────────────────────────┐
│ 사용 가능 항목                        │
│ - 임신 확인 및 정기 검진              │
│ - 초음파 검사 (2D, 3D, 4D)           │
│ - 기형아 검사, 양수검사               │
└────────────────────────────────────┘

【2. 바우처 잔액 조회 방법】

▶ 방법 1: 모바일 앱
1. 국민행복카드 앱 실행
2. 로그인 후 '바우처 잔액' 메뉴
3. 실시간 잔액 확인
```

---

### 5. `general` - 일반 정보, 공지사항, 참고 자료
**용도**: 간단한 참고 정보, 고지 사항, 고객센터 안내  
**특징**: 간략한 텍스트, 공지 사항  
**예시**:
```
【고객 지원】

▶ 고객센터: 1577-1234
- 평일 09:00~18:00 (공휴일 휴무)
- 바우처 문의: 2번 선택

▶ 모바일 앱 채팅 상담
- 24시간 운영 (AI 챗봇)
- 평일 09:00~18:00 (상담사 연결)
```

---

## 🔄 API 응답 예시

### 예시 1: product-spec (상품 정보 카드)

```json
{
  "id": "card-6-1-1",
  "title": "현재 보유 카드 혜택",
  "keywords": ["보유카드", "포인트형", "혜택"],
  "content": "현재 사용 중인 테디 포인트 플러스 카드의 혜택 정보입니다.",
  "systemPath": "카드관리 > 혜택조회 > 보유카드",
  "requiredChecks": ["현재 혜택", "월 평균 적립"],
  "exceptions": [],
  "time": "즉시 조회",
  "note": "월 평균 2만 포인트 적립 중",
  "regulation": "여신전문금융업법 제11조",
  "fullText": "【테디 포인트 플러스 카드 상품설명서】\n\n제1조 (카드 개요)\n본 카드는 다양한 가맹점에서...",
  "type": "product-info",
  "documentType": "product-spec",
  "attributes": [
    { "label": "카드명", "value": "테디 포인트 플러스", "highlight": true },
    { "label": "연회비", "value": "10,000원", "highlight": false },
    { "label": "기본적립", "value": "1.0%", "highlight": false },
    { "label": "특별적립", "value": "쇼핑/카페 3%", "highlight": true }
  ]
}
```

---

### 예시 2: analysis-report (분석 리포트)

```json
{
  "id": "card-6-1-2",
  "title": "고객 소비 패턴 분석",
  "keywords": ["소비패턴", "여행비중", "분석"],
  "content": "최근 3개월 소비 패턴을 분석하여 최적의 카드를 추천합니다.",
  "systemPath": "고객관리 > 분석 > 소비패턴",
  "requiredChecks": ["주요 사용처", "해외 결제 비중"],
  "exceptions": [],
  "time": "분석 완료",
  "note": "여행/항공 비중 40% 증가",
  "regulation": "신용정보법 제15조",
  "fullText": "【고객 소비 패턴 분석 보고서】\n\n■ 분석 기간: 2024년 10월 ~ 2024년 12월...",
  "documentType": "analysis-report"
}
```

**주의**: `analysis-report`는 일반적으로 `type`을 지정하지 않음 (기본 'text' 렌더링)

---

### 예시 3: guide (이용 가이드)

```json
{
  "id": "card-7-1-4",
  "title": "바우처 이용 안내",
  "keywords": ["이용안내", "사용처", "잔액조회"],
  "content": "산부인과, 약국 등 지정 요양기관에서 바우처를 사용할 수 있습니다.",
  "systemPath": "상담지원 > 바우처 > 이용안내",
  "requiredChecks": ["사용 가능처", "잔액 조회 방법"],
  "exceptions": [],
  "time": "안내 필요",
  "note": "앱에서 잔액 확인 가능",
  "regulation": "사회서비스 이용권법",
  "fullText": "【국민행복카드 바우처 이용 안내】\n\n【1. 바우처 사용 가능처】\n...",
  "documentType": "guide"
}
```

---

## 🎯 필드별 가이드

### 필수 필드
- `id`: 고유 식별자 (예: "card-6-1-1")
- `title`: 카드 제목
- `keywords`: 태그 배열 (최소 1개 이상)
- `content`: 간단 설명 (1-2문장)
- `systemPath`: 시스템 경로
- `requiredChecks`: 필수 확인 사항 배열
- `exceptions`: 예외 사항 배열 (없으면 빈 배열)
- `time`: 소요 시간
- `note`: 간단 메모
- `regulation`: 관련 규정
- `fullText`: 전체 문서 내용

### 선택 필드
- `type`: `'text'` | `'product-info'` (기본값: 'text')
- `attributes`: product-info일 때만 사용
- `documentType`: 문서 타입 (권장)

---

## ⚙️ 렌더링 로직

### 1. 카드 상단 정보 표시
```
┌─────────────────────────────┐
│ [title]                     │
│ [keywords 태그들]            │
│ [content]                   │
│ ─────────────────────────── │
│ 시스템 경로: [systemPath]    │
│ ─────────────────────────── │
│ ✓ [requiredChecks]          │
│ ⚠️ [exceptions]              │
│ ─────────────────────────── │
│ [🔵 자세히 보기] 버튼        │
└─────────────────────────────┘
```

### 2. product-info 타입 (attributes grid 표시)
```
┌─────────────────────────────┐
│ 카드명    테디 포인트 플러스  │ ← highlight
│ 연회비    10,000원           │
│ 기본적립  1.0%               │
│ 특별적립  쇼핑/카페 3%        │ ← highlight
└─────────────────────────────┘
```

### 3. "자세히 보기" 클릭 시
- `fullText` 내용을 모달로 표시
- `documentType`에 따라 향후 렌더링 방식 차별화 가능

---

## 🚨 주의사항

1. **`type`과 `documentType`은 별개**
   - `type`: UI 렌더링 방식 (attributes grid 표시 여부)
   - `documentType`: 문서의 성격 (fullText 내용 타입)

2. **product-info는 대부분 product-spec**
   - `type: "product-info"` → 일반적으로 `documentType: "product-spec"`
   - 카드 상품 정보는 attributes와 fullText 모두 필요

3. **documentType 생략 가능**
   - `documentType`이 없으면 기본 렌더링 적용
   - 기존 시나리오 1-6은 `documentType` 없이도 정상 작동

4. **fullText 포맷팅**
   - 마크다운 문법 사용 지양 (일반 텍스트 권장)
   - 구조화를 위해 박스 문자(┌─┐), 이모지(✓, ⚠️, ▶) 활용
   - 조항 번호, 섹션 제목은 【】로 강조

---

## 📊 시나리오별 documentType 매핑

### 시나리오 6 (포인트/혜택)
| 카드 ID | 제목 | documentType |
|---------|------|--------------|
| card-6-1-1 | 현재 보유 카드 혜택 | product-spec |
| card-6-1-2 | 고객 소비 패턴 분석 | analysis-report |
| card-6-1-3 | 추천 카드: 테디 트래블로그 | product-spec |
| card-6-1-4 | 혜택 비교 시뮬레이션 | analysis-report |

### 시나리오 7 (정부지원)
| 카드 ID | 제목 | documentType |
|---------|------|--------------|
| card-7-1-1 | 국민행복카드 안내 | product-spec |
| card-7-1-2 | 바우처 자격 조회 | analysis-report |
| card-7-1-3 | 카드 발급 신청 | product-spec |
| card-7-1-4 | 바우처 이용 안내 | guide |

---

## 🔮 향후 확장 가능성

현재는 `documentType`을 지정만 하고 있으며, 향후 다음과 같은 기능 추가 가능:

1. **DocumentType별 Viewer 컴포넌트**
   - `TermsViewer`: 조항 번호 인덱싱, 법적 구조 유지
   - `ProductSpecViewer`: 조항별 구분, 강조 표시
   - `AnalysisReportViewer`: 표 형식 파싱, 수치 하이라이트
   - `GuideViewer`: Step 번호 자동 생성, 체크리스트 형식

2. **검색 및 필터링**
   - documentType별 카드 필터링
   - 특정 타입 카드만 우선 표시

3. **AI 추천 개선**
   - documentType 기반 카드 추천 로직
   - 상황별 적절한 문서 타입 자동 선택

---

## 📝 변경 이력

- **2025-01-26**: Phase 2 업데이트 - `documentType` 필드 추가, 5가지 문서 타입 정의
- **2025-01-XX**: 초기 스키마 정의 - 하이브리드 카드 시스템 구축

---

## 💡 개발자 참고

- **타입 정의**: `/src/data/scenarios.ts`
- **카드 렌더링**: `/src/app/pages/RealTimeConsultationPage.tsx`
- **상세 정보 모달**: `/src/app/components/modals/DocumentDetailModal.tsx`
- **Attributes Grid**: `/src/app/components/cards/ProductAttributesGrid.tsx`
