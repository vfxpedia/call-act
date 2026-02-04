# Phase: 검색 레이어 시스템 구현 계획

## 날짜: 2025-01-29

---

## 1. 기존 코드 구조 분석 완료

### 1.1 정보 카드 구조
- **위치**: `/src/data/scenarios.ts`
- **인터페이스**: `ScenarioCard`
- **필드**:
  - id, title, keywords, content
  - systemPath, requiredChecks, exceptions
  - time, note, regulation, fullText
  - type, attributes (하이브리드 카드용)
  - documentType (5가지: terms, product-spec, analysis-report, guide, general)

### 1.2 칸반보드 렌더링
- **위치**: `/src/app/pages/RealTimeConsultationPage.tsx`
- **현재 구조**:
  - "현재 상황 관련 정보" (라인 2504)
  - "다음 단계 예상 정보" (라인 2716)
  - 2x2 그리드 (각 섹션당 2개 카드)
  - Step별 슬라이딩 캐러셀 (좌우 드래그)

### 1.3 AI 검색 어시스턴트
- **위치**: 라인 2991-3051
- **현재 형태**: 채팅 UI (chatMessages 배열)
- **구성**: 채팅 메시지 영역 + 검색 입력창 + 전송 버튼

### 1.4 localStorage 패턴
- **사용 예시**:
  - `activeCallState`: 통화 상태 저장
  - `consultationMemo`: 메모 자동 저장
  - 페이지 이동 시에도 상태 유지

---

## 2. 구현 범위 (Phase 1)

### 2.1 타임스탬프 추가
**대상**: 모든 정보 카드

**위치**: 카드 제목 우측 상단
```tsx
<div className="flex items-center justify-between mb-2">
  <h3 className="text-base font-bold text-[#0047AB]">{card.title}</h3>
  <span className="text-[11px] text-[#9CA3AF] italic opacity-85">
    {card.displayTime}
  </span>
</div>
```

**형식**: "HH:MM (N분 전)"

**스타일**:
```css
.card-timestamp {
  font-size: 11px;
  font-style: italic; /* 이탤릭 - 부수적 정보 표현 */
  color: #9CA3AF; /* 연한 그레이 (Gray-400) */
  font-weight: 400;
  opacity: 0.85; /* 살짝 투명 - 눈에 안 띄지만 필요 시 읽기 가능 */
}
```

**생성 시점**: 
- 카드가 화면에 표시되는 순간
- 프론트엔드에서 `addTimestampToCard()` 호출
- localStorage에 저장하여 유지
- 1분마다 displayTime 자동 업데이트

**유틸리티**: `/src/utils/timeFormatter.ts` (이미 작성 완료 ✓)

### 2.2 태그 시스템 정리

**기존 태그 유지** (변경 없음):
- **AI 추천 카드**: "Step 1", "Step 2" 등 (파란색 배경)
- **다음 단계 예상 정보**: "Step 1 예상", "Step 2 예상" 등 (노란색 배경)

**새로 추가**:
- **검색 결과 카드**: "검색 결과" (보라색 배경)

**위치**: 모든 태그는 카드 좌측 상단 (기존 패턴 유지)

**구현**:
```tsx
{/* 기존 AI 추천 */}
<span className="text-[9px] px-1.5 py-0.5 rounded bg-[#0047AB] text-white">
  Step {stepNumber}
</span>

{/* 새로 추가: 검색 결과 */}
<span className="text-[9px] px-1.5 py-0.5 rounded bg-[#7C3AED] text-white">
  검색 결과
</span>
```

### 2.3 AI 검색 어시스턴트 UI 변경

**변경 전**: 채팅 형식
**변경 후**: 검색바 형식

**새 구조**:
```tsx
<div id="ai-search-area">
  <h3>AI 검색 어시스턴트</h3>
  
  {/* 검색 중 로딩 상태 */}
  {isSearching && (
    <div className="flex items-center gap-2 text-xs text-[#0047AB] mb-2">
      <div className="w-3 h-3 border-2 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      <span>검색 중...</span>
    </div>
  )}
  
  {/* 검색 입력창 */}
  <input type="text" placeholder="검색어 입력..." />
  <button>검색</button>
  
  {/* 검색 이력 드롭다운 */}
  <SearchHistoryDropdown />
</div>
```

