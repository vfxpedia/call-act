# Phase 11-3: 녹취 파일 관리 종합 가이드

## 📋 작업 개요

**목적:** 녹취 파일(WAV) 및 텍스트 녹취록(TXT) 관리 체계 구축

**작업 일자:** 2025-01-23  
**Phase:** 11-3  
**상태:** ✅ **완료 (프론트엔드) + 📝 백엔드 설계**

---

## 🎯 질문 & 답변

### Q1. 녹취 파일 형식: TXT vs WAV?

**A: 둘 다 필요합니다!**

| 형식 | 용도 | 저장 위치 | 다운로드 |
|------|------|-----------|----------|
| **WAV** | • 법적 증거 자료<br>• 상담 품질 평가<br>• 교육 시뮬레이션<br>• 감독/모니터링 | S3/MinIO<br>(오브젝트 스토리지) | ✅ 가능 |
| **TXT** | • 빠른 검색/조회<br>• STT 변환 결과<br>• 텍스트 분석<br>• 보고서 생성 | PostgreSQL<br>(TEXT 컬럼) | ✅ 가능 |

---

### Q2. 백그라운드 실시간 녹음 저장?

**A: 반드시 필요합니다!**

#### ❌ 프론트엔드에서만 저장 시 문제점

```
❌ 브라우저 강제 종료 → 데이터 손실
❌ 네트워크 끊김 → 녹음 유실
❌ 메모리 부족 → 저장 실패
❌ 사용자 실수로 탭 닫기 → 복구 불가
```

#### ✅ 백엔드 실시간 저장 (권장)

```
1. WebRTC로 음성 스트리밍
2. 백엔드 서버에서 실시간 녹음
3. 5초마다 청크 단위 임시 저장
4. 통화 종료 시 청크 병합 → 최종 WAV 생성
5. S3 업로드 후 임시 파일 삭제
```

---

### Q3. DB에 WAV 파일 저장?

**A: 오브젝트 스토리지 사용 + DB에는 경로만 저장 (권장)**

#### ❌ DB에 직접 저장 시 문제점

```
❌ DB 크기 급증 (1건당 5-10MB)
   → 1,000건 = 5-10GB
   → 10,000건 = 50-100GB

❌ 쿼리 성능 저하
   → SELECT 시 대용량 BLOB 로드
   → 인덱스 크기 증가

❌ 백업/복구 시간 증가
   → 전체 백업 수 GB ~ 수십 GB

❌ 비용 증가
   → DB 스토리지 비용 > S3 비용
```

#### ✅ 오브젝트 스토리지 사용 (권장)

```
✅ 무제한 확장 가능
✅ CDN 연동 가능
✅ 저렴한 비용 (S3: $0.023/GB/월)
✅ DB는 경로만 저장 (50바이트)
✅ 파일 다운로드 속도 빠름
```

---

### Q4. 상담관리 페이지 인라인 다운로드?

**A: ✅ 구현 완료!**

- 인라인 플레이어 우측에 다운로드 버튼 추가
- 클릭 시 녹취록 텍스트 파일(.txt) 다운로드

---

## 🏗️ 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────┐
│          사용자 (상담사/관리자)               │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│     프론트엔드 (React + WebRTC)              │
│  • 음성 스트리밍                              │
│  • STT 실시간 표시                            │
│  • 다운로드 버튼                              │
└────────────┬────────────────────────────────┘
             │ WebSocket/WebRTC
             ▼
┌─────────────────────────────────────────────┐
│     백엔드 (FastAPI)                         │
│  • WebRTC 시그널링 서버                       │
│  • 실시간 녹음 (청크 단위)                    │
│  • STT API 호출 (Google/AWS/Azure)           │
│  • 파일 병합 및 업로드                        │
└─────┬──────────────────────┬────────────────┘
      │                      │
      │ 저장                 │ 저장
      ▼                      ▼
