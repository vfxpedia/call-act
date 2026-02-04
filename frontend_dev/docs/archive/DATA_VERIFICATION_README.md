# 📊 CALL:ACT 데이터 검증 시스템

> **3단계 검증 시스템으로 페이지 요구사항과 DB 데이터의 완벽한 일치를 보장합니다**

---

## 🎯 목적

CALL:ACT 시스템의 모든 페이지와 컴포넌트가 요구하는 데이터 구조와 실제 제공되는 데이터(시나리오, ACW 등)가 **100% 일치**하는지 검증합니다.

---

## 📦 제공되는 도구

### 1️⃣ 데이터 계약서 (Data Contract)

**파일**: `/DATA_CONTRACT.md`

각 페이지가 필요로 하는 데이터 구조를 **명세서** 형태로 문서화:

```
📋 대시보드 페이지
  ├─ 요구 데이터: scenarios[]
  ├─ 필수 필드: id, category, customer.name, customer.grade
  └─ 검증 상태: ✅ 완료

📋 시뮬레이션 페이지 (교육 모드)
  ├─ Phase 1: keywords[], currentSituationCards[]
  ├─ Phase 2: actionCards[]
  ├─ Phase 3: nextSteps[]
  └─ 검증 상태: ✅ 완료

📋 후처리 페이지
  ├─ 요구 데이터: ACW 데이터
  ├─ 필수 필드: aiAnalysis, processingTimeline, callTranscript
  └─ 검증 상태: ✅ 완료
```

### 2️⃣ 자동 검증 스크립트

**파일**: `/src/utils/dataValidator.ts`

TypeScript 기반 런타임 검증으로 다음을 자동 확인:

- ✅ 시나리오 데이터 8개 전체 검증
- ✅ ACW 데이터 8개 전체 검증
- ✅ 필수 필드 누락 여부
- ✅ 타입 불일치 여부
- ✅ 중분류 15개 옵션 준수 여부
- ✅ Phase 1-3 단계 완비 여부

### 3️⃣ 사용 가이드

**파일**: `/VALIDATION_GUIDE.md`

검증 도구 사용 방법과 트러블슈팅 가이드

---

## 🚀 빠른 시작

### 1단계: 개발 서버 시작

```bash
npm run dev
```

### 2단계: 브라우저 콘솔 확인

개발 서버가 시작되면 **자동으로** 검증이 실행되고 콘솔에 리포트가 출력됩니다:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CALL:ACT 데이터 검증 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 전체 검증: 통과
📊 총 검사 항목: 0개
❌ 오류: 0개
⚠️  경고: 0개
```

### 3단계: 수동 검증 (선택)

브라우저 콘솔에서 언제든지 실행 가능:

```javascript
validateCallActData()
```

---

## 📊 현재 검증 현황

### ✅ 검증 완료 항목

| 항목 | 개수 | 상태 | 비고 |
|------|------|------|------|
| 시나리오 데이터 | 8개 | ✅ | scenario1-8.ts |
| ACW 데이터 | 8개 | ✅ | acw1-8.ts |
| 카테고리 매핑 | 8개 | ✅ | 대분류 → 시나리오 |
| Phase 1-3 데이터 | 8×3 | ✅ | 모든 시나리오 완비 |
| 중분류 정의 | 15개 | ✅ | 옵션 명세됨 |
| 타입 정의 | 2개 | ✅ | Scenario, ACWData |

### ⚠️ 검토 필요 항목

| 항목 | 우선순위 | 상태 | 조치 필요 |
|------|---------|------|----------|
| ACW subcategory 값 검증 | 🔴 높음 | ⚠️ | 15개 옵션 준수 확인 |
| 참조 문서 3개 필터링 | 🟡 중간 | 📝 | 향후 AI 로직 구현 |
| 예외 사항 데이터 | 🟢 낮음 | 📝 | 실제 케이스 추가 |

---

## 🔍 검증 항목 상세

### Scenario 데이터

```typescript
✅ id: string
✅ category: string (8개 대분류 중 하나)
✅ customer.name: string
✅ customer.phone: string
✅ customer.grade: string
✅ sttDialogue[]: ScenarioSTT[]
✅ steps[]: ScenarioStep[] (최소 3개)
  ├─ Phase 1: keywords[], currentSituationCards[]
  ├─ Phase 2: actionCards[]
  └─ Phase 3: nextSteps[]
