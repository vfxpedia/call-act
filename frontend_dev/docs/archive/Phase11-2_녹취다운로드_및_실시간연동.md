# Phase 11-2: 녹취 다운로드 및 우수사례 실시간 연동

## 📋 작업 개요

**목적:** 
1. 상담 상세 모달에서 녹취록 텍스트 다운로드 기능 구현
2. 상담 관리 페이지의 우수사례 등록이 교육 시뮬레이션 페이지에 실시간 반영

**작업 일자:** 2025-01-23  
**Phase:** 11-2  
**상태:** ✅ **완료**

---

## 🎯 구현된 기능

### 1. **녹취 다운로드 기능** ✅

#### 기능 설명
- 상담 상세 모달의 "다운로드" 버튼 클릭 시 녹취록 텍스트 파일 다운로드
- 파일 형식: `.txt` (UTF-8 인코딩)
- 파일명: `녹취록_[상담ID]_[날짜].txt` (예: `녹취록_CS-EMP001-202501051432_2025-01-23.txt`)

#### 다운로드 내용
```
[CALL:ACT 녹취록]
========================================
상담 ID: CS-EMP001-202501051432
상담사: 홍길동
고객: 김민수
카테고리: 카드분실
일시: 14:32:15 - 14:37:42
통화 시간: 5:27
========================================

[상담 요약]
고객님께서 카드 분실 신고를 요청하셨습니다...

[처리 내역]
1. [14:32:30] 카드 분실 신고 접수
2. [14:33:15] 카드 사용 즉시 정지 처리
...

[참조 문서]
1. 카드 즉시 사용 정지
2. 분실 신고 접수 완료
3. 재발급 카드 신청

========================================
고객 만족도: 5/5
FCR 달성: 예
========================================

본 녹취록은 CALL:ACT 시스템에서 자동 생성되었습니다.
생성 일시: 2025-01-23 14:30:00
```

#### 구현 코드
```typescript
// ConsultationDetailModal.tsx
const handleDownloadRecording = () => {
  const recordingText = `
[CALL:ACT 녹취록]
========================================
상담 ID: ${consultation.id}
상담사: ${consultation.agent || '정보 없음'}
고객: ${detailData.customerName}
카테고리: ${consultation.category}
일시: ${detailData.startTime} - ${detailData.endTime}
통화 시간: ${detailData.duration}
========================================

[상담 요약]
${detailData.summary}

[처리 내역]
${detailData.actions.map((action, index) => 
  `${index + 1}. [${action.time}] ${action.action}`
).join('\\n')}

[참조 문서]
${detailData.documents.map((doc, index) => 
  `${index + 1}. ${doc.title}`
).join('\\n')}

========================================
고객 만족도: ${detailData.satisfaction}/5
FCR 달성: ${consultation.fcr ? '예' : '아니오'}
========================================

본 녹취록은 CALL:ACT 시스템에서 자동 생성되었습니다.
생성 일시: ${new Date().toLocaleString('ko-KR')}
  `.trim();

  // Blob 생성 및 다운로드
  const blob = new Blob([recordingText], { 
    type: 'text/plain;charset=utf-8' 
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `녹취록_${consultation.id}_${new Date().toISOString().split('T')[0]}.txt`;
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
```

---

### 2. **우수사례 실시간 연동** ✅

#### 기능 설명
- 관리자가 상담 관리 페이지에서 우수사례 등록
- localStorage를 통한 상태 관리
- 교육 시뮬레이션 페이지에 즉시 반영 (새로고침 시에도 유지)

#### 데이터 흐름

