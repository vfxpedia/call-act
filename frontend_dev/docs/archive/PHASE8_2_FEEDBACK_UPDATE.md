# Phase 8-2 피드백 모달 업데이트 (2026-01-20)

## 📋 개요

피드백 모달의 UX를 개선하여 업계 표준에 맞는 후처리 시간 평가 및 통화 시간 정보를 통합 표시합니다. 모든 평가 항목에 점수별 격려 메시지를 추가하여 상담사의 동기부여를 강화했습니다.

---

## 🎯 주요 개선 사항

### 1. 후처리 시간 기준 업계 표준 반영

**기존 기준 (문제):**
- 3분(180초) 이내 = 20점 만점
- 실제 업계 표준(45초~90초)보다 너무 느슨함

**개선된 기준 (카드사 콜센터 업계 표준):**

| 소요 시간 | 점수 | 메시지 | 설명 |
|----------|------|--------|------|
| 45초 이내 | 20점 | 🎉 완벽해요! | 업계 최고 수준 |
| 45초~1분 | 19점 | 👍 우수해요! | 매우 빠름 |
| 1분~1분 30초 | 18점 | ✅ 좋아요! | 표준 범위 |
| 1분 30초~2분 | 16점 | 💪 Good! | 양호 |
| 2분~2분 30초 | 14점 | ⏱️ 조금 더 빠르게! | 개선 필요 |
| 2분 30초~3분 | 12점 | 💡 시간 단축 필요 | 느림 |
| 3분 초과 | 10점 | ⚠️ 효율 개선 필요 | 매우 느림 |

**참고 문서:**
```
카드사 고객센터의 상담 후처리 시간(After Call Work, ACW) 및 관련 처리 시간은 
상담 유형과 업무 복잡도에 따라 다르지만, 통상적으로 다음과 같이 나뉩니다.

1. 일반적인 콜센터 후처리 시간 (통화 종료 후)
   - 평균 수준: 약 45초~1분 30초 내외
   - 카드사 특성: 본인 확인, 금융 거래 내역 기록 등으로 일반 소매업보다 조금 더 길 수 있음

2. AHT(평균 처리 시간): 
   - 상담원의 통화 시간 + 대기 시간 + 후처리 시간(ACW)
   - 카드 상담의 경우 8~15분 정도의 AHT 권장
```

---

### 2. AHT (Average Handle Time) 통합 표시

**새로 추가된 AHT 섹션:**

```
┌────────────────────────────────────────────┐
│ 💼 총 처리 시간 (AHT)                       │
├────────────────────────────────────────────┤
│  📞 통화 시간    ⏱️ 후처리 시간    💼 총 AHT │
│    5분 32초         1분 15초       6분 47초  │
│                                            │
│  업계 표준 대비: 양호 ✅                     │
│  (권장 AHT: 8~15분)                        │
└────────────────────────────────────────────┘
```

**AHT 평가 기준:**
- 8분 이내: "업계 표준 대비: 매우 우수 🌟"
- 8~12분: "업계 표준 대비: 양호 ✅"
- 12~15분: "업계 표준 대비: 보통 💼"
- 15분 초과: "업계 표준 대비: 개선 필요 💡"

---

### 3. 점수별 격려 메시지 추가

**모든 평가 항목에 메시지 추가:**

#### 1. 매뉴얼 준수 (50점 만점)
```typescript
if (percentage >= 96) return "✨ 완벽해요!";         // 48점 이상
if (percentage >= 90) return "🌟 우수해요!";         // 45점 이상
if (percentage >= 80) return "👍 잘했어요!";         // 40점 이상
if (percentage >= 70) return "💪 양호해요!";         // 35점 이상
return "📋 매뉴얼 재확인 필요";                      // 35점 미만
```

#### 2. 고객 감사 표현 (10점 만점)
```typescript
if (score >= 10) return "💖 고객이 매우 만족했어요!";
if (score >= 8) return "😊 좋은 응대였어요!";
if (score >= 5) return "🙂 만족스러운 상담!";
return "💬 고객 반응 확인 필요";
```

#### 3. 후처리 시간 (20점 만점)
```typescript
if (acwTimeSeconds <= 45) return "🎉 완벽해요!";
if (acwTimeSeconds <= 60) return "👍 우수해요!";
if (acwTimeSeconds <= 90) return "✅ 좋아요!";
if (acwTimeSeconds <= 120) return "💪 Good!";
if (acwTimeSeconds <= 150) return "⏱️ 조금 더 빠르게!";
if (acwTimeSeconds <= 180) return "💡 시간 단축 필요";
return "⚠️ 효율 개선 필요";
```

