# CALL:ACT 과거 상담 데이터 활용 구조

## 1. 개요

과거 상담 데이터는 **VectorDB(RAG) + RDB(관계형 DB)**에 저장되어 전체 시스템에서 핵심적으로 활용됩니다.

---

## 2. 데이터베이스 구조

### 2.1 RDB (관계형 데이터베이스) - PostgreSQL

구조화된 상담 데이터 저장

```sql
-- 상담 마스터 테이블
CREATE TABLE consultations (
  id VARCHAR(50) PRIMARY KEY,                    -- 'CS-20250105-1432'
  customer_id VARCHAR(50) NOT NULL,              -- 'CUST-001'
  agent_id VARCHAR(50) NOT NULL,                 -- 'EMP-001'
  status VARCHAR(20),                            -- '완료', '진행중', '미완료'
  category VARCHAR(50),                          -- '카드분실', '해외결제', 수수료문의'
  title TEXT,                                    -- '카드 분실 신고 및 재발급 요청'
  call_date DATE,                                -- 2025-01-05
  call_time TIME,                                -- 14:32
  call_duration VARCHAR(20),                     -- '5:23'
  fcr BOOLEAN,                                   -- true/false (First Call Resolution)
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- 고객 정보 테이블
CREATE TABLE customers (
  id VARCHAR(50) PRIMARY KEY,                    -- 'CUST-001'
  name VARCHAR(100),                             -- '홍길동'
  phone VARCHAR(20),                             -- '010-1234-5678'
  birth_date DATE,                               -- 1985-03-15
  address TEXT,                                  -- '서울시 강남구 테헤란로 123'
  created_at TIMESTAMP
);

-- 상담 전문 (통화 내용)
CREATE TABLE consultation_transcripts (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  speaker VARCHAR(20),                           -- 'customer' or 'agent'
  message TEXT,
  timestamp TIME,
  created_at TIMESTAMP
);

-- 상담 요약 및 후처리
CREATE TABLE consultation_summaries (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  ai_summary TEXT,                               -- AI가 생성한 요약
  memo TEXT,                                     -- 상담사 메모
  follow_up_tasks TEXT,                          -- 후속 일정
  handoff_department VARCHAR(100),               -- 이관 부서
  handoff_notes TEXT,                            -- 이관 사항
  created_at TIMESTAMP
);

-- 감정 분석 및 피드백
CREATE TABLE consultation_feedback (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  emotion_start VARCHAR(20),                     -- '부정적', '중립', '긍정적'
  emotion_middle VARCHAR(20),
  emotion_end VARCHAR(20),
  quality_score VARCHAR(10),                     -- '상', '중', '하'
  processing_time_score INT,                     -- 85점
  gratitude_score INT,                           -- 75점
  emotion_shift_score INT,                       -- 88점
  manual_compliance_score INT,                   -- 92점
  created_at TIMESTAMP
);

-- STT 키워드 추출
CREATE TABLE stt_keywords (
  id SERIAL PRIMARY KEY,
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  keyword VARCHAR(100),                          -- '카드분실', '해외결제'
  confidence FLOAT,                              -- 0.95 (신뢰도)
  created_at TIMESTAMP
);
```

---

### 2.2 VectorDB (벡터 데이터베이스) - RAG 시스템

문서 임베딩 및 유사도 검색을 위한 저장소 (예: Pinecone, Weaviate, pgvector)

```json
{
  "id": "DOC-20250105-1432-001",
  "consultation_id": "CS-20250105-1432",
  "document_type": "current_situation",
  "title": "카드 분실 신고 처리 절차",
  "keywords": ["#분실신고", "#즉시정지", "#재발급"],
  "content": "고객의 카드 분실 신고를 접수하고 즉시 카드 사용을 정지합니다...",
  "embedding": [0.234, -0.123, 0.567, ...],
  "metadata": {
    "category": "카드분실",
    "usage_count": 127,
    "last_used": "2025-01-05T14:32:00Z",
    "effectiveness_score": 0.92
  }
}
```

---

## 3. 페이지별 과거 상담 데이터 활용

### 3.1 실시간 상담 페이지 (RealTimeConsultationPage)

#### 3.1.1 활용 데이터

