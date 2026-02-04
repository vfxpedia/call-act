# Phase 6: 데이터 구조 분석 및 개선방안

## 1. 현재 상황 요약

### 1.1 MVP 완료 현황
- ✅ Phase 1~5 완료 (총 26개 문서, 약 9,500줄)
- ✅ MVP 완전 작동
- ✅ 42개 카드의 약관 형식 fullText 확장 100% 완료
- ✅ 문서 구조 정리 완료 (/docs/archive/)
- ✅ 수평 슬라이딩 칸반보드 구현 완료

### 1.2 남은 과제
1. **백엔드 DB 구조와 프론트엔드 화면 구조 간 불일치 해결**
2. 기능적으로 미구현된 부분 파악
3. 화면설계서 문서화

---

## 2. 데이터 구조 분석

### 2.1 프론트엔드 기대 구조 (ScenarioCard)

**위치**: `/src/data/scenarios.ts`

```typescript
export interface ScenarioCard {
  id: string;
  title: string;
  keywords: string[];
  content: string;
  systemPath: string;
  requiredChecks: string[];
  exceptions: string[];
  time: string;
  note: string;
  regulation: string;
  fullText: string;
}
```

**특징**:
- 상담 가이드 중심의 구조
- 필수 확인 사항, 예외 사항, 법규, 약관 전문 등 포함
- 칸반보드에서 "자세히 보기"로 fullText(약관 형식) 표시

---

### 2.2 백엔드 DB 구조

#### 2.2.1 카드 정보 DB (`teddycard_card_products_with_embeddings.json`)

**structured 필드 구조**:
```json
{
  "cardName": "(이응패스 여민전) K-패스 체크",
  "cardType": "체크카드",
  "annualFee": {
    "domestic": null,
    "global": null
  },
  "mainBenefits": ["대중교통부터 생활 할인까지", ...],
  "benefitDetails": {
    "pointAccrual": "",
    "conditions": "",
    "limit": ""
  },
  "performanceConditions": "없음",
  "usageGuide": "① 여민전 App 회원가입 후 카드발급...",
  "detailContent": "본 카드는 세종시 통합교통서비스...",
  "fullTerms": "※ 계약을 체결 전, 반드시 금융상품설명서...",
  "note": ""
}
```

**특징**:
- ❌ ScenarioCard와 구조가 완전히 다름
- ❌ systemPath, requiredChecks, exceptions, regulation 등 상담 가이드 필드 없음
- ✅ fullTerms는 있지만, 카드 약관 내용 (상담 가이드가 아님)
- ✅ 카드 상품 정보 중심 (카드명, 연회비, 혜택, 이용 조건 등)

**문제점**:
- 고객이 "K-패스 카드 혜택이 뭔가요?"라고 질문했을 때, 현재 칸반보드는 이 데이터를 어떻게 표시할지 정의되어 있지 않음

---

#### 2.2.2 공지사항 DB (`teddycard_notices_with_embedding.json`)

**주요 필드**:
```json
{
  "id": "notice_01",
  "title": "쿠팡 정보유출 사고 관련, 금융사기 피해 우려 NOTICE 발령!",
  "content": "■ NOTICE 발령 배경\n2025년 12월 1일...",
  "category": "emergency",
  "priority": "urgent",
  "start_date": "2025-12-03",
  "end_date": "2025-12-10",
  "status": "inactive",
  "is_pinned": false,
  "keywords": ["개인정보", "보이스피싱", ...]
}
```

**특징**:
- ❌ structured 필드가 없음
- ❌ ScenarioCard와 구조 완전히 다름
- ✅ 공지사항 표시에 특화된 구조
- ✅ 긴급/중요도 구분 가능

**문제점**:
- 상담 중 긴급 공지사항을 칸반보드에 띄울 때 ScenarioCard 형식으로 변환 필요
- fullText가 없음 (content가 전체 내용)

---

#### 2.2.3 서비스 가이드 DB (`teddycard_service_guides_with_embeddings.json`)

**structured 필드 구조**:
```json
{
  "title": "신용도 관리 방법",
  "content": "개인신용평점에 관심을 기울이고 연체를 방지하며...",
  "systemPath": "고객관리 > 신용관리 > 신용도 관리",
  "requiredChecks": [
    "본인의 개인신용평점 주기적 확인 여부",
    "연체 발생 여부 및 연체 방지 조치 확인",
    ...
  ],
  "exceptions": [
    "명의도용 피해자 및 취약계층은 신용정보 무료 조회 횟수 연 3회 가능",
    ...
  ],
  "regulation": "카드업무 취급요령 제34조",
  "detailContent": "개인신용평점은 주기적으로 확인하고...",
  "fullTerms": "",
  "time": "약 5분",
  "note": ""
}
```