┌──────────────┐     ┌──────────────────┐
│  PostgreSQL  │     │  S3/MinIO        │
│              │     │  (오브젝트 저장)  │
│  • 경로 저장 │     │  • WAV 파일      │
│  • TXT 저장  │     │  • 메타데이터    │
└──────────────┘     └──────────────────┘
```

---

## 📂 파일 저장 구조

### S3 버킷 구조

```
s3://call-act-recordings/
├── 2025/
│   ├── 01/
│   │   ├── 23/
│   │   │   ├── CS-EMP001-202501231432.wav           (원본 음성)
│   │   │   ├── CS-EMP001-202501231432.txt           (텍스트 녹취록)
│   │   │   ├── CS-EMP001-202501231432_metadata.json (메타데이터)
│   │   │   └── CS-EMP001-202501231432_chunks/       (임시 청크)
│   │   │       ├── chunk_001.wav
│   │   │       ├── chunk_002.wav
│   │   │       └── ...
│   │   └── 24/
│   └── 02/
└── temp/                                            (임시 녹음 중)
    └── CS-EMP002-202501231530_chunks/
        ├── chunk_001.wav
        ├── chunk_002.wav
        └── ...
```

### 메타데이터 구조 (JSON)

```json
{
  "consultation_id": "CS-EMP001-202501231432",
  "employee_id": "EMP001",
  "customer_id": "CUST-TEDDY-00001",
  "recording": {
    "start_time": "2025-01-23T14:32:15Z",
    "end_time": "2025-01-23T14:37:42Z",
    "duration_seconds": 327,
    "file_path": "s3://call-act-recordings/2025/01/23/CS-EMP001-202501231432.wav",
    "file_size_bytes": 5242880,
    "format": "wav",
    "sample_rate": 16000,
    "channels": 1,
    "bitrate": 128000
  },
  "transcript": {
    "file_path": "s3://call-act-recordings/2025/01/23/CS-EMP001-202501231432.txt",
    "stt_provider": "Google Cloud Speech-to-Text",
    "confidence": 0.95,
    "language": "ko-KR"
  },
  "processing": {
    "status": "completed",
    "chunks_count": 65,
    "merged_at": "2025-01-23T14:37:50Z"
  }
}
```

---

## 🗄️ 데이터베이스 스키마

### consultations 테이블 (확장)

```sql
CREATE TABLE consultations (
  id VARCHAR(50) PRIMARY KEY,
  employee_id VARCHAR(50) REFERENCES employees(id),
  customer_id VARCHAR(50) REFERENCES customers(id),
  
  -- 기존 컬럼들
  category VARCHAR(100),
  status VARCHAR(20),
  fcr BOOLEAN DEFAULT FALSE,
  is_best_practice BOOLEAN DEFAULT FALSE,
  
  -- ⭐ 녹음 파일 정보 (신규)
  recording_file_path VARCHAR(500),              -- S3 URL (WAV)
  recording_file_size BIGINT,                    -- 파일 크기 (bytes)
  recording_duration INT,                        -- 통화 시간 (초)
  recording_format VARCHAR(10) DEFAULT 'wav',    -- 파일 형식
  recording_sample_rate INT DEFAULT 16000,       -- 샘플링 레이트
  recording_channels INT DEFAULT 1,              -- 채널 (1=모노, 2=스테레오)
  recording_bitrate INT DEFAULT 128000,          -- 비트레이트
  
  -- ⭐ STT 녹취록 (신규)
  recording_transcript TEXT,                     -- 텍스트 녹취록 전문
  recording_transcript_path VARCHAR(500),        -- TXT 파일 S3 URL
  stt_provider VARCHAR(50),                      -- STT 서비스 제공자
  stt_confidence DECIMAL(3,2),                   -- STT 신뢰도 (0.00-1.00)
  
  -- ⭐ 메타데이터 (신규)
  recording_metadata JSONB,                      -- 전체 메타데이터 JSON
  
  -- ⭐ 녹음 상태 (신규)
  recording_status VARCHAR(20) DEFAULT 'pending', -- 'recording', 'processing', 'completed', 'failed'
  recording_started_at TIMESTAMP,
  recording_ended_at TIMESTAMP,
  recording_processed_at TIMESTAMP,
  
  -- 기존 컬럼들
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_consultations_recording_status ON consultations(recording_status);
CREATE INDEX idx_consultations_recording_date ON consultations(DATE(recording_started_at));
CREATE INDEX idx_consultations_employee_recording ON consultations(employee_id, recording_started_at DESC);
```

### recording_chunks 테이블 (임시 청크 관리)

```sql
CREATE TABLE recording_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  consultation_id VARCHAR(50) REFERENCES consultations(id) ON DELETE CASCADE,
  
  chunk_index INT NOT NULL,                      -- 청크 순서 (1, 2, 3, ...)
  chunk_file_path VARCHAR(500),                  -- S3 임시 경로
  chunk_duration INT,                            -- 청크 길이 (초)
  chunk_size BIGINT,                             -- 청크 크기 (bytes)
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(consultation_id, chunk_index)
);

