# CALL:ACT 카드정보 및 혜택 데이터 활용 구조

## 1. 개요

CALL:ACT 시스템의 핵심 서비스는 **내부 고객(상담사)을 위한 AI 기반 실시간 정보 제공**입니다. 고객이 카드 정보, 혜택, 수수료 등을 문의하면 AI가 관련 정보를 즉시 칸반보드와 AI 어시스턴트를 통해 상담사에게 제공합니다.

### 1.1 핵심 목적

- **상담 업무 효율화**: 상담사가 매뉴얼을 찾아보지 않고 AI가 자동으로 관련 정보 제공
- **후처리 시간 단축**: AI 자동 요약 및 문서 생성으로 후처리 시간 최소화
- **실시간 정보 제공**: STT 기반 키워드 추출 → RAG 검색 → 칸반보드 자동 표시

---

## 2. 카드 정보/혜택 데이터 종류

### 2.1 현재 시스템에서 다루는 카테고리

```
1. 카드분실: 분실신고, 재발급, 긴급정지
2. 해외결제: 결제차단, 한도증액, 승인거부
3. 수수료문의: 연회비, 해외수수료, 환급요청
4. 포인트: 적립오류, 사용가능확인
5. 한도조회: 한도증액, 일시불한도
6. 기타: 시스템 문의, 프로모션 등
```

### 2.2 카드 상품 정보 (확장 예정)

```
- 카드 상품별 혜택 정보
- 연회비 및 실적 조건
- 포인트 적립률
- 제휴사 할인 혜택
- 부가 서비스 (공항라운지, 보험 등)
```

---

## 3. 데이터베이스 구조

### 3.1 RDB (관계형 데이터베이스) - 구조화된 카드 정보

```sql
-- 카드 상품 마스터 테이블
CREATE TABLE card_products (
  id VARCHAR(50) PRIMARY KEY,                    -- 'CARD-001'
  name VARCHAR(200),                             -- '하나카드 원큐 VIVA 체크카드'
  card_type VARCHAR(50),                         -- '신용카드', '체크카드'
  annual_fee_domestic INT,                       -- 국내전용 연회비
  annual_fee_global INT,                         -- 해외겸용 연회비
  performance_condition TEXT,                    -- 실적 조건
  main_benefits TEXT,                            -- 주요 혜택
  status VARCHAR(20),                            -- '정상판매', '판매중지'
  created_at TIMESTAMP
);

-- 카드 혜택 상세 테이블
CREATE TABLE card_benefits (
  id SERIAL PRIMARY KEY,
  card_id VARCHAR(50) REFERENCES card_products(id),
  category VARCHAR(100),                         -- '주유', '커피', '편의점', '통신비'
  benefit_type VARCHAR(50),                      -- '할인', '포인트적립', '캐시백'
  benefit_rate DECIMAL(5,2),                     -- 5.00 (5% 할인)
  benefit_limit INT,                             -- 월 한도 (원)
  condition_text TEXT,                           -- '월 30만원 이상 이용시'
  created_at TIMESTAMP
);

-- 수수료 정보 테이블
CREATE TABLE fee_info (
  id SERIAL PRIMARY KEY,
  fee_type VARCHAR(100),                         -- '해외수수료', '현금서비스수수료', '연회비'
  card_id VARCHAR(50) REFERENCES card_products(id),
  fee_rate DECIMAL(5,2),                         -- 1.50 (1.5%)
  fixed_fee INT,                                 -- 고정 수수료 (원)
  description TEXT,
  created_at TIMESTAMP
);

-- 포인트 정책 테이블
CREATE TABLE point_policy (
  id SERIAL PRIMARY KEY,
  card_id VARCHAR(50) REFERENCES card_products(id),
  category VARCHAR(100),                         -- '일반가맹점', '해외가맹점'
  point_rate DECIMAL(5,2),                       -- 0.50 (0.5% 적립)
  point_unit INT,                                -- 적립 단위 (1000원당)
  expiry_months INT,                             -- 포인트 유효기간 (개월)
  created_at TIMESTAMP
);

-- 프로모션 정보 테이블
CREATE TABLE promotions (
  id VARCHAR(50) PRIMARY KEY,                    -- 'PROMO-2025-001'
  title VARCHAR(200),                            -- '하나카드x메가커피 프로모션'
  card_id VARCHAR(50) REFERENCES card_products(id),
  start_date DATE,
  end_date DATE,
  benefit_description TEXT,
  conditions TEXT,
  status VARCHAR(20),                            -- '진행중', '종료'
  created_at TIMESTAMP
);
```