**또는 FAQ 타입**:
```json
{
  "title": "지급일 안내",
  "content": "K-패스 적립금은 당월 적립분을 익월 7영업일에...",
  "keyPoints": [
    "K-패스 적립금은 당월 적립분 기준으로 지급됨",
    ...
  ],
  "benefits": [],
  "usageGuide": "적립금은 당월 적립 후 익월 7영업일에...",
  "relatedTopics": ["적립금 지급 절차", "카드사 정책", ...],
  "detailContent": "...",
  "fullTerms": "",
  "note": ""
}
```

**특징**:
- ✅ ScenarioCard와 가장 유사한 구조
- ✅ systemPath, requiredChecks, exceptions, regulation 있음
- ⚠️ keywords 필드는 루트에 있고, structured에는 없음
- ⚠️ fullTerms는 대부분 비어있음 (detailContent에 상세 내용)
- ⚠️ FAQ 타입과 가이드 타입의 structured 구조가 다름

**문제점**:
- 같은 DB 내에서도 document_type에 따라 structured 구조가 다름
- fullText 대신 detailContent 사용

---

### 2.3 데이터 흐름 비교

| 항목 | 프론트엔드 (ScenarioCard) | 카드 정보 DB | 공지사항 DB | 서비스 가이드 DB |
|------|--------------------------|------------|-----------|---------------|
| **id** | ✅ string | ✅ string | ✅ string | ✅ string |
| **title** | ✅ string | ❌ (cardName) | ✅ title | ✅ title |
| **keywords** | ✅ string[] | ❌ keywords[] (루트) | ✅ keywords[] (루트) | ✅ keywords[] (루트) |
| **content** | ✅ string | ❌ (detailContent?) | ✅ content | ✅ content |
| **systemPath** | ✅ string | ❌ | ❌ | ✅ systemPath |
| **requiredChecks** | ✅ string[] | ❌ | ❌ | ✅ requiredChecks |
| **exceptions** | ✅ string[] | ❌ | ❌ | ✅ exceptions |
| **time** | ✅ string | ❌ | ❌ | ✅ time |
| **note** | ✅ string | ✅ note | ❌ | ✅ note |
| **regulation** | ✅ string | ❌ | ❌ | ✅ regulation |
| **fullText** | ✅ string (약관 전문) | ⚠️ fullTerms | ❌ (content가 전체) | ⚠️ fullTerms (대부분 비어있음) |

---

## 3. 문제점 정리

### 3.1 핵심 문제

1. **프론트엔드는 단일 ScenarioCard 인터페이스를 기대하지만, 백엔드는 3가지 다른 데이터 구조를 제공함**
   - 카드 정보 DB: 카드 상품 정보 중심
   - 공지사항 DB: 공지사항 정보 중심
   - 서비스 가이드 DB: 상담 가이드 중심 (ScenarioCard와 가장 유사)

2. **칸반보드는 "상담 가이드" 형식을 기대하는데, 카드 정보 DB는 "카드 상품 정보"를 제공함**
   - 고객: "K-패스 카드 혜택이 뭔가요?"
   - RAG 검색: 카드 정보 DB에서 K-패스 카드 문서 반환
   - 칸반보드: systemPath, requiredChecks, exceptions가 없어서 표시 불가 ❌

3. **fullText(약관 전문) 일관성 부족**
   - 서비스 가이드 DB: fullTerms 대부분 비어있음
   - 카드 정보 DB: fullTerms 있지만 카드 약관 (상담 가이드 약관 아님)
   - 공지사항 DB: fullText 개념 없음

### 3.2 시나리오별 문제점

#### 시나리오 1: 카드 혜택 문의
**고객**: "K-패스 카드 대중교통 할인이 얼마나 되나요?"

**백엔드 응답** (카드 정보 DB):
```json
{
  "id": "CARD-SHINHAN-(이응패스-여민전)-K-패스-체크",
  "structured": {
    "cardName": "(이응패스 여민전) K-패스 체크",
    "mainBenefits": ["대중교통부터 생활 할인까지", ...],
    "detailContent": "본 카드는 세종시 통합교통서비스..."
  }
}
```

