# 📚 CALL:ACT 백엔드 연결 가이드

> **CALL:ACT** (카드사 상담사를 위한 AI 기반 실시간 상담 지원 시스템)를 FastAPI + PostgreSQL + pgvector 백엔드와 연결하는 방법을 안내합니다.

---

## 🎯 현재 시스템 구조

### Frontend Only (Phase 1 완료)
```
┌─────────────────────────────────────┐
│  Frontend (React + Tailwind v4)    │
│  ↓                                  │
│  LocalStorage (브라우저 내부 저장소)  │  ← 현재 상태
└─────────────────────────────────────┘
```

**제약사항**:
- ❌ 데이터가 **브라우저에만 저장**됨
- ❌ 다른 기기/브라우저와 **데이터 공유 불가**
- ❌ 브라우저 캐시 삭제 시 **모든 데이터 손실**
- ❌ 실시간 STT + RAG 기능 **동작 불가**

---

## 🚀 백엔드 연결 후 시스템 구조 (Phase 2 목표)

### Full Stack Architecture
```
┌─────────────────────────────────────┐
│  Frontend (React + Tailwind v4)    │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│  Backend API (FastAPI)              │
│  - RESTful API                      │
│  - WebSocket (실시간 STT)            │
│  - JWT 인증                          │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│  Database (PostgreSQL + pgvector)   │
│  - 카드 정보 DB                      │
│  - 카드사 이용 안내 DB                │
│  - 상담 사례 DB                      │
│  - 벡터 검색 (RAG)                   │
└─────────────────────────────────────┘
```

**장점**:
- ✅ **영구 데이터 저장**
- ✅ **실시간 동기화** (모든 기기)
- ✅ **STT + RAG 기반 칸반보드** 동작
- ✅ **보안 강화** (JWT 인증)
- ✅ **확장 가능한 아키텍처**

---

## 📋 백엔드 연결 단계별 가이드

### **Step 1: 백엔드 서버 준비**

#### 1.1. FastAPI 프로젝트 생성
```bash
# 프로젝트 디렉토리 생성
mkdir callact-backend
cd callact-backend

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-jose[cryptography] passlib[bcrypt] python-multipart websockets
```

#### 1.2. PostgreSQL + pgvector 설치
```bash
# Docker로 PostgreSQL + pgvector 실행
docker run -d \
  --name callact-db \
  -e POSTGRES_USER=callact \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=callact_db \
  -p 5432:5432 \
  ankane/pgvector
```

#### 1.3. 환경 변수 설정 (`.env`)
```env
DATABASE_URL=postgresql://callact:your_password@localhost:5432/callact_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### **Step 2: 데이터베이스 스키마 생성**

#### 2.1. SQLAlchemy 모델 정의 (`models.py`)
```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(String, primary_key=True)  # EMP-001
    name = Column(String, nullable=False)
    team = Column(String, nullable=False)  # 상담1팀, 상담2팀, 상담3팀
    position = Column(String, nullable=False)  # 사원, 대리, 과장, 팀장
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    status = Column(String, default='active')  # active, vacation, inactive
    join_date = Column(DateTime, default=datetime.utcnow)
    
    # 성과 데이터
    consultations = Column(Integer, default=0)
    fcr = Column(Float, default=0.0)
    avg_time = Column(String, default='0:00')
    rank = Column(Integer, default=0)
    trend = Column(String, default='same')  # up, down, same

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(String, primary_key=True)  # CS-20250105-1432
    agent = Column(String, nullable=False)
    customer = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, default='진행중')
    datetime = Column(DateTime, default=datetime.utcnow)
    duration = Column(String, nullable=False)
    fcr = Column(Boolean, default=False)
    is_best_practice = Column(Boolean, default=False)
    memo = Column(Text)
    audio_url = Column(String)  # 녹음 파일 URL