### 3.2 VectorDB (벡터 데이터베이스) - RAG 검색용

```json
{
  "id": "DOC-BENEFIT-001",
  "document_type": "card_benefit",
  "card_id": "CARD-001",
  "card_name": "하나카드 원큐 VIVA 체크카드",
  "category": "주유",
  "title": "주유 할인 혜택",
  "keywords": ["주유", "할인", "SK에너지", "GS칼텍스"],
  "content": "SK에너지, GS칼텍스에서 리터당 100원 할인. 월 최대 5만원까지 할인 가능. 전월 실적 30만원 이상 시 적용.",
  "embedding": [0.123, -0.456, 0.789, ...],
  "metadata": {
    "benefit_rate": 100,
    "monthly_limit": 50000,
    "condition": "전월 실적 30만원 이상",
    "priority": "high",
    "last_updated": "2025-01-05T10:00:00Z"
  }
}
```

```json
{
  "id": "DOC-FEE-001",
  "document_type": "fee_info",
  "category": "수수료문의",
  "title": "해외 결제 수수료 안내",
  "keywords": ["해외수수료", "환전수수료", "해외결제"],
  "content": "해외 가맹점 이용 시 국제브랜드 수수료 1.0% + 해외서비스 수수료 0.5% = 총 1.5% 수수료 부과. 단, VIVA 체크카드는 해외서비스 수수료 면제.",
  "embedding": [0.234, -0.567, 0.890, ...],
  "metadata": {
    "fee_type": "해외수수료",
    "total_rate": 1.5,
    "exemption_cards": ["CARD-001", "CARD-005"],
    "priority": "high"
  }
}
```

---

## 4. 페이지별 카드 정보/혜택 데이터 활용

### 4.1 실시간 상담 페이지 (RealTimeConsultationPage)

#### 4.1.1 AI 검색 어시스턴트

**현재 Mock 데이터:**
```typescript
const getAIResponse = (query: string): string => {
  if (query.includes('재발급') || query.includes('배송')) {
    return '재발급 카드는 신청 후 3-5 영업일 내 등록된 주소로 배송됩니다. 배송비는 무료이며, 택배 추적 번호는 SMS로 발송됩니다.';
  } else if (query.includes('수수료') || query.includes('연회비')) {
    return '연회비는 카드 발급 후 1년 후 청구됩니다. 전년도 실적 조건을 충족하면 면제됩니다. 실적 기준은 월 30만원 이상 사용입니다.';
  } else if (query.includes('해외') || query.includes('결제')) {
    return '해외 결제는 기본적으로 활성화되어 있습니다. 단, 일부 국가는 보안 정책으로 인해 사전 승인이 필요할 수 있습니다. 고객센터에서 즉시 해제 가능합니다.';
  }
};
```

**실제 API 호출 구조:**
```typescript
POST /api/ai/assistant

// 요청
{
  "query": "연회비 환불이 가능한가요?",
  "consultationId": "CS-20250105-1432",
  "customerId": "CUST-001",
  "context": {
    "sttKeywords": ["연회비", "환불"],
    "currentCategory": "수수료문의"
  }
}

// 응답
{
  "answer": "연회비는 카드 발급 후 1년 후 청구됩니다. 전년도 실적 조건(월 30만원 이상)을 충족하면 면제됩니다. 이미 납부한 연회비는 중도 해지 시 일할 계산하여 환불 가능합니다.",
  "relatedDocuments": [
    {
      "id": "DOC-FEE-003",
      "title": "연회비 정책 및 환불 안내",
      "relevanceScore": 0.95
    }
  ],
  "suggestedActions": [
    "고객의 전년도 실적 확인",
    "연회비 면제 조건 안내"
  ]
}
```

#### 4.1.2 칸반보드 (현재 상황 / 다음 단계)

**현재 Mock 데이터:**
```typescript
const currentSituationCards = [
  {
    id: 1,
    title: '카드 분실 신고 처리 절차',
    keywords: ['#분실신고', '#즉시정지', '#재발급'],
    content: '고객의 카드 분실 신고를 접수하고...'
  }
];

const nextStepCards = [
  {
    id: 1,
    title: '재발급 카드 배송 안내',
    keywords: ['#배송', '#3-5일', '#주소확인'],
    content: '재발급 카드는 등록된 주소로...'
  }
];
```