**문제**:
- ❌ systemPath 없음 → 칸반보드에서 "🖥️ 시스템 경로" 표시 불가
- ❌ requiredChecks 없음 → "필수 확인 사항" 표시 불가
- ❌ exceptions 없음 → "예외 사항" 표시 불가
- ❌ regulation 없음 → "관련 법규" 표시 불가
- ⚠️ fullTerms는 있지만 "카드 약관"이지 "상담 가이드 약관"이 아님

**현재 칸반보드 표시 결과**:
- 카드가 제대로 렌더링되지 않거나, 빈 필드가 많이 표시됨

---

#### 시나리오 2: 서비스 가이드 문의
**고객**: "신용도 관리 방법을 알려주세요."

**백엔드 응답** (서비스 가이드 DB):
```json
{
  "id": "신용도 관리방법_merged",
  "structured": {
    "title": "신용도 관리 방법",
    "content": "개인신용평점에 관심을 기울이고...",
    "systemPath": "고객관리 > 신용관리 > 신용도 관리",
    "requiredChecks": ["본인의 개인신용평점 주기적 확인 여부", ...],
    "exceptions": ["명의도용 피해자 및 취약계층...", ...],
    "regulation": "카드업무 취급요령 제34조",
    "detailContent": "개인신용평점은 주기적으로 확인하고...",
    "fullTerms": "",
    "time": "약 5분",
    "note": ""
  },
  "keywords": ["신용도", "자동이체", "체크카드", ...]
}
```

**문제**:
- ⚠️ keywords가 루트에 있고 structured에 없음
- ⚠️ fullTerms가 비어있음 (detailContent에 상세 내용)
- ⚠️ fullText가 아니라 fullTerms

**현재 칸반보드 표시 결과**:
- 대부분 필드가 있어서 잘 표시되지만, fullText(약관 전문)가 비어있을 수 있음

---

#### 시나리오 3: 긴급 공지사항
**STT 키워드 감지**: "쿠팡", "정보유출", "보이스피싱"

**백엔드 응답** (공지사항 DB):
```json
{
  "id": "notice_01",
  "title": "쿠팡 정보유출 사고 관련, 금융사기 피해 우려 NOTICE 발령!",
  "content": "■ NOTICE 발령 배경\n2025년 12월 1일...",
  "category": "emergency",
  "priority": "urgent",
  "keywords": ["개인정보", "보이스피싱", "스미싱", ...]
}
```

**문제**:
- ❌ structured 필드 자체가 없음
- ❌ systemPath, requiredChecks, exceptions, regulation 모두 없음
- ❌ fullText 없음 (content가 전체 내용)

**현재 칸반보드 표시 결과**:
- 공지사항을 ScenarioCard 형식으로 변환하지 못하면 표시 불가

---

## 4. 해결 방안

### 4.1 옵션 1: 백엔드 API에서 통합 변환 (권장 ✅)

**개념**: 백엔드 API가 모든 DB의 데이터를 ScenarioCard 형식으로 변환하여 반환

#### 장점
- ✅ 프론트엔드 코드 변경 최소화
- ✅ 데이터 정합성 보장 (백엔드에서 일괄 관리)
- ✅ 새로운 DB 추가 시 백엔드에서만 변환 로직 추가

#### 구현 방법