-- 인덱스
CREATE INDEX idx_recording_chunks_consultation ON recording_chunks(consultation_id, chunk_index);
```

---

## 🔄 실시간 녹음 프로세스

### 1. 통화 시작

```typescript
// 프론트엔드 (React)
const startRecording = async () => {
  // WebRTC 연결
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  
  // 백엔드 시그널링
  const response = await fetch('/api/consultations/start', {
    method: 'POST',
    body: JSON.stringify({
      employee_id: 'EMP001',
      customer_id: 'CUST-TEDDY-00001',
    }),
  });
  
  const { consultation_id, websocket_url } = await response.json();
  
  // WebSocket 연결
  const ws = new WebSocket(websocket_url);
  
  // 음성 스트리밍 시작
  const mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = (event) => {
    ws.send(event.data); // 실시간 전송
  };
  mediaRecorder.start(5000); // 5초마다 청크 전송
};
```

```python
# 백엔드 (FastAPI)
@app.post("/api/consultations/start")
async def start_consultation(data: ConsultationStart):
    consultation_id = generate_consultation_id()
    
    # DB에 초기 레코드 생성
    await db.execute("""
        INSERT INTO consultations (id, employee_id, customer_id, recording_status, recording_started_at)
        VALUES ($1, $2, $3, 'recording', NOW())
    """, consultation_id, data.employee_id, data.customer_id)
    
    # WebSocket URL 생성
    websocket_url = f"wss://api.call-act.com/ws/recording/{consultation_id}"
    
    return {"consultation_id": consultation_id, "websocket_url": websocket_url}
```

---

### 2. 실시간 청크 저장

```python
# 백엔드 WebSocket 핸들러
@app.websocket("/ws/recording/{consultation_id}")
async def recording_websocket(websocket: WebSocket, consultation_id: str):
    await websocket.accept()
    chunk_index = 1
    
    while True:
        # 클라이언트로부터 음성 청크 수신
        audio_chunk = await websocket.receive_bytes()
        
        # S3에 임시 저장
        chunk_path = f"temp/{consultation_id}/chunk_{chunk_index:03d}.wav"
        await s3.upload_bytes(audio_chunk, chunk_path)
        
        # DB에 청크 정보 저장
        await db.execute("""
            INSERT INTO recording_chunks (consultation_id, chunk_index, chunk_file_path, chunk_size)
            VALUES ($1, $2, $3, $4)
        """, consultation_id, chunk_index, chunk_path, len(audio_chunk))
        
        # STT 처리 (비동기)
        asyncio.create_task(process_stt(audio_chunk, consultation_id, chunk_index))
        
        chunk_index += 1