**로딩 상태**:
- 간단한 회전 인디케이터 (보라색)
- "검색 중..." 텍스트만 표시
- 0.3초 딜레이 후 결과 표시
- 문서 탐색 과정 표시는 추후 구현 (킵)

### 2.4 검색 이력 UI

**위치**: AI 검색 어시스턴트 하단
**구조**:
```tsx
<div className="search-history">
  <button onClick={toggleHistory}>검색 이력 {historyCount}건 ▼</button>
  {isHistoryOpen && (
    <ul>
      {searchHistory.map(item => (
        <li onClick={() => openSearchDocument(item)}>
          "{item.query}" ({item.timestamp})
        </li>
      ))}
    </ul>
  )}
</div>
```

**동작**:
- 클릭 시 해당 검색 결과 문서를 모달로 즉시 표시
- 레이어 이동 필요 없이 빠른 참조

**초기화 로직** (중요):
- **저장 조건**: 상담 중 (통화 중)일 때만 검색 이력 저장
- **초기화 시점**:
  1. 새로운 상담 시작 (다른 대기 콜 잡음)
  2. 통화 종료 후 새로운 인입
  3. 페이지 새로고침 (세션 종료)

```typescript
// 통화 시작 시 이력 초기화
const handleCallStart = () => {
  localStorage.removeItem('searchHistory');
  setSearchHistory([]);
  // ... 기존 로직
};
```

---

## 3. 데이터 구조 확장

### 3.1 타임스탬프 필드 추가

**ScenarioCard 인터페이스 확장**:
```typescript
export interface ScenarioCard {
  // ... 기존 필드
  timestamp?: string; // ISO 8601 형식 (YYYY-MM-DDTHH:mm:ss)
  displayTime?: string; // 화면 표시용 (HH:MM (N분 전))
}
```

### 3.2 검색 이력 타입

**새 인터페이스**:
```typescript
export interface SearchHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  results: ScenarioCard[]; // 검색 결과 2개
  documentNames: string[]; // 문서명 목록
}
```

### 3.3 Mock 검색 데이터

**위치**: `/src/data/searchMockData.ts` (신규 파일)

**구조**:
```typescript
export const searchMockData: Record<string, ScenarioCard[]> = {
  "포인트 조회": [
    {
      id: 'SEARCH-POINT-001',
      title: '포인트 조회 방법',
      // ... 기존 카드와 동일한 구조
      timestamp: '2025-01-29T09:15:00',
    },
    {
      id: 'SEARCH-POINT-002',
      title: '포인트 유효기간 안내',
      timestamp: '2025-01-29T09:15:00',
    }
  ],
  // 20개 쿼리 케이스
};
```

---

## 4. 컴포넌트 아키텍처

### 4.1 파일 구조

```
/src/app/components/
├─ consultation/
│  ├─ SearchResultLayer.tsx (신규)
│  ├─ KanbanBoardLayer.tsx (신규)
│  ├─ InfoCard.tsx (신규 - 기존 카드 로직 분리)
│  ├─ SearchHistoryDropdown.tsx (신규)
│  └─ LayerTransitionWrapper.tsx (신규)
```

### 4.2 InfoCard 컴포넌트 (기존 카드 로직 분리)

**역할**: 정보 카드 렌더링 통일

**Props**:
```typescript
interface InfoCardProps {
  card: ScenarioCard;
  stepNumber?: number; // AI 추천 카드만
  source: 'ai-recommend' | 'search-result' | 'next-step';
  onDetailClick: () => void;
}
```

**타임스탬프 추가 위치**:
```tsx
<div className="flex items-center justify-between mb-2">
  {source === 'ai-recommend' && (
    <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#0047AB] text-white">
      Step {stepNumber}
    </span>
  )}
  {source === 'search-result' && (
    <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#7C3AED] text-white">
      검색 결과
    </span>
  )}
  <span className="text-[11px] text-[#9CA3AF] ml-auto">
    {card.displayTime}
  </span>
</div>
```

### 4.3 SearchResultLayer 컴포넌트

**Props**:
```typescript
interface SearchResultLayerProps {
  searchResults: ScenarioCard[][];
  onCardClick: (card: ScenarioCard) => void;
}
```