**백엔드 API 응답 구조**:
```python
# FastAPI 예시
from typing import List, Optional
from pydantic import BaseModel

class ScenarioCard(BaseModel):
    id: str
    title: str
    keywords: List[str]
    content: str
    systemPath: str
    requiredChecks: List[str]
    exceptions: List[str]
    time: str
    note: str
    regulation: str
    fullText: str
    # 추가 메타데이터
    sourceDB: str  # 'card_info', 'notice', 'service_guide'
    documentType: str  # 'card_product', 'notice', 'faq', 'guide'
    priority: Optional[str] = 'normal'

class RAGSearchResponse(BaseModel):
    cards: List[ScenarioCard]
    keywords: List[str]
    matchedKeywords: List[str]

# 변환 매퍼
def convert_card_info_to_scenario_card(doc: dict) -> ScenarioCard:
    """카드 정보 DB → ScenarioCard 변환"""
    structured = doc.get('structured', {})
    
    return ScenarioCard(
        id=doc['id'],
        title=f"{structured.get('cardName', '카드 정보')} 상담 가이드",
        keywords=doc.get('keywords', []),
        content=structured.get('detailContent', structured.get('usageGuide', '')),
        systemPath="카드관리 > 카드상품 > 혜택조회",  # 기본값
        requiredChecks=[
            f"✓ 카드 종류: {structured.get('cardType', 'N/A')}",
            f"✓ 연회비: 국내 {structured.get('annualFee', {}).get('domestic', '없음')}원, 해외 {structured.get('annualFee', {}).get('global', '없음')}원",
            f"✓ 실적 조건: {structured.get('performanceConditions', '없음')}"
        ],
        exceptions=[
            "⚠️ 프로모션 기간 및 혜택은 변경될 수 있습니다.",
            "⚠️ 카드 발급 조건을 확인해주세요."
        ],
        time="처리 시간: 약 2-3분",
        note=structured.get('note', '카드 혜택은 전월 실적에 따라 달라질 수 있습니다.'),
        regulation="여신전문금융업법 제10조 (카드 발급)",
        fullText=structured.get('fullTerms', structured.get('detailContent', '')),
        sourceDB='card_info',
        documentType='card_product',
        priority='normal'
    )

def convert_notice_to_scenario_card(doc: dict) -> ScenarioCard:
    """공지사항 DB → ScenarioCard 변환"""
    return ScenarioCard(
        id=doc['id'],
        title=f"[{doc.get('category', '공지').upper()}] {doc['title']}",
        keywords=doc.get('keywords', []),
        content=doc['content'][:200] + '...',  # 요약
        systemPath="공지사항 > 긴급안내",
        requiredChecks=[
            f"✓ 공지 기간: {doc.get('start_date', 'N/A')} ~ {doc.get('end_date', 'N/A')}",
            f"✓ 우선순위: {doc.get('priority', 'normal')}",
            "✓ 고객에게 정확히 전달 필수"
        ],
        exceptions=[
            "⚠️ 긴급 공지사항은 즉시 고객에게 안내해야 합니다.",
        ],
        time="처리 시간: 즉시",
        note=f"상단 고정: {'예' if doc.get('is_pinned') else '아니오'}",
        regulation="금융소비자보호법 제19조 (정보 제공)",
        fullText=doc['content'],
        sourceDB='notice',
        documentType='notice',
        priority=doc.get('priority', 'normal')
    )

def convert_service_guide_to_scenario_card(doc: dict) -> ScenarioCard:
    """서비스 가이드 DB → ScenarioCard 변환"""
    structured = doc.get('structured', {})
    
    return ScenarioCard(
        id=doc['id'],
        title=structured.get('title', doc.get('title', '')),
        keywords=doc.get('keywords', []),
        content=structured.get('content', ''),
        systemPath=structured.get('systemPath', '고객관리 > 서비스안내'),
        requiredChecks=structured.get('requiredChecks', []),
        exceptions=structured.get('exceptions', []),
        time=structured.get('time', '약 3-5분'),
        note=structured.get('note', ''),
        regulation=structured.get('regulation', ''),
        fullText=structured.get('fullTerms', structured.get('detailContent', '')),
        sourceDB='service_guide',
        documentType=doc.get('document_type', 'guide'),
        priority=doc.get('priority', 'normal')
    )

# API 엔드포인트
@app.post("/api/rag/search")
async def rag_search(query: str, keywords: List[str]) -> RAGSearchResponse:
    # 1. RAG 검색 (3개 DB에서 벡터 검색)
    results = await vector_search(query, keywords)
    
    # 2. 각 결과를 ScenarioCard로 변환
    cards = []
    for doc in results:
        source_db = doc.get('database')
        
        if source_db == 'card_info':
            card = convert_card_info_to_scenario_card(doc)
        elif source_db == 'notice':
            card = convert_notice_to_scenario_card(doc)
        elif source_db == 'service_guide':
            card = convert_service_guide_to_scenario_card(doc)
        else:
            continue  # 알 수 없는 DB는 스킵
        
        cards.append(card)
    
    # 3. 우선순위 정렬 (긴급 공지사항 우선)
    cards.sort(key=lambda x: (x.priority != 'urgent', x.priority != 'high'))
    
    return RAGSearchResponse(
        cards=cards,
        keywords=keywords,
        matchedKeywords=extract_matched_keywords(query, keywords)
    )
```

---

### 4.2 옵션 2: 프론트엔드에서 타입별 처리

**개념**: 프론트엔드에서 여러 카드 타입을 처리할 수 있도록 인터페이스 확장

#### 장점
- ✅ 백엔드 변경 최소화
- ✅ 각 카드 타입별 최적화된 UI 표시 가능

#### 단점
- ❌ 프론트엔드 코드 복잡도 증가
- ❌ 새로운 DB 추가 시 프론트엔드 코드 수정 필요

#### 구현 방법

