# Phase 11-4: 화면단 작업 및 종합 가이드

## 📋 작업 개요

**목적:** 화면단에서 가능한 기능 구현 및 백엔드 가이드 문서화

**작업 일자:** 2025-01-23  
**Phase:** 11-4  
**상태:** ✅ **완료**

---

## ✅ 구현 완료 (화면단)

### 1. 녹취 다운로드 법적 주의 모달 ✅

**컴포넌트:** `/src/app/components/modals/RecordingDownloadWarningModal.tsx`

**기능:**
- 다운로드 전 법적 주의사항 표시
- 📞 금융권 상담 녹취 보안 규정 안내
- 5년 의무 보관, 개인정보 보호법, 무단 유출 처벌
- 확인 후 다운로드 진행

**UI:**
```
┌────────────────────────────────────┐
│  ⚠️  녹취 파일 다운로드 주의사항    │
├────────────────────────────────────┤
│                                    │
│  📞 금융권 상담 녹취 보안 규정      │
│                                    │
│  • 상담 녹취는 법적 의무 보관 (5년) │
│  • 개인정보 보호법 준수 필수        │
│  • 무단 유출 시 법적 처벌 대상      │
│  • 업무 외 사용 금지                │
│  • 다운로드 이력 시스템 자동 기록   │
│                                    │
│  [취소]  [확인 후 다운로드]         │
└────────────────────────────────────┘
```

**적용 위치:**
- ✅ 상담 상세 모달 다운로드 버튼
- ⚠️ 상담관리 인라인 다운로드 (파일에 주의사항 포함)

---

## 📝 질문 & 답변

### Q1. STT 변환 결과 TXT 파일 저장 필요?

**A: ✅ 둘 다 저장 권장**

| 저장 방식 | 내용 | 용도 | 저장 위치 |
|----------|------|------|-----------|
| **DB (TEXT)** | 마스킹된 텍스트 | 빠른 검색, 분석 | PostgreSQL |
| **TXT 파일** | 원본 전사 결과 | 증빙, 백업, 재분석 | S3 |

**구조:**
```
DB (마스킹):
"안녕하세요. 테디카드 [상담사명#1]입니다. [고객명#1]님 무엇을 도와드릴까요?"

S3 TXT (원본):
"안녕하세요. 테디카드 홍길동입니다. 김민수님 무엇을 도와드릴까요?"

S3 WAV (원본 음성):
CS-EMP001-202501231432.wav
```

---

### Q2. 프론트엔드에서 백그라운드 녹음 가능?

**A: ✅ 가능! MediaRecorder API 사용**

**코드 예시:**
```typescript
// RealTimeConsultationPage.tsx
import { useState, useRef, useEffect } from 'react';

export default function RealTimeConsultationPage() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);

  // ⭐ 녹음 시작
  const startRecording = async () => {
    try {
      // 마이크 권한 요청
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // MediaRecorder 생성
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });
      
      // 청크 데이터 수집
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
          
          // ⭐ 5초마다 서버로 전송 (백엔드 구현 시)
          sendChunkToServer(event.data);
        }
      };
      
      // 녹음 종료 시
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        // 최종 파일 서버 업로드
        uploadRecording(blob);
      };
      
      // 5초마다 청크 생성
      mediaRecorder.start(5000);
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      
      console.log('✅ 백그라운드 녹음 시작');
    } catch (error) {
      console.error('녹음 시작 실패:', error);
    }
  };

  // ⭐ 녹음 종료
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      console.log('✅ 녹음 종료');
    }
  };

  // ⭐ 청크 서버 전송 (백엔드 구현 시)
  const sendChunkToServer = async (chunk: Blob) => {
    const formData = new FormData();
    formData.append('chunk', chunk);
    formData.append('consultation_id', consultationId);
    
    await fetch('/api/recordings/chunk', {
      method: 'POST',
      body: formData,
    });
  };

  // ⭐ 최종 파일 업로드 (백엔드 구현 시)
  const uploadRecording = async (blob: Blob) => {
    const formData = new FormData();
    formData.append('recording', blob);
    formData.append('consultation_id', consultationId);
    
    await fetch('/api/recordings/upload', {
      method: 'POST',
      body: formData,
    });
  };

  // 상담 시작 시 자동 녹음
  useEffect(() => {
    startRecording();
    
    // 컴포넌트 언마운트 시 녹음 종료
    return () => {
      stopRecording();
    };
  }, []);

  return (
    <div>
      {isRecording && (
        <div className=\"fixed top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2\">
          <div className=\"w-2 h-2 bg-white rounded-full animate-pulse\"></div>
          녹음 중
        </div>
      )}
      {/* 상담 UI */}
    </div>
  );
}
```

