# 📋 CALL:ACT 데이터 계약서 (Data Contract)

> **목적**: 각 페이지/컴포넌트가 요구하는 데이터 구조와 실제 제공되는 데이터의 일치 여부를 검증  
> **작성일**: 2025-02-03  
> **버전**: 1.0

---

## 📊 전체 데이터 플로우 개요

```
┌─────────────────┐
│   시나리오 DB    │ scenarios/*.ts
└────────┬────────┘
         │
         ├──→ [대시보드] 카드 리스트 표시
         │
         ├──→ [교육 모드] 시나리오 선택 & 단계별 진행
         │
         └──→ [다이렉트 콜] 실시간 상담 데이터 제공
                │
                └──→ localStorage 저장
                         │
                         └──→ [후처리 페이지] ACW 데이터 로드
```

---

## 1️⃣ 대시보드 페이지 (DashboardPage)

### 📥 요구 데이터

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `scenarios[]` | `Scenario[]` | `/data/scenarios/index.ts` | ✅ | 전체 시나리오 목록 |
| `scenarios[].id` | `string` | 시나리오 파일 | ✅ | 시나리오 고유 ID |
| `scenarios[].category` | `string` | 시나리오 파일 | ✅ | 대분류 카테고리 |
| `scenarios[].customer.name` | `string` | 시나리오 파일 | ✅ | 고객명 |
| `scenarios[].customer.grade` | `string` | 시나리오 파일 | ✅ | 고객 등급 |

### ✅ 검증 상태

- [x] 타입 정의 존재: `/src/data/scenarios/types.ts`
- [x] 데이터 제공: 8개 시나리오 모두 제공
- [x] 필수 필드 완비
- [ ] **검토 필요**: 추가 필터링 옵션 (등급별, 난이도별)

---

## 2️⃣ 교육 모드 - 시뮬레이션 페이지 (SimulationPage)

### 📥 요구 데이터

#### A. 시나리오 선택 단계

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `scenario.customer` | `CustomerInfo` | 시나리오 파일 | ✅ | 고객 정보 |
| `scenario.customer.name` | `string` | 시나리오 파일 | ✅ | 고객명 |
| `scenario.customer.phone` | `string` | 시나리오 파일 | ✅ | 전화번호 |
| `scenario.customer.cardNumber` | `string` | 시나리오 파일 | ✅ | 카드번호 |
| `scenario.customer.grade` | `string` | 시나리오 파일 | ✅ | 등급 |
| `scenario.recentConsultations[]` | `RecentConsultation[]` | 시나리오 파일 | ⚠️ | 최근 상담 이력 (선택) |

#### B. Phase 1 - 상황 분석

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `steps[0].keywords[]` | `ScenarioKeyword[]` | 시나리오 파일 | ✅ | 키워드 목록 |
| `steps[0].keywords[].text` | `string` | 시나리오 파일 | ✅ | 키워드 텍스트 |
| `steps[0].keywords[].appearTime` | `number` | 시나리오 파일 | ✅ | 출현 시간 |
| `steps[0].currentSituationCards[]` | `ScenarioCard[]` | 시나리오 파일 | ✅ | 상황 분석 카드 |
| `steps[0].currentSituationCards[].title` | `string` | 시나리오 파일 | ✅ | 카드 제목 |
| `steps[0].currentSituationCards[].fullText` | `string` | 시나리오 파일 | ✅ | 전체 문서 내용 |
| `steps[0].currentSituationCards[].documentType` | `DocumentType` | 시나리오 파일 | ✅ | 문서 타입 |

#### C. Phase 2 - 대응 방안

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `steps[1].actionCards[]` | `ScenarioCard[]` | 시나리오 파일 | ✅ | 대응 방안 카드 |
| `steps[1].actionCards[].requiredChecks[]` | `string[]` | 시나리오 파일 | ✅ | 필수 확인 사항 |
| `steps[1].actionCards[].exceptions[]` | `string[]` | 시나리오 파일 | ⚠️ | 예외 사항 |

#### D. Phase 3 - 후처리

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `steps[2].nextSteps[]` | `string[]` | 시나리오 파일 | ✅ | 다음 단계 |

### ✅ 검증 상태

- [x] 타입 정의 존재
- [x] 8개 시나리오 모두 Phase 1-3 데이터 보유
- [x] documentType 필드 존재
- [x] 키워드 출현 시간 정의됨
- [ ] **검토 필요**: `exceptions` 배열 비어있는 카드 존재

---

## 3️⃣ 다이렉트 콜 - 실시간 상담 페이지 (RealTimeConsultationPage)

### 📥 요구 데이터

#### A. 통화 시작 시

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `inboundCase.category` | `string` | localStorage | ✅ | 인입 케이스 대분류 |
| `inboundCase.subcategory` | `string` | localStorage | ⚠️ | 소분류 (선택) |