```typescript
// /src/types/cards.ts

// 기본 카드 인터페이스
interface BaseCard {
  id: string;
  title: string;
  keywords: string[];
  content: string;
  sourceDB: 'card_info' | 'notice' | 'service_guide';
  documentType: string;
  priority?: 'urgent' | 'high' | 'normal';
}

// 상담 가이드 카드 (기존 ScenarioCard)
export interface GuideCard extends BaseCard {
  sourceDB: 'service_guide';
  systemPath: string;
  requiredChecks: string[];
  exceptions: string[];
  time: string;
  note: string;
  regulation: string;
  fullText: string;
}

// 카드 상품 카드
export interface CardProductCard extends BaseCard {
  sourceDB: 'card_info';
  cardName: string;
  cardType: string;
  annualFee: {
    domestic: number | null;
    global: number | null;
  };
  mainBenefits: string[];
  performanceConditions: string;
  usageGuide: string;
  fullTerms: string;
}

// 공지사항 카드
export interface NoticeCard extends BaseCard {
  sourceDB: 'notice';
  category: string;
  startDate: string;
  endDate: string;
  isPinned: boolean;
  status: string;
}

// 통합 카드 타입
export type UnifiedCard = GuideCard | CardProductCard | NoticeCard;

// 타입 가드
export function isGuideCard(card: UnifiedCard): card is GuideCard {
  return card.sourceDB === 'service_guide';
}

export function isCardProductCard(card: UnifiedCard): card is CardProductCard {
  return card.sourceDB === 'card_info';
}

export function isNoticeCard(card: UnifiedCard): card is NoticeCard {
  return card.sourceDB === 'notice';
}
```