#### 4. 감정 전환 (20점 만점)
```typescript
// 부정 → 긍정 전환 성공
if (emotion.early === 'negative' && emotion.late === 'positive') {
  return "🎯 감정 전환 성공!";
}

// 중립 → 긍정 전환
if (emotion.early === 'neutral' && emotion.late === 'positive') {
  return "😊 긍정적 마무리!";
}

// 부정 → 중립 개선
if (emotion.early === 'negative' && emotion.late === 'neutral') {
  return "📈 개선 중이에요!";
}

// 점수 기반 메시지
if (score >= 18) return "🎯 훌륭한 감정 케어!";
if (score >= 15) return "😊 좋은 감정 전환!";
if (score >= 12) return "💪 양호한 응대!";
return "💡 감정 케어 필요";
```

---

### 4. UI 레이아웃 개선

**최종 레이아웃:**

```
┌──────────────────────────────────────────────────────┐
│ 🎯 상담 품질 피드백    90 / 100점 (우수)              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─── 좌측: 오각형 차트 ───┐  ┌─── 우측: 점수 ──┐  │
│  │                         │  │                  │  │
│  │   ⭐⭐⭐⭐⭐            │  │ 1. 매뉴얼 준수   │  │
│  │   (매뉴얼 준수)          │  │    - 🌟 우수해요!│  │
│  │                         │  │    45/50 (90%)  │  │
│  │   도입부, 응대, 설명,    │  │                  │  │
│  │   적극성, 정확성         │  │ 2. 고객 감사    │  │
│  │                         │  │    - 💖 매우 만족│  │
│  │   (280px 높이)          │  │    10/10 (100%) │  │
│  │                         │  │                  │  │
│  │                         │  │ 3. 후처리 시간   │  │
│  │                         │  │    - ⌛1분15초   │  │
│  │                         │  │    ✅ 좋아요!    │  │
│  │                         │  │    18/20 (90%)  │  │
│  │                         │  │                  │  │
│  │                         │  │ 4. 감정 전환     │  │
│  │                         │  │    - 😊 좋은 전환│  │
│  │                         │  │    15/20 (75%)  │  │
│  └─────────────────────────┘  └──────────────────┘  │
│                                                      │
│  ┌─── 💼 총 처리 시간 (AHT) ───────────────────┐   │
│  │  📞 통화: 5분32초 | ⏱️ 후처리: 1분15초 | 💼 AHT: 6분47초 │   │
│  │  업계 표준 대비: 양호 ✅ (권장: 8~15분)      │   │
│  └───────────────────────────────────────────┘   │
│                                                      │
│  감정 변화: 😠 부정 → 😐 중립 → 😊 긍정              │
│                                                      │
│  ⚠️ 개선 필요: 고객확인 시 정보 누출 (-5점)          │
│                                                      │
│  [▶ 매뉴얼 상세 점수 보기] (9개 항목)                │
│                                                      │
│  ☑️ 오늘 하루 보지 않기                              │
│         [닫기]        [확인]                         │
└──────────────────────────────────────────────────────┘
```

**주요 개선 포인트:**
1. ✅ 후처리 시간을 한 줄에 표시: `3. 후처리 - ⌛1분15초 ✅ 좋아요!`
2. ✅ 모든 항목에 격려 메시지 추가
3. ✅ AHT 섹션 추가 (통화 시간 + 후처리 시간 + 총 AHT)
4. ✅ 오각형 차트 숫자 겹침 해결 (숫자 숨김 + Tooltip 추가)
5. ✅ 시각적 통일성 확보

---

### 5. 오각형 차트 개선 (Option 2: 라벨에 점수 포함) ⭐

**문제점:**
- 숫자 "10"과 "도입부" 라벨이 겹쳐서 읽기 어려움

**해결 방법:**
```typescript
<PolarAngleAxis 
  dataKey="category" 
  tick={({ payload, x, y, textAnchor, index }: any) => {
    const data = radarData[index];
    return (
      <g>
        <text 
          x={x} 
          y={y - 5}               // 위로 5px
          textAnchor={textAnchor} 
          fill="#666666"          // 진한 회색
          fontSize="12"           // 크게
          fontWeight="500"        // 강조
        >
          {payload.value}         // 라벨 (도입부, 응대 등)
        </text>
        <text 
          x={x} 
          y={y + 9}               // 아래로 9px
          textAnchor={textAnchor} 
          fill="#999999"          // 연한 회색
          fontSize="9"            // 작게
        >
          ({data.score})          // 점수 (9.5, 10 등)
        </text>
      </g>
    );
  }}
/>
<PolarRadiusAxis 
  angle={90} 
  domain={[0, 10]} 
  tick={false}                    // 숫자 제거
/>
// Tooltip 제거 (불필요)
```