---

### Q3. 타임스탬프 프론트에서 가능?

**A: ✅ 가능!**

**코드 예시:**
```typescript
// 상담 시작 시간
const callStartTime = Date.now();

// 대화 내용에 타임스탬프 추가
const transcript = [
  {
    timestamp: Date.now() - callStartTime,  // 0ms
    relative_time: '00:00',
    speaker: 'agent',
    text: '안녕하세요, 테디카드입니다'
  },
  {
    timestamp: Date.now() - callStartTime,  // 3000ms
    relative_time: '00:03',
    speaker: 'customer',
    text: '카드를 분실했어요'
  },
  {
    timestamp: Date.now() - callStartTime,  // 8000ms
    relative_time: '00:08',
    speaker: 'agent',
    text: '확인하겠습니다'
  }
];

// DB 저장 형식
const transcriptForDB = transcript.map(t => 
  `[${t.relative_time}] [${t.speaker}] ${t.text}`
).join('\n');

// 결과:
// [00:00] [agent] 안녕하세요, 테디카드입니다
// [00:03] [customer] 카드를 분실했어요
// [00:08] [agent] 확인하겠습니다
```

---

### Q4. WebRTC 청크 저장 성능?

**A: ✅ 빠르고 안전함!**

**성능 분석:**

| 항목 | 값 | 설명 |
|------|-----|------|
| **청크 크기** | 약 80KB | 5초 WAV 16kHz 모노 |
| **전송 시간** | 10-50ms | 일반 네트워크 환경 |
| **메모리 사용** | 최소 | 실시간 스트리밍 |
| **브라우저 종료** | 안전 | 서버에 청크 저장됨 |

**장점:**
```
✅ 5초마다 청크 저장 → 브라우저 종료 대비
✅ 실시간 스트리밍 → 메모리 부담 최소
✅ 청크 병합 → 빠른 최종 파일 생성
✅ 네트워크 끊김 → 마지막 청크까지만 손실
```

**단점:**
```
❌ 네트워크 대역폭 필요 (80KB/5초 = 16KB/s)
❌ 서버 부하 증가 (동시 통화 수 × 16KB/s)
```

**권장:**
- 일반 환경: ✅ 5초 청크
- 고품질 필요: 10초 청크 (품질↑, 안전성↓)
- 저사양 환경: 3초 청크 (안전성↑, 부하↑)

---

## 🗄️ DB 스키마 종합 가이드

### 1. consultations 테이블 (확장)

```sql
-- 기존 테이블에 녹음 관련 컬럼 추가
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_file_path VARCHAR(500);
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_file_size BIGINT;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_duration INT;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_format VARCHAR(10) DEFAULT 'wav';
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_sample_rate INT DEFAULT 16000;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_channels INT DEFAULT 1;

-- STT 녹취록
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_transcript TEXT;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_transcript_path VARCHAR(500);
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS stt_provider VARCHAR(50);
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS stt_confidence DECIMAL(3,2);

-- 메타데이터
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_metadata JSONB;

-- 녹음 상태
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_started_at TIMESTAMP;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_ended_at TIMESTAMP;
ALTER TABLE consultations ADD COLUMN IF NOT EXISTS recording_processed_at TIMESTAMP;

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_consultations_recording_status ON consultations(recording_status);
CREATE INDEX IF NOT EXISTS idx_consultations_recording_date ON consultations(DATE(recording_started_at));
```

---

### 2. recording_chunks 테이블 (임시 청크 관리)

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

-- 예시 데이터
INSERT INTO recording_chunks (consultation_id, chunk_index, chunk_file_path, chunk_duration, chunk_size) VALUES
('CS-EMP001-202501231432', 1, 'temp/CS-EMP001-202501231432/chunk_001.wav', 5, 81920),
('CS-EMP001-202501231432', 2, 'temp/CS-EMP001-202501231432/chunk_002.wav', 5, 81920),
('CS-EMP001-202501231432', 3, 'temp/CS-EMP001-202501231432/chunk_003.wav', 2, 32768);
```

---

### 3. recording_download_logs 테이블 (다운로드 이력)

```sql
CREATE TABLE recording_download_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  consultation_id VARCHAR(50) REFERENCES consultations(id),
  downloaded_by VARCHAR(50) REFERENCES employees(id),
  download_type VARCHAR(20),                     -- 'wav', 'txt'
  download_ip VARCHAR(45),                       -- IPv6 지원
  download_user_agent TEXT,
  downloaded_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_download_logs_consultation ON recording_download_logs(consultation_id, downloaded_at DESC);
