# CALL:ACT 모드 시스템 정리 및 DB 저장 가이드

## 1. 모드 시스템 종합 정리

### 1.1 데이터 모드 (2가지)

| 모드 | 변수 | 설정 위치 | 설명 |
|------|------|----------|------|
| **Mock Data** | `USE_MOCK_DATA = true` | `localStorage.mockMode` | 실제 API 호출 안함, 가짜 데이터 |
| **Real DB** | `USE_MOCK_DATA = false` | `localStorage.mockMode` | FastAPI 백엔드 호출 |

### 1.2 앱 모드 (4가지)

| 모드 | 변수 | 설정 방식 | 설명 |
|------|------|----------|------|
| **실전 모드** | `isSimulationMode = false` | 기본값 | 실제 고객 상담 |
| **기본 교육** | `isSimulationMode = true` + `educationType = 'basic'` | sessionStorage | 시나리오 학습 |
| **우수사례 교육** | `isSimulationMode = true` + `educationType = 'advanced'` | sessionStorage | 우수 상담 학습 |
| **가이드 모드** | `isGuideModeActive = true` | localStorage | 튜토리얼 오버레이 |

### 1.3 인입 타입 (2가지)

| 타입 | 변수 | 값 | 설명 |
|------|------|-----|------|
| **대기콜** | `isDirectIncoming` | `false` | 8개 분류 시나리오 기반 |
| **다이렉트콜** | `isDirectIncoming` | `true` | 랜덤 고객, STT+RAG 실시간 |

---

## 2. 모드 조합별 동작 매트릭스

### 2.1 저장 동작 (16가지 조합)

```
Real DB 저장 조건 = Real모드 AND 다이렉트콜 AND 실전모드(교육X)

┌────────────┬──────────┬────────────┬─────────────┬─────────────────┐
│ 데이터모드  │ 앱모드   │ 인입타입   │ 저장 방식    │ 저장 테이블      │
├────────────┼──────────┼────────────┼─────────────┼─────────────────┤
│ Mock       │ 모든     │ 모든       │ Mock 저장    │ -               │
├────────────┼──────────┼────────────┼─────────────┼─────────────────┤
│ Real       │ 실전     │ 대기콜     │ Mock 저장    │ -               │
│ Real       │ 교육     │ 모든       │ Mock 저장    │ (simulation별도)│
│ Real       │ 실전     │ 다이렉트콜 │ ✅ Real DB   │ consultations   │
└────────────┴──────────┴────────────┴─────────────┴─────────────────┘
```

### 2.2 각 모드별 기능 차이

| 기능 | Real+실전+다이렉트 | Real+실전+대기콜 | Real+교육+다이렉트 | Mock+다이렉트 | Mock+대기콜 |
|------|-------------------|-----------------|-------------------|--------------|------------|
| **STT 음성인식** | ✅ WebSocket | ❌ 시나리오 | ✅ WebSocket | ✅ WebSocket | ❌ 시나리오 |
| **RAG 검색** | ✅ 실시간 | ❌ 시나리오 카드 | ✅ 실시간 | ✅ 실시간 | ❌ 시나리오 카드 |
| **LLM 화자분리** | ✅ | ❌ | ✅ | ✅ | ❌ |
| **LLM 후처리 분석** | ✅ /api/v1/followup | ❌ | ✅ /api/v1/followup | ✅ /api/v1/followup | ❌ |
| **DB 저장** | ✅ consultations | ❌ | ❌ simulation_results | ❌ Mock 저장 | ❌ Mock 저장 |
| **고객 정보** | 랜덤 API (전체) | 시나리오 고정 | 실제 페르소나 + 가짜 개인정보 | 랜덤 API | 시나리오 고정 |

> **Mock + 다이렉트콜 핵심**:
> - API 호출, WebSocket, STT, RAG, LLM 모두 **실제 동작** (다이렉트콜이니까!)
> - 후처리 "저장 및 완료" 시에만 DB 저장 안 함 (Mock 저장)
> - 실제 기능 테스트하면서 DB 오염 방지용

> **교육 모드 + 다이렉트콜 핵심**:
> - STT/RAG/LLM은 실제로 동작 (실전과 동일)
> - 하지만 consultations 테이블에 저장하지 않음
> - 대신 `simulation_results` 테이블에 저장
> - 고객 정보: DB에서 실제 페르소나(직업, 성격 등) 가져오되, 이름/전화번호는 가짜로 생성

---

## 3. 저장 로직 흐름 (consultationApi.ts)

```typescript
// 저장 분기 결정 (라인 289)
const shouldUseMockSave = USE_MOCK_DATA || !isDirectIncoming || isSimulationMode;

// Mock 저장 조건 (하나라도 true면 Mock)
// 1. USE_MOCK_DATA === true        → Mock 모드
// 2. isDirectIncoming === false    → 대기콜
// 3. isSimulationMode === true     → 교육 모드

// Real DB 저장 조건 (세 가지 모두 만족)
// 1. USE_MOCK_DATA === false       → Real 모드
// 2. isDirectIncoming === true     → 다이렉트콜
// 3. isSimulationMode === false    → 실전 모드
```

---

## 4. 디버깅 가이드

### 4.1 DB 저장 안 되는 경우 체크리스트

| 가능한 원인 | 확인 방법 |
|------------|----------|
| **localStorage.mockMode 값 차이** | 콘솔에서 `localStorage.getItem('mockMode')` 확인 |
| **activeCallState 복원 실패** | AfterCallWorkPage 진입 시 콘솔 로그 확인 |
| **sessionStorage 잔류** | 브라우저 개발자도구 → Application → Session Storage |
| **DB 연결 문제** | 백엔드 로그에서 PostgreSQL 연결 확인 |
| **422 에러** | 콘솔에서 API 에러 상세 메시지 확인 |

