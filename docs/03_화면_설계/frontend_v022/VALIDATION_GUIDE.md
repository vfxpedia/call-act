# 🔍 CALL:ACT 데이터 검증 가이드

> **목적**: 페이지/컴포넌트가 요구하는 데이터 구조와 실제 DB 데이터의 일치 여부를 자동으로 검증  
> **작성일**: 2025-02-03

---

## 📚 제공되는 검증 도구

### 1️⃣ 데이터 계약서 (Data Contract)
- **파일**: `/DATA_CONTRACT.md`
- **내용**: 각 페이지별 요구 데이터 구조 명세
- **용도**: 수동 검토 및 팀 공유

### 2️⃣ 자동 검증 스크립트
- **파일**: `/src/utils/dataValidator.ts`
- **내용**: TypeScript 기반 런타임 검증
- **용도**: 개발 중 실시간 오류 감지

---

## 🚀 사용 방법

### 방법 1: 앱 시작 시 자동 검증 (추천)

개발 서버를 시작하면 **자동으로 검증이 실행**됩니다:

```bash
npm run dev
```

브라우저 콘솔에 다음과 같은 리포트가 출력됩니다:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CALL:ACT 데이터 검증 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 전체 검증: 통과
📊 총 검사 항목: 0개
❌ 오류: 0개
⚠️  경고: 0개
```

### 방법 2: 브라우저 콘솔에서 수동 실행

개발 모드에서 브라우저 콘솔에 다음 명령어 입력:

```javascript
validateCallActData()
```

즉시 검증 리포트가 출력됩니다.

### 방법 3: 코드에서 직접 호출

```typescript
import { validateAllData, printValidationReport } from '@/utils/dataValidator';

// 검증 실행
const report = validateAllData();

// 콘솔에 리포트 출력
printValidationReport(report);

// 또는 프로그래밍 방식으로 처리
if (!report.passed) {
  console.error('데이터 검증 실패!');
  report.errors.forEach(error => {
    console.error(`[${error.location}] ${error.field}: ${error.message}`);
  });
}
```

---

## 📊 검증 항목

### ✅ Scenario 데이터 검증

#### 필수 필드
- `id` - 시나리오 고유 ID
- `category` - 대분류 카테고리
- `customer.name` - 고객명
- `customer.phone` - 전화번호
- `customer.grade` - 고객 등급
- `sttDialogue[]` - STT 대화 내역
- `steps[]` - Phase 1-3 단계

#### Phase별 검증
- **Phase 1**: 키워드, 상황 분석 카드, documentType, fullText
- **Phase 2**: 대응 방안 카드
- **Phase 3**: 다음 단계

### ✅ ACW 데이터 검증

#### 필수 필드
- `aiAnalysis.title` - 상담 제목
- `aiAnalysis.inboundCategory` - 인입 카테고리
- `aiAnalysis.handledCategories[]` - 처리한 카테고리
- `aiAnalysis.subcategory` - 중분류 (15개 옵션 중 하나)
- `aiAnalysis.summary` - AI 상담 요약본
- `aiAnalysis.followUpTasks` - 추후 할 일
- `aiAnalysis.handoffDepartment` - 이관 부서
- `aiAnalysis.handoffNotes` - 이관 전달사항
- `processingTimeline[]` - 처리 타임라인
- `callTranscript[]` - 상담 전문

#### 중분류 15개 옵션 검증
다음 중 하나여야 합니다:
- 조회/안내
- 신청/등록
- 변경
- 취소/해지
- 처리/실행
- 발급
- 확인서
- 배송
- 즉시출금
- 상향/증액
- 이체/전환
- 환급/반환
- 정지/해제
- 결제일
- 기타

---

## 🔴 오류 등급

### Error (❌)
**심각한 오류로 즉시 수정 필요**

예시:
```
❌ [Scenario 1] customer.name: 고객명이 없습니다
❌ [ACW Data (분실/도난)] aiAnalysis.subcategory: 유효하지 않은 중분류
```

### Warning (⚠️)
**권장 사항으로 검토 필요**

예시:
```
⚠️ [Scenario 3] steps[0].keywords: Phase 1 키워드가 없습니다
⚠️ [ACW Data (한도)] aiAnalysis.handoffDepartment: 이관 부서 정보가 없습니다
```

---

## 📝 검증 리포트 예시

### 성공 케이스

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CALL:ACT 데이터 검증 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 전체 검증: 통과
📊 총 검사 항목: 0개
❌ 오류: 0개
⚠️  경고: 0개

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 실패 케이스

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CALL:ACT 데이터 검증 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 전체 검증: 실패
📊 총 검사 항목: 3개
❌ 오류: 2개
⚠️  경고: 1개

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 오류 상세
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [Scenario 2 (scenario-2)]
   필드: customer.phone
   내용: 전화번호가 없습니다

2. [ACW Data (한도)]
   필드: aiAnalysis.subcategory
   내용: 유효하지 않은 중분류: "증액". 15개 옵션 중 하나여야 합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  경고 상세
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [Scenario 5 (scenario-5)]
   필드: steps[2].nextSteps
   내용: Phase 3 다음 단계가 없습니다

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🛠️ 커스터마이징

### 새로운 검증 규칙 추가

`/src/utils/dataValidator.ts` 파일을 수정하여 추가 검증 로직을 구현할 수 있습니다:

```typescript
// 예시: 고객 전화번호 형식 검증
if (scenario.customer.phone && !/^010-\d{4}-\d{4}$/.test(scenario.customer.phone)) {
  errors.push({
    location,
    field: 'customer.phone',
    message: '전화번호 형식이 올바르지 않습니다 (010-XXXX-XXXX)',
    severity: 'warning',
  });
}
```

### 중분류 옵션 수정

중분류 옵션을 변경하려면 다음 부분을 수정하세요:

```typescript
const VALID_SUBCATEGORIES = [
  '조회/안내',
  '신청/등록',
  // ... 여기에 새로운 옵션 추가
] as const;
```

---

## 🎯 권장 워크플로우

### 1. 새 시나리오 추가 시

```bash
# 1. 시나리오 파일 생성
/src/data/scenarios/scenario9.ts