**실제 API 호출 구조:**
```typescript
POST /api/kanban/search

// 요청
{
  "sttKeywords": ["연회비", "수수료", "환불"],
  "customerId": "CUST-001",
  "cardId": "CARD-001"
}

// 응답
{
  "currentSituation": [
    {
      "id": 1,
      "title": "연회비 정책 안내",
      "keywords": ["#연회비", "#실적조건", "#면제"],
      "content": "하나카드 VIVA 체크카드 연회비는 국내전용 10,000원, 해외겸용 13,000원입니다. 전년도 월평균 30만원 이상 사용 시 다음연도 연회비 면제됩니다.",
      "relevanceScore": 0.96,
      "source": "카드상품설명서_2025.pdf"
    },
    {
      "id": 2,
      "title": "연회비 환불 절차",
      "keywords": ["#환불", "#중도해지", "#일할계산"],
      "content": "카드 해지 시 사용하지 않은 기간에 대해 일할 계산하여 환불됩니다. 해지 신청 후 7영업일 내 등록 계좌로 입금됩니다.",
      "relevanceScore": 0.92,
      "source": "연회비_환불정책.pdf"
    }
  ],
  "nextStep": [
    {
      "id": 1,
      "title": "연회비 면제 조건 확인",
      "keywords": ["#실적확인", "#면제조건"],
      "content": "고객의 전년도 이용 실적을 확인하여 연회비 면제 대상인지 확인합니다. 시스템에서 자동 조회 가능합니다.",
      "relevanceScore": 0.89
    },
    {
      "id": 2,
      "title": "연회비 청구 일정 안내",
      "keywords": ["#청구일", "#납부방법"],
      "content": "연회비는 카드 발급일 기준 1년 후 청구됩니다. 카드 대금과 함께 자동 청구되며, 별도 납부 절차는 없습니다.",
      "relevanceScore": 0.85
    }
  ]
}
```

---

### 4.2 상담 후처리 페이지 (AfterCallWorkPage)

**활용 방식:**
- AI가 상담 전문을 분석하여 카드 정보/혜택 관련 내용 자동 추출
- 유사 사례 검색 시 카드 정보/혜택 문의 케이스 참조

---

### 4.3 대시보드 (DashboardPage)

**금주의 이슈 - 트렌드 분석:**
```typescript
const weeklyIssues = [
  { id: 1, summary: '해외 결제 차단 문의 급증 (42건)', time: '3시간 전' },
  { id: 4, summary: '연회비 환불 관련 문의 증가 추세', time: '2일 전' }
];
```

**실제 API:**
```typescript
GET /api/dashboard/trending-issues?days=7

// 응답
{
  "issues": [
    {
      "category": "해외결제",
      "summary": "해외 결제 차단 문의 급증 (42건)",
      "count": 42,
      "trend": "상승",
      "relatedKeywords": ["해외결제", "차단", "승인거부"],
      "timestamp": "2025-01-05T14:00:00Z"
    },
    {
      "category": "수수료문의",
      "summary": "연회비 환불 관련 문의 증가 추세",
      "count": 28,
      "trend": "상승",
      "relatedKeywords": ["연회비", "환불", "면제"],
      "timestamp": "2025-01-03T10:00:00Z"
    }
  ]
}
```

---

## 5. RAG 시스템 작동 원리 (카드 정보/혜택)

### 5.1 실시간 검색 흐름

```
1. 고객 문의: "연회비가 얼마인가요?"
   ↓
2. STT 변환: "연회비가 얼마인가요?"
   ↓
3. 키워드 추출: ["연회비"]
   ↓
4. VectorDB 검색:
   - 임베딩 생성: embedding("연회비")
   - 유사 문서 검색: cosine_similarity > 0.8
   ↓
5. 관련 문서 반환:
   - "연회비 정책 안내" (0.96)
   - "연회비 면제 조건" (0.92)
   - "연회비 환불 절차" (0.89)
   ↓
6. 칸반보드 표시:
   - 현재 상황: Top 2 문서
   - 다음 단계: Top 2 예상 문서
   ↓
7. AI 답변 생성:
   - GPT-4 기반 자연어 답변 생성
   - 검색된 문서를 컨텍스트로 활용
```

### 5.2 문서 우선순위 로직

