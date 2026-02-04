# 📋 가이드 모드 향후 업데이트 사항

> **작성일**: 2025-01-28  
> **상태**: 계획 중  
> **우선순위**: Medium ~ High

---

## ✅ 완료된 사항 (2025-01-28)

### 1. 가이드 모드 기본 구현
- ✅ 자동 튜토리얼 시작 제거 → 도움말 버튼 클릭 시에만 시작
- ✅ `isGuideModeActive` 플래그 추가 (localStorage 기반)
- ✅ 가이드 모드에서 다이렉트 콜 차단 모달 구현
- ✅ Phase 1 가이드 메시지 수정 (대기콜 선택 유도)
- ✅ 가이드 모드 상태 유지 (상담 중 → 후처리 전체 워크플로우)
- ✅ 튜토리얼 완료/건너뛰기 시 가이드 모드 자동 종료

### 2. 사용자 경험 개선
- ✅ 교육 모드 vs 실전 모드 후처리 완료 후 이동 경로 분기
  - 교육 모드: `/simulation` (시뮬레이션 페이지)
  - 실전 모드: `/consultation/live` (상담 중 페이지)

---

## ⚠️ 향후 업데이트 예정 사항

### 1️⃣ 가이드 말풍선 위치 최적화 (High Priority)
**문제점:**
- 일부 말풍선이 화면 밖으로 벗어남
- 특히 모바일/태블릿 환경에서 위치 이탈 발생

**해결 방안:**
- `TutorialGuide` 컴포넌트 말풍선 위치 계산 로직 개선
- 화면 경계 감지 후 자동 위치 조정 (auto-positioning)
- Viewport 크기에 따른 반응형 위치 조정

**영향 범위:**
- `/src/app/components/tutorial/TutorialGuide.tsx`
- Phase 1, 2, 3 모든 가이드 단계

---

### 2️⃣ 가이드 스탭 추가 (High Priority)
**필요 사항:**
- **"다음 예상 정보 카드" 설명 단계 추가**

**현재 상태:**
```
Phase 2 (통화 중):
1. 환영 메시지
2. 고객 정보 카드 ✅
3. STT 영역 ✅
4. 키워드 영역 ✅
5. 현재 상황 정보 카드 ✅  ← 여기까지만 설명
6. AI 검색 어시스턴트 ✅
7. 메모 ✅
8. 통화 종료 ✅
```

**개선안:**
```
Phase 2 (통화 중):
1. 환영 메시지
2. 고객 정보 카드
3. STT 영역
4. 키워드 영역
5. 현재 상황 정보 카드 (Step 1)  ← 현재 상태
6. 다음 예상 정보 카드 (Step 2)  ← 🆕 추가 필요
7. Step 인디케이터 사용법
8. AI 검색 어시스턴트
9. 메모
10. 통화 종료
```

**구현 위치:**
- `/src/data/tutorialSteps.ts` → `tutorialStepsPhase2` 배열 수정
- 새 단계 추가: `targetId: 'next-step-cards-area'` (예상)

**예상 설명 내용:**
> "Step이 진행되면 다음 단계에서 필요한 정보가 미리 표시됩니다. 상담을 준비하고 고객에게 선제적으로 안내할 수 있습니다."

---

### 3️⃣ Outliner 디자인 개선 (Medium Priority)
**문제점:**
- 가이드 중 강조 영역(outliner)이 다소 단조로움
- 시각적 피드백이 약함

**개선 방안:**
```css
현재:
.tutorial-highlight {
  outline: 2px solid #0047AB;
  outline-offset: 4px;
}

개선안:
.tutorial-highlight {
  outline: 3px solid #0047AB;
  outline-offset: 6px;
  box-shadow: 
    0 0 0 3px rgba(0, 71, 171, 0.1),
    0 0 20px rgba(0, 71, 171, 0.2);
  animation: pulse-outline 2s ease-in-out infinite;
}

@keyframes pulse-outline {
  0%, 100% { outline-color: #0047AB; }
  50% { outline-color: #0066FF; }
}
```