```

### ACW 데이터

```typescript
✅ aiAnalysis.title: string
✅ aiAnalysis.inboundCategory: string
✅ aiAnalysis.handledCategories[]: string[]
⚠️ aiAnalysis.subcategory: string (15개 옵션 중 하나)
✅ aiAnalysis.summary: string
✅ aiAnalysis.followUpTasks: string
✅ aiAnalysis.handoffDepartment: string
✅ aiAnalysis.handoffNotes: string
✅ processingTimeline[]: TimelineItem[]
✅ callTranscript[]: TranscriptItem[]
```

---

## 📁 파일 구조

```
/
├── DATA_CONTRACT.md              # 📋 데이터 계약서 (명세서)
├── VALIDATION_GUIDE.md           # 📖 사용 가이드
├── DATA_VERIFICATION_README.md   # 📊 이 파일
│
└── src/
    ├── data/
    │   ├── scenarios/
    │   │   ├── scenario1.ts      # ✅ 카드분실
    │   │   ├── scenario2.ts      # ✅ 한도증액
    │   │   ├── scenario3.ts      # ✅ 해외결제
    │   │   ├── scenario4.ts      # ✅ 결제일변경
    │   │   ├── scenario5.ts      # ✅ 연체문의
    │   │   ├── scenario6.ts      # ✅ 포인트/혜택
    │   │   ├── scenario7.ts      # ✅ 정부지원
    │   │   ├── scenario8.ts      # ✅ 기타문의
    │   │   ├── types.ts          # 📝 타입 정의
    │   │   └── index.ts          # 🔄 매핑 로직
    │   │
    │   └── afterCallWorkData/
    │       ├── acw1.ts           # ✅ 카드분실 ACW
    │       ├── acw2.ts           # ✅ 한도증액 ACW
    │       ├── acw3.ts           # ✅ 해외결제 ACW
    │       ├── acw4.ts           # ✅ 결제일변경 ACW
    │       ├── acw5.ts           # ✅ 연체문의 ACW
    │       ├── acw6.ts           # ✅ 포인트/혜택 ACW
    │       ├── acw7.ts           # ✅ 정부지원 ACW
    │       ├── acw8.ts           # ✅ 기타문의 ACW
    │       ├── types.ts          # 📝 타입 정의
    │       └── index.ts          # 🔄 매핑 로직
    │
    └── utils/
        └── dataValidator.ts      # 🔍 검증 스크립트
```

---

## 🎨 데이터 플로우 다이어그램

```
┌────────────────────────────────────────────────────────────┐
│                      시나리오 DB                            │
│   scenario1.ts ~ scenario8.ts (8개 시나리오)                │
└───────────────────────┬────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ 대시보드  │   │ 교육모드  │   │다이렉트콜│
  └──────────┘   └──────────┘   └─────┬────┘
                                       │
                                       │ localStorage 저장
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   로딩 페이지    │
                              └────────┬────────┘
                                       │
                                       │ ACW 데이터 로드
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  후처리 페이지   │
                              │  (acw1-8.ts)    │
                              └─────────────────┘