### 4.2 디버깅 콘솔 로그 체크리스트

```
✅ 확인해야 할 로그:
- "🎯 데이터 모드: Real" (Real이어야 함)
- "📞 콜 타입: 다이렉트콜" (다이렉트콜이어야 함)
- "🎓 교육 모드 (실제 저장용): false" (false여야 함)
- "🔗 [실전 다이렉트콜] 실제 API 호출: POST /api/v1/consultations"
- "✅ [실전 다이렉트콜] DB 저장 성공:"

❌ 문제 발생 시 보이는 로그:
- "🎭 Mock 저장 - [이유] (consultations DB 저장 안 함):"
- "❌ API 에러 상세: ..."
```

---

## 5. Real DB 저장 테스트 단계

### Step 1: 환경 준비
```bash
# 1-1. Docker PostgreSQL 초기화 및 실행
cd backend_dev
docker-compose down -v     # 볼륨까지 삭제 (클린 상태)
docker-compose up -d       # DB 컨테이너 시작

# 1-2. 백엔드 서버 실행
cd backend_dev
.venv/Scripts/activate     # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 1-3. 프론트엔드 실행
cd frontend_dev
npm run dev
```

### Step 2: 브라우저 초기화
```
1. 개발자도구 열기 (F12)
2. Application 탭 → Storage 섹션
3. Local Storage, Session Storage 모두 Clear
4. 새로고침 (Ctrl+Shift+R)
```

### Step 3: Mock 모드 OFF 확인
```
1. 화면 좌측 상단 Mock 토글 → OFF (Real DB 모드)
2. 콘솔에서 확인: localStorage.getItem('mockMode') → "off" 또는 null
```

### Step 4: 다이렉트콜 실행
```
1. 사이드바 → "직접 통화" 버튼 클릭 (교육모드 아님!)
2. 랜덤 고객 정보 로드 확인 (API: /api/v1/customers/random)
3. "통화 시작" 버튼 클릭
4. 마이크로 몇 마디 말하기 (STT 테스트)
5. "통화 종료" 버튼 클릭
```

### Step 5: 후처리 페이지 확인
```
1. 자동으로 AfterCallWorkPage 이동 확인
2. LLM 분석 완료 대기 (30초~1분)
3. 콘솔 로그 확인:
   - "llmApiResult에서 데이터 로드됨"
   - 화자분리 스크립트 표시 확인
```

### Step 6: 저장 및 DB 확인
```
1. 피드백 점수 입력 (선택사항)
2. "저장 및 완료" 버튼 클릭
3. 콘솔 로그 확인 (핵심!):
   ✅ "🎯 데이터 모드: Real"
   ✅ "📞 콜 타입: 다이렉트콜"
   ✅ "🎓 교육 모드 (실제 저장용): false"
   ✅ "🔗 [실전 다이렉트콜] 실제 API 호출: POST /api/v1/consultations"
   ✅ "✅ [실전 다이렉트콜] DB 저장 성공:"
```

### Step 7: DB 저장 검증
```bash
# 방법 1: API로 확인
curl http://localhost:8000/api/v1/consultations

# 방법 2: FastAPI Docs에서 확인
http://localhost:8000/docs → GET /api/v1/consultations → Try it out

# 방법 3: DB 직접 확인
docker exec -it callact_db psql -U callact_admin -d callact_db -c "SELECT id, customer_name, status, created_at FROM consultations ORDER BY created_at DESC LIMIT 5;"
```

---

## 6. 문제 발생 시 디버깅

### 6.1 Mock 저장으로 빠지는 경우
콘솔에 `🎭 Mock 저장` 로그가 보이면:
```javascript
// 콘솔에서 확인
localStorage.getItem('mockMode')           // "off" 또는 null이어야 함
localStorage.getItem('activeCallState')    // isDirectIncoming: true 확인
sessionStorage.getItem('simulationMode')   // null 또는 "false"여야 함
```

### 6.2 422 에러 발생 시
```
1. 콘솔에서 "❌ API 에러 상세:" 로그 확인
2. 백엔드 uvicorn 로그에서 상세 에러 확인
3. 필수 필드 누락 여부 확인
```

### 6.3 LLM 분석 안 나오는 경우
```
1. 백엔드 로그에서 Redis 연결 확인
2. whisper STT가 실제로 텍스트 출력하는지 확인
3. /api/v1/followup API 응답 확인
```

---

## 7. 핵심 파일 목록

| 파일 | 역할 |
|------|------|
| `frontend_dev/src/config/mockConfig.ts` | Mock/Real 모드 토글 |
| `frontend_dev/src/api/consultationApi.ts` | 저장 분기 로직 (라인 280-340) |
| `frontend_dev/src/app/pages/RealTimeConsultationPage.tsx` | activeCallState 저장 |
| `frontend_dev/src/app/pages/AfterCallWorkPage.tsx` | 저장 호출 + LLM 이벤트 리스너 |
| `backend_dev/app/api/v1/endpoints/consultations.py` | DB 저장 API |
| `backend_dev/app/api/v1/endpoints/followup.py` | LLM 후처리 API (retry 30회) |
| `backend_dev/app/audio/diarizer_manager.py` | 화자분리 + Redis 처리 마커 |

---

## 8. 테스트 체크리스트

- [ ] Docker DB 컨테이너 실행 중
- [ ] 백엔드 uvicorn 실행 중
- [ ] 프론트엔드 npm run dev 실행 중
- [ ] Mock 토글 OFF 상태
- [ ] 브라우저 Storage 초기화됨
- [ ] 다이렉트콜 → 후처리 → 저장 완료
- [ ] DB에 새 레코드 생성 확인