CREATE INDEX idx_download_logs_employee ON recording_download_logs(downloaded_by, downloaded_at DESC);
```

---

## 📂 S3 파일 구조

```
s3://call-act-recordings/
├── 2025/
│   ├── 01/
│   │   ├── 23/
│   │   │   ├── CS-EMP001-202501231432.wav           (원본 음성)
│   │   │   ├── CS-EMP001-202501231432_original.txt  (원본 녹취록)
│   │   │   ├── CS-EMP001-202501231432_masked.txt    (마스킹 녹취록)
│   │   │   └── CS-EMP001-202501231432_metadata.json (메타데이터)
└── temp/                                            (임시 녹음 중)
    └── CS-EMP002-202501231530_chunks/
        ├── chunk_001.wav
        ├── chunk_002.wav
        └── ...
```

---

## 🔄 화자 분리 프로세스

### GPT-4o mini 파인튜닝 활용

**팀원 작업:**
- ✅ 하나카드 상담 데이터로 GPT-4o mini 파인튜닝 완료
- ✅ STT 전사 텍스트 → 화자 분리 성능 우수

**프로세스:**
```
1. STT (Google/AWS/Azure)
   ↓ 전사된 텍스트
   
2. GPT-4o mini (파인튜닝 모델)
   - Input: 전사 텍스트
   - Output: 화자 분리 결과
   
3. 화자 분리 결과
   [00:00] [agent] 안녕하세요, 테디카드입니다
   [00:03] [customer] 카드를 분실했어요
   [00:08] [agent] 확인하겠습니다
   