**매핑 로직**:
```typescript
category → getScenarioByCategory() → Scenario 객체
```

#### B. 상담 중

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `scenario.sttDialogue[]` | `ScenarioSTT[]` | 시나리오 파일 | ✅ | STT 대화 내역 |
| `scenario.sttDialogue[].speaker` | `'agent' \| 'customer'` | 시나리오 파일 | ✅ | 발화자 |
| `scenario.sttDialogue[].message` | `string` | 시나리오 파일 | ✅ | 메시지 내용 |
| `scenario.sttDialogue[].timestamp` | `number` | 시나리오 파일 | ✅ | 타임스탬프 |

#### C. 참조 문서 클릭 시

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `card.documentType` | `DocumentType` | 시나리오 카드 | ✅ | 문서 타입 |
| `card.fullText` | `string` | 시나리오 카드 | ✅ | 문서 전체 내용 |
| `card.title` | `string` | 시나리오 카드 | ✅ | 문서 제목 |

**저장 로직**:
```typescript
localStorage.setItem('referencedDocuments', JSON.stringify([
  { type: card.documentType, title: card.title, fullText: card.fullText }
]))
```

### ✅ 검증 상태

- [x] 시나리오 매핑 로직 정상 작동
- [x] STT 대화 데이터 존재
- [x] 참조 문서 저장 기능 구현
- [✅] **최근 수정**: STT 메시지 별도 state 관리로 분리

---

## 4️⃣ 후처리 페이지 (AfterCallWorkPage)

### 📥 요구 데이터

#### A. localStorage에서 로드

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `currentScenarioId` | `string` | localStorage | ✅ | 현재 시나리오 ID |
| `callDuration` | `number` | localStorage | ✅ | 통화 시간 (초) |
| `sttMessages` | `ScenarioSTT[]` | localStorage | ✅ | STT 대화 전문 |
| `referencedDocuments` | `Document[]` | localStorage | ⚠️ | 참조 문서 목록 |

#### B. ACW 데이터 로드

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `acwData.aiAnalysis` | `object` | ACW 파일 | ✅ | AI 분석 데이터 |
| `acwData.aiAnalysis.title` | `string` | ACW 파일 | ✅ | 상담 제목 |
| `acwData.aiAnalysis.inboundCategory` | `string` | ACW 파일 | ✅ | 인입 카테고리 |
| `acwData.aiAnalysis.handledCategories[]` | `string[]` | ACW 파일 | ✅ | 처리한 카테고리 |
| `acwData.aiAnalysis.subcategory` | `string` | ACW 파일 | ✅ | 중분류 (15개 옵션) |
| `acwData.aiAnalysis.summary` | `string` | ACW 파일 | ✅ | AI 상담 요약본 |
| `acwData.aiAnalysis.followUpTasks` | `string` | ACW 파일 | ✅ | 추후 할 일 |
| `acwData.aiAnalysis.handoffDepartment` | `string` | ACW 파일 | ✅ | 이관 부서 |
| `acwData.aiAnalysis.handoffNotes` | `string` | ACW 파일 | ✅ | 이관 전달사항 |

#### C. 처리 타임라인

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `acwData.processingTimeline[]` | `TimelineItem[]` | ACW 파일 | ✅ | 처리 타임라인 |
| `acwData.processingTimeline[].time` | `string` | ACW 파일 | ✅ | 시간 (HH:mm:ss) |
| `acwData.processingTimeline[].action` | `string` | ACW 파일 | ✅ | 처리 내역 |
| `acwData.processingTimeline[].categoryRaw` | `string \| null` | ACW 파일 | ✅ | 처리 카테고리 |

#### D. 상담 전문

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `acwData.callTranscript[]` | `TranscriptItem[]` | ACW 파일 | ✅ | 상담 전문 |
| `acwData.callTranscript[].speaker` | `'agent' \| 'customer'` | ACW 파일 | ✅ | 발화자 |
| `acwData.callTranscript[].message` | `string` | ACW 파일 | ✅ | 메시지 |
| `acwData.callTranscript[].timestamp` | `string` | ACW 파일 | ✅ | 시간 (HH:mm) |

### 📦 ACW 데이터 매핑 테이블

| 인입 카테고리 | 시나리오 ID | ACW 파일 | 고객명 | 상태 |
|--------------|------------|---------|--------|------|
| 분실/도난 | scenario-1 | acw1.ts | 김민지 | ✅ |
| 한도 | scenario-2 | acw2.ts | 최우식 | ✅ |
| 결제/승인 | scenario-3 | acw3.ts | 박서준 | ✅ |
| 이용내역 | scenario-4 | acw4.ts | 한지민 | ✅ |
| 수수료/연체 | scenario-5 | acw5.ts | 강동원 | ✅ |
| 포인트/혜택 | scenario-6 | acw6.ts | 강민지 | ✅ |
| 정부지원 | scenario-7 | acw7.ts | 김영희 | ✅ |
| 기타 | scenario-8 | acw8.ts | 이정재 | ✅ |

