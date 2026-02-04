# 녹취 파일 다운로드 이력 기록 시스템

## 📋 개요

CALL:ACT 시스템의 녹취 파일 다운로드 이력 자동 기록 시스템 설계 및 구현 가이드

**작성일:** 2025-01-23  
**Phase:** 12-1 (프론트엔드 localStorage 기반 구현)  
**향후 작업:** 백엔드 API 연동 (FastAPI + PostgreSQL)

---

## 🎯 목적

1. **법적 준수**: 금융권 녹취 파일 관리 의무 (5년 보관, 접근 기록)
2. **보안 강화**: 개인정보 포함 파일 다운로드 추적
3. **감사 추적**: 누가, 언제, 어떤 파일을 다운로드했는지 기록
4. **책임 소재**: 무단 유출 발생 시 책임자 특정

---

## 📊 시스템 아키텍처

### Phase 12-1: 프론트엔드 (현재 구현)

```
사용자 다운로드 클릭
    ↓
경고 모달 표시
    ↓
사용자 확인
    ↓
파일 다운로드 (Blob)
    ↓
⭐ localStorage에 로그 기록
    ↓
Toast 알림
```

**저장 위치:** `localStorage.downloadLogs`  
**저장 형식:** JSON Array  
**최대 보관:** 500개 (FIFO)

### Phase 12-2: 백엔드 연동 (향후 구현)

```
사용자 다운로드 클릭
    ↓
경고 모달 표시
    ↓
사용자 확인
    ↓
파일 다운로드 (S3/서버)
    ↓
⭐ POST /api/recordings/download-log
    ↓
PostgreSQL에 로그 INSERT
    ↓
Toast 알림
```

---

## 🗄️ 데이터베이스 스키마

### 1. recording_download_logs 테이블

```sql
CREATE TABLE recording_download_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  consultation_id VARCHAR(50) NOT NULL REFERENCES consultations(id),
  downloaded_by VARCHAR(50) NOT NULL REFERENCES employees(id),
  download_type VARCHAR(20) NOT NULL,      -- 'txt', 'wav', 'mp3'
  download_ip VARCHAR(45) NOT NULL,        -- IPv4/IPv6
  download_user_agent TEXT,                -- 브라우저 정보
  file_name VARCHAR(500) NOT NULL,         -- 다운로드 파일명
  file_path VARCHAR(500),                  -- 서버 파일 경로 (S3 등)
  file_size BIGINT,                        -- 바이트 단위
  downloaded_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- 인덱스
CREATE INDEX idx_download_logs_consultation 
  ON recording_download_logs(consultation_id, downloaded_at DESC);

CREATE INDEX idx_download_logs_employee 
  ON recording_download_logs(downloaded_by, downloaded_at DESC);

CREATE INDEX idx_download_logs_date 
  ON recording_download_logs(downloaded_at DESC);

-- 코멘트
COMMENT ON TABLE recording_download_logs IS '녹취 파일 다운로드 이력 (법적 의무 준수)';
COMMENT ON COLUMN recording_download_logs.download_ip IS '다운로드 시점 IP 주소 (감사용)';
COMMENT ON COLUMN recording_download_logs.downloaded_at IS '다운로드 시각 (UTC)';
```