**효과:**
- ✅ 중복 정보 완전 제거
- ✅ 정보 손실 없음 (점수 항상 보임)
- ✅ 주객전도 방지 (라벨 크게, 점수 작게)
- ✅ Tooltip 불필요 → 가장 깔끔한 UX
- ✅ 항상 모든 정보 표시

**UI 예시:**
```
    도입부      ← fontSize: 12, #666666 (주)
     (9.5)      ← fontSize: 9, #999999 (보조)

     응대
     (10)

    설명
     (10)
```

---

## 📊 데이터 흐름

```
[상담 중 페이지]
통화 시작 (14:32) → 통화 종료 (14:37)
└─ localStorage.setItem('consultationCallTime', '300') // 5분 = 300초

[후처리 페이지]
진입 (14:37) → 저장 버튼 클릭 (14:38:15)
└─ acwTimeSeconds = 75 // 1분 15초

[피드백 모달]
- 통화 시간: localStorage.getItem('consultationCallTime') // 300초 = 5분
- 후처리 시간: acwTimeSeconds // 75초 = 1분 15초
- AHT: 300 + 75 = 375초 (6분 15초)
- 후처리 점수: calculateAcwTimeScore(75) // 18/20점
- 메시지: getAcwTimeMessage(75) // "✅ 좋아요!"
- AHT 평가: getAhtMessage(375) // "업계 표준 대비: 매우 우수 🌟"
```

---

## 🔧 수정된 파일

### 1. `/src/data/feedbackRules.ts` ⭐ 대폭 개선

**추가된 함수들:**

```typescript
// ⭐ 매뉴얼 준수 메시지 함수
export function getManualComplianceMessage(score: number): string {
  const percentage = (score / 50) * 100;
  if (percentage >= 96) return "✨ 완벽해요!";
  if (percentage >= 90) return "🌟 우수해요!";
  if (percentage >= 80) return "👍 잘했어요!";
  if (percentage >= 70) return "💪 양호해요!";
  return "📋 매뉴얼 재확인 필요";
}

// ⭐ 고객 감사 표현 메시지 함수
export function getGratitudeMessage(score: number): string {
  if (score >= 10) return "💖 고객이 매우 만족했어요!";
  if (score >= 8) return "😊 좋은 응대였어요!";
  if (score >= 5) return "🙂 만족스러운 상담!";
  return "💬 고객 반응 확인 필요";
}

// ⭐ 후처리 시간 메시지 함수
export function getAcwTimeMessage(acwTimeSeconds: number): string {
  if (acwTimeSeconds <= 45) return "🎉 완벽해요!";
  if (acwTimeSeconds <= 60) return "👍 우수해요!";
  if (acwTimeSeconds <= 90) return "✅ 좋아요!";
  if (acwTimeSeconds <= 120) return "💪 Good!";
  if (acwTimeSeconds <= 150) return "⏱️ 조금 더 빠르게!";
  if (acwTimeSeconds <= 180) return "💡 시간 단축 필요";
  return "⚠️ 효율 개선 필요";
}

// ⭐ AHT (Average Handle Time) 평가 메시지
export function getAhtMessage(ahtSeconds: number): string {
  const ahtMinutes = Math.floor(ahtSeconds / 60);
  if (ahtMinutes <= 8) return "업계 표준 대비: 매우 우수 🌟";
  if (ahtMinutes <= 12) return "업계 표준 대비: 양호 ✅";
  if (ahtMinutes <= 15) return "업계 표준 대비: 보통 💼";
  return "업계 표준 대비: 개선 필요 💡";
}

// ⭐ 감정 전환 메시지 함수
export function getEmotionTransitionMessage(score: number, emotion: EmotionAnalysis): string {
  // 부정 → 긍정 전환 성공
  if (emotion.early === 'negative' && emotion.late === 'positive') {
    return "🎯 감정 전환 성공!";
  }
  
  // 중립 → 긍정 전환
  if (emotion.early === 'neutral' && emotion.late === 'positive') {
    return "😊 긍정적 마무리!";
  }
  
  // 부정 → 중립 개선
  if (emotion.early === 'negative' && emotion.late === 'neutral') {
    return "📈 개선 중이에요!";
  }
  
  // 점수 기반 메시지
  if (score >= 18) return "🎯 훌륭한 감정 케어!";
  if (score >= 15) return "😊 좋은 감정 전환!";
  if (score >= 12) return "💪 양호한 응대!";
  return "💡 감정 케어 필요";
}
```