```
┌─────────────────────────────────────────┐
│   AdminConsultationManagePage           │
│   (관리자)                               │
│                                          │
│   1. 우수사례 토글 클릭                   │
│      toggleBestPractice(id)             │
│                                          │
│   2. consultations 상태 업데이트         │
│      setConsultations(...)              │
└──────────────┬──────────────────────────┘
               │
               │ 3. useEffect 트리거
               │    localStorage.setItem()
               ▼
┌─────────────────────────────────────────┐
│   localStorage                           │
│   key: 'consultations'                   │
│   value: JSON.stringify(consultations)   │
└──────────────┬──────────────────────────┘
               │
               │ 4. 페이지 로드/새로고침
               ▼
┌─────────────────────────────────────────┐
│   SimulationPage                         │
│   (상담사)                               │
│                                          │
│   5. useEffect() 실행                    │
│      localStorage.getItem()             │
│                                          │
│   6. consultations 상태 업데이트         │
│      setConsultations(...)              │
│                                          │
│   7. 우수사례 필터링 및 표시              │
│      consultations.filter(              │
│        c => c.isBestPractice            │
│      )                                  │
└─────────────────────────────────────────┘
```

#### AdminConsultationManagePage 수정

```typescript
// ⭐ localStorage에서 우수사례 데이터 로드
const loadConsultations = () => {
  const saved = localStorage.getItem('consultations');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (error) {
      console.error('상담 데이터 로드 실패:', error);
      return initialConsultationsData;
    }
  }
  return initialConsultationsData;
};

const [consultations, setConsultations] = useState(loadConsultations);

// ⭐ consultations 변경 시 localStorage에 저장
useEffect(() => {
  localStorage.setItem('consultations', JSON.stringify(consultations));
}, [consultations]);
```

#### SimulationPage 수정

```typescript
// ⭐ localStorage에서 우수사례 로드 (실시간 연동)
useEffect(() => {
  const loadConsultations = () => {
    const saved = localStorage.getItem('consultations');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (error) {
        console.error('상담 데이터 로드 실패:', error);
        return consultationsData;
      }
    }
    return consultationsData;
  };

  setConsultations(loadConsultations());
}, []);
```

---

## ✅ 테스트 시나리오

### 테스트 1: 녹취 다운로드

**단계:**
1. 대시보드 또는 상담 관리 페이지 접속
2. 상담 목록에서 상담 클릭
3. 상담 상세 모달 열림
4. "녹취 재생" 섹션의 "다운로드" 버튼 클릭
5. 파일 다운로드 확인

**예상 결과:**
- ✅ 파일명: `녹취록_CS-EMP001-202501051432_2025-01-23.txt`
- ✅ 파일 형식: 텍스트 파일 (UTF-8)
- ✅ 내용 포함:
  - 상담 ID, 상담사, 고객, 카테고리
  - 상담 요약
  - 처리 내역 (시간별)
  - 참조 문서 목록
  - 고객 만족도, FCR 달성 여부
  - 생성 일시

---

### 테스트 2: 우수사례 실시간 연동

#### 2-1. 개별 우수사례 등록

**단계:**
1. 관리자 계정으로 로그인
2. 상담 관리 페이지 접속 (`/admin/consultation-manage`)
3. 상담 목록에서 우수사례로 등록할 상담 선택
4. 별(⭐) 아이콘 클릭
5. Toast 알림: "교육 시뮬레이션 자료로 등록되었습니다!" 확인
6. 별 아이콘이 **채워진 상태**(금색)로 변경 확인
7. 교육 시뮬레이션 페이지 접속 (`/simulation`)
8. "우수 상담 사례" 섹션에 해당 상담 표시 확인

**예상 결과:**
- ✅ 상담 관리: 별 아이콘 금색 채워짐
- ✅ 시뮬레이션: 우수사례 섹션에 즉시 표시
- ✅ 새로고침 후에도 유지

#### 2-2. 일괄 우수사례 등록

**단계:**
1. 상담 관리 페이지에서 여러 상담 체크박스 선택 (2개 이상)
2. "우수 사례 일괄 등록" 버튼 클릭
3. Toast 알림: "N개의 상담이 교육 시뮬레이션 자료로 등록되었습니다!" 확인
4. 모든 선택된 상담의 별 아이콘 금색으로 변경 확인
5. 교육 시뮬레이션 페이지에서 모든 등록된 상담 표시 확인

**예상 결과:**
- ✅ 일괄 등록된 상담 모두 별 아이콘 금색
- ✅ 시뮬레이션 페이지에 모두 표시
- ✅ 최대 4개까지 표시 (초과 시 최근 4개)