**레이아웃**:
```tsx
<div className="search-result-layer">
  <div className="grid grid-cols-2 gap-4">
    {/* 최신 검색 결과 2개 */}
    {searchResults[0]?.map(card => (
      <InfoCard 
        card={card} 
        source="search-result"
        onDetailClick={() => onCardClick(card)}
      />
    ))}
  </div>
  <div className="grid grid-cols-2 gap-4 mt-4">
    {/* 이전 검색 결과 2개 */}
    {searchResults[1]?.map(card => (
      <InfoCard card={card} source="search-result" />
    ))}
  </div>
</div>
```

### 4.4 LayerTransitionWrapper

**역할**: 레이어 전환 애니메이션 관리

**Props**:
```typescript
interface LayerTransitionWrapperProps {
  currentLayer: 'kanban' | 'search';
  onLayerChange: (layer: 'kanban' | 'search') => void;
  children: React.ReactNode;
}
```

**전환 로직**:
```tsx
const handleWheel = (e: WheelEvent) => {
  if (wheelTimeout) return;
  
  const delta = e.deltaY;
  if (Math.abs(delta) > WHEEL_THRESHOLD) {
    if (delta > 0) {
      toggleLayer(); // 칸반 ↔ 검색
      wheelTimeout = setTimeout(() => {
        wheelTimeout = null;
      }, COOLDOWN);
    }
  }
};
```

---

## 5. 스타일링

### 5.0 반응형 레이아웃 - 비율 유지 (최우선 중요 이슈) ⭐

**문제 현황**:
- 개발 환경: 스크롤 존재
- 웹 게시 환경: 하단 빈 공간 발생
- 해상도별 레이아웃 깨짐
- 말풍선 가이드 위치 어긋남

**목표**:
- **모든 해상도에서 스크롤 없이 화면에 정확히 fit**
- **비율 유지**: 확대/축소 시 이미지처럼 비율 유지하며 전체가 크기 조정
- 1920x1080, 4K, 모바일 모두 대응
- 카드 정보 누락 없이 모두 표시

**구현 방법**: `rem 기준값 동적 조정 + vh/vw 단위`

**Step 1: 기준 해상도 설정** (`/src/styles/theme.css`)
```css
/* 기준 해상도: 1920x1080 */
:root {
  --base-width: 1920;
  --base-height: 1080;
  --base-font-size: 16px;
}

/* 동적 rem 계산 */
html {
  /* 가로 기준 비율 조정 */
  font-size: calc(100vw / var(--base-width) * var(--base-font-size));
}

/* 세로가 더 작은 경우 (세로 기준) */
@media (max-aspect-ratio: 16/9) {
  html {
    font-size: calc(100vh / var(--base-height) * var(--base-font-size));
  }
}
```

**Step 2: 페이지 레이아웃 vh 단위**
```tsx
<div className="consultation-page" style={{ height: '100vh', overflow: 'hidden' }}>
  {/* 헤더: 고정 높이 (rem 단위) */}
  <header style={{ height: '3.75rem' }} /> {/* 60px = 3.75rem */}
  
  {/* 메인: 남은 공간 정확히 채움 */}
  <main style={{ height: 'calc(100vh - 3.75rem)' }}>
    <div className="flex h-full">
      {/* 좌측 칸반/검색 레이어 */}
      <div className="flex-1 flex flex-col p-4">
        {/* 카드 영역: flex-1로 남은 공간 정확히 분배 */}
        <div className="flex-1 grid grid-rows-2 gap-4">
          {/* 각 행이 정확히 50% */}
          <div className="grid grid-cols-2 gap-4">...</div>
          <div className="grid grid-cols-2 gap-4">...</div>
        </div>
      </div>
    </div>
  </main>
</div>
```

**Step 3: 모든 크기를 rem으로 통일**
```css
/* 기존: px 단위 (고정) */
.card {
  width: 320px;
  padding: 12px;
  font-size: 14px;
}

/* 변경: rem 단위 (비율 유지) */
.card {
  width: 20rem; /* 320px / 16 = 20rem */
  padding: 0.75rem; /* 12px / 16 */
  font-size: 0.875rem; /* 14px / 16 */
}
```