# 2. ACW 데이터 파일 생성
/src/data/afterCallWorkData/acw9.ts

# 3. 개발 서버 시작 (자동 검증)
npm run dev

# 4. 브라우저 콘솔 확인
# 오류가 있으면 수정

# 5. 모든 오류 해결 후 커밋
git commit -m "Add scenario 9"
```

### 2. 기존 데이터 수정 시

```bash
# 1. 데이터 수정
vim /src/data/scenarios/scenario1.ts

# 2. 브라우저 콘솔에서 수동 검증
validateCallActData()

# 3. 오류 확인 및 수정
# 4. 통과 확인 후 커밋
```

### 3. 정기 검증

```bash
# 매주 월요일 또는 배포 전
# 브라우저 콘솔에서 전체 검증
validateCallActData()

# 리포트 스크린샷 저장
# 팀과 공유
```

---

## 📋 체크리스트

### 새 시나리오 추가 시

- [ ] `scenario.id` 중복 없음
- [ ] `scenario.category` 8개 대분류 중 하나
- [ ] `scenario.customer` 모든 필수 필드 포함
- [ ] `scenario.sttDialogue[]` 최소 5개 이상
- [ ] `scenario.steps[]` Phase 1-3 모두 존재
- [ ] Phase 1 카드에 `documentType`, `fullText` 포함
- [ ] 검증 스크립트 통과

### 새 ACW 데이터 추가 시

- [ ] `aiAnalysis.subcategory` 15개 옵션 중 하나
- [ ] `aiAnalysis.summary` 구체적이고 상세함
- [ ] `processingTimeline[]` 최소 5개 이상
- [ ] `callTranscript[]` 실제 대화 형식
- [ ] 시나리오와 매핑 정확함
- [ ] 검증 스크립트 통과

---

## 🐛 트러블슈팅

### Q: 검증이 실행되지 않아요

**A**: 개발 모드인지 확인하세요:
```bash
# .env 파일 확인
NODE_ENV=development

# 또는 개발 서버로 실행
npm run dev
```

### Q: 오류가 너무 많이 나와요

**A**: 단계별로 수정하세요:
1. Error 등급부터 먼저 수정
2. Warning은 나중에 검토
3. 한 번에 하나의 시나리오씩 수정

### Q: 커스텀 검증 규칙을 추가하고 싶어요

**A**: `/src/utils/dataValidator.ts`의 `validateScenario()` 또는 `validateACWData()` 함수에 로직 추가

---

## 📞 도움말

- **데이터 계약서**: `/DATA_CONTRACT.md` 참조
- **타입 정의**: `/src/data/scenarios/types.ts`, `/src/data/afterCallWorkData/types.ts`
- **검증 스크립트**: `/src/utils/dataValidator.ts`

**최종 업데이트**: 2025-02-03