```

---

### 3. 통화 종료 및 병합

```python
# 백엔드 (FastAPI)
@app.post("/api/consultations/{consultation_id}/end")
async def end_consultation(consultation_id: str):
    # 1. 상태 업데이트
    await db.execute("""
        UPDATE consultations
        SET recording_status = 'processing', recording_ended_at = NOW()
        WHERE id = $1
    """, consultation_id)
    
    # 2. 청크 가져오기
    chunks = await db.fetch("""
        SELECT chunk_file_path FROM recording_chunks
        WHERE consultation_id = $1
        ORDER BY chunk_index
    """, consultation_id)
    
    # 3. WAV 파일 병합
    merged_wav = await merge_wav_chunks([c['chunk_file_path'] for c in chunks])
    
    # 4. 최종 파일 S3 업로드
    date = datetime.now()
    final_path = f"{date.year}/{date.month:02d}/{date.day:02d}/{consultation_id}.wav"
    await s3.upload_file(merged_wav, final_path)
    
    # 5. 메타데이터 생성
    metadata = {
        "consultation_id": consultation_id,
        "recording": {
            "file_path": f"s3://call-act-recordings/{final_path}",
            "duration_seconds": calculate_duration(merged_wav),
            "file_size_bytes": len(merged_wav),
        }
    }
    
    # 6. DB 업데이트
    await db.execute("""
        UPDATE consultations
        SET recording_file_path = $1,
            recording_file_size = $2,
            recording_duration = $3,
            recording_status = 'completed',
            recording_processed_at = NOW(),
            recording_metadata = $4
        WHERE id = $5
    """, metadata['recording']['file_path'],
        metadata['recording']['file_size_bytes'],
        metadata['recording']['duration_seconds'],
        json.dumps(metadata),
        consultation_id)
    
    # 7. 임시 청크 삭제
    await s3.delete_folder(f"temp/{consultation_id}")
    await db.execute("DELETE FROM recording_chunks WHERE consultation_id = $1", consultation_id)
    
    return {"status": "completed", "file_path": final_path}
```

---

## 📥 다운로드 기능

### 현재 구현 (프론트엔드)

#### 1. 상담 상세 모달 다운로드

```typescript
// ConsultationDetailModal.tsx
const handleDownloadRecording = () => {
  const recordingText = `
[CALL:ACT 녹취록]
========================================
상담 ID: ${consultation.id}
상담사: ${consultation.agent}
고객: ${detailData.customerName}
...
  `.trim();

  const blob = new Blob([recordingText], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `녹취록_${consultation.id}_${new Date().toISOString().split('T')[0]}.txt`;
  link.click();
  URL.revokeObjectURL(url);
};
```

#### 2. 상담관리 인라인 플레이어 다운로드 ✅ (신규)

```typescript
// AdminConsultationManagePage.tsx
const handleInlineDownload = (consultation: any) => {
  const recordingText = `
[CALL:ACT 녹취록]
========================================
상담 ID: ${consultation.id}
상담사: ${consultation.agent}
고객: ${consultation.customer}
카테고리: ${consultation.category}
...
  `.trim();

  const blob = new Blob([recordingText], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `녹취록_${consultation.id}_${new Date().toISOString().split('T')[0]}.txt`;
  link.click();
  URL.revokeObjectURL(url);
};
```

**UI 위치:**
```
인라인 플레이어:
[▶] ━━━━━━━━━━ 2:15 / 5:27 [↓] [1x▼]
                              ↑
                         다운로드 버튼
```

---

### 향후 구현 (백엔드 연동)

#### WAV 파일 다운로드

```python
# 백엔드 (FastAPI)
@app.get("/api/consultations/{consultation_id}/recording/download")
async def download_recording(consultation_id: str, format: str = "wav"):
    # 1. DB에서 파일 경로 가져오기
    consultation = await db.fetchrow("""
        SELECT recording_file_path, recording_transcript_path
        FROM consultations
        WHERE id = $1
    """, consultation_id)
    
    if format == "wav":
        file_path = consultation['recording_file_path']
    elif format == "txt":
        file_path = consultation['recording_transcript_path']
    else:
        raise HTTPException(400, "Invalid format")
    
    # 2. S3에서 파일 가져오기
    file_data = await s3.download_file(file_path)
    
    # 3. 다운로드 응답
    return Response(
        content=file_data,
        media_type="audio/wav" if format == "wav" else "text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={consultation_id}.{format}"
        }
    )
```

```typescript
// 프론트엔드 (React)
const handleDownloadWAV = async (consultationId: string) => {
  const response = await fetch(`/api/consultations/${consultationId}/recording/download?format=wav`);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `녹취_${consultationId}.wav`;
  link.click();
  URL.revokeObjectURL(url);
};
```

---

## 📊 비용 산정

### S3 스토리지 비용

**가정:**
- 1통화 = 5분 = 5MB (WAV)
- 1일 1,000통화
- 1년 보관

**계산:**
```
월간 저장량: 1,000통화 × 5MB × 30일 = 150GB
S3 비용: 150GB × $0.023/GB/월 = $3.45/월

연간 저장량: 150GB × 12개월 = 1,800GB
S3 비용: 1,800GB × $0.023/GB/월 = $41.40/월
```

**비교:**
- PostgreSQL RDS (db.t3.medium, 100GB SSD): $50/월
- S3 (1,800GB): $41.40/월
- **→ S3가 훨씬 저렴!**

---

## 🔒 보안 및 권한

### 파일 접근 권한

```python
# 백엔드 권한 체크
@app.get("/api/consultations/{consultation_id}/recording/download")
async def download_recording(
    consultation_id: str,
    current_user: User = Depends(get_current_user)
):
    # 1. 상담 권한 확인
    consultation = await db.fetchrow("""
        SELECT employee_id FROM consultations WHERE id = $1
    """, consultation_id)
    
    # 2. 본인 상담 또는 관리자만 다운로드 가능
    if consultation['employee_id'] != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "접근 권한이 없습니다")
    
    # 3. 다운로드 로그 기록
    await db.execute("""
        INSERT INTO recording_access_logs (consultation_id, accessed_by, action)
        VALUES ($1, $2, 'download')
    """, consultation_id, current_user.id)
    
    # 4. 파일 다운로드
    ...