- 최근 상담 내역 (RDB)
- 현재 상황 칸반보드 (VectorDB - RAG)
- 다음 단계 칸반보드 (VectorDB - RAG)
- 권장 안내 멘트 (AI 생성 + 과거 우수 사례)

#### 3.1.2 API 호출 구조

**고객 정보 + 최근 상담 내역 조회:**

```typescript
GET /api/customers/{customerId}/consultations/recent

// 응답 예시
{
  "customer": {
    "id": "CUST-001",
    "name": "홍길동",
    "phone": "010-1234-5678",
    "birthDate": "1985-03-15",
    "address": "서울시 강남구 테헤란로 123"
  },
  "recentConsultations": [
    {
      "id": "CS-20250103-1030",
      "title": "카드 재발급 문의",
      "date": "2025-01-03 10:30",
      "category": "카드분실",
      "status": "완료"
    }
  ]
}
```

**STT 키워드 기반 RAG 검색 (실시간):**

```typescript
POST /api/rag/search

// 요청 예시
{
  "sttKeywords": ["카드분실", "해외결제", "수수료문의"],
  "customerId": "CUST-001",
  "consultationId": "CS-20250105-1432"
}

// 응답 예시
{
  "currentSituation": [
    {
      "id": 1,
      "title": "카드 분실 신고 처리 절차",
      "keywords": ["#분실신고", "#즉시정지", "#재발급"],
      "content": "고객의 카드 분실 신고를 접수하고 즉시 카드 사용을 정지합니다...",
      "relevanceScore": 0.95
    },
    {
      "id": 2,
      "title": "긴급 카드 정지 안내",
      "keywords": ["#긴급처리", "#즉시정지"],
      "content": "카드 분실 시 즉시 사용 정지가 가능합니다...",
      "relevanceScore": 0.88
    }
  ],
  "nextStep": [
    {
      "id": 1,
      "title": "재발급 카드 배송 안내",
      "keywords": ["#배송", "#3-5일", "#주소확인"],
      "content": "재발급 카드는 등록된 주소로 3-5일 내 배송됩니다...",
      "relevanceScore": 0.92
    },
    {
      "id": 2,
      "title": "분실 카드 부정 사용 보상",
      "keywords": ["#보상", "#부정사용", "#보험"],
      "content": "분실 신고 후 발생한 부정 사용에 대해서는 보험 처리가 가능합니다...",
      "relevanceScore": 0.85
    }
  ],
  "guidanceScript": "고객님, 카드 분실 신고 접수되었습니다. 즉시 카드 사용이 정지되며, 3-5일 내 재발급 카드가 등록된 주소로 배송됩니다."
}
```

---

### 3.2 상담 후처리 페이지 (AfterCallWorkPage)

#### 3.2.1 활용 데이터

- 현재 상담 케이스 (현재 통화 데이터)
- 유사 사례 참고 (VectorDB - 과거 유사 케이스 검색)
- AI 상담 요약본 (STT 전문 + AI 요약)
- 상담 전문 (현재 통화 STT 결과)

#### 3.2.2 API 호출 구조

**유사 사례 검색:**

```typescript
POST /api/consultations/similar

// 요청 예시
{
  "currentConsultationId": "CS-20250105-1432",
  "category": "카드분실",
  "keywords": ["분실신고", "재발급", "긴급"],
  "limit": 3
}

// 응답 예시
{
  "similarCases": [
    {
      "consultationId": "CS-20241228-1015",
      "category": "카드분실",
      "summary": "2024-12-28 처리 사례. 고객 카드 분실 신고 후 재발급 처리. 해외 여행 전 긴급 배송 요청하여 익일 배송으로 변경 처리.",
      "aiRecommendation": "긴급 배송 옵션 제안 권장",
      "similarityScore": 0.94,
      "outcome": "성공",
      "fcrAchieved": true
    }
  ]
}
```

**AI 상담 요약 생성:**

```typescript
POST /api/ai/summarize

// 요청 예시
{
  "consultationId": "CS-20250105-1432",
  "transcript": [
    {"speaker": "customer", "message": "안녕하세요, 카드를 분실했어요.", "timestamp": "14:32"},
    {"speaker": "agent", "message": "안녕하세요. 즉시 카드 사용을 정지하겠습니다.", "timestamp": "14:33"}
  ]
}

// 응답 예시
{
  "summary": "문의사항: 고객이 카드를 분실하여 즉시 사용 정지 및 재발급 요청\n\n처리 결과: 카드 사용 즉시 정지 처리 완료. 재발급 카드 신청 접수하였으며, 등록된 주소(서울시 강남구 테헤란로 123)로 3-5일 내 배송 예정. 고객에게 배송 추적 안내 완료.",
  "keywords": ["카드분실", "재발급", "긴급정지"],
  "recommendedCategory": "카드분실",
  "recommendedStatus": "완료"
}
```