**칸반보드 렌더링**:
```tsx
// RealTimeConsultationPage.tsx

const renderCard = (card: UnifiedCard, cardIndex: number) => {
  // 공통 외부 컨테이너
  const cardContainer = (
    <div
      key={card.id}
      className="bg-gradient-to-br from-white to-[#F8FBFF] border-2 border-[#0047AB]/20 rounded-lg p-5 shadow-md hover:shadow-xl hover:border-[#0047AB]/40 transition-all flex flex-col flex-shrink-0"
      style={{
        width: 'calc(50% - 8px)',
        minWidth: '320px'
      }}
    >
      {/* 타입별 내용 렌더링 */}
      {isGuideCard(card) && renderGuideCard(card)}
      {isCardProductCard(card) && renderCardProductCard(card)}
      {isNoticeCard(card) && renderNoticeCard(card)}
    </div>
  );

  return cardContainer;
};

const renderGuideCard = (card: GuideCard) => (
  <>
    <h3 className="text-base font-bold text-[#0047AB] mb-2.5">{card.title}</h3>
    <div className="flex flex-wrap gap-1.5 mb-3">
      {card.keywords.map((keyword, index) => (
        <span key={index} className="text-[11px] px-2 py-0.5 bg-[#E8F1FC] text-[#0047AB] rounded font-medium">
          {keyword}
        </span>
      ))}
    </div>
    <p className="text-xs text-[#666666] leading-relaxed mb-3">{card.content}</p>
    
    <div className="bg-white/60 rounded-md p-2.5 mb-2.5 space-y-2">
      <div className="text-[11px] text-[#0047AB] font-medium border-b border-[#0047AB]/10 pb-1.5">
        🖥️ {card.systemPath}
      </div>
      
      <div>
        <div className="text-[11px] font-semibold text-[#333333] mb-1">필수 확인 사항:</div>
        {card.requiredChecks.slice(0, 2).map((check, index) => (
          <div key={index} className="text-[10px] text-[#666666] leading-relaxed">{check}</div>
        ))}
      </div>
      
      <div>
        <div className="text-[11px] font-semibold text-[#333333] mb-1">예외 사항:</div>
        {card.exceptions.slice(0, 1).map((exception, index) => (
          <div key={index} className="text-[10px] text-[#EA4335] leading-relaxed">{exception}</div>
        ))}
      </div>
    </div>
    
    <div className="mt-auto space-y-1.5">
      <div className="flex items-center justify-between pt-2 border-t border-[#0047AB]/10">
        <div className="text-[11px] text-[#0047AB] font-medium">⏱️ {card.time}</div>
      </div>
      <div className="text-[11px] text-[#34A853] font-medium">✅ {card.note}</div>
      <button
        onClick={() => setSelectedDetailCard(card)}
        className="w-full mt-1.5 px-2.5 py-1.5 bg-[#0047AB] text-white rounded text-[11px] font-medium hover:bg-[#003580] transition-all flex items-center justify-center gap-1.5"
      >
        <FileText className="w-3.5 h-3.5" />
        자세히 보기 (약관 전문)
      </button>
    </div>
  </>
);

const renderCardProductCard = (card: CardProductCard) => (
  <>
    <div className="flex items-center justify-between mb-2">
      <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#FBBC04] text-white">카드 상품</span>
      {card.priority === 'urgent' && (
        <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#EA4335] text-white">긴급</span>
      )}
    </div>
    <h3 className="text-base font-bold text-[#0047AB] mb-2.5">{card.cardName}</h3>
    <div className="flex flex-wrap gap-1.5 mb-3">
      {card.keywords.map((keyword, index) => (
        <span key={index} className="text-[11px] px-2 py-0.5 bg-[#FFF9E6] text-[#FBBC04] rounded font-medium">
          {keyword}
        </span>
      ))}
    </div>
    
    <div className="bg-white/60 rounded-md p-2.5 mb-2.5 space-y-2">
      <div className="text-[11px] font-semibold text-[#333333] mb-1">카드 정보:</div>
      <div className="text-[10px] text-[#666666] leading-relaxed">
        ✓ 카드 종류: {card.cardType}
      </div>
      <div className="text-[10px] text-[#666666] leading-relaxed">
        ✓ 연회비: 국내 {card.annualFee.domestic ? `${card.annualFee.domestic.toLocaleString()}원` : '없음'}, 
        해외 {card.annualFee.global ? `${card.annualFee.global.toLocaleString()}원` : '없음'}
      </div>
      <div className="text-[10px] text-[#666666] leading-relaxed">
        ✓ 실적 조건: {card.performanceConditions}
      </div>
      
      <div className="text-[11px] font-semibold text-[#333333] mb-1 mt-3">주요 혜택:</div>
      {card.mainBenefits.slice(0, 2).map((benefit, index) => (
        <div key={index} className="text-[10px] text-[#34A853] leading-relaxed">
          • {benefit}
        </div>
      ))}
    </div>
    
    <div className="mt-auto space-y-1.5">
      <div className="text-[11px] text-[#999999]">💳 카드상품 안내</div>
      <button
        onClick={() => setSelectedDetailCard(card)}
        className="w-full mt-1.5 px-2.5 py-1.5 bg-[#FBBC04] text-white rounded text-[11px] font-medium hover:bg-[#F9AB00] transition-all flex items-center justify-center gap-1.5"
      >
        <FileText className="w-3.5 h-3.5" />
        카드 약관 보기
      </button>
    </div>
  </>
);

const renderNoticeCard = (card: NoticeCard) => (
  <>
    <div className="flex items-center justify-between mb-2">
      <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#EA4335] text-white">
        {card.category.toUpperCase()}
      </span>
      {card.isPinned && (
        <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#0047AB] text-white">상단고정</span>
      )}
    </div>
    <h3 className="text-base font-bold text-[#EA4335] mb-2.5">{card.title}</h3>
    <div className="flex flex-wrap gap-1.5 mb-3">
      {card.keywords.slice(0, 4).map((keyword, index) => (
        <span key={index} className="text-[11px] px-2 py-0.5 bg-[#FDECEA] text-[#EA4335] rounded font-medium">
          {keyword}
        </span>
      ))}
    </div>
    <p className="text-xs text-[#666666] leading-relaxed mb-3">{card.content.substring(0, 120)}...</p>
    
    <div className="bg-[#FFF3F0] rounded-md p-2.5 mb-2.5 space-y-2">
      <div className="text-[11px] font-semibold text-[#EA4335] mb-1">⚠️ 긴급 공지사항</div>
      <div className="text-[10px] text-[#666666] leading-relaxed">
        ✓ 공지 기간: {card.startDate} ~ {card.endDate}
      </div>
      <div className="text-[10px] text-[#666666] leading-relaxed">
        ✓ 우선순위: {card.priority}
      </div>
      <div className="text-[10px] text-[#EA4335] font-semibold">
        고객에게 정확히 안내 필수
      </div>
    </div>
    
    <div className="mt-auto space-y-1.5">
      <div className="text-[11px] text-[#999999]">📢 공지사항 전문</div>
      <button
        onClick={() => setSelectedDetailCard(card)}
        className="w-full mt-1.5 px-2.5 py-1.5 bg-[#EA4335] text-white rounded text-[11px] font-medium hover:bg-[#D93025] transition-all flex items-center justify-center gap-1.5"
      >
        <FileText className="w-3.5 h-3.5" />
        전문 보기
      </button>
    </div>
  </>
);
```