#### 2-3. 우수사례 제외

**단계:**
1. 우수사례로 등록된 상담의 별(⭐) 아이콘 다시 클릭
2. Toast 알림: "우수사례에서 제외되었습니다." 확인
3. 별 아이콘이 **빈 상태**(회색)로 변경 확인
4. 교육 시뮬레이션 페이지에서 해당 상담 미표시 확인

**예상 결과:**
- ✅ 상담 관리: 별 아이콘 회색 빈 상태
- ✅ 시뮬레이션: 우수사례 섹션에서 제거
- ✅ 새로고침 후에도 유지

#### 2-4. 페이지 새로고침 후 데이터 유지

**단계:**
1. 우수사례 등록
2. 브라우저 새로고침 (F5)
3. 상담 관리 페이지에서 별 아이콘 상태 확인
4. 교육 시뮬레이션 페이지에서 우수사례 표시 확인

**예상 결과:**
- ✅ 새로고침 후에도 별 아이콘 상태 유지
- ✅ 시뮬레이션 페이지에 우수사례 표시 유지

---

## 🚀 향후 시뮬레이션 구조 설계

### Phase 12: AI 페르소나 기반 실전 시뮬레이션

사용자가 제시한 방향성에 따라 다음과 같은 구조로 구현 예정:

#### 1. **AI 고객 페르소나 시스템**

**8가지 고객 유형 (mockCustomerDB 기반):**
1. **급한 성향** - 빠른 답변 요구, 대기 시간 최소화
2. **꼼꼼한 성향** - 세부 설명 요구, 확인 반복
3. **감정적 성향** - 공감 필요, 감정 표현 많음
4. **논리적 성향** - 근거 중시, 체계적 설명 선호
5. **불만 고객** - 불평/항의 많음, 감정 전환 필요
6. **우호적 고객** - 협조적, 이해심 많음
7. **노년층** - 천천히 설명, 반복 안내 필요
8. **VIP 고객** - 우대 서비스 기대, 높은 수준 요구

**페르소나 데이터 구조:**
```typescript
export interface AICustomerPersona {
  id: string;
  type: '급한성향' | '꼼꼼한성향' | '감정적성향' | ... ;
  traits: string[];              // 성격 특성
  communicationStyle: {
    speed: 'fast' | 'moderate' | 'slow';
    tone: 'formal' | 'neutral' | 'casual' | 'warm' | 'empathetic';
    interruption: 'high' | 'moderate' | 'low';  // 말 끊는 빈도
  };
  expectations: string[];        // 기대사항
  reactionPatterns: {
    positive: string[];          // 긍정 반응
    negative: string[];          // 부정 반응
    neutral: string[];           // 중립 반응
  };
}
```

#### 2. **TTS (Text-to-Speech) 통합**

**TTS 음성 생성:**
- 우수사례의 실제 상담 내역(`content`) 분석
- AI 고객 페르소나에 맞는 음성 톤/속도 설정
- 실시간으로 TTS 음성 생성 및 재생

**TTS 설정 예시:**
```typescript
interface TTSConfig {
  voice: 'male' | 'female';
  pitch: number;         // 0.5 ~ 2.0
  rate: number;          // 0.5 ~ 2.0 (속도)
  volume: number;        // 0.0 ~ 1.0
  emotion: 'neutral' | 'happy' | 'sad' | 'angry' | 'surprised';
}
```

#### 3. **실전 상담 프로세스**

**흐름:**
```
1. 우수사례 "학습하기" 클릭
   ↓
2. AI 고객 페르소나 자동 선택
   (우수사례의 고객 DB 페르소나 매핑)
   ↓
3. RealTimeConsultationPage 진입
   - 좌측: AI 고객 정보 (페르소나 표시)
   - 중앙: STT 대화 내용 (실시간)
   - 우측: 칸반보드 (문서 검색)
   ↓
4. TTS로 AI 고객 음성 재생
   (실제 상담 content 기반)
   ↓
5. 상담사 응대 (실제 상담과 동일)
   - 키워드 추출
   - 문서 검색
   - Step 전환
   ↓
6. 상담 종료 후 LoadingPage (피드백 생성)
   ↓
7. AfterCallWorkPage (후처리)
   - 기존 피드백 (말투, 속도, 공감 등)
   - ⭐ 추가: 우수사례 유사도 점수
```