---

### 3.3 대시보드 (DashboardPage)

#### 3.3.1 활용 데이터

- 상담 통계 (RDB 집계)
- 상담 내역 (RDB)
- 공지사항 (RDB)
- 금주의 이슈 (RDB + AI 트렌드 분석)
- 우수사원 사례집 (과거 우수 상담 케이스)

#### 3.3.2 API 호출 구조

```typescript
GET /api/dashboard/stats?agentId=EMP-001&date=2025-01-05

// 응답 예시
{
  "stats": {
    "total": 127,
    "completed": 95,
    "pending": 12,
    "incomplete": 20
  },
  "recentConsultations": [
    {
      "id": "CS-20250105-1432",
      "status": "완료",
      "category": "카드분실",
      "title": "카드 분실 신고 및 재발급 요청",
      "customer": "홍길동",
      "time": "14:32",
      "fcr": true
    }
  ],
  "bestPractices": [
    {
      "id": 1,
      "agentName": "김민수",
      "title": "진상 고객 대응 우수 사례",
      "consultationId": "CS-20250103-1122",
      "score": 95
    }
  ]
}
```

---

### 3.4 상담 내역 조회 (ConsultationHistoryPage)

#### 3.4.1 활용 데이터

- 전체 상담 내역 (RDB)
- 검색/필터링 (RDB 쿼리)

#### 3.4.2 API 호출 구조

```typescript
GET /api/consultations?search=카드분실&status=완료&page=1&limit=20

// 응답 예시
{
  "total": 127,
  "page": 1,
  "limit": 20,
  "consultations": [
    {
      "id": "CS-20250105-1432",
      "status": "완료",
      "category": "카드분실",
      "title": "카드 분실 신고 및 재발급 요청",
      "customer": "홍길동",
      "agent": "홍길동",
      "date": "2025-01-05",
      "time": "14:32",
      "duration": "5:23",
      "fcr": true
    }
  ]
}
```

---

## 4. RAG 시스템 작동 원리

### 4.1 상담 시작 시 (실시간)

```
1. 고객 전화 인입
   ↓
2. STT: 음성 → 텍스트 변환
   ↓
3. 키워드 추출: ["카드분실", "해외결제"]
   ↓
4. VectorDB 검색: 키워드 임베딩 → 유사 문서 검색
   ↓
5. 칸반보드 표시:
   - 현재 상황: Top 2 관련 문서
   - 다음 단계: Top 2 예상 문서
```

### 4.2 상담 후처리 시

```
1. 상담 종료
   ↓
2. 전문(Transcript) 저장
   ↓
3. AI 요약 생성
   ↓
4. VectorDB 검색: 현재 케이스와 유사한 과거 사례
   ↓
5. 유사 사례 제시 (참고용)
   ↓
6. 후처리 문서 저장 (RDB + VectorDB)
```

---

## 5. 현재 Mock 데이터 구조 정리

### 5.1 실시간 상담 페이지

```typescript
// 최근 상담 내역
const recentConsultations = [
  { 
    id: 1, 
    title: '카드 재발급 문의', 
    date: '2025-01-03 10:30', 
    category: '카드분실', 
    status: '완료' 
  }
];

// 칸반보드 카드 (현재 상황)
const currentSituationCards = [
  {
    id: 1,
    title: '카드 분실 신고 처리 절차',
    keywords: ['#분실신고', '#즉시정지', '#재발급'],
    content: '고객의 카드 분실 신고를 접수하고...'
  }
];

// 칸반보드 카드 (다음 단계)
const nextStepCards = [
  {
    id: 1,
    title: '재발급 카드 배송 안내',
    keywords: ['#배송', '#3-5일', '#주소확인'],
    content: '재발급 카드는 등록된 주소로...'
  }
];
```

### 5.2 상담 후처리 페이지