### ✅ 검증 상태

- [x] 타입 정의 존재: `/src/data/afterCallWorkData/types.ts`
- [x] 8개 ACW 데이터 파일 생성 완료
- [x] 중분류 15개 옵션 정의됨
- [x] localStorage 데이터 로드 로직 구현
- [x] 타이핑 애니메이션 분리 처리
- [ ] **검토 필요**: `referencedDocuments` 3개 제한 로직 미구현

---

## 5️⃣ 로딩 페이지 (LoadingPage)

### 📥 요구 데이터

| 필드 | 타입 | 출처 | 필수 | 설명 |
|------|------|------|------|------|
| `currentScenarioId` | `string` | localStorage | ✅ | 시나리오 ID |
| `callDuration` | `number` | localStorage | ✅ | 통화 시간 |

**기능**: 
- 3초 대기 후 `/after-call-work`로 리디렉션
- 애니메이션 효과 표시

### ✅ 검증 상태

- [x] 데이터 로드 정상
- [x] 리디렉션 로직 정상

---

## 🔍 중요 타입 정의 검증

### Scenario 타입

```typescript
interface Scenario {
  id: string;
  category: string;
  customer: CustomerInfo;
  recentConsultations: RecentConsultation[];
  sttDialogue: ScenarioSTT[];
  steps: ScenarioStep[];
}
```

**검증 결과**: ✅ 모든 시나리오 파일이 이 타입을 준수

### ACWData 타입

```typescript
interface ACWData {
  aiAnalysis: {
    title: string;
    inboundCategory: string;
    handledCategories: string[];
    subcategory: string;
    summary: string;
    followUpTasks: string;
    handoffDepartment: string;
    handoffNotes: string;
  };
  processingTimeline: TimelineItem[];
  callTranscript: TranscriptItem[];
}
```

**검증 결과**: ✅ 모든 ACW 파일이 이 타입을 준수

---

## ⚠️ 발견된 불일치 사항

### 1. 중분류 옵션 미사용
- **위치**: 후처리 페이지
- **문제**: 15개 중분류 옵션이 정의되어 있지만, ACW 데이터에 실제 적용 여부 미확인
- **권장 조치**: ACW 데이터의 `subcategory` 필드가 15개 옵션 중 하나인지 검증 필요

### 2. 참조 문서 3개 제한 미구현
- **위치**: 로딩 페이지 → 후처리 페이지
- **문제**: AI가 참조 문서를 3개로 필터링하는 로직이 아직 구현되지 않음
- **권장 조치**: 향후 AI 필터링 로직 추가 필요 (주석으로 명시됨)

### 3. 예외 사항 배열 비어있음
- **위치**: 시나리오 카드의 `exceptions[]` 필드
- **문제**: 대부분의 카드에서 빈 배열로 설정됨
- **권장 조치**: 실제 예외 사항 데이터 추가 검토

---

## ✅ 전체 검증 체크리스트

| 항목 | 상태 | 비고 |
|------|------|------|
| Scenario 타입 정의 | ✅ | types.ts 존재 |
| ACWData 타입 정의 | ✅ | types.ts 존재 |
| 8개 시나리오 데이터 | ✅ | scenario1-8.ts |
| 8개 ACW 데이터 | ✅ | acw1-8.ts |
| 카테고리 매핑 로직 | ✅ | index.ts |
| localStorage 저장/로드 | ✅ | 정상 작동 |
| STT 메시지 관리 | ✅ | 별도 state 분리 |
| 타이핑 애니메이션 | ✅ | 후처리 페이지 적용 |
| 중분류 15개 옵션 검증 | ⚠️ | 수동 확인 필요 |
| 참조 문서 3개 필터링 | ⚠️ | 향후 구현 예정 |

---

## 🚀 다음 단계 권장사항

### 우선순위 1 (긴급)
- [ ] ACW 데이터의 `subcategory` 값이 15개 옵션 중 하나인지 검증

### 우선순위 2 (중요)
- [ ] 런타임 검증 스크립트 추가
- [ ] 참조 문서 3개 필터링 로직 구현

### 우선순위 3 (개선)
- [ ] 예외 사항 데이터 보완
- [ ] 타입 가드 함수 추가

---

## 📞 문의

데이터 구조 관련 문의사항이 있으시면 이 문서를 참조하세요.

**최종 업데이트**: 2025-02-03
