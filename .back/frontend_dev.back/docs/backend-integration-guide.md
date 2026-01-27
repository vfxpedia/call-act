# CALL:ACT Backend 연동 가이드

## 📊 **기술 스택**
- **Frontend**: React + TypeScript
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL + pgvector
- **Vector Search**: OpenAI Embeddings (1536차원)

---

## 🗄️ **PostgreSQL + pgvector 데이터베이스 설계**

### **1. Extension 활성화**
```sql
-- pgvector extension 활성화
CREATE EXTENSION IF NOT EXISTS vector;
```

### **2. 상담 테이블 (consultations)**
```sql
CREATE TABLE consultations (
    id SERIAL PRIMARY KEY,
    consultation_id VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    status VARCHAR(20),  -- '진행중', '완료'
    category VARCHAR(50),  -- '카드분실', '해외결제', '수수료문의'
    ai_summary TEXT,  -- AI가 생성한 상담 요약
    memo TEXT,  -- 상담사가 작성한 메모
    follow_up_tasks TEXT,  -- 후속 일정
    handoff_department VARCHAR(50),  -- 이관 부서
    handoff_notes TEXT,  -- 이관 메모
    call_time INTEGER,  -- 통화 시간 (초)
    datetime TIMESTAMP,  -- 통화 일시
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 추가 (빠른 검색)
CREATE INDEX idx_consultation_id ON consultations(consultation_id);
CREATE INDEX idx_customer_id ON consultations(customer_id);
CREATE INDEX idx_category ON consultations(category);
CREATE INDEX idx_datetime ON consultations(datetime DESC);
```

### **3. Vector 검색용 테이블 (consultation_embeddings)**
```sql
CREATE TABLE consultation_embeddings (
    id SERIAL PRIMARY KEY,
    consultation_id VARCHAR(50) REFERENCES consultations(consultation_id),
    embedding vector(1536),  -- OpenAI text-embedding-ada-002 차원
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector 유사도 검색 인덱스 (IVFFlat)
CREATE INDEX idx_embedding_cosine ON consultation_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### **4. 고객 정보 테이블 (customers)**
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    birth_date DATE,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_customer_phone ON customers(phone);
```

---

## 🔌 **FastAPI 엔드포인트**