#### 4. **우수사례 유사도 평가 시스템**

**평가 기준:**
```typescript
interface SimilarityEvaluation {
  // 1. 키워드 일치도
  keywordMatch: {
    score: number;           // 0-100
    matched: string[];       // 일치한 키워드
    missed: string[];        // 누락한 키워드
  };
  
  // 2. 문서 참조 일치도
  documentMatch: {
    score: number;           // 0-100
    matched: string[];       // 참조한 문서 ID
    missed: string[];        // 누락한 문서 ID
    extra: string[];         // 추가로 참조한 문서
  };
  
  // 3. 처리 순서 일치도
  sequenceMatch: {
    score: number;           // 0-100
    correctSequence: boolean;
    differences: string[];   // 순서 차이점
  };
  
  // 4. 응대 시간 비교
  timeComparison: {
    original: number;        // 우수사례 통화 시간
    simulation: number;      // 시뮬레이션 통화 시간
    difference: number;      // 시간 차이
    efficiency: 'faster' | 'similar' | 'slower';
  };
  
  // 5. 종합 유사도 점수
  overallSimilarity: number; // 0-100
}
```

#### 5. **피드백 구성 (기존 + 신규)**

**기존 피드백 (유지):**
```typescript
interface ExistingFeedback {
  speakingSpeed: number;      // 말투 속도
  empathy: number;            // 공감 표현
  clarity: number;            // 명확성
  professionalism: number;    // 전문성
  overallScore: number;       // 종합 점수
  suggestions: string[];      // 개선 제안
}
```

**신규 피드백 (추가):**
```typescript
interface SimulationFeedback extends ExistingFeedback {
  // ⭐ 우수사례 유사도
  similarityEvaluation: SimilarityEvaluation;
  
  // ⭐ 학습 포인트
  learningPoints: {
    wellDone: string[];       // 잘한 점
    toImprove: string[];      // 개선할 점
    expertTips: string[];     // 우수사례의 핵심 포인트
  };
  
  // ⭐ 비교 분석
  comparison: {
    youDid: string;           // 귀하의 응대
    expertDid: string;        // 우수사례 응대
    difference: string;       // 차이점 분석
  }[];
}
```

#### 6. **UI 변경 사항**

**AfterCallWorkPage 피드백 섹션:**

```
┌─────────────────────────────────────────┐
│  📊 상담 평가 결과                       │
├─────────────────────────────────────────┤
│                                          │
│  종합 점수: 85점                         │
│                                          │
│  말투 속도: ████████░░ 80점              │
│  공감 표현: █████████░ 90점              │
│  명확성: ███████░░░ 70점                 │
│  전문성: ████████░░ 80점                 │
│                                          │
│  ─────────────────────────────────────  │
│                                          │
│  ⭐ 우수사례 유사도 점수: 88점            │
│                                          │
│  키워드 일치도: 92점                      │
│  문서 참조: 85점                         │
│  처리 순서: 90점                         │
│  응대 시간: 82점                         │
│                                          │
│  ✅ 잘한 점:                              │
│  • 고객 본인 확인 절차 정확히 수행        │
│  • 필수 문서 모두 참조                    │
│                                          │
│  💡 개선할 점:                            │
│  • "재발급 배송 안내" 문서 참조 누락      │
│  • 응대 속도가 우수사례 대비 15% 느림     │
│                                          │
│  📚 우수사례 핵심 포인트:                 │
│  • 즉시 카드 정지 → 재발급 순서 중요      │
│  • 고객 불안감 해소를 위한 공감 표현      │
│                                          │
└─────────────────────────────────────────┘
```

---

## 📚 데이터 스키마 (향후 DB 연동)

### 1. simulation_results 테이블