```typescript
// 현재 케이스
const currentCase = {
  category: '카드분실',
  summary: '고객이 카드 분실 신고 요청...',
  aiRecommendation: 'AI 추천 처리: 재발급 신청 완료...'
};

// 유사 사례
const similarCase = {
  category: '카드분실',
  summary: '2024-12-28 처리 사례. 고객 카드 분실 신고 후...'
};

// 상담 전문
const callTranscript = [
  { speaker: 'customer', message: '안녕하세요...', timestamp: '14:32' },
  { speaker: 'agent', message: '안녕하세요...', timestamp: '14:33' }
];
```

### 5.3 상담 내역 조회 페이지

```typescript
const consultationsData = [
  { 
    id: 'CS-20250105-1432', 
    status: '완료', 
    category: '카드분실', 
    title: '카드 분실 신고 및 재발급 요청',
    customer: '홍길동',
    agent: '홍길동',
    time: '14:32',
    date: '2025-01-05',
    fcr: true,
    duration: '5:23'
  }
];
```

---

## 6. 백엔드 연동 시 권장 구조

### 6.1 FastAPI 엔드포인트 예시

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import openai
from pinecone import Pinecone

app = FastAPI()

# VectorDB 초기화 (Pinecone 예시)
pc = Pinecone(api_key="YOUR_API_KEY")
index = pc.Index("consultations")

class RAGSearchRequest(BaseModel):
    sttKeywords: List[str]
    customerId: str
    consultationId: str

class DocumentCard(BaseModel):
    id: int
    title: str
    keywords: List[str]
    content: str
    relevanceScore: float

class RAGSearchResponse(BaseModel):
    currentSituation: List[DocumentCard]
    nextStep: List[DocumentCard]
    guidanceScript: str

@app.post("/api/rag/search", response_model=RAGSearchResponse)
async def search_rag(request: RAGSearchRequest):
    # 1. STT 키워드를 임베딩으로 변환
    keywords_text = " ".join(request.sttKeywords)
    embedding = get_embedding(keywords_text)
    
    # 2. VectorDB에서 유사 문서 검색
    results = index.query(
        vector=embedding,
        top_k=10,
        filter={"customerId": request.customerId}
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
            relevanceScore=match['score']
        )
        
        if doc['document_type'] == 'current_situation':
            current_situation.append(card)
        else:
            next_step.append(card)
    
    # 4. AI 권장 안내 멘트 생성
    guidance_script = generate_guidance_script(
        keywords=request.sttKeywords,
        documents=current_situation + next_step
    )
    
    return RAGSearchResponse(
        currentSituation=current_situation[:2],
        nextStep=next_step[:2],
        guidanceScript=guidance_script
    )

def get_embedding(text: str):
    """OpenAI Embedding API 호출"""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

def generate_guidance_script(keywords: List[str], documents: List[DocumentCard]) -> str:
    """AI 권장 안내 멘트 생성"""
    context = "\n".join([doc.content[:200] for doc in documents])
    
    prompt = f"""
    고객의 문의 키워드: {", ".join(keywords)}
    관련 문서 정보:
    {context}
    
    위 정보를 바탕으로 상담사가 고객에게 안내할 수 있는 간결한 멘트를 생성하세요.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 카드사 상담 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
```

---

## 7. 데이터 흐름 요약

### 7.1 실시간 상담 중

STT → 키워드 추출 → VectorDB 검색 → 칸반보드 표시

### 7.2 상담 후처리

전문 저장 → AI 요약 → 유사 사례 검색 → 후처리 문서 저장

### 7.3 상담 내역 조회

RDB 쿼리 → 검색/필터링

### 7.4 통계 대시보드

RDB 집계 → 실시간 통계 표시

---

## 8. 핵심 포인트

### 8.1 데이터 저장 방식

- **RDB**: 구조화된 데이터 (ID, 날짜, 상태 등)
- **VectorDB**: 문서 임베딩 (RAG 검색용)

### 8.2 활용 방식

- **칸반보드**: 실시간 STT 키워드 기반 RAG 검색 결과
- **유사 사례**: VectorDB에서 과거 케이스 검색
- **AI 요약**: GPT-4 기반 자동 생성

### 8.3 차별점

상담사는 과거 데이터 기반으로 실시간 지원을 받아 효율적인 상담 진행이 가능합니다.