class Notice(Base):
    __tablename__ = "notices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String, nullable=False)  # 긴급, 이벤트, 시스템
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    views = Column(Integer, default=0)
    pinned = Column(Boolean, default=False)
```

#### 2.2. 데이터베이스 초기화 (`database.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 테이블 생성
from models import Base
Base.metadata.create_all(bind=engine)
```

---

### **Step 3: FastAPI 엔드포인트 생성**

#### 3.1. 사원 관리 API (`main.py`)
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from models import Employee, Consultation, Notice
from pydantic import BaseModel
from typing import List

app = FastAPI()

# CORS 설정 (React 앱과 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 사원 관리 API ====================

class EmployeeCreate(BaseModel):
    name: str
    team: str
    position: str
    email: str
    phone: str

@app.get("/api/employees", response_model=List[Employee])
def get_employees(db: Session = Depends(get_db)):
    """모든 사원 조회"""
    return db.query(Employee).all()

@app.get("/api/employees/{employee_id}")
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    """특정 사원 조회"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다")
    return employee

@app.post("/api/employees", status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """신규 사원 추가"""
    # 자동으로 다음 사번 생성 (EMP-001, EMP-002, ...)
    last_emp = db.query(Employee).order_by(Employee.id.desc()).first()
    next_id = f"EMP-{int(last_emp.id.split('-')[1]) + 1:03d}" if last_emp else "EMP-001"
    
    new_employee = Employee(
        id=next_id,
        name=employee.name,
        team=employee.team,
        position=employee.position,
        email=employee.email,
        phone=employee.phone,
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@app.put("/api/employees/{employee_id}")
def update_employee(employee_id: str, employee: EmployeeCreate, db: Session = Depends(get_db)):
    """사원 정보 수정"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다")
    
    for key, value in employee.dict().items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    """사원 삭제"""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="사원을 찾을 수 없습니다")
    
    db.delete(db_employee)
    db.commit()
    return {"message": "사원이 삭제되었습니다"}

# ==================== 상담 관리 API ====================

@app.get("/api/consultations")
def get_consultations(db: Session = Depends(get_db)):
    """모든 상담 내역 조회"""
    return db.query(Consultation).all()

@app.get("/api/consultations/{consultation_id}")
def get_consultation(consultation_id: str, db: Session = Depends(get_db)):
    """특정 상담 조회"""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="상담 내역을 찾을 수 없습니다")
    return consultation

# ==================== 공지사항 API ====================

@app.get("/api/notices")
def get_notices(db: Session = Depends(get_db)):
    """모든 공지사항 조회"""
    return db.query(Notice).order_by(Notice.pinned.desc(), Notice.date.desc()).all()

@app.post("/api/notices")
def create_notice(notice: dict, db: Session = Depends(get_db)):
    """공지사항 작성"""
    new_notice = Notice(**notice)
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return new_notice
```

#### 3.2. 서버 실행
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### **Step 4: Frontend에서 API 연결**

#### 4.1. Axios 설치
```bash
npm install axios
```