### **1. 후처리 저장 API**
```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from pgvector.psycopg2 import register_vector
import openai

app = FastAPI()

# DB 연결
conn = psycopg2.connect(
    host="localhost",
    database="callact_db",
    user="postgres",
    password="your_password"
)
register_vector(conn)

# OpenAI API 키 설정
openai.api_key = "YOUR_OPENAI_API_KEY"

class ACWData(BaseModel):
    consultationId: str
    customerId: str
    title: str
    status: str
    category: str
    aiSummary: str
    memo: str
    followUpTasks: str
    handoffDepartment: str
    handoffNotes: str
    callTime: str
    datetime: str

@app.post("/api/consultations/acw")
async def save_acw(data: ACWData):
    """후처리 데이터 저장 (PostgreSQL + pgvector)"""
    try:
        cursor = conn.cursor()
        
        # 1. 상담 데이터 저장
        cursor.execute("""
            INSERT INTO consultations 
            (consultation_id, customer_id, title, status, category, 
             ai_summary, memo, follow_up_tasks, handoff_department, 
             handoff_notes, call_time, datetime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.consultationId, data.customerId, data.title, 
            data.status, data.category, data.aiSummary, data.memo,
            data.followUpTasks, data.handoffDepartment, 
            data.handoffNotes, int(data.callTime), data.datetime
        ))
        
        consultation_db_id = cursor.fetchone()[0]
        
        # 2. AI 요약을 벡터로 변환 (OpenAI Embeddings)
        embedding_response = openai.Embedding.create(
            input=data.aiSummary,
            model="text-embedding-ada-002"
        )
        embedding = embedding_response['data'][0]['embedding']
        
        # 3. pgvector에 임베딩 저장
        cursor.execute("""
            INSERT INTO consultation_embeddings 
            (consultation_id, embedding)
            VALUES (%s, %s)
        """, (data.consultationId, embedding))
        
        conn.commit()
        cursor.close()
        
        return {
            "status": "success",
            "consultationId": data.consultationId,
            "dbId": consultation_db_id
        }
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### **2. 유사 상담 검색 API (Vector Search)**
```python
@app.get("/api/consultations/similar/{consultation_id}")
async def get_similar_consultations(consultation_id: str, limit: int = 5):
    """유사 상담 사례 검색 (pgvector 코사인 유사도)"""
    try:
        cursor = conn.cursor()
        
        # 1. 현재 상담의 임베딩 가져오기
        cursor.execute("""
            SELECT embedding FROM consultation_embeddings
            WHERE consultation_id = %s
        """, (consultation_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        current_embedding = result[0]
        
        # 2. 유사도 검색 (코사인 유사도)
        cursor.execute("""
            SELECT 
                c.consultation_id,
                c.title,
                c.category,
                c.ai_summary,
                c.datetime,
                1 - (e.embedding <=> %s::vector) AS similarity
            FROM consultation_embeddings e
            JOIN consultations c ON e.consultation_id = c.consultation_id
            WHERE e.consultation_id != %s
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s
        """, (current_embedding, consultation_id, current_embedding, limit))
        
        results = cursor.fetchall()
        cursor.close()
        
        similar_cases = []
        for row in results:
            similar_cases.append({
                "consultationId": row[0],
                "title": row[1],
                "category": row[2],
                "aiSummary": row[3],
                "datetime": row[4].isoformat(),
                "similarity": float(row[5])
            })
        
        return {"similarCases": similar_cases}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **3. STT 키워드 기반 검색 API**
```python
@app.post("/api/consultations/search-by-keyword")
async def search_by_keyword(keyword: str, limit: int = 5):
    """STT 키워드로 관련 문서 검색 (Vector Search)"""
    try:
        # 1. 키워드를 임베딩으로 변환
        embedding_response = openai.Embedding.create(
            input=keyword,
            model="text-embedding-ada-002"
        )
        keyword_embedding = embedding_response['data'][0]['embedding']
        
        # 2. pgvector로 유사 문서 검색
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.consultation_id,
                c.title,
                c.category,
                c.ai_summary,
                1 - (e.embedding <=> %s::vector) AS similarity
            FROM consultation_embeddings e
            JOIN consultations c ON e.consultation_id = c.consultation_id
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s
        """, (keyword_embedding, keyword_embedding, limit))
        
        results = cursor.fetchall()
        cursor.close()
        
        documents = []
        for row in results:
            documents.append({
                "consultationId": row[0],
                "title": row[1],
                "category": row[2],
                "aiSummary": row[3],
                "similarity": float(row[4])
            })
        
        return {"documents": documents}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📡 **Frontend 연동 (React)**

### **1. AfterCallWorkPage.tsx - 후처리 저장**
```typescript
const handleSaveACW = async () => {
  setIsSaving(true);

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
  };

  try {
    const response = await fetch('/api/consultations/acw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(acwData)
    });

    if (!response.ok) {
      throw new Error('저장 실패');
    }

    const result = await response.json();
    console.log('✅ 저장 완료:', result);

    // localStorage 정리
    localStorage.removeItem('currentConsultationMemo');
    localStorage.removeItem('consultationCallTime');

    // 상담 중 페이지로 이동
    navigate('/consultation');
  } catch (error) {
    console.error('❌ 저장 실패:', error);
    alert('저장에 실패했습니다.');
  } finally {
    setIsSaving(false);
  }
};
```

### **2. RealTimeConsultationPage.tsx - STT 키워드 검색**
```typescript
const handleSTTKeyword = async (keyword: string) => {
  try {
    const response = await fetch('/api/consultations/search-by-keyword', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keyword, limit: 5 })
    });

    const data = await response.json();
    
    // 칸반보드에 카드 추가 (Fade-in 애니메이션)
    setKanbanCards(prev => [...prev, ...data.documents]);
  } catch (error) {
    console.error('검색 실패:', error);
  }
};
```

---

## 🚀 **성능 최적화**

### **1. Vector 검색 속도 비교**
| 방식 | 속도 | 정확도 |
|------|------|--------|
| **PostgreSQL Full-Text Search** | 0.5~2초 | 낮음 |
| **pgvector (IVFFlat)** | **0.3~1초** | 높음 |
| **pgvector (HNSW)** | **0.1~0.5초** | 매우 높음 |

### **2. HNSW 인덱스 (더 빠른 검색)**
```sql
-- IVFFlat 대신 HNSW 사용 (PostgreSQL 14+)
CREATE INDEX idx_embedding_hnsw ON consultation_embeddings 
USING hnsw (embedding vector_cosine_ops);
```

---

## 📊 **데이터 흐름**

```
1. 상담사 ➡️ 실시간 상담 페이지
2. STT ➡️ "카드분실" 키워드 캐치
3. Backend ➡️ OpenAI Embedding 변환
4. pgvector ➡️ 유사도 검색 (< 1초)
5. Frontend ➡️ 칸반보드에 카드 표시
6. 상담 완료 ➡️ 후처리 페이지
7. Backend ➡️ PostgreSQL 저장 + pgvector 임베딩 저장
8. Frontend ➡️ 다음 상담 대기
```

---

## 🔐 **환경 변수 설정**

### **.env (Backend)**
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/callact_db
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

### **실행 방법**
```bash
# Backend 실행
cd backend
pip install fastapi uvicorn psycopg2-binary pgvector openai
uvicorn main:app --reload --port 8000

# Frontend 실행
cd frontend
npm run dev
```

---

## ✅ **체크리스트**

- [ ] PostgreSQL + pgvector 설치
- [ ] 테이블 생성 (consultations, consultation_embeddings, customers)
- [ ] FastAPI 서버 실행
- [ ] OpenAI API 키 설정
- [ ] Frontend API 연동
- [ ] Vector 검색 테스트
- [ ] 성능 모니터링

---

## 📞 **API 요구명세서 참고**
자세한 API 엔드포인트는 `/docs/CALL_ACT_API_요구명세서.md` 참고
