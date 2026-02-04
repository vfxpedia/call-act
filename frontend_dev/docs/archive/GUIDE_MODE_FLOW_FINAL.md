# 🎓 가이드 모드 완벽 플로우 (최종 완성)

> **작업일**: 2025-01-28  
> **버전**: 2.0 (완전 수정)  
> **상태**: ✅ 모든 연속성 문제 해결 완료  

---

## 🎯 핵심 원칙

### 가이드 모드 생명주기

```
도움말 클릭 (어느 페이지든)
  ↓
[가이드 모드 시작] (isGuideModeActive = true)
  ↓
Phase 1 가이드 (상담 중 페이지 - 대기콜 선택)
  ↓ (가이드 모드 유지 ✅)
Phase 2 가이드 (통화 중)
  ↓ (가이드 모드 유지 ✅)
Phase 3 가이드 (후처리 페이지)
  ↓
[가이드 모드 종료] ← 여기서만 종료!
```

---

## 🔧 수정 사항 요약

### ❌ Before (문제 있음)

```typescript
// Phase 1 완료 시
if (tutorialPhase === 1) {
  setIsGuideModeActive(false);  // ❌ 여기서 종료하면 안 됨!
  console.log('✅ Phase 1 가이드 완료 → 가이드 모드 종료');
}

// Phase 2 완료 시
if (tutorialPhase === 2) {
  setIsGuideModeActive(false);  // ❌ 여기서 종료하면 안 됨!
  console.log('✅ Phase 2 가이드 완료 → 가이드 모드 종료');
}
```

**결과:**
- ❌ Phase 1 완료 → 가이드 모드 종료 → Phase 2 자동 시작 안 됨
- ❌ Phase 2 완료 → 가이드 모드 종료 → Phase 3 자동 시작 안 됨
- ❌ 다이렉트 콜 차단 안 됨 (isGuideModeActive = false)

---

### ✅ After (수정 완료)

```typescript
// Phase 1 완료 시
if (tutorialPhase === 1) {
  localStorage.setItem('tutorial-phase1-completed', 'true');
  setIsTutorialActive(false);
  
  // ⭐ 가이드 모드 유지! (종료하지 않음)
  console.log('✅ Phase 1 가이드 완료 → 가이드 모드 유지 (연속성)');
  
  if (activeScenario) {
    handleStartCall();  // 자동으로 통화 시작
  }
}

// Phase 2 완료 시
if (tutorialPhase === 2) {
  localStorage.setItem('tutorial-phase2-completed', 'true');
  setIsTutorialActive(false);
  
  // ⭐ 가이드 모드 유지! (Phase 3까지 연속성 확보)
  console.log('✅ Phase 2 가이드 완료 → 가이드 모드 유지 (Phase 3 대기)');
}

// Phase 3 완료 시 (후처리 페이지)
onComplete={() => {
  localStorage.setItem('tutorial-phase3-completed', 'true');
  setIsTutorialActive(false);
  
  // ⭐ 전체 가이드 완료 → 이제 종료!
  setIsGuideModeActive(false);
  localStorage.removeItem('isGuideModeActive');
  console.log('✅ [후처리] Phase 3 가이드 완료 → 가이드 모드 종료');
}}
```

**결과:**
- ✅ Phase 1 → Phase 2 → Phase 3 자동 연결
- ✅ 다이렉트 콜 차단 정상 작동
- ✅ 후처리 페이지 가이드 자동 시작

---

## 🎬 완벽한 사용자 시나리오

### 시나리오 1: 전체 가이드 플로우 (정상 케이스)

```
1. 교육 시뮬레이션 → 시작하기 클릭
   📍 상담 중 페이지 진입
   
2. 도움말 버튼 클릭
   ✅ isGuideModeActive = true
   ✅ localStorage.setItem('isGuideModeActive', 'true')
   
3. Phase 1 가이드 시작 (대기콜 선택 안내)
   - 3단계 가이드 진행
   - 다이렉트 콜 클릭 시 → ✅ 차단 모달 표시
   - 대기콜 선택
   
4. Phase 1 완료
   ✅ isGuideModeActive 유지 (true)
   ✅ 자동으로 통화 시작
   
5. Phase 2 가이드 시작 (통화 중 기능 안내)
   - 5단계 가이드 진행
   - STT, 키워드, 문서 검색 등 안내
   
6. Phase 2 완료 → 통화 종료 버튼 클릭
   ✅ isGuideModeActive 유지 (true)
   ✅ localStorage.removeItem('tutorial-phase3-completed')
   
7. 로딩 페이지 (3초)
   ✅ isGuideModeActive 유지됨
   
8. 후처리 페이지 진입
   ✅ isGuideModeActive 감지
   ✅ Phase 3 가이드 자동 시작!
   
9. Phase 3 가이드 완료
   ✅ isGuideModeActive = false
   ✅ localStorage.removeItem('isGuideModeActive')
   
10. 전체 가이드 종료 ✅
```

---

### 시나리오 2: 건너뛰기

```
1. 도움말 클릭 → Phase 1 시작
2. "건너뛰기" 클릭
   ✅ isGuideModeActive = false (즉시 종료)
   ✅ Phase 2, 3 자동 시작 안 됨 (정상)
3. 사용자가 자유롭게 실습
```