### 2. audit_logs 테이블 (추가 감사)

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id VARCHAR(50) NOT NULL REFERENCES employees(id),
  action VARCHAR(100) NOT NULL,            -- 'RECORDING_DOWNLOAD', 'RECORDING_DELETE', etc.
  resource_type VARCHAR(50) NOT NULL,      -- 'consultation', 'recording', etc.
  resource_id VARCHAR(50) NOT NULL,        -- 'CS-EMP001-202501231432'
  ip_address VARCHAR(45) NOT NULL,
  user_agent TEXT,
  details JSONB,                           -- 추가 정보 (파일명, 크기 등)
  created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- 인덱스
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- 코멘트
COMMENT ON TABLE audit_logs IS '시스템 전체 감사 로그';
COMMENT ON COLUMN audit_logs.details IS '액션별 추가 정보 (JSON)';
```

---

## 💾 데이터 구조

### localStorage 저장 형식 (프론트엔드)

```typescript
interface DownloadLog {
  id: string;                          // UUID
  consultation_id: string;             // 'CS-EMP001-202501231432'
  consultation_category: string;       // '카드분실'
  customer_name: string;               // '김**' (마스킹)
  downloaded_by: string;               // 'EMP001'
  downloaded_by_name: string;          // '홍길동'
  download_type: 'txt' | 'wav' | 'mp3';
  file_name: string;                   // '녹취록_CS-EMP001-202501231432_2025-01-23.txt'
  file_size: number;                   // 2048 (bytes)
  download_ip: string;                 // 'localhost' (프론트엔드에서는 미지원)
  user_agent: string;                  // 'Mozilla/5.0 ...'
  downloaded_at: string;               // ISO 8601 형식 '2025-01-23T14:30:00.000Z'
}

// localStorage 저장
localStorage.setItem('downloadLogs', JSON.stringify(downloadLogs));
```

### DB 저장 예시 데이터

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "consultation_id": "CS-EMP001-202501231432",
  "downloaded_by": "EMP001",
  "download_type": "txt",
  "download_ip": "192.168.1.100",
  "download_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "file_name": "녹취록_CS-EMP001-202501231432_2025-01-23.txt",
  "file_path": "s3://call-act-recordings/2025/01/23/CS-EMP001-202501231432.txt",
  "file_size": 2048,
  "downloaded_at": "2025-01-23T14:30:00.000Z"
}
```

---

## 🚀 프론트엔드 구현 (현재)

### 1. 다운로드 로그 기록

**파일:** `/src/app/pages/AdminConsultationManagePage.tsx`

```typescript
const confirmInlineDownload = () => {
  if (!pendingDownloadConsultation) return;

  // 1. 파일 다운로드 실행
  const recordingText = `...`;
  const blob = new Blob([recordingText], { type: 'text/plain;charset=utf-8' });
  const fileName = `녹취록_${pendingDownloadConsultation.id}_${new Date().toISOString().split('T')[0]}.txt`;
  
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  // ⭐ 2. 다운로드 이력 기록
  try {
    const downloadLog = {
      id: crypto.randomUUID(),
      consultation_id: pendingDownloadConsultation.id,
      consultation_category: pendingDownloadConsultation.category,
      customer_name: pendingDownloadConsultation.customer,
      downloaded_by: 'EMP001',          // TODO: 실제 로그인 사용자
      downloaded_by_name: '홍길동',      // TODO: 실제 로그인 사용자
      download_type: 'txt',
      file_name: fileName,
      file_size: blob.size,
      download_ip: 'localhost',         // 프론트엔드에서는 알 수 없음
      user_agent: navigator.userAgent,
      downloaded_at: new Date().toISOString()
    };

    // 기존 로그 가져오기
    const existingLogs = JSON.parse(localStorage.getItem('downloadLogs') || '[]');
    
    // 새 로그 추가 (최신 로그가 앞에)
    existingLogs.unshift(downloadLog);
    
    // 저장 (최대 500개만 유지)
    localStorage.setItem('downloadLogs', JSON.stringify(existingLogs.slice(0, 500)));

    console.log('✅ 다운로드 이력 기록 완료:', downloadLog);
    showSuccess('녹취 파일이 다운로드되었습니다. 이력이 기록되었습니다.');
  } catch (error) {
    console.error('❌ 다운로드 이력 기록 실패:', error);
  }

  setPendingDownloadConsultation(null);
};
```

### 2. 로그 조회 (향후 UI 추가)