**업데이트된 함수:**

```typescript
// ⭐ 업계 표준 기준 (카드사 콜센터)
export const acwTimeStandard = {
  perfect: 45,      // 45초 이내: 완벽
  excellent: 60,    // 1분 이내: 우수
  good: 90,         // 1분 30초 이내: 좋음
  acceptable: 120,  // 2분 이내: 양호
  needImprovement: 150, // 2분 30초: 개선 필요
  slow: 180,        // 3분: 느림
};

export function calculateAcwTimeScore(acwTimeSeconds: number): number {
  if (acwTimeSeconds <= 45) return 20;   // 45초 이내: 완벽! 🎉
  if (acwTimeSeconds <= 60) return 19;   // 1분 이내: 우수! 👍
  if (acwTimeSeconds <= 90) return 18;   // 1분 30초 이내: 좋아요! ✅
  if (acwTimeSeconds <= 120) return 16;  // 2분 이내: Good! 💪
  if (acwTimeSeconds <= 150) return 14;  // 2분 30초: 조금 더 빠르게! ⏱️
  if (acwTimeSeconds <= 180) return 12;  // 3분: 개선 필요 💡
  return 10;                              // 3분 초과: 효율 개선 필요 ⚠️
}
```

---

### 2. `/src/app/components/modals/FeedbackModal.tsx` ⭐ 완전 재작성

**주요 변경 사항:**

1. **Props 추가:**
```typescript
interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  acwTimeSeconds?: number;      // ⭐ 실제 후처리 시간
  callTimeSeconds?: number;     // ⭐ 통화 시간
}
```

2. **AHT 계산 로직 추가:**
```typescript
const actualCallTime = callTimeSeconds > 0 
  ? callTimeSeconds 
  : parseInt(localStorage.getItem('consultationCallTime') || '0');
const ahtSeconds = actualCallTime + (acwTimeSeconds > 0 ? acwTimeSeconds : 0);
const ahtDisplay = formatTime(ahtSeconds);
```

3. **메시지 함수 호출:**
```typescript
const manualMessage = getManualComplianceMessage(mockFeedbackData.manualCompliance);
const gratitudeMessage = getGratitudeMessage(mockFeedbackData.customerGratitude);
const acwMessage = getAcwTimeMessage(acwTimeSeconds > 0 ? acwTimeSeconds : mockFeedbackData.acwTimeSeconds);
const emotionMessage = getEmotionTransitionMessage(mockFeedbackData.emotionTransition, mockFeedbackData.emotion);
const ahtMessage = getAhtMessage(ahtSeconds);
```

4. **UI 개선:**
   - 후처리 시간 한 줄 표시: `3. 후처리 - ⌛1분15초 ✅ 좋아요!`
   - AHT 섹션 추가 (3열 그리드)
   - 오각형 차트 숫자 숨김 + Tooltip 추가
   - 모든 항목에 메시지 표시

---

### 3. `/src/app/pages/AfterCallWorkPage.tsx` ⭐ 수정

**변경 사항:**

```typescript
// ⭐ Phase 8-2: 피드백 모달에 통화 시간 전달
<FeedbackModal
  isOpen={isFeedbackModalOpen}
  onClose={() => setIsFeedbackModalOpen(false)}
  onConfirm={handleFeedbackConfirm}
  acwTimeSeconds={getCurrentAcwTime()}
  callTimeSeconds={parseInt(localStorage.getItem('consultationCallTime') || '0')}
/>
```

---

## 🎨 UI/UX 개선 효과

### Before (기존):
```
3. 후처리 시간      20/20

⏱️ 2분 15초  소요

━━━━━━━━━━━ 100%
100%
```
→ 시각적으로 분리되어 있고, 메시지 없음

### After (개선):
```
3. 후처리 - ⌛1분15초 ✅ 좋아요!     18/20
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 90%
90%
```
→ 한 줄로 정리되고, 격려 메시지로 즉각 피드백

### 🎯 최종 UI 개선 (2026-01-20 추가) ⭐⭐⭐

**1. 메시지 크기 축소**
```
Before: 1. 매뉴얼 준수 - 🌟 우수해요!  (text-sm, 같은 크기)
After:  1. 매뉴얼 준수 - 🌟 우수해요!  (text-xs, 작고 연함)
        └─ 제목 강조, 메시지 보조
```