```sql
CREATE TABLE simulation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id VARCHAR(50) REFERENCES employees(id),
  original_consultation_id VARCHAR(50) REFERENCES consultations(id),  -- 우수사례 원본
  simulation_id VARCHAR(50) UNIQUE NOT NULL,  -- 시뮬레이션 상담 ID
  
  -- 페르소나 정보
  persona_type VARCHAR(50),
  persona_traits JSONB,
  
  -- 평가 결과
  overall_score INT,              -- 기존 종합 점수
  similarity_score INT,           -- 우수사례 유사도
  keyword_match_score INT,
  document_match_score INT,
  sequence_match_score INT,
  time_comparison JSONB,
  
  -- 피드백 상세
  feedback_data JSONB,            -- 전체 피드백 JSON
  learning_points JSONB,
  
  -- 통계
  call_duration INT,              -- 통화 시간 (초)
  completed_at TIMESTAMP DEFAULT NOW(),
  
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. simulation_learning_analytics 테이블

```sql
CREATE TABLE simulation_learning_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id VARCHAR(50) REFERENCES employees(id),
  
  -- 학습 통계
  total_simulations INT DEFAULT 0,
  average_similarity_score DECIMAL(5,2),
  improvement_rate DECIMAL(5,2),          -- 개선율 (%)
  
  -- 강점/약점 분석
  strengths JSONB,                        -- ['키워드 추출', '문서 참조']
  weaknesses JSONB,                       -- ['응대 시간', '순서']
  
  -- 카테고리별 성과
  category_performance JSONB,             -- {'카드분실': 85, '해외결제': 90}
  
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 구현 우선순위

### Phase 12-1: AI 페르소나 시스템 (우선)
- [ ] 8가지 고객 페르소나 데이터 정의
- [ ] 우수사례 ↔ 페르소나 매핑 로직
- [ ] RealTimeConsultationPage에 페르소나 정보 표시

### Phase 12-2: TTS 통합 (우선)
- [ ] TTS API 연동 (Web Speech API 또는 외부 서비스)
- [ ] 페르소나별 음성 설정
- [ ] 우수사례 content → TTS 스크립트 변환

### Phase 12-3: 시뮬레이션 실행 엔진 (핵심)
- [ ] localStorage에서 simulationCase 로드
- [ ] AI 고객 음성 재생
- [ ] 상담사 응대 기록
- [ ] 실시간 STT 시뮬레이션

### Phase 12-4: 유사도 평가 시스템 (핵심)
- [ ] 키워드 일치도 알고리즘
- [ ] 문서 참조 비교
- [ ] 처리 순서 분석
- [ ] 종합 유사도 계산

### Phase 12-5: 피드백 UI 개선 (필수)
- [ ] AfterCallWorkPage 피드백 섹션 확장
- [ ] 우수사례 유사도 점수 표시
- [ ] 학습 포인트 및 비교 분석 UI

### Phase 12-6: DB 연동 및 통계 (추후)
- [ ] simulation_results 테이블 생성
- [ ] 학습 데이터 저장
- [ ] 개인별 학습 분석 대시보드

---

## ✅ 완료 체크리스트

- [x] 녹취 다운로드 기능 구현
- [x] 다운로드 버튼에 onClick 핸들러 연결
- [x] localStorage 기반 우수사례 관리
- [x] AdminConsultationManagePage에서 localStorage 저장
- [x] SimulationPage에서 localStorage 로드
- [x] 실시간 연동 확인 (새로고침 후에도 유지)
- [x] 기존 기능 영향 없음 확인
- [x] 문서 작성 완료

---

## 📚 관련 문서

- [Phase 11: 우수사례 시뮬레이션 연동](/docs/Phase11_우수사례_시뮬레이션_연동.md)
- [Phase 10-6: 참조문서 모달 통일](/docs/Phase10-6_참조문서_모달_통일.md)
- [고객 DB 최종 스키마](/docs/고객DB_최종_스키마.md)
- [Mock Customer DB](/docs/Phase10_고객DB_마스킹_가이드.md)

---

**작성자:** AI Assistant  
**마지막 업데이트:** 2025-01-23  
**Phase:** 11-2  
**상태:** ✅ 완료