```

### S3 Presigned URL (권장)

```python
# S3 임시 다운로드 링크 생성 (1시간 유효)
@app.get("/api/consultations/{consultation_id}/recording/presigned-url")
async def get_presigned_url(consultation_id: str):
    # 권한 확인
    ...
    
    # S3 Presigned URL 생성
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'call-act-recordings', 'Key': file_path},
        ExpiresIn=3600  # 1시간
    )
    
    return {"download_url": url, "expires_in": 3600}
```

---

## 📝 TODO 체크리스트

### Phase 11-3 (완료)
- [x] 상담 상세 모달 다운로드 기능 구현
- [x] 상담관리 인라인 플레이어 다운로드 구현
- [x] 녹취록 텍스트 포맷 정의
- [x] 파일명 규칙 정의

### Phase 12 (백엔드 구현)
- [ ] WebRTC 시그널링 서버 구축
- [ ] 실시간 음성 스트리밍 수신
- [ ] 청크 단위 임시 저장 (S3)
- [ ] 통화 종료 시 청크 병합
- [ ] STT API 연동 (Google/AWS/Azure)
- [ ] DB 스키마 적용 (consultations, recording_chunks)
- [ ] S3 버킷 생성 및 권한 설정
- [ ] WAV 파일 다운로드 API
- [ ] Presigned URL 생성 API
- [ ] 접근 로그 기록

### Phase 13 (고급 기능)
- [ ] 녹음 품질 자동 평가 (음량, 노이즈)
- [ ] 음성 압축 (FLAC, MP3 옵션)
- [ ] 다중 채널 녹음 (상담사/고객 분리)
- [ ] 실시간 STT 결과 표시 (프론트엔드)
- [ ] 녹취록 편집 기능
- [ ] 키워드 하이라이팅
- [ ] 감정 분석 (Sentiment Analysis)

---

## 🚀 다음 단계

### 우선순위 1: 백엔드 녹음 인프라
1. WebRTC 시그널링 서버
2. 청크 단위 실시간 저장
3. S3 버킷 설정

### 우선순위 2: STT 연동
1. Google Cloud Speech-to-Text API
2. 실시간 텍스트 변환
3. DB 저장

### 우선순위 3: 다운로드 API
1. WAV 다운로드 엔드포인트
2. TXT 다운로드 엔드포인트
3. Presigned URL 생성

---

## 📚 참고 자료

- [WebRTC 공식 문서](https://webrtc.org/)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [AWS S3 Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [FFmpeg WAV 병합](https://ffmpeg.org/ffmpeg-formats.html#concat)

---

**작성자:** AI Assistant  
**마지막 업데이트:** 2025-01-23  
**Phase:** 11-3  
**상태:** ✅ 프론트엔드 완료 + 📝 백엔드 설계