**효과:**
- ✅ 정보 계층 명확: 제목(크게) > 메시지(작게)
- ✅ 메시지는 독려/칭찬 용도로 보조적 표시
- ✅ 잘한 사람은 칭찬, 못한 사람은 독려

**2. 오각형 차트 개선**
```
Before: 
- 숫자 완전 숨김
- Tooltip: "도입부 9.5" (중복!)
- 애니메이션 부자연스러움

After (Option 2):
- 라벨에 점수 포함: "도입부 (9.5)"
- 라벨 크게, 점수 작게 표시
- Tooltip 완전 제거 (불필요)
- 커스텀 렌더링으로 2줄 표시
```

**효과:**
- ✅ 중복 정보 완전 제거
- ✅ 정보 손실 없음 (점수 항상 보임)
- ✅ 주객전도 방지 (라벨 크게, 점수 작게)
- ✅ Tooltip 불필요 → 가장 깔끔한 UX
- ✅ 항상 모든 정보 표시

---

## 📱 동작 흐름

1. **후처리 페이지 진입**
   - `acwStartTime = Date.now()` 기록

2. **"후처리 완료 및 저장" 클릭**
   - "오늘 하루 보지 않기" 확인
   - 피드백 모달 표시

3. **피드백 모달 표시**
   - `getCurrentAcwTime()` 호출로 실시간 시간 계산
   - localStorage에서 통화 시간 읽기
   - AHT 계산 및 표시
   - 점수별 메시지 표시

4. **"확인" 클릭**
   - `handleSaveACW()` 실행
   - 최종 시간 계산 및 DB 저장
   - localStorage 초기화
   - 상담 중 페이지로 이동

---

## 🧪 테스트 시나리오

### Test 1: 후처리 시간 메시지 확인
1. 후처리 페이지 진입
2. **30초 대기** → 저장 클릭
3. 피드백 모달 확인: `⌛0분30초 🎉 완벽해요!` ✅

### Test 2: AHT 표시 확인
1. 통화 시간 5분 (300초)
2. 후처리 시간 1분 15초 (75초)
3. 피드백 모달 확인:
   - 📞 통화 시간: 5분0초
   - ⏱️ 후처리 시간: 1분15초
   - 💼 총 AHT: 6분15초
   - 업계 표준 대비: 매우 우수 🌟

### Test 3: 모든 항목 메시지 확인
1. 매뉴얼 준수 45/50 → `🌟 우수해요!`
2. 고객 감사 10/10 → `💖 고객이 매우 만족했어요!`
3. 후처리 시간 1분 → `👍 우수해요!`
4. 감정 전환 15/20 → `😊 좋은 감정 전환!`

---

## 📝 Backend 연동 준비

### Frontend에서 전달할 데이터:
```typescript
const acwData = {
  // ... 기존 데이터
  acwTimeSeconds: 75,           // ⭐ 후처리 시간 (초)
  callTimeSeconds: 300,         // ⭐ 통화 시간 (초)
  ahtSeconds: 375,              // ⭐ AHT (초)
};
```

### Backend에서 받을 데이터 (LLM 분석):
```typescript
{
  feedbackScore: {
    manualCompliance: 45,       // 매뉴얼 준수 점수
    customerGratitude: 10,      // 고객 감사 표현 점수
    acwTime: 18,                // 후처리 시간 점수 (자동 계산)
    emotionTransition: 15,      // 감정 전환 점수
    total: 88,                  // 총점
    
    manualDetails: {            // 매뉴얼 상세 점수
      greeting: 0,
      customerCheck: -5,
      empathy: 0,
      // ...
    },
    
    emotion: {                  // 감정 분석
      early: 'negative',
      middle: 'neutral',
      late: 'positive',
    },
  }
}
```

---

## ✅ 완료 기준

- [x] feedbackRules.ts에 메시지 함수 추가
- [x] 후처리 시간 기준 업계 표준으로 변경 (45초 기준)
- [x] AHT 섹션 추가
- [x] 모든 평가 항목에 메시지 추가
- [x] 오각형 차트 숫자 겹침 해결
- [x] 한 줄 레이아웃으로 개선
- [x] 통화 시간 props 전달
- [x] 시각적 통일성 확보
- [x] 문서화 완료

---

## 🚀 다음 단계

1. **Backend API 연동**
   - LLM에서 실제 점수 받기
   - STT 전문 분석 결과 적용

2. **추가 개선 사항**
   - 이전 상담과 비교 기능
   - 주간/월간 통계 그래프
   - 개인 성장 곡선 표시

---

**Phase 8-2 업데이트 완료!** 🎉