---

### 4.3 옵션 3: 하이브리드 방식 (권장 ✅✅)

**개념**: 백엔드에서 기본 변환 + 프론트엔드에서 타입별 최적화 렌더링

#### 장점
- ✅ 백엔드: 데이터 정합성 보장 (ScenarioCard 통일)
- ✅ 프론트엔드: 타입별 최적화된 UI 표시
- ✅ 확장성 우수
- ✅ 유지보수 용이

#### 구현 방법

**백엔드**:
- 모든 DB 데이터를 `ScenarioCard` + `sourceDB` + `documentType`으로 변환
- 공통 필드는 모두 채워서 반환 (없으면 기본값)

**프론트엔드**:
- `ScenarioCard`를 기본으로 받음
- `sourceDB`와 `documentType`에 따라 UI 최적화

```typescript
// ScenarioCard + 메타데이터
export interface ScenarioCard {
  // 기본 필드 (모든 카드 공통)
  id: string;
  title: string;
  keywords: string[];
  content: string;
  systemPath: string;
  requiredChecks: string[];
  exceptions: string[];
  time: string;
  note: string;
  regulation: string;
  fullText: string;
  
  // 메타데이터 (타입 구분용)
  sourceDB: 'card_info' | 'notice' | 'service_guide';
  documentType: 'card_product' | 'notice' | 'faq' | 'guide' | 'emergency';
  priority?: 'urgent' | 'high' | 'normal';
  
  // 선택적 추가 데이터 (타입별 특화 정보)
  additionalData?: {
    // 카드 상품 전용
    cardType?: string;
    annualFee?: { domestic: number | null; global: number | null };
    mainBenefits?: string[];
    
    // 공지사항 전용
    startDate?: string;
    endDate?: string;
    isPinned?: boolean;
    category?: string;
  };
}
```

**렌더링**:
```tsx
const renderCard = (card: ScenarioCard) => {
  // 타입별 스타일 정의
  const getCardStyle = () => {
    switch (card.sourceDB) {
      case 'card_info':
        return {
          badgeColor: 'bg-[#FBBC04] text-white',
          badgeText: '카드 상품',
          keywordBg: 'bg-[#FFF9E6]',
          keywordColor: 'text-[#FBBC04]',
          buttonBg: 'bg-[#FBBC04] hover:bg-[#F9AB00]'
        };
      case 'notice':
        return {
          badgeColor: 'bg-[#EA4335] text-white',
          badgeText: card.priority === 'urgent' ? '긴급 공지' : '공지사항',
          keywordBg: 'bg-[#FDECEA]',
          keywordColor: 'text-[#EA4335]',
          buttonBg: 'bg-[#EA4335] hover:bg-[#D93025]'
        };
      default:
        return {
          badgeColor: 'bg-[#0047AB] text-white',
          badgeText: '상담 가이드',
          keywordBg: 'bg-[#E8F1FC]',
          keywordColor: 'text-[#0047AB]',
          buttonBg: 'bg-[#0047AB] hover:bg-[#003580]'
        };
    }
  };

  const style = getCardStyle();

  return (
    <div className="...">
      {/* 배지 */}
      <div className={`text-[9px] px-1.5 py-0.5 rounded ${style.badgeColor}`}>
        {style.badgeText}
      </div>
      
      {/* 제목 */}
      <h3 className="...">{card.title}</h3>
      
      {/* 키워드 */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {card.keywords.map((keyword, index) => (
          <span key={index} className={`text-[11px] px-2 py-0.5 ${style.keywordBg} ${style.keywordColor} rounded`}>
            {keyword}
          </span>
        ))}
      </div>
      
      {/* 공통 내용 렌더링 */}
      <p>{card.content}</p>
      <div>🖥️ {card.systemPath}</div>
      
      {/* 타입별 추가 정보 */}
      {card.sourceDB === 'card_info' && card.additionalData && (
        <div className="...">
          <div>카드 종류: {card.additionalData.cardType}</div>
          <div>연회비: ...</div>
        </div>
      )}
      
      {/* 버튼 */}
      <button className={`${style.buttonBg} ...`}>
        자세히 보기
      </button>
    </div>
  );
};
```

---

## 5. 권장 사항

### 5.1 최종 권장: **옵션 3 (하이브리드 방식)**

