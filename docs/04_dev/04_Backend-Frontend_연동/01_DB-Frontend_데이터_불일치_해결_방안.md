# DB-Frontend 데이터 불일치 해결 방안

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0  
**관련 문서**: 
- [Phase6 데이터 구조 분석 및 개선방안](../../../frontend_dev/docs/Phase6_데이터_구조_분석_및_개선방안.md)
- [Backend-Frontend 연동 TODO 리스트](./00_Backend-Frontend_연동_TODO_리스트.md)

---

## 개요

이 문서는 Backend DB 구조와 Frontend 화면 구조 간의 불일치를 해결하기 위한 방안을 제시합니다. 특히 카드 상품, 공지사항, 서비스 가이드 데이터의 구조적 차이를 해결하는 방법을 다룹니다.

---

## 1. 문제 상황

### 1.1 프론트엔드 기대 구조 (ScenarioCard)

**위치**: `frontend_dev/src/data/scenarios.ts`

```typescript
export interface ScenarioCard {
  id: string;
  title: string;
  keywords: string[];
  content: string;
  systemPath: string;        // 상담 가이드 경로
  requiredChecks: string[];  // 필수 확인 사항
  exceptions: string[];      // 예외 사항
  time: string;              // 예상 소요 시간
  note: string;             // 참고 사항
  regulation: string;        // 법규
  fullText: string;         // 약관 전문
}
```

**특징**:
- 상담 가이드 중심의 구조
- 필수 확인 사항, 예외 사항, 법규, 약관 전문 등 포함
- 칸반보드에서 "자세히 보기"로 fullText(약관 형식) 표시

### 1.2 백엔드 DB 구조

#### 1.2.1 카드 상품 DB (`card_products` 테이블)

**주요 필드**:
```json
{
  "cardName": "(이응패스 여민전) K-패스 체크",
  "cardType": "체크카드",
  "annualFee": { "domestic": null, "global": null },
  "mainBenefits": ["대중교통부터 생활 할인까지", ...],
  "benefitDetails": {
    "pointAccrual": "",
    "conditions": "",
    "limit": ""
  },
  "performanceConditions": "없음",
  "usageGuide": "① 여민전 App 회원가입 후 카드발급...",
  "detailContent": "본 카드는 세종시 통합교통서비스...",
  "fullTerms": "※ 계약을 체결 전, 반드시 금융상품설명서...",
  "note": ""
}
```

**문제점**:
- ❌ ScenarioCard와 구조가 완전히 다름
- ❌ `systemPath`, `requiredChecks`, `exceptions`, `regulation` 등 상담 가이드 필드 없음
- ✅ `fullTerms`는 있지만, 카드 약관 내용 (상담 가이드가 아님)
- ✅ 카드 상품 정보 중심 (카드명, 연회비, 혜택, 이용 조건 등)

#### 1.2.2 공지사항 DB (`notices` 테이블)

**주요 필드**:
```json
{
  "id": "notice_01",
  "title": "쿠팡 정보유출 사고 관련, 금융사기 피해 우려 NOTICE 발령!",
  "content": "■ NOTICE 발령 배경\n2025년 12월 1일...",
  "category": "emergency",
  "priority": "urgent",
  "start_date": "2025-12-03",
  "end_date": "2025-12-10",
  "status": "inactive",
  "is_pinned": false,
  "keywords": ["개인정보", "보이스피싱", ...]
}
```

**문제점**:
- ❌ `structured` 필드 없음
- ❌ `systemPath`, `requiredChecks`, `exceptions` 등 상담 가이드 필드 없음
- ✅ 공지사항 내용 중심

#### 1.2.3 서비스 가이드 DB (`service_guide_documents` 테이블)

**주요 필드**:
```json
{
  "id": "guide_01",
  "title": "카드 분실 신고 절차",
  "content": "카드 분실 시 즉시 신고하세요...",
  "keywords": ["카드분실", "신고", ...],
  "fullTerms": "※ 카드 분실 신고는 24시간 가능합니다...",
  "structured": {
    "systemPath": "/card/lost",
    "requiredChecks": ["본인 확인", "카드 번호 확인"],
    "exceptions": ["해외 사용 중 분실 시"],
    "regulation": "전자금융거래법 제XX조",
    "time": "5분"
  }
}
```

**특징**:
- ✅ ScenarioCard와 가장 유사
- ✅ `structured` 필드에 상담 가이드 정보 포함
- ⚠️ `fullTerms` 대부분 비어있음

---

## 2. 해결 방안

### 2.1 권장 방안: 하이브리드 방식 (옵션 3)

**핵심 아이디어**:
1. **Backend**: 모든 DB 데이터를 `ScenarioCard` 형식으로 변환
2. **Frontend**: `sourceDB`, `documentType`에 따라 UI 최적화

#### 2.1.1 Backend 변환 로직

**카드 상품 → ScenarioCard**:
```python
def convert_card_to_scenario_card(card: dict) -> dict:
    return {
        "id": f"card_{card['id']}",
        "title": card['cardName'],
        "keywords": card.get('keywords', []),
        "content": card.get('usageGuide', '') or card.get('detailContent', ''),
        "systemPath": f"/card/{card['id']}",  # 생성
        "requiredChecks": extract_required_checks(card),  # 생성
        "exceptions": extract_exceptions(card),  # 생성
        "time": estimate_time(card),  # 생성
        "note": card.get('note', ''),
        "regulation": extract_regulation(card),  # 생성
        "fullText": card.get('fullTerms', ''),
        "sourceDB": "card_products",
        "documentType": "card_product"
    }
```