**Step 4: 말풍선 가이드 위치 수정**
```typescript
// TutorialGuide 컴포넌트
const calculatePosition = (targetId: string) => {
  const element = document.getElementById(targetId);
  if (!element) return { top: 0, left: 0 };
  
  const rect = element.getBoundingClientRect();
  // vh/vw 단위로 상대 위치 계산
  return {
    top: `${(rect.top / window.innerHeight) * 100}vh`,
    left: `${(rect.left / window.innerWidth) * 100}vw`,
  };
};
```

**Step 5: 모바일/4K 대응**
```css
/* 모바일 (768px 미만) */
@media (max-width: 768px) {
  html {
    /* 모바일은 세로 기준 */
    font-size: calc(100vh / 1080 * 10px); /* 폰트 크기 축소 */
  }
  
  .card-grid {
    grid-template-columns: 1fr; /* 1열로 변경 */
  }
}

/* 4K (2560px 이상) */
@media (min-width: 2560px) {
  html {
    /* 최대 크기 제한 */
    font-size: min(calc(100vw / 1920 * 16px), 20px);
  }
}
```

**Step 6: 스크롤 완전 차단**
```css
body, html {
  overflow: hidden; /* 모든 스크롤 차단 */
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
}

.consultation-page {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
```

**테스트 체크리스트**:
- [ ] 1920x1080: 스크롤 없이 정확히 fit
- [ ] 1366x768: 비율 유지하며 축소
- [ ] 2560x1440 (QHD): 비율 유지하며 확대
- [ ] 3840x2160 (4K): 최대 크기 제한 적용
- [ ] 모바일 (375x667): 1열 레이아웃, 스크롤 없음
- [ ] 말풍선 가이드 위치 정확
- [ ] 모든 카드 정보 누락 없이 표시

**중요**: 이 작업은 모든 페이지에 동일하게 적용되어야 하므로, 
Phase 1에서는 RealTimeConsultationPage만 구현하고, 
이후 다른 페이지에도 점진적으로 확장 예정.

### 5.1 배경 전환 (대기 중 검색만)

**CSS 변수 추가** (`/src/styles/theme.css`):
```css
:root {
  --bg-waiting: #FFFFFF;
  --bg-search: linear-gradient(135deg, rgba(240, 247, 255, 0.25) 0%, rgba(230, 242, 255, 0.35) 100%);
  --bg-consultation: #FFFFFF;
}
```

**애니메이션**:
```css
@keyframes wave-in {
  0% { background: var(--bg-waiting); }
  100% { background: var(--bg-search); }
}

@keyframes wave-out {
  0% { background: var(--bg-search); }
  100% { background: var(--bg-consultation); }
}
```

### 5.2 레이어 슬라이드

```css
@keyframes slide-down {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.layer-transition {
  animation: slide-down 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 5.3 검색 결과 카드 스타일

```css
.card-search-result {
  background: #FFFFFF;
  border: 2px solid #C4B5FD; /* 연한 보라 */
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.1); /* 보라 계열 그림자 */
  transition: all 0.3s ease;
}

.card-search-result:hover {
  border-color: #7C3AED; /* 진한 보라 */
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.15);
}

