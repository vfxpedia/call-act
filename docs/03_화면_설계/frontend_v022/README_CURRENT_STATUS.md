# 📋 CALL:ACT 프로젝트 - 현재 상태 요약

## 🎯 프로젝트 개요
React + FastAPI 기반의 상담 지원 시스템 **CALL:ACT**

---

## ✅ 완료된 주요 기능 (2025-01-29)

### **1. 가이드 모드 vs 교육 모드 완전 분리**
- ✅ 가이드 모드: 헤더 "가이드" 버튼 → UI 학습 (말풍선 투어)
- ✅ 교육 모드: 교육 페이지 → 시나리오 선택 → 실전 연습
- ✅ 두 모드 간 명확한 차단 로직:
  - 가이드 모드: 대기콜 허용 ✅ / 다이렉트 콜 차단 ❌
  - 교육 모드: 대기콜 차단 ❌ / 다이렉트 콜 허용 ✅

### **2. 🚨 CRITICAL 버그 수정 (3건)**
1. ✅ **교육 모드 대기콜 차단 순서 문제**
   - 문제: 대기콜 클릭 시 상태 변경 후 차단 → 데이터 오염
   - 해결: 차단 로직을 함수 최상단으로 이동 (1650번째 줄)
   
2. ✅ **교육 모드 진입 시 가이드 자동 활성화 방지**
   - 문제: localStorage에 남아있는 플래그로 인한 자동 활성화
   - 해결: 교육 모드 진입 시 4곳에서 가이드 플래그 제거
   
3. ✅ **교육 모드 Mock 데이터 연결 제거**
   - 문제: 프론트엔드 하드코딩 데이터 즉시 로드 (백엔드 개입 불가)
   - 해결: 백엔드 API 호출 구조 구축 + Timeline 기반 순차 표시
   
4. ✅ **Phase 1 완료 시 자동 통화 시작 버그**
   - 문제: 교육 모드에서 시나리오 로드 시 자동으로 통화 시작
   - 원인: TutorialGuide onComplete에서 `isGuideModeActive` 체크 누락
   - 해결: 조건에 `&& isGuideModeActive` 추가 (3256줄)

### **3. 백엔드 API 연동 준비**
- ✅ `fetchScenarioData()` 함수 추가 (Mock API)
- ✅ `processScenarioTimeline()` 함수 추가 (타임라인 처리)
- ✅ Timeline 기반 이벤트 시스템 (stt, keyword, infoCard, step)
- ✅ Mock → 실제 API 교체 구조 완성 (주석 해제만 하면 됨)

### **4. 전체 워크플로우 구현**
- ✅ Phase 1: 대기콜 현황
- ✅ Phase 2: 상담 중 (키워드 추출, 정보 카드)
- ✅ Phase 3: 후처리 (메모, LLM 분석)
- ✅ 페이지 이동 시 상태 유지 (헤더 배지 + localStorage)

---

## 📁 주요 파일 구조

```
/src/app/pages/
├── RealTimeConsultationPage.tsx    # 메인 상담 페이지
├── AfterCallWorkPage.tsx           # 후처리 페이지
├── SimulationPage.tsx              # 교육 시뮬레이션 페이지
└── ...

/src/data/
├── scenarios.ts                    # 시나리오 데이터
├── tutorialSteps.ts                # 가이드 모드 스텝
└── ...

/문서/
├── FEATURE_CHANGES_GUIDE_VS_EDUCATION.md    # 가이드 vs 교육 모드 완전 가이드
├── FEATURE_BACKEND_API_INTEGRATION.md       # 백엔드 API 연동 가이드
└── README_CURRENT_STATUS.md                 # 이 파일
```

---

## 🔧 핵심 함수 위치

### **RealTimeConsultationPage.tsx**

| 함수명 | 줄 번호 | 설명 |
|--------|---------|------|
| `processScenarioTimeline()` | 1248 | Timeline 기반 순차 표시 |
| `fetchScenarioData()` | 1308 | 백엔드 API 호출 (Mock) |
| `handleStartCall()` | 1383 | 다이렉트 콜 시작 |
| `handleCallConnect()` | 1647 | 대기콜 연결 |
| `handleEndCall()` | 1425 | 통화 종료 → 후처리 이동 |

---

## 🚀 다음 단계

### **즉시 진행 가능:**
- [ ] **해상도 최적화** (1920×1080 기준)
  - 말풍선 위치 정확도
  - 4개 카드 스크롤 없이 표시
  - 폰트 크기 일관성

### **백엔드 팀 협업 필요:**
- [ ] API 엔드포인트 구현: `POST /api/scenarios/:id/start`
- [ ] AI TTS 연동 (고객 음성 생성)
- [ ] RAG 시스템 연동 (키워드 → 정보 카드)
- [ ] Vector DB 검색 최적화

### **향후 개선:**
- [ ] Timeline 재생 속도 조절
- [ ] 로딩 상태 개선 (스켈레톤 UI)
- [ ] Step 2, 3 자동 전환 로직
- [ ] 에러 핸들링 강화

---

## 🧪 테스트 가이드

### **가이드 모드 테스트:**
```
1. 상담 페이지 진입
2. 헤더 "가이드" 버튼 클릭
3. Phase 1 말풍선 확인
4. 대기콜 클릭 → Phase 2 전환 확인
5. 통화 버튼 클릭 → 차단 모달 확인
```

### **교육 모드 테스트:**
```
1. 교육 페이지 → "불만 고객 응대" 선택
2. 녹색 배너 확인: "🎓 교육 시나리오 대기중"
3. 대기콜 클릭 → 차단 모달 확인
4. 통화 버튼 클릭 → 키워드 추출 중 표시
5. 1초 후: STT "안녕하세요" 확인
6. 2.5초 후: 고객 대화 확인
7. 4초 후: 첫 키워드 확인
8. 6초 후: 첫 정보 카드 확인
```

---

## 📖 상세 문서

- **가이드 vs 교육 모드:** `/FEATURE_CHANGES_GUIDE_VS_EDUCATION.md`
- **백엔드 API 연동:** `/FEATURE_BACKEND_API_INTEGRATION.md`

---

## ⚠️ 알려진 이슈

1. **해상도 최적화 필요:**
   - 개발 환경과 프로덕션 환경에서 폰트 크기 차이
   - 낮은 해상도에서 스크롤 발생
   - 말풍선 위치 틀어짐

2. **백엔드 API 미연동:**
   - 현재 Mock API 사용 중
   - 실제 AI TTS, RAG 미연동

---

## 👥 팀 협업 가이드

### **프론트엔드 개발자:**
- 해상도 최적화 진행
- Timeline 애니메이션 개선
- 에러 핸들링 추가

### **백엔드 개발자:**
- API 엔드포인트 구현 (`/api/scenarios/:id/start`)
- AI TTS 시스템 구축
- RAG 시스템 연동

### **QA 팀:**
- 가이드 모드 / 교육 모드 테스트 시나리오 실행
- 크로스 브라우징 테스트 (해상도별)
- 버그 리포트 작성

---

**📅 마지막 업데이트:** 2025-01-29
**📝 작성자:** AI Assistant
**✅ 상태:** Step 1 + Step 4 완료, Step 2 & 3 대기 중