```typescript
// 다운로드 이력 조회
const getDownloadLogs = (): DownloadLog[] => {
  const logs = localStorage.getItem('downloadLogs');
  return logs ? JSON.parse(logs) : [];
};

// 특정 상담의 다운로드 이력 조회
const getConsultationDownloadHistory = (consultationId: string): DownloadLog[] => {
  const logs = getDownloadLogs();
  return logs.filter(log => log.consultation_id === consultationId);
};

// 특정 직원의 다운로드 이력 조회
const getEmployeeDownloadHistory = (employeeId: string): DownloadLog[] => {
  const logs = getDownloadLogs();
  return logs.filter(log => log.downloaded_by === employeeId);
};
```

---

## 🔌 백엔드 API 설계 (향후 구현)

### 1. POST /api/recordings/download-log

**요청 (Request)**

```typescript
POST /api/recordings/download-log
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}

{
  "consultation_id": "CS-EMP001-202501231432",
  "download_type": "txt",
  "file_name": "녹취록_CS-EMP001-202501231432_2025-01-23.txt"
}
```

**응답 (Response)**

```json
{
  "status": "logged",
  "log_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-23T14:30:00.000Z"
}
```

**FastAPI 구현 예시**

```python
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

class DownloadLogRequest(BaseModel):
    consultation_id: str
    download_type: str  # 'txt', 'wav', 'mp3'
    file_name: str

@router.post("/api/recordings/download-log")
async def log_recording_download(
    request: Request,
    data: DownloadLogRequest,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    # IP 주소 가져오기
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    
    # 상담 정보 조회 (권한 확인)
    consultation = await db.fetchrow("""
        SELECT employee_id, recording_file_path, recording_file_size
        FROM consultations
        WHERE id = $1
    """, data.consultation_id)
    
    if not consultation:
        raise HTTPException(status_code=404, detail="상담 정보를 찾을 수 없습니다")
    
    # 권한 확인: 본인 상담 또는 관리자만 가능
    if consultation['employee_id'] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="다운로드 권한이 없습니다")
    
    # ⭐ 다운로드 로그 기록
    log_id = str(uuid.uuid4())
    await db.execute("""
        INSERT INTO recording_download_logs (
            id, consultation_id, downloaded_by, download_type,
            download_ip, download_user_agent, file_name,
            file_path, file_size
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    """,
        log_id,
        data.consultation_id,
        current_user.id,
        data.download_type,
        client_ip,
        user_agent,
        data.file_name,
        consultation['recording_file_path'],
        consultation['recording_file_size']
    )
    
    # ⭐ 감사 로그 추가 기록
    await db.execute("""
        INSERT INTO audit_logs (
            user_id, action, resource_type, resource_id,
            ip_address, user_agent, details
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
    """,
        current_user.id,
        "RECORDING_DOWNLOAD",
        "consultation",
        data.consultation_id,
        client_ip,
        user_agent,
        json.dumps({
            "file_name": data.file_name,
            "download_type": data.download_type,
            "file_size": consultation['recording_file_size']
        })
    )
    
    return {
        "status": "logged",
        "log_id": log_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

### 2. GET /api/recordings/download-logs

**요청 (Request)**

```
GET /api/recordings/download-logs?consultation_id=CS-EMP001-202501231432&limit=50
Authorization: Bearer {JWT_TOKEN}
```

**응답 (Response)**

```json
{
  "logs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "consultation_id": "CS-EMP001-202501231432",
      "downloaded_by": "EMP001",
      "downloaded_by_name": "홍길동",
      "consultation_category": "카드분실",
      "download_type": "txt",
      "file_name": "녹취록_CS-EMP001-202501231432_2025-01-23.txt",
      "download_ip": "192.168.1.100",
      "downloaded_at": "2025-01-23T14:30:00.000Z"
    }
  ],
  "total": 1
}
```

**FastAPI 구현 예시**

```python
@router.get("/api/recordings/download-logs")
async def get_download_logs(
    consultation_id: Optional[str] = None,
    employee_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    # 관리자만 전체 로그 조회 가능
    if not current_user.is_admin and employee_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    query = """
        SELECT 
            rdl.*,
            e.name as downloaded_by_name,
            c.category as consultation_category
        FROM recording_download_logs rdl
        LEFT JOIN employees e ON rdl.downloaded_by = e.id
        LEFT JOIN consultations c ON rdl.consultation_id = c.id
        WHERE 1=1
    """
    params = []
    param_count = 0
    
    if consultation_id:
        param_count += 1
        query += f" AND rdl.consultation_id = ${param_count}"
        params.append(consultation_id)
    
    if employee_id:
        param_count += 1
        query += f" AND rdl.downloaded_by = ${param_count}"
        params.append(employee_id)
    
    if start_date:
        param_count += 1
        query += f" AND rdl.downloaded_at >= ${param_count}"
        params.append(start_date)
    
    if end_date:
        param_count += 1
        query += f" AND rdl.downloaded_at <= ${param_count}"
        params.append(end_date)
    
    param_count += 1
    query += f" ORDER BY rdl.downloaded_at DESC LIMIT ${param_count}"
    params.append(limit)
    
    logs = await db.fetch(query, *params)
    
    return {
        "logs": [dict(log) for log in logs],
        "total": len(logs)
    }
```

---

## 🔄 프론트엔드-백엔드 연동 가이드

### Step 1: API 유틸리티 생성

**파일:** `/src/utils/recordingDownloadAPI.ts`

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface DownloadLogPayload {
  consultation_id: string;
  download_type: 'txt' | 'wav' | 'mp3';
  file_name: string;
}

export async function logRecordingDownload(payload: DownloadLogPayload): Promise<void> {
  const token = localStorage.getItem('auth_token');
  
  const response = await fetch(`${API_BASE_URL}/api/recordings/download-log`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) {
    throw new Error(`다운로드 로그 기록 실패: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getDownloadLogs(filters?: {
  consultation_id?: string;
  employee_id?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
}): Promise<DownloadLog[]> {
  const token = localStorage.getItem('auth_token');
  const params = new URLSearchParams(filters as any);
  
  const response = await fetch(`${API_BASE_URL}/api/recordings/download-logs?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error(`다운로드 로그 조회 실패: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.logs;
}
```

### Step 2: 컴포넌트 수정

**파일:** `/src/app/pages/AdminConsultationManagePage.tsx`

```typescript
import { logRecordingDownload } from '@/utils/recordingDownloadAPI';

const confirmInlineDownload = async () => {
  if (!pendingDownloadConsultation) return;

  // 1. 파일 다운로드 실행
  // ... (기존 코드)

  // ⭐ 2. 백엔드 API 호출
  try {
    await logRecordingDownload({
      consultation_id: pendingDownloadConsultation.id,
      download_type: 'txt',
      file_name: fileName
    });
    
    console.log('✅ 다운로드 이력 기록 완료 (DB)');
    showSuccess('녹취 파일이 다운로드되었습니다. 이력이 기록되었습니다.');
  } catch (error) {
    console.error('❌ 다운로드 이력 기록 실패:', error);
    // Fallback: localStorage에 기록
    // ... (기존 localStorage 코드)
  }

  setPendingDownloadConsultation(null);
};
```

---

## 🔐 보안 고려사항

### 1. 권한 관리

```python
# 본인 상담 또는 관리자만 다운로드 가능
def check_download_permission(user: User, consultation: Consultation) -> bool:
    return user.is_admin or user.id == consultation.employee_id
```

### 2. IP 주소 기록

```python
# 실제 IP 가져오기 (Proxy 고려)
def get_client_ip(request: Request) -> str:
    # X-Forwarded-For 헤더 확인 (프록시 환경)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host
```

### 3. 개인정보 마스킹

```typescript
// 로그 조회 시 고객 이름 마스킹
const maskCustomerName = (name: string): string => {
  if (name.length <= 1) return name;
  return name[0] + '*'.repeat(name.length - 1);
};
```

---

## 📈 모니터링 및 알림

### 1. 이상 다운로드 감지

```sql
-- 1시간 내 동일 사용자가 10건 이상 다운로드
SELECT 
  downloaded_by,
  COUNT(*) as download_count,
  MAX(downloaded_at) as last_download
FROM recording_download_logs
WHERE downloaded_at >= NOW() - INTERVAL '1 hour'
GROUP BY downloaded_by
HAVING COUNT(*) >= 10;
```

### 2. 일일 다운로드 통계

```sql
-- 일별 다운로드 건수
SELECT 
  DATE(downloaded_at) as download_date,
  COUNT(*) as total_downloads,
  COUNT(DISTINCT downloaded_by) as unique_users
FROM recording_download_logs
WHERE downloaded_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(downloaded_at)
ORDER BY download_date DESC;
```

---

## 🧪 테스트 시나리오

### 1. 단위 테스트 (프론트엔드)

```typescript
describe('Download Log', () => {
  it('should save download log to localStorage', () => {
    const log = {
      consultation_id: 'CS-EMP001-202501231432',
      downloaded_by: 'EMP001',
      download_type: 'txt'
    };
    
    // localStorage에 저장
    saveDownloadLog(log);
    
    // 검증
    const logs = getDownloadLogs();
    expect(logs).toContainEqual(expect.objectContaining(log));
  });
});
```

### 2. API 테스트 (백엔드)

```python
async def test_log_recording_download():
    response = await client.post(
        "/api/recordings/download-log",
        json={
            "consultation_id": "CS-EMP001-202501231432",
            "download_type": "txt",
            "file_name": "녹취록_CS-EMP001-202501231432_2025-01-23.txt"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "logged"
    
    # DB 확인
    log = await db.fetchrow("""
        SELECT * FROM recording_download_logs
        WHERE consultation_id = $1
    """, "CS-EMP001-202501231432")
    
    assert log is not None
    assert log["downloaded_by"] == "EMP001"
```

---

## 📝 TODO 체크리스트

### Phase 12-1: 프론트엔드 (완료)

- [x] localStorage 기반 로그 저장 구현
- [x] 다운로드 시 자동 로그 기록
- [x] Toast 알림 표시
- [ ] 관리자 UI: 다운로드 이력 조회 페이지

### Phase 12-2: 백엔드 연동 (예정)

- [ ] DB 테이블 생성 (`recording_download_logs`, `audit_logs`)
- [ ] FastAPI 엔드포인트 구현 (`POST /api/recordings/download-log`)
- [ ] FastAPI 엔드포인트 구현 (`GET /api/recordings/download-logs`)
- [ ] 권한 검사 미들웨어
- [ ] IP 주소 자동 추출
- [ ] 프론트엔드 API 연동

### Phase 12-3: 고도화 (선택)

- [ ] 이상 다운로드 감지 알림
- [ ] 일일/주간 다운로드 통계 대시보드
- [ ] CSV/Excel 내보내기
- [ ] 다운로드 승인 워크플로우 (민감 파일)

---

## 🔗 관련 문서

- [DB 스키마 설계](/docs/database-schema.md)
- [API 명세서](/docs/api-specification.md)
- [보안 정책](/docs/security-policy.md)
- [감사 로그 가이드](/docs/audit-log-guide.md)

---

## ✅ 최종 체크

**현재 상태 (Phase 12-1):**
- ✅ 프론트엔드 localStorage 기반 로그 기록 완료
- ✅ 다운로드 시 경고 모달 표시
- ✅ 로그 데이터 구조 정의
- ⏳ 백엔드 API 연동 대기 (Phase 12-2)

**다음 단계:**
1. DB 테이블 생성 (PostgreSQL)
2. FastAPI 엔드포인트 구현
3. 프론트엔드 API 호출로 전환
4. 관리자 로그 조회 UI 구현

---

**문서 버전:** 1.0.0  
**최종 수정:** 2025-01-23  
**작성자:** CALL:ACT Development Team