.card-search-result .badge {
  background: #7C3AED; /* 진한 보라 */
  color: white;
}
```

### 5.4 빈 공간 디자인

**위치**: 검색 레이어 하단 2칸 (검색 결과 없을 때)

**디자인 옵션 A** (선택됨):
```tsx
<div className="empty-search-slot">
  <div className="border-2 border-dashed border-[#E0E0E0] rounded-lg h-full 
                  flex flex-col items-center justify-center bg-[#FAFAFA]
                  hover:border-[#C4B5FD] hover:bg-[#F8F7FF] transition-colors">
    <div className="text-4xl mb-2 opacity-40">🔍</div>
    <p className="text-xs text-[#999999] font-medium">추가 검색 시 표시됩니다</p>
    <p className="text-[10px] text-[#BBBBBB] mt-1">
      최대 4개까지 저장
    </p>
  </div>
</div>
```

**특징**:
- 점선 테두리 (회색 → hover 시 보라색)
- 검색 아이콘 🔍 (투명도 40%)
- 안내 텍스트 2줄 (추가 검색 안내 + 최대 개수)
- hover 시 배경색 변화 (피드백)

**상태별 표시**:
- **검색 0개**: 상단 2칸 + 하단 2칸 모두 빈 공간
- **검색 2개**: 상단 2칸 = 검색 결과, 하단 2칸 = 빈 공간
- **검색 4개**: 상단 2칸 = 최신 검색, 하단 2칸 = 이전 검색

---

## 6. 상태 관리 (localStorage)

### 6.1 저장 데이터

```typescript
interface StoredSearchState {
  searchHistory: SearchHistoryItem[];
  currentLayer: 'kanban' | 'search';
  lastSearchTime: string;
}

// 저장
localStorage.setItem('searchState', JSON.stringify(state));

// 복원
const savedState = JSON.parse(localStorage.getItem('searchState') || '{}');
```

### 6.2 카드 타임스탬프 저장

```typescript
// 카드 표시 시 타임스탬프 추가
const addTimestampToCard = (card: ScenarioCard): ScenarioCard => {
  const now = new Date();
  return {
    ...card,
    timestamp: now.toISOString(),
    displayTime: formatTimestamp(now),
  };
};

// 상대 시간 업데이트 (1분마다)
useEffect(() => {
  const interval = setInterval(() => {
    updateRelativeTimestamps();
  }, 60000); // 1분
  
  return () => clearInterval(interval);
}, []);
```

---

## 7. 유틸리티 함수

### 7.1 타임스탬프 포맷

**위치**: `/src/utils/timeFormatter.ts` (신규)

```typescript
export const formatTimestamp = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  
  if (diffMins < 1) return `${hours}:${minutes} (방금 전)`;
  if (diffMins < 60) return `${hours}:${minutes} (${diffMins}분 전)`;
  
  const diffHours = Math.floor(diffMins / 60);
  return `${hours}:${minutes} (${diffHours}시간 전)`;
};
```

### 7.2 검색 Mock 로직

**위치**: `/src/utils/searchSimulator.ts` (신규)

```typescript
import { searchMockData } from '@/data/searchMockData';
import { ScenarioCard } from '@/data/scenarios';

export const simulateSearch = (query: string): ScenarioCard[] => {
  // 정확한 매칭
  if (searchMockData[query]) {
    return searchMockData[query].map(card => ({
      ...card,
      timestamp: new Date().toISOString(),
    }));
  }
  
  // 부분 매칭 (키워드 포함)
  for (const [key, cards] of Object.entries(searchMockData)) {
    if (key.includes(query) || query.includes(key)) {
      return cards.map(card => ({
        ...card,
        timestamp: new Date().toISOString(),
      }));
    }
  }
  
  // 결과 없음
  return [];
};
```

---

## 8. 구현 순서

### Step 1: 타임스탬프 추가 (1일)
1. ScenarioCard 인터페이스 확장
2. formatTimestamp 유틸리티 함수 작성
3. InfoCard 컴포넌트 분리 및 타임스탬프 표시
4. 기존 칸반보드에 적용
5. 테스트: 시간 표시 및 1분마다 업데이트

### Step 2: 검색 Mock 데이터 (1일)
1. searchMockData.ts 파일 생성
2. 포인트/혜택 시나리오 20개 쿼리 케이스 작성
3. simulateSearch 함수 작성
4. 테스트: 검색 쿼리 → 결과 반환

### Step 3: AI 검색 어시스턴트 UI 변경 (0.5일)
1. 채팅 UI 제거
2. 검색바 형식으로 변경
3. 검색 상태 표시 추가
4. 테스트: 검색 입력 및 실행

### Step 4: 검색 이력 UI (0.5일)
1. SearchHistoryDropdown 컴포넌트 작성
2. localStorage 연동
3. 클릭 시 문서 모달 표시
4. 테스트: 이력 저장 및 조회

### Step 5: 레이어 시스템 구조 (1일)
1. SearchResultLayer 컴포넌트 작성
2. KanbanBoardLayer 컴포넌트 작성
3. LayerTransitionWrapper 작성
4. currentLayer 상태 관리
5. 테스트: 레이어 전환 (수동)

### Step 6: 휠/키보드 전환 (1일)
1. 휠 이벤트 핸들러 추가
2. Tab/Space 키 이벤트 추가
3. 쿨다운 로직 구현
4. 애니메이션 적용
5. 테스트: 휠/키보드로 레이어 전환

### Step 7: 배경 전환 (대기 중 검색만) (0.5일)
1. CSS 변수 추가
2. wave-in/wave-out 애니메이션 작성
3. 상담 중 검색 시 배경 유지 로직
4. 테스트: 대기 중 검색 시 파란 배경, 상담 중은 흰색

### Step 8: 통합 테스트 (0.5일)
1. 전체 플로우 테스트
2. 버그 수정
3. 성능 최적화

**총 예상 기간: 6일**

---

## 9. 주의사항

### 9.1 기존 코드 보호
- RealTimeConsultationPage.tsx의 기존 칸반보드 로직은 최대한 보존
- 컴포넌트 분리 시 점진적으로 이동
- 백업 파일 유지

### 9.2 타입 안전성
- TypeScript 타입 엄격하게 유지
- any 타입 사용 금지
- 모든 Props에 인터페이스 정의

### 9.3 성능 최적화
- React.memo로 불필요한 리렌더링 방지
- 타임스탬프 업데이트는 1분 간격 (너무 빈번하지 않게)
- 검색 이력은 최대 20개로 제한

### 9.4 접근성
- 키보드 네비게이션 완전 지원
- focus-visible 스타일 적용
- aria-label 추가

---

## 10. 미확정 사항 (사용자 컨펌 필요)

### 10.1 검색 직후 동작
- [x] **확정**: 자동으로 검색 레이어 전환 (위→아래 슬라이드)

### 10.2 상담 중 검색 배경색
- [x] **확정**: 흰색 유지 (상담 중이므로 업무 집중)

### 10.3 검색 결과 4칸 구성
- [x] **확정**: 검색 2개 + 빈 공간 2개 (옵션 A)

### 10.4 후처리 참조 문서 추가
- [x] **확정**: 자동 추가 + 후처리 페이지에서 선택 삭제

### 10.5 검색 정확도/시간 표시
- [x] **확정**: Mock으로 먼저 구현, 백엔드 연동 시 교체

### 10.6 검색 로딩 시간
- [x] **확정**: 0.3초 딜레이 + 회전 인디케이터

### 10.7 빈 공간 디자인
- [x] **확정**: 옵션 A (점선 테두리 + 아이콘 + 안내 텍스트)

### 10.8 태그 시스템
- [x] **확정**: 기존 유지 + 검색 결과 "검색 결과" 태그 추가 (보라색)

---

## 11. 다음 Phase 준비

### Phase 2: 키보드 네비게이션 (3일)
- 방향키 카드 선택
- 경계 넘김 (이전 카드, 레이어 전환)
- 전역 단축키 (Ctrl+F, M, Enter)
- 모달 내 키보드 네비게이션

### Phase 3: Mock 데이터 확장 (5일)
- 포인트/혜택 시나리오 완성 (60장)
- 추가 시나리오 (분실/도난, 한도 조회 등)
- 타임스탬프 시뮬레이션
- 매칭 정확도 Mock

### Phase 4: 후처리 연동 (2일)
- 검색 문서 자동 수집
- 참조 문서 표시
- 선택 삭제 기능

---

## 12. 문서 버전 관리

- **작성일**: 2025-01-29
- **작성자**: AI Assistant
- **검토자**: 사용자
- **버전**: 1.0 (초안)
- **다음 업데이트**: 사용자 컨펌 후 확정

---

## 13. 체크리스트

구현 전 확인:
- [x] 기존 코드 구조 파악 완료
- [x] 타임스탬프 위치 확정 (우측 상단, 이탤릭 연한 그레이)
- [x] 카드 form 형식 확인 (기존과 동일)
- [x] 레이어 시스템 구조 설계 완료
- [x] 사용자 컨펌 완료 ✓

구현 시작 전 최종 확인:
- [x] 미확정 사항 모두 결정 ✓
- [x] Phase 1 범위 명확히 정의 ✓
- [x] 개발 환경 설정 완료 ✓
- [x] 백업 파일 생성 (구현 시작 시) ✓

**구현 진행 상황**:
- [x] Step 1: Mock 검색 데이터 생성 (searchMockData.ts) ✓
- [x] Step 2: Scenario 인터페이스 확장 (timestamp 필드) ✓
- [x] Step 3: 검색 시뮬레이터 작성 (searchSimulator.ts) ✓
- [x] Step 4: 타임스탬프 유틸리티 (timeFormatter.ts) ✓ [사용자 작성]
- [x] Step 5: InfoCard 컴포넌트 분리 ✓
- [x] Step 6: EmptySearchSlot 컴포넌트 ✓
- [x] Step 7: SearchHistoryDropdown 컴포넌트 ✓
- [x] Step 8: SearchResultLayer 컴포넌트 ✓
- [ ] Step 9: 기존 칸반보드에 InfoCard 적용 (진행 예정)
- [ ] Step 10: AI 검색 어시스턴트 UI 변경 (진행 예정)
- [ ] Step 11: 반응형 레이아웃 적용 (진행 예정)
- [ ] Step 12: 레이어 전환 시스템 (진행 예정)
- [ ] Step 13: 통합 테스트 (진행 예정)

**완성된 파일 목록**:
1. ✓ `/src/data/searchMockData.ts` - Mock 검색 데이터 (20개 쿼리)
2. ✓ `/src/data/scenarios.ts` - timestamp 필드 추가
3. ✓ `/src/utils/searchSimulator.ts` - 검색 시뮬레이션 로직
4. ✓ `/src/utils/timeFormatter.ts` - 타임스탬프 포맷팅 [사용자 작성]
5. ✓ `/src/app/components/consultation/InfoCard.tsx` - 통합 카드 컴포넌트
6. ✓ `/src/app/components/consultation/EmptySearchSlot.tsx` - 빈 공간 컴포넌트
7. ✓ `/src/app/components/consultation/SearchHistoryDropdown.tsx` - 검색 이력 드롭다운
8. ✓ `/src/app/components/consultation/SearchResultLayer.tsx` - 검색 레이어

**다음 작업**: 기존 RealTimeConsultationPage에 InfoCard 적용 및 검색 어시스턴트 UI 변경

---

## 14. 최종 확인 사항 (사용자 추가 요청)

### 14.1 반응형 레이아웃 - 비율 유지 강조
- **목표**: 사진처럼 확대/축소 시 비율 유지
- **방법**: rem 기준값 동적 조정 + vh/vw 단위
- **중요도**: 최우선 ⭐⭐⭐
- **적용 범위**: 모든 페이지 (Phase 1은 RealTimeConsultationPage만)

### 14.2 코드 품질 요구사항
- ✓ 중앙 관리 방식 (컴포넌트 모듈화)
- ✓ 반복 코드 최소화
- ✓ 사용자 가독성 우선
- ✓ 재귀적 검토 및 셀프 디버깅
- ✓ 체크리스트 작업 시 업데이트

### 14.3 디자인 일관성
- **유지**: 현재 디자인 시스템 해치지 않음
- **추가**: 검색 레이어만 보라색 테마 (구분)
- **통일**: 모든 카드 form 동일 (Step 태그만 변경)

---

## 컨펌 요청 사항

다음 항목을 확인해주세요:

1. **타임스탬프 위치 및 형식**: 우측 상단, "HH:MM (N분 전)" 형식 - 확정되었나요?
   → **✓ 확정: 이탤릭 연한 그레이**

2. **검색 직후 동작**: 자동 전환 vs 수동 전환 - 어떤 것을 선호하시나요?
   → **✓ 확정: 자동 레이어 전환 (위→아래)**

3. **검색 결과 4칸 구성**: 검색 2개 + 빈 공간 2개 vs 검색 2개 + 관련 2개 - 어떤 방식으로 할까요?
   → **✓ 확정: 검색 2개 + 빈 공간 2개**

4. **구현 우선순위**: Step 1~8 순서가 적절한가요? 변경이 필요한가요?
   → **✓ 확정: 논리적 흐름 유지 (Mock 우선)**

5. **기타 수정 사항**: 이 계획서에서 수정이 필요한 부분이 있나요?
   → **✓ 확정: 반응형 레이아웃 강화 + 코드 품질 요구사항 추가**

**✅ 모든 컨펌 완료! 구현을 시작합니다.**