---

### 시나리오 3: 중간 건너뛰기

```
1. 도움말 클릭 → Phase 1 완료
2. Phase 2 시작
3. "건너뛰기" 클릭
   ✅ isGuideModeActive = false
   ✅ Phase 3 자동 시작 안 됨 (정상)
```

---

## 🔍 디버깅 로그 (정상 플로우)

### 상담 중 페이지

```javascript
// 도움말 클릭 시
🎓 도움말 버튼 클릭 → 가이드 모드 시작

// Phase 1 시작
🎓 가이드 모드: Phase 1 튜토리얼 시작

// Phase 1 완료
✅ Phase 1 가이드 완료 → 가이드 모드 유지 (연속성)
🎓 Phase 1 완료 → 자동 통화 시작 (시나리오 기반)

// Phase 2 시작
🎓 가이드 모드: Phase 2 튜토리얼 시작

// Phase 2 완료 → 통화 종료
✅ Phase 2 가이드 완료 → 가이드 모드 유지 (Phase 3 대기)
🎓 가이드 모드: Phase 3 완료 플래그 제거 → 후처리에서 자동 시작
```

### 후처리 페이지

```javascript
// 페이지 진입 시
🔍 [후처리] isGuideModeActive (state): true ✅
🔍 [후처리] localStorage.isGuideModeActive: "true" ✅
🔍 [후처리] localStorage.tutorial-phase3-completed: null ✅

// Phase 3 자동 시작
🎓 가이드 모드: Phase 3 튜토리얼 자동 시작 ✅

// Phase 3 완료
✅ [후처리] Phase 3 가이드 완료 → 가이드 모드 종료 ✅
```

---

## 🚫 다이렉트 콜 차단 (가이드 모드 전용)

### Before (작동 안 함)

```typescript
// Phase 1 완료 시 isGuideModeActive = false
// → 다이렉트 콜 차단 조건 미충족

if (isGuideModeActive && isSimulationMode) {  // false && true = false
  setShowDirectCallBlockModal(true);  // ❌ 실행 안 됨
}
```

### After (정상 작동)

```typescript
// Phase 1 완료 시에도 isGuideModeActive = true
// → 다이렉트 콜 차단 정상 작동

if (isGuideModeActive && isSimulationMode) {  // true && true = true
  console.log('🚫 가이드 모드: 다이렉트 콜 차단 → 대기콜 선택 유도');
  setShowDirectCallBlockModal(true);  // ✅ 차단 모달 표시
  return;  // 통화 시작 중단
}
```

**차단 모달 메시지:**
```
🎓 가이드 모드 안내

가이드 모드에서는 아래 대기콜 목록에서 선택해주세요.

💡 다이렉트 콜은 실제 STT와 백엔드 연동으로 가이드 미제공

[확인]
```

---

## 📊 가이드 모드 상태 관리

### localStorage 저장 항목

| 키 | 값 | 설명 |
|---|---|---|
| `isGuideModeActive` | `"true"` / null | 가이드 모드 활성화 여부 |
| `tutorial-phase1-completed` | `"true"` / null | Phase 1 완료 여부 |
| `tutorial-phase2-completed` | `"true"` / null | Phase 2 완료 여부 |
| `tutorial-phase3-completed` | `"true"` / null | Phase 3 완료 여부 |

### 초기화 시점

```typescript
// 교육 모드 진입 시 (상담 중 페이지)
localStorage.removeItem('tutorial-phase1-completed');
localStorage.removeItem('tutorial-phase2-completed');
localStorage.removeItem('tutorial-completed');

// 통화 종료 시 (가이드 모드일 때만)
if (isGuideModeActive) {
  localStorage.removeItem('tutorial-phase3-completed');
}

// Phase 3 완료 또는 건너뛰기 시
localStorage.removeItem('isGuideModeActive');
```

---

## ✅ 최종 체크리스트

- [x] Phase 1 완료 시 가이드 모드 유지
- [x] Phase 2 완료 시 가이드 모드 유지
- [x] Phase 3 완료 시에만 가이드 모드 종료
- [x] 건너뛰기 시 가이드 모드 즉시 종료
- [x] 다이렉트 콜 차단 정상 작동
- [x] 후처리 페이지 가이드 자동 시작
- [x] localStorage 상태 동기화
- [x] 디버깅 로그 완비
- [x] 전체 플로우 테스트 완료

---

## 🎉 결론

**가이드 모드의 연속성이 완벽히 구현되었습니다!**

- ✅ 도움말 1번 클릭으로 Phase 1 → 2 → 3 자동 진행
- ✅ 페이지 전환에도 가이드 모드 상태 유지
- ✅ 다이렉트 콜 차단으로 안전한 학습 보장
- ✅ 자연스러운 학습 흐름으로 교육 효율 극대화

**Flow Continuity (흐름 연속성) 원칙 100% 준수!** 🎯

---

**작성자**: CALL:ACT Development Team  
**검토자**: Product Manager  
**최종 승인**: 2025-01-28  
**버전**: 2.0 (완전 수정)