#### 4.2. API 클라이언트 생성 (`src/api/client.ts`)
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// JWT 토큰 인터셉터 (로그인 후 토큰 자동 추가)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### 4.3. API 호출 함수 (`src/api/employees.ts`)
```typescript
import { apiClient } from './client';

export interface Employee {
  id: string;
  name: string;
  team: string;
  position: string;
  email: string;
  phone: string;
  status: 'active' | 'vacation' | 'inactive';
  consultations: number;
  fcr: number;
  avg_time: string;
  rank: number;
  trend: 'up' | 'down' | 'same';
}

// 모든 사원 조회
export const getEmployees = async (): Promise<Employee[]> => {
  const { data } = await apiClient.get('/api/employees');
  return data;
};

// 특정 사원 조회
export const getEmployee = async (id: string): Promise<Employee> => {
  const { data } = await apiClient.get(`/api/employees/${id}`);
  return data;
};

// 사원 추가
export const createEmployee = async (employee: Partial<Employee>): Promise<Employee> => {
  const { data } = await apiClient.post('/api/employees', employee);
  return data;
};

// 사원 수정
export const updateEmployee = async (id: string, employee: Partial<Employee>): Promise<Employee> => {
  const { data } = await apiClient.put(`/api/employees/${id}`, employee);
  return data;
};

// 사원 삭제
export const deleteEmployee = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/employees/${id}`);
};
```

#### 4.4. React에서 API 사용 예시 (`EmployeesPage.tsx` 수정)
```typescript
import { useEffect, useState } from 'react';
import { getEmployees, Employee } from '../../api/employees';

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);

  // LocalStorage 대신 API 호출
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const data = await getEmployees();
        setEmployees(data);
      } catch (error) {
        console.error('Failed to fetch employees', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEmployees();
  }, []);

  if (loading) return <div>로딩 중...</div>;

  return (
    <MainLayout>
      {/* 기존 UI 코드 유지 */}
      <div className="employees-list">
        {employees.map(emp => (
          <div key={emp.id}>{emp.name}</div>
        ))}
      </div>
    </MainLayout>
  );
}
```

---

### **Step 5: 실시간 STT + RAG 칸반보드 연결 (WebSocket)**

#### 5.1. FastAPI WebSocket 엔드포인트
```python
from fastapi import WebSocket
import json

@app.websocket("/ws/consultation")
async def websocket_consultation(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # STT 음성 데이터 수신
            audio_data = await websocket.receive_bytes()
            
            # STT 처리 (음성 → 텍스트)
            transcript = await process_stt(audio_data)
            
            # RAG 기반 문서 검색 (pgvector)
            search_results = await search_documents(transcript)
            
            # 칸반보드 카드 생성
            kanban_card = {
                "category": classify_category(transcript),
                "documents": search_results,
                "transcript": transcript
            }
            
            # 클라이언트에 전송
            await websocket.send_json(kanban_card)
    except Exception as e:
        await websocket.close()
```

#### 5.2. React에서 WebSocket 연결
```typescript
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/consultation');

  ws.onmessage = (event) => {
    const kanbanCard = JSON.parse(event.data);
    // 칸반보드 업데이트
    setKanbanCards(prev => [...prev, kanbanCard]);
  };

  return () => ws.close();
}, []);
```

---

## 📊 데이터 마이그레이션 (LocalStorage → PostgreSQL)

### 1. 기존 LocalStorage 데이터 추출
```typescript
// 브라우저 콘솔에서 실행
const employees = JSON.parse(localStorage.getItem('employees'));
console.log(JSON.stringify(employees, null, 2));
```

### 2. 백엔드로 일괄 업로드
```python
import json

def migrate_employees():
    with open('employees.json', 'r') as f:
        employees = json.load(f)
    
    for emp in employees:
        new_employee = Employee(**emp)
        db.add(new_employee)
    
    db.commit()
```

---

## 🔒 보안 및 인증 (JWT)

### 1. 로그인 API
```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/api/auth/login")
def login(employee_id: str, password: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee or not verify_password(password, employee.hashed_password):
        raise HTTPException(status_code=401, detail="인증 실패")
    
    access_token = create_access_token(data={"sub": employee.id})
    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

## 🎯 최종 체크리스트

- [ ] PostgreSQL + pgvector 설치 완료
- [ ] FastAPI 서버 실행 (포트 8000)
- [ ] React 환경 변수 설정 (`VITE_API_URL`)
- [ ] CORS 설정 확인
- [ ] 데이터 마이그레이션 완료
- [ ] JWT 인증 구현
- [ ] WebSocket 연결 테스트
- [ ] pgvector RAG 검색 성능 테스트

---

## 📞 문의 및 지원

**이메일**: support@callact.com  
**Slack**: #callact-dev  
**문서**: https://docs.callact.com

---

**마지막 업데이트**: 2025-01-11  
**작성자**: CALL:ACT 개발팀