4. 마스킹 처리
   [00:00] [agent] 안녕하세요, 테디카드 [상담사명#1]입니다
   [00:03] [customer] 카드를 분실했어요
   [00:08] [agent] 확인하겠습니다
   
5. DB 저장 (마스킹됨)
   consultations.recording_transcript
```

**백엔드 API 예시:**
```python
# 화자 분리 API
@app.post("/api/stt/speaker-separation")
async def speaker_separation(transcript: str):
    # GPT-4o mini 파인튜닝 모델 호출
    response = await openai.ChatCompletion.create(
        model="ft:gpt-4o-mini:hanacard:speaker-separation:abc123",
        messages=[
            {"role": "system", "content": "화자를 분리하세요"},
            {"role": "user", "content": transcript}
        ]
    )
    
    separated_transcript = response.choices[0].message.content
    return {"separated_transcript": separated_transcript}
```

---

## 🔐 마스킹 처리

### AfterCallWorkPage 저장 시 마스킹

**현재 구현 확인 필요:**
```typescript
// AfterCallWorkPage.tsx
const handleSaveConsultation = async () => {
  // ⭐ 마스킹 처리 필요
  const maskedTranscript = maskPersonalInfo(transcript);
  
  // DB 저장
  await fetch('/api/consultations', {
    method: 'POST',
    body: JSON.stringify({
      ...consultationData,
      recording_transcript: maskedTranscript  // 마스킹됨
    })
  });
};

// 마스킹 함수
const maskPersonalInfo = (text: string): string => {
  // 1. 상담사 이름 마스킹
  text = text.replace(/홍길동/g, '[상담사명#1]');
  
  // 2. 고객 이름 마스킹
  text = text.replace(/김민수/g, '[고객명#1]');
  
  // 3. 전화번호 마스킹
  text = text.replace(/010-\d{4}-\d{4}/g, '[전화번호#1]');
  
  // 4. 주민번호 마스킹
  text = text.replace(/\d{6}-\d{7}/g, '[주민번호#1]');
  
  // 5. 카드번호 마스킹
  text = text.replace(/\d{4}-\d{4}-\d{4}-\d{4}/g, '[카드번호#1]');
  
  return text;
};
```

**백엔드 마스킹 (권장):**
```python
import re

def mask_personal_info(text: str, employee_name: str, customer_name: str) -> str:
    # 상담사 이름 마스킹
    text = text.replace(employee_name, '[상담사명#1]')
    
    # 고객 이름 마스킹
    text = text.replace(customer_name, '[고객명#1]')
    
    # 전화번호 마스킹
    text = re.sub(r'010-\d{4}-\d{4}', '[전화번호#1]', text)
    
    # 주민번호 마스킹
    text = re.sub(r'\d{6}-\d{7}', '[주민번호#1]', text)
    
    # 카드번호 마스킹
    text = re.sub(r'\d{4}-\d{4}-\d{4}-\d{4}', '[카드번호#1]', text)
    
    return text
```

---

## 📚 백엔드 구현 가이드

### 1. 녹음 시작 API

```python
# FastAPI
@app.post("/api/consultations/start-recording")
async def start_recording(data: RecordingStart):
    consultation_id = generate_consultation_id()
    
    # DB에 초기 레코드 생성
    await db.execute("""
        INSERT INTO consultations (
            id, employee_id, customer_id, 
            recording_status, recording_started_at
        ) VALUES ($1, $2, $3, 'recording', NOW())
    """, consultation_id, data.employee_id, data.customer_id)
    
    return {
        "consultation_id": consultation_id,
        "websocket_url": f"wss://api.call-act.com/ws/recording/{consultation_id}"
    }
```

---

### 2. 청크 수신 WebSocket

```python
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
            INSERT INTO recording_chunks 
            (consultation_id, chunk_index, chunk_file_path, chunk_size)
            VALUES ($1, $2, $3, $4)
        """, consultation_id, chunk_index, chunk_path, len(audio_chunk))
        
        chunk_index += 1
```

---

### 3. 녹음 종료 및 병합 API

```python
@app.post("/api/consultations/{consultation_id}/end-recording")
async def end_recording(consultation_id: str):
    # 1. 청크 가져오기
    chunks = await db.fetch("""
        SELECT chunk_file_path FROM recording_chunks
        WHERE consultation_id = $1
        ORDER BY chunk_index
    """, consultation_id)
    
    # 2. WAV 파일 병합 (FFmpeg)
    merged_wav = await merge_wav_chunks([c['chunk_file_path'] for c in chunks])
    
    # 3. S3 업로드
    date = datetime.now()
    final_path = f"{date.year}/{date.month:02d}/{date.day:02d}/{consultation_id}.wav"
    await s3.upload_file(merged_wav, final_path)
    
    # 4. STT 처리
    transcript = await stt_service.transcribe(merged_wav)
    
    # 5. 화자 분리 (GPT-4o mini)
    separated_transcript = await gpt_speaker_separation(transcript)
    
    # 6. 마스킹 처리
    masked_transcript = mask_personal_info(separated_transcript, ...)
    
    # 7. DB 업데이트
    await db.execute("""
        UPDATE consultations
        SET recording_file_path = $1,
            recording_transcript = $2,
            recording_status = 'completed',
            recording_ended_at = NOW()
        WHERE id = $3
    """, final_path, masked_transcript, consultation_id)
    
    # 8. 임시 청크 삭제
    await s3.delete_folder(f"temp/{consultation_id}")
    await db.execute("DELETE FROM recording_chunks WHERE consultation_id = $1", consultation_id)
    
    return {"status": "completed"}
```

---

## 🎯 다음 단계: Phase 12

### Phase 12-1: 백그라운드 녹음 구현
- [ ] RealTimeConsultationPage에 MediaRecorder API 적용
- [ ] 상담 시작 시 자동 녹음 시작
- [ ] 5초마다 청크 생성
- [ ] WebSocket으로 서버 전송 (백엔드 구현 후)

### Phase 12-2: 타임스탬프 기록
- [ ] 상담 시작 시간 기록
- [ ] 대화 내용에 타임스탬프 추가
- [ ] DB 저장 형식 정의

### Phase 12-3: 마스킹 처리 확인
- [ ] AfterCallWorkPage 저장 로직 확인
- [ ] 마스킹 함수 구현 또는 확인
- [ ] 테스트 데이터로 검증

### Phase 12-4: "학습하기" / "시작하기" 개선
- [ ] SimulationPage 수정
- [ ] RealTimeConsultationPage 자동 시작
- [ ] AI 고객 페르소나 연동

---

## ✅ 완료 체크리스트

- [x] 녹취 다운로드 법적 주의 모달 구현
- [x] RecordingDownloadWarningModal 컴포넌트 생성
- [x] ConsultationDetailModal에 모달 적용
- [x] 주의사항 텍스트 파일에 포함
- [x] TXT vs WAV 저장 가이드 작성
- [x] MediaRecorder API 코드 예시
- [x] 타임스탬프 기록 코드 예시
- [x] WebRTC 청크 성능 분석
- [x] DB 스키마 종합 가이드
- [x] 화자 분리 프로세스 문서화
- [x] 마스킹 처리 가이드
- [x] 백엔드 API 가이드

---

**작성자:** AI Assistant  
**마지막 업데이트:** 2025-01-23  
**Phase:** 11-4  
**상태:** ✅ 완료