```python
def calculate_document_priority(doc, query_keywords):
    """
    문서 우선순위 계산
    1. 임베딩 유사도 (40%)
    2. 키워드 매칭 (30%)
    3. 문서 사용 빈도 (20%)
    4. 최근 업데이트 여부 (10%)
    """
    similarity_score = cosine_similarity(doc.embedding, query_embedding) * 0.4
    keyword_score = keyword_match_score(doc.keywords, query_keywords) * 0.3
    usage_score = normalize(doc.usage_count) * 0.2
    recency_score = recency_factor(doc.last_updated) * 0.1
    
    return similarity_score + keyword_score + usage_score + recency_score
```

---

## 6. 백엔드 API 구조 (FastAPI 예시)

### 6.1 AI 어시스턴트 엔드포인트

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import openai
from pinecone import Pinecone

app = FastAPI()

class AIAssistantRequest(BaseModel):
    query: str
    consultationId: str
    customerId: str
    context: Optional[dict] = None

class AIAssistantResponse(BaseModel):
    answer: str
    relatedDocuments: List[dict]
    suggestedActions: List[str]

@app.post("/api/ai/assistant", response_model=AIAssistantResponse)
async def ai_assistant(request: AIAssistantRequest):
    # 1. 쿼리 임베딩
    query_embedding = get_embedding(request.query)
    
    # 2. VectorDB 검색
    pc = Pinecone(api_key="YOUR_API_KEY")
    index = pc.Index("card-info")
    
    results = index.query(
        vector=query_embedding,
        top_k=5,
        filter={
            "document_type": {"$in": ["card_benefit", "fee_info", "point_policy"]}
        }
    )
    
    # 3. 컨텍스트 구성
    context_docs = []
    for match in results['matches']:
        context_docs.append({
            "id": match['metadata']['id'],
            "title": match['metadata']['title'],
            "content": match['metadata']['content'],
            "relevanceScore": match['score']
        })
    
    # 4. GPT-4 답변 생성
    context_text = "\n\n".join([f"{doc['title']}: {doc['content']}" for doc in context_docs])
    
    prompt = f"""
    당신은 하나카드 상담 전문가입니다.
    
    고객 질문: {request.query}
    
    관련 정보:
    {context_text}
    
    위 정보를 바탕으로 고객 질문에 대한 정확하고 친절한 답변을 작성하세요.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 하나카드 상담 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    answer = response.choices[0].message.content
    
    # 5. 추천 액션 생성
    suggested_actions = generate_suggested_actions(request.query, context_docs)
    
    return AIAssistantResponse(
        answer=answer,
        relatedDocuments=context_docs[:3],
        suggestedActions=suggested_actions
    )

def generate_suggested_actions(query: str, docs: List[dict]) -> List[str]:
    """상황별 추천 액션 생성"""
    actions = []
    
    if "연회비" in query:
        actions.append("고객의 전년도 실적 확인")
        actions.append("연회비 면제 조건 안내")
    
    if "해외" in query and "결제" in query:
        actions.append("해외 결제 차단 해제 처리")
        actions.append("사전 승인 필요 국가 안내")
    
    if "포인트" in query:
        actions.append("포인트 잔액 조회")
        actions.append("포인트 사용 가능 가맹점 안내")
    
    return actions
```

### 6.2 칸반보드 검색 엔드포인트

```python
class KanbanSearchRequest(BaseModel):
    sttKeywords: List[str]
    customerId: str
    cardId: Optional[str] = None

class DocumentCard(BaseModel):
    id: int
    title: str
    keywords: List[str]
    content: str
    relevanceScore: float
    source: Optional[str] = None

class KanbanSearchResponse(BaseModel):
    currentSituation: List[DocumentCard]
    nextStep: List[DocumentCard]

@app.post("/api/kanban/search", response_model=KanbanSearchResponse)
async def search_kanban(request: KanbanSearchRequest):
    # 1. 키워드 조합 임베딩
    keywords_text = " ".join(request.sttKeywords)
    embedding = get_embedding(keywords_text)
    
    # 2. VectorDB 검색
    pc = Pinecone(api_key="YOUR_API_KEY")
    index = pc.Index("card-info")
    
    results = index.query(
        vector=embedding,
        top_k=10,
        filter={"cardId": request.cardId} if request.cardId else {}
    )
    
    # 3. 현재 상황 vs 다음 단계 분류
    current_situation = []
    next_step = []
    
    for match in results['matches']:
        doc = match['metadata']
        card = DocumentCard(
            id=doc['id'],
            title=doc['title'],
            keywords=doc['keywords'],
            content=doc['content'],
            relevanceScore=match['score'],
            source=doc.get('source')
        )
        
        # 문서 타입에 따라 분류
        if doc.get('document_type') == 'current_info':
            current_situation.append(card)
        elif doc.get('document_type') == 'next_step':
            next_step.append(card)
        else:
            # 기본적으로 현재 상황에 배치
            if len(current_situation) < 2:
                current_situation.append(card)
            else:
                next_step.append(card)
    
    return KanbanSearchResponse(
        currentSituation=current_situation[:2],
        nextStep=next_step[:2]
    )
```

---

## 7. 데이터 흐름 요약

### 7.1 실시간 상담 중

```
고객: "연회비가 얼마인가요?"
  ↓
STT: "연회비가 얼마인가요?"
  ↓
키워드 추출: ["연회비"]
  ↓
VectorDB 검색: 연회비 관련 문서
  ↓
칸반보드 표시:
  - 현재: 연회비 정책, 연회비 환불
  - 다음: 면제 조건, 청구 일정
  ↓
AI 어시스턴트: 자연어 답변 생성
  ↓
상담사: 고객에게 안내
```

### 7.2 카드 정보 업데이트

```
관리자: 새 카드 상품 등록
  ↓
RDB: card_products 테이블 INSERT
  ↓
혜택 정보 입력: card_benefits 테이블 INSERT
  ↓
문서 생성: 상품설명서 → 텍스트 추출
  ↓
임베딩 생성: OpenAI Embedding API
  ↓
VectorDB: 임베딩 벡터 저장
  ↓
실시간 검색: 새 정보 즉시 반영
```

---

## 8. 현재 Mock 데이터 구조 정리

### 8.1 AI 어시스턴트 응답 패턴

```typescript
// /src/app/pages/RealTimeConsultationPage.tsx (114-124행)

const getAIResponse = (query: string): string => {
  // 패턴 1: 재발급/배송 문의
  if (query.includes('재발급') || query.includes('배송')) {
    return '재발급 카드는 신청 후 3-5 영업일 내...';
  }
  
  // 패턴 2: 수수료/연회비 문의
  else if (query.includes('수수료') || query.includes('연회비')) {
    return '연회비는 카드 발급 후 1년 후 청구됩니다...';
  }
  
  // 패턴 3: 해외 결제 문의
  else if (query.includes('해외') || query.includes('결제')) {
    return '해외 결제는 기본적으로 활성화되어 있습니다...';
  }
  
  // 패턴 4: 기타
  else {
    return '해당 내용에 대한 자세한 정보를 찾았습니다...';
  }
};
```

### 8.2 상담 카테고리 분류

```typescript
// 전체 시스템에서 사용되는 카테고리
const categories = [
  '카드분실',
  '해외결제',
  '수수료문의',
  '포인트',
  '한도조회',
  '기타'
];
```

### 8.3 STT 키워드 예시

```typescript
// /src/app/pages/RealTimeConsultationPage.tsx (22행)

const sttKeywords = ['카드분실', '해외결제', '수수료문의'];
```

---

## 9. 확장 계획

### 9.1 카드 상품 DB 구축

- 전체 카드 상품 정보 DB화
- 실시간 혜택 정보 업데이트
- 프로모션 자동 반영

### 9.2 지능형 추천 시스템

- 고객 프로파일 기반 맞춤 카드 추천
- 과거 상담 이력 기반 선호도 분석
- 실시간 트렌드 기반 혜택 우선 안내

### 9.3 멀티모달 검색

- 텍스트뿐만 아니라 이미지(카드 디자인) 검색
- 음성 명령 기반 카드 정보 조회
- PDF, 엑셀 등 다양한 형식의 문서 자동 임베딩

---

## 10. 핵심 포인트

### 10.1 데이터 저장 방식

- **RDB**: 구조화된 카드 정보 (상품, 혜택, 수수료, 포인트)
- **VectorDB**: 문서 임베딩 (자연어 검색용)

### 10.2 실시간 제공 방식

- **칸반보드**: STT 키워드 기반 자동 문서 표시
- **AI 어시스턴트**: 상담사 질문에 즉시 답변

### 10.3 핵심 차별점

- 상담사가 매뉴얼을 찾지 않아도 AI가 자동으로 정보 제공
- STT 기반 실시간 키워드 추출 → RAG 검색 → 즉시 표시
- 과거 상담 데이터와 카드 정보를 결합한 지능형 추천