**이유**:
1. ✅ **데이터 일관성**: 백엔드에서 ScenarioCard로 통일
2. ✅ **UI 최적화**: 프론트엔드에서 타입별 최적화 렌더링
3. ✅ **확장성**: 새 DB 추가 시 백엔드 매퍼만 추가
4. ✅ **유지보수**: 역할 분리 (백엔드: 데이터 변환, 프론트엔드: UI)

---

### 5.2 구현 우선순위

#### Phase 6-1: 백엔드 데이터 변환 로직 구현 (1주)
1. ScenarioCard 통합 모델 정의 (Python Pydantic)
2. 3개 DB별 변환 매퍼 구현
   - `convert_card_info_to_scenario_card()`
   - `convert_notice_to_scenario_card()`
   - `convert_service_guide_to_scenario_card()`
3. RAG 검색 API 수정 (변환 로직 적용)
4. 테스트 (각 DB별 샘플 데이터로 변환 확인)

#### Phase 6-2: 프론트엔드 타입별 렌더링 구현 (3일)
1. ScenarioCard 인터페이스 업데이트 (sourceDB, documentType, additionalData 추가)
2. 칸반보드에서 타입별 스타일 적용
   - 카드 상품: 노란색 (#FBBC04)
   - 공지사항: 빨간색 (#EA4335)
   - 상담 가이드: 파란색 (#0047AB)
3. 타입별 추가 정보 렌더링
4. "자세히 보기" 모달에서 fullText 표시 확인

#### Phase 6-3: 통합 테스트 및 최적화 (2일)
1. 실제 시나리오 테스트
   - 카드 혜택 문의 → 카드 정보 DB 카드 표시
   - 신용도 관리 문의 → 서비스 가이드 카드 표시
   - 긴급 키워드 감지 → 공지사항 카드 표시
2. 성능 테스트 (로딩 속도, 애니메이션)
3. UI/UX 피드백 반영

---

## 6. 미구현 기능 목록

### 6.1 핵심 기능

1. **실제 RAG 검색 연동** ❌
   - 현재: mockData.ts 하드코딩
   - 필요: FastAPI RAG 엔드포인트 연동

2. **실제 STT 연동** ❌
   - 현재: 시뮬레이션 (사전 정의된 대화)
   - 필요: 실시간 STT API 연동 (Google Cloud Speech-to-Text 등)

3. **고객 정보 조회 API** ❌
   - 현재: defaultCustomerInfo 하드코딩
   - 필요: 전화번호 기반 고객 DB 조회

4. **상담 이력 저장** ❌
   - 현재: 세션 메모리에만 저장
   - 필요: PostgreSQL에 저장

5. **상담 후처리 자동화** ⚠️
   - 현재: 수동 입력
   - 필요: AI 기반 자동 요약 및 카테고리 분류

### 6.2 부가 기능

1. **다중 상담 동시 처리** ❌
   - 현재: 1:1 상담만 가능
   - 필요: 여러 창으로 다중 상담 지원

2. **상담사 성과 대시보드** ⚠️
   - 현재: 기본 통계만 표시
   - 필요: 실시간 FCR, 평균 처리 시간 등

3. **관리자 알림 시스템** ❌
   - 긴급 공지사항 자동 푸시
   - 미처리 상담 알림

4. **음성 녹음 및 재생** ❌
   - 상담 내용 녹음
   - 교육용 우수 사례 재생

5. **키워드 자동 학습** ❌
   - 현재: 키워드 사전 하드코딩
   - 필요: 상담 데이터 기반 자동 키워드 추출 및 업데이트

---

## 7. 다음 단계

### 7.1 즉시 착수 (Phase 6)
1. ✅ **데이터 구조 통일**: 백엔드 변환 로직 구현
2. ✅ **화면설계서 작성**: 별도 문서로 작성

### 7.2 단기 (2주 내)
1. RAG 검색 API 연동
2. STT 연동 (시뮬레이션 → 실제)
3. 고객 정보 조회 API 구현

### 7.3 중기 (1개월 내)
1. 상담 이력 저장 기능
2. 상담 후처리 자동화
3. 성과 대시보드 개선

---

## 8. 참고 자료

- `/docs/CALL_ACT_3개_데이터베이스_구조.md`: DB 구조 상세
- `/docs/07_MockData_구조.md`: 현재 mockData 구조
- `/docs/14_칸반보드_시스템.md`: 칸반보드 설계
- `/docs/16_API_명세서.md`: API 명세
- `/src/data/scenarios.ts`: ScenarioCard 인터페이스

---

**문서 작성일**: 2026-01-17  
**작성자**: AI Assistant  
**버전**: 1.0