**공지사항 → ScenarioCard**:
```python
def convert_notice_to_scenario_card(notice: dict) -> dict:
    return {
        "id": f"notice_{notice['id']}",
        "title": notice['title'],
        "keywords": notice.get('keywords', []),
        "content": notice['content'],
        "systemPath": f"/notice/{notice['id']}",  # 생성
        "requiredChecks": [],  # 공지사항은 확인 사항 없음
        "exceptions": [],
        "time": "1분",  # 공지사항은 빠른 확인
        "note": "",
        "regulation": "",
        "fullText": notice['content'],  # 공지사항 내용을 fullText로
        "sourceDB": "notices",
        "documentType": "notice"
    }
```

**서비스 가이드 → ScenarioCard**:
```python
def convert_service_guide_to_scenario_card(guide: dict) -> dict:
    structured = guide.get('structured', {})
    return {
        "id": f"guide_{guide['id']}",
        "title": guide['title'],
        "keywords": guide.get('keywords', []),
        "content": guide['content'],
        "systemPath": structured.get('systemPath', f"/guide/{guide['id']}"),
        "requiredChecks": structured.get('requiredChecks', []),
        "exceptions": structured.get('exceptions', []),
        "time": structured.get('time', '5분'),
        "note": guide.get('note', ''),
        "regulation": structured.get('regulation', ''),
        "fullText": guide.get('fullTerms', guide['content']),
        "sourceDB": "service_guide_documents",
        "documentType": "service_guide"
    }
```

#### 2.1.2 Frontend UI 최적화

**칸반보드 타입별 렌더링**:
```typescript
// CardProductCard.tsx
function CardProductCard({ card }: { card: ScenarioCard }) {
  if (card.documentType === 'card_product') {
    return (
      <div>
        <h3>{card.title}</h3>
        <div>카드 타입: {card.cardType}</div>
        <div>연회비: {card.annualFee}</div>
        <div>주요 혜택: {card.mainBenefits.join(', ')}</div>
        <button onClick={() => showFullText(card.fullText)}>자세히 보기</button>
      </div>
    );
  }
  // ...
}

// NoticeCard.tsx
function NoticeCard({ notice }: { notice: ScenarioCard }) {
  if (notice.documentType === 'notice') {
    return (
      <div className="urgent">
        <h3>{notice.title}</h3>
        <div>{notice.content}</div>
        <div>기간: {notice.start_date} ~ {notice.end_date}</div>
      </div>
    );
  }
  // ...
}

// ServiceGuideCard.tsx
function ServiceGuideCard({ guide }: { guide: ScenarioCard }) {
  if (guide.documentType === 'service_guide') {
    return (
      <div>
        <h3>{guide.title}</h3>
        <div>필수 확인: {guide.requiredChecks.join(', ')}</div>
        <div>예외 사항: {guide.exceptions.join(', ')}</div>
        <div>예상 시간: {guide.time}</div>
        <button onClick={() => showFullText(guide.fullText)}>자세히 보기</button>
      </div>
    );
  }
  // ...
}
```

---

## 3. 구현 단계

### Phase 1: Backend 변환 로직 구현
- [ ] 카드 상품 → ScenarioCard 변환 함수 구현
- [ ] 공지사항 → ScenarioCard 변환 함수 구현
- [ ] 서비스 가이드 → ScenarioCard 변환 함수 구현
- [ ] RAG 검색 API에서 변환된 데이터 반환

### Phase 2: Frontend UI 컴포넌트 구현
- [ ] `CardProductCard` 컴포넌트 생성
- [ ] `NoticeCard` 컴포넌트 생성
- [ ] `ServiceGuideCard` 컴포넌트 생성
- [ ] 칸반보드에서 `documentType`에 따라 적절한 컴포넌트 렌더링

### Phase 3: 데이터 보강 (필요 시)
- [ ] 카드 상품의 `requiredChecks`, `exceptions` 데이터 보강
- [ ] 공지사항의 `structured` 필드 생성
- [ ] 서비스 가이드의 `fullTerms` 보강

### Phase 4: 테스트 및 검증
- [ ] 변환 로직 테스트
- [ ] UI 렌더링 테스트
- [ ] 데이터 일치성 검증

---

## 4. 주의사항

### 4.1 데이터 보강 필요성
- 카드 상품의 `systemPath`, `requiredChecks`, `exceptions`, `regulation`는 현재 DB에 없음
- LLM을 활용한 자동 생성 또는 수동 입력 필요
- Phase6 문서의 "데이터 보강 전략" 참고

### 4.2 성능 고려
- 변환 로직은 Backend에서 실행 (DB 조회 시)
- 캐싱 전략 고려 (변환된 데이터 캐싱)
- 대량 데이터 처리 시 성능 테스트 필요

### 4.3 하위 호환성
- 기존 Mock 데이터(`scenarios.ts`)와의 호환성 유지
- 점진적 마이그레이션 전략

---

## 5. 관련 문서

- [Phase6 데이터 구조 분석 및 개선방안](../../../frontend_dev/docs/Phase6_데이터_구조_분석_및_개선방안.md): 상세 분석 및 옵션 비교
- [Backend-Frontend 연동 TODO 리스트](./00_Backend-Frontend_연동_TODO_리스트.md): 전체 연동 작업 리스트

---

**문서 버전**: v1.0  
**최종 업데이트**: 2026-01-13