**영향 범위:**
- `/src/app/components/tutorial/TutorialGuide.tsx`
- 모든 Phase에 공통 적용

---

### 4️⃣ 후처리 페이지 하이라이트 영역 개선 (Medium Priority)
**문제점:**
- 후처리 페이지에서 가이드 하이라이트 영역이 부정확
- 배경 하이라이트(흰색)가 일부 요소만 덮음

**확인 필요 영역:**
- `#acw-transcript` (상담 전문)
- `#acw-docs` (참조 문서)
- `#acw-summary` (AI 상담 요약본)
- `#acw-save-button` (저장 버튼)

**개선 방안:**
- 각 영역의 정확한 DOM 구조 확인
- `targetId`가 실제 요소와 일치하는지 검증
- 필요 시 wrapper div 추가하여 정확한 영역 지정

---

### 5️⃣ 후처리 페이지 가이드 완성도 향상 (Medium Priority)
**개선 항목:**

#### A. 가이드 내용 보완
- 각 단계별 설명이 더 구체적이고 실무 중심적이어야 함
- 예시:
  ```
  현재: "AI가 생성한 상담 요약본입니다."
  개선: "AI가 통화 내용을 분석하여 자동 생성한 요약본입니다. 
        누락된 내용이 있다면 직접 편집하세요. 
        평균 수정 시간: 10~15초"
  ```

#### B. 말풍선 위치 정밀 조정
- 현재 `position: 'top'` / `'right'` 등이 일부 요소에서 겹침
- 각 단계별 최적 위치 재설정 필요

#### C. 디자인 일관성
- Phase 1, 2와 동일한 시각적 스타일 유지
- 하이라이트 효과 강도 통일

---

## 📊 우선순위 매트릭스

| 항목 | 영향도 | 긴급도 | 난이도 | 우선순위 |
|------|--------|--------|--------|----------|
| 말풍선 위치 최적화 | High | High | Medium | **P1** |
| 가이드 스탭 추가 | High | High | Low | **P1** |
| Outliner 디자인 | Medium | Low | Low | P2 |
| 후처리 하이라이트 영역 | Medium | Medium | Medium | P2 |
| 후처리 가이드 완성도 | Medium | Low | Low | P3 |

---

## 🔧 구현 시 참고사항

### 관련 파일
```
/src/data/tutorialSteps.ts              # 가이드 스탭 정의
/src/app/components/tutorial/TutorialGuide.tsx  # 가이드 컴포넌트
/src/app/pages/RealTimeConsultationPage.tsx    # 상담 중 페이지
/src/app/pages/AfterCallWorkPage.tsx           # 후처리 페이지
```

### 테스트 체크리스트
- [ ] 데스크톱(1920x1080)에서 말풍선 위치 확인
- [ ] 태블릿(768px ~ 1024px)에서 위치 확인
- [ ] 모바일(< 768px)에서 위치 확인
- [ ] 가이드 모드 진입/종료 플로우 검증
- [ ] localStorage 상태 동기화 확인
- [ ] 다이렉트 콜 차단 모달 동작 확인

---

## 📝 업데이트 이력
- **2025-01-28**: 문서 초안 작성
- **향후**: 각 항목 완료 시 업데이트 예정

---

## 💡 추가 아이디어 (선택사항)

### 가이드 진행률 시각화
```
상단 배너에 표시:
[가이드 모드] Step 2/8 | 대기콜 선택 단계
```

### 가이드 완료 후 복습 옵션
- 첫 가이드 완료 시: "처음부터 다시 보기" 버튼
- 특정 단계만 다시 보기 (가이드 메뉴)

### 첫 진입 시 선택지 제공
```
┌─────────────────────────────────┐
│  처음이신가요?                   │
│  ○ 가이드와 함께 시작하기 (추천) │
│  ○ 직접 시작하기                 │
└─────────────────────────────────┘
```

---

**문서 관리자**: CALL:ACT Development Team  
**최종 수정**: 2025-01-28