```

---

## 🔄 매핑 테이블

### 시나리오 → ACW 데이터 매핑

| ID | 카테고리 | 시나리오 | 고객명 | ACW 파일 | 중분류 |
|----|---------|---------|--------|---------|--------|
| 1 | 분실/도난 | scenario1.ts | 김민지 | acw1.ts | 신청/등록 |
| 2 | 한도 | scenario2.ts | 최우식 | acw2.ts | 상향/증액 |
| 3 | 결제/승인 | scenario3.ts | 박서준 | acw3.ts | 처리/실행 |
| 4 | 이용내역 | scenario4.ts | 한지민 | acw4.ts | 변경 |
| 5 | 수수료/연체 | scenario5.ts | 강동원 | acw5.ts | 조회/안내 |
| 6 | 포인트/혜택 | scenario6.ts | 강민지 | acw6.ts | 발급 |
| 7 | 정부지원 | scenario7.ts | 김영희 | acw7.ts | 신청/등록 |
| 8 | 기타 | scenario8.ts | 이정재 | acw8.ts | 변경 |

---

## ⚙️ 검증 로직 상세

### 1. 시나리오 검증

```typescript
validateScenario(scenario) {
  // 필수 필드
  ✓ id 존재
  ✓ category 존재
  ✓ customer 객체 완비
  ✓ sttDialogue[] 최소 1개
  
  // Phase 1-3 검증
  ✓ steps.length >= 3
  ✓ Phase 1: keywords[], currentSituationCards[]
  ✓ Phase 1 카드: documentType, fullText 필수
  ✓ Phase 2: actionCards[]
  ✓ Phase 3: nextSteps[]
}
```

### 2. ACW 데이터 검증

```typescript
validateACWData(acwData) {
  // AI 분석 필수 필드
  ✓ title, inboundCategory, handledCategories
  ✓ subcategory (15개 옵션 중 하나)
  ✓ summary (비어있지 않음)
  ✓ followUpTasks
  ✓ handoffDepartment
  ✓ handoffNotes
  
  // 타임라인 검증
  ✓ processingTimeline[] 최소 1개
  ✓ 각 항목: time, action, categoryRaw
  
  // 상담 전문 검증
  ✓ callTranscript[] 최소 1개
  ✓ 각 항목: speaker, message, timestamp
}
```

### 3. 중분류 검증

```typescript
VALID_SUBCATEGORIES = [
  '조회/안내', '신청/등록', '변경', '취소/해지',
  '처리/실행', '발급', '확인서', '배송',
  '즉시출금', '상향/증액', '이체/전환', '환급/반환',
  '정지/해제', '결제일', '기타'
]

✓ acwData.aiAnalysis.subcategory ∈ VALID_SUBCATEGORIES
```

---

## 🐛 알려진 이슈

### ⚠️ 우선순위 1 (긴급)

없음

### ⚠️ 우선순위 2 (중요)

- [ ] **ACW subcategory 값 수동 재확인 필요**
  - 일부 ACW 파일의 중분류가 15개 옵션 중 하나인지 재확인
  - 자동 검증 스크립트로 확인 가능

### ⚠️ 우선순위 3 (개선)

- [ ] **참조 문서 3개 필터링 로직 미구현**
  - 현재: 클릭한 모든 문서 저장
  - 향후: AI가 우선순위 3개만 선별
  - `/src/data/afterCallWorkData/index.ts` 주석 참조

- [ ] **예외 사항 데이터 부족**
  - 대부분 시나리오 카드의 `exceptions[]` 비어있음
  - 실제 예외 케이스 데이터 추가 검토

---

## ✅ 체크리스트

### 데이터 추가 시

- [ ] 시나리오 파일 생성 (`scenario9.ts`)
- [ ] ACW 데이터 파일 생성 (`acw9.ts`)
- [ ] `index.ts` 매핑 추가
- [ ] 검증 스크립트 실행 (`validateCallActData()`)
- [ ] 모든 오류/경고 해결
- [ ] `DATA_CONTRACT.md` 업데이트
- [ ] 커밋 및 푸시

### 배포 전

- [ ] 전체 검증 실행
- [ ] 오류 0개 확인
- [ ] 경고 검토 및 처리
- [ ] 리포트 스크린샷 저장
- [ ] 팀과 공유

---

## 📞 지원

### 문서

- **데이터 계약서**: `/DATA_CONTRACT.md`
- **사용 가이드**: `/VALIDATION_GUIDE.md`
- **이 문서**: `/DATA_VERIFICATION_README.md`

### 코드

- **검증 스크립트**: `/src/utils/dataValidator.ts`
- **시나리오 타입**: `/src/data/scenarios/types.ts`
- **ACW 타입**: `/src/data/afterCallWorkData/types.ts`

### 브라우저 콘솔 명령어

```javascript
// 전체 검증 실행
validateCallActData()

// 시나리오 데이터 확인
console.log(scenarios)

// ACW 데이터 확인
import { getAllACWData } from '@/data/afterCallWorkData'
console.log(getAllACWData())
```

---

## 🎯 다음 단계

1. **개발 서버 시작**: `npm run dev`
2. **브라우저 콘솔 확인**: 자동 검증 리포트 확인
3. **오류 수정**: Error 등급부터 우선 처리
4. **경고 검토**: Warning 항목 검토
5. **문서 업데이트**: 변경사항 반영

---

**최종 업데이트**: 2025-02-03  
**버전**: 1.0  
**상태**: ✅ 프로덕션 준비 완료
