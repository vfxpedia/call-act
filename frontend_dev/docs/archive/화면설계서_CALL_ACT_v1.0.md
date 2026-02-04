# CALL:ACT 화면설계서 v1.0

## 문서 정보

| 항목 | 내용 |
|------|------|
| **문서명** | CALL:ACT (카드사 상담사를 위한 AI 기반 실시간 상담 지원 시스템) 화면설계서 |
| **버전** | 1.0 |
| **작성일** | 2026-01-17 |
| **작성자** | CALL:ACT 개발팀 |
| **기술 스택** | React + TypeScript + Tailwind CSS v4 + FastAPI + PostgreSQL + pgvector |
| **디자인 시스템** | HD~4K 최적화, 메인 색상: #0047AB (블루), #FBBC04 (옐로우), 화이트/그레이 |

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [화면 구조](#2-화면-구조)
3. [페이지별 상세 설계](#3-페이지별-상세-설계)
4. [공통 컴포넌트](#4-공통-컴포넌트)
5. [칸반보드 시스템 (핵심 차별점)](#5-칸반보드-시스템-핵심-차별점)
6. [데이터 흐름](#6-데이터-흐름)
7. [인터랙션 및 애니메이션](#7-인터랙션-및-애니메이션)
8. [반응형 디자인](#8-반응형-디자인)
9. [접근성 (Accessibility)](#9-접근성-accessibility)
10. [부록](#10-부록)

---

## 1. 시스템 개요

### 1.1 프로젝트 소개

**CALL:ACT**는 카드사 상담사를 위한 **AI 기반 실시간 상담 지원 시스템**입니다.

**핵심 차별점**:
- **STT (Speech-to-Text)**: 실시간 음성 인식으로 고객과 상담사의 대화를 텍스트로 변환
- **RAG (Retrieval-Augmented Generation)**: 3개의 하이브리드 DB(RDB + VectorDB)에서 실시간 문서 검색
- **칸반보드 형태의 문서 표시**: 검색된 문서를 Step별로 수평 슬라이딩 캐러셀 형태로 표시
- **AI 기반 자동 요약**: 상담 종료 시 자동으로 상담 내용 요약 및 후처리

### 1.2 디자인 철학

1. **고급스러운 느낌**: HD~4K 해상도 최적화, 미니멀한 디자인
2. **일관된 색상 시스템**: 
   - **Primary**: #0047AB (블루) - 신뢰감, 전문성
   - **Secondary**: #FBBC04 (옐로우) - 활력, 강조
   - **Neutral**: 화이트, 그레이 계열 - 가독성
3. **직관적인 UX**: 상담사가 빠르게 정보를 찾고 활용할 수 있도록 설계
4. **실시간성 강조**: 로딩, 애니메이션으로 시스템 상태 명확히 표시

### 1.3 핵심 기능

| 기능 | 설명 |
|------|------|
| **실시간 상담** | STT로 대화를 텍스트화하고, 키워드 자동 감지 |
| **칸반보드 문서 검색** | Step별로 관련 문서를 칸반보드 형태로 표시 (수평 슬라이딩) |
| **고객 정보 조회** | 전화번호 기반 고객 정보 및 최근 상담 이력 조회 |
| **상담 후처리** | AI 기반 자동 요약 및 카테고리 분류 |
| **대시보드** | 실시간 통계 및 성과 지표 (FCR, 평균 처리 시간 등) |
| **공지사항 관리** | 긴급 공지사항 자동 표시 및 관리 |
| **관리자 기능** | 직원 관리, 상담 통계, 공지사항 작성 |

---

## 2. 화면 구조

### 2.1 전체 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│ Header (상단 고정)                                            │
│ - 로고, 현재 페이지, 알림, 프로필                               │
├──────┬──────────────────────────────────────────────────────┤
│      │                                                      │
│      │                                                      │
│ Side │              Main Content Area                       │
│ bar  │              (페이지별 콘텐츠)                          │
│      │                                                      │
│      │                                                      │
└──────┴──────────────────────────────────────────────────────┘
```

### 2.2 레이아웃 시스템

| 요소 | 스펙 |
|------|------|
| **Header 높이** | 64px (고정) |
| **Sidebar 너비** | 240px (기본), 80px (축소), 0px (모바일 숨김) |
| **Main Content 여백** | padding: 24px (desktop), 16px (mobile) |
| **최대 너비** | 1920px (4K 대응) |
| **Grid 시스템** | Tailwind CSS 기본 그리드 활용 |

---

## 3. 페이지별 상세 설계

### 3.1 로그인 페이지 (`/login`)

#### 3.1.1 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                         CALL:ACT                            │
│                  AI 상담 지원 시스템                           │
│                                                             │
│              ┌─────────────────────────┐                    │
│              │  사원번호 입력           │                    │
│              ├─────────────────────────┤                    │
│              │  비밀번호 입력           │                    │
│              ├─────────────────────────┤                    │
│              │  [ 로그인 ]             │                    │
│              └─────────────────────────┘                    │
│                                                             │
│                  비밀번호 찾기 | 도움말                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 3.1.2 UI 요소

| 요소 | 스펙 | 색상 |
|------|------|------|
| **로고** | 48px 높이, 중앙 정렬 | #0047AB |
| **제목** | text-2xl, font-bold | #333333 |
| **입력 필드** | w-80, h-12, border-2 | border-#E0E0E0 |
| **로그인 버튼** | w-80, h-12, rounded-lg | bg-#0047AB, hover:bg-#003580 |
| **링크** | text-sm, underline | text-#0047AB |

#### 3.1.3 상태 및 인터랙션

| 상태 | 설명 |
|------|------|
| **기본** | 입력 필드 비활성화 상태 |
| **입력 중** | 입력 필드 focus 시 border-#0047AB |
| **로딩** | 로그인 버튼에 스피너 표시 |
| **오류** | 입력 필드 아래 빨간색 오류 메시지 표시 |
| **성공** | 대시보드로 리다이렉트 (transition) |

#### 3.1.4 데이터 흐름

```
사용자 입력 → 유효성 검사 → API 호출 (/api/auth/login)
→ JWT 토큰 저장 (localStorage) → 대시보드 이동
```

---

### 3.2 대시보드 (`/dashboard`)

#### 3.2.1 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│ Header: CALL:ACT | 대시보드 | [알림] [프로필]                 │
├──────┬──────────────────────────────────────────────────────┤
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 실시간 상담 현황 (4개 카드)                        │  │
│      │ │ - 상담 중: 12명                                   │  │
│      │ │ - 대기 중: 8명                                    │  │
│ Side │ │ - 오늘 완료: 142건                                │  │
│ bar  │ │ - FCR: 87.5%                                     │  │
│      │ └─────────────────────────────────────────────────┘  │
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 대기 콜 현황 (테이블)                              │  │
│      │ │ 카테고리 | 대기 수 | 평균 대기 시간 | 우선순위     │  │
│      │ │ ─────────┼────────┼───────────────┼──────────   │  │
│      │ │ 카드분실 | 3       | 02:35         | 긴급        │  │
│      │ │ 해외결제 | 2       | 01:20         | 일반        │  │
│      │ └─────────────────────────────────────────────────┘  │
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 주요 공지사항 (3개)                                │  │
│      │ │ [긴급] KT 화재로 인한 통신망 장애 대응             │  │
│      │ │ [이벤트] 하나카드x메가커피 프로모션 안내            │  │
│      │ └─────────────────────────────────────────────────┘  │
└──────┴──────────────────────────────────────────────────────┘
```

#### 3.2.2 UI 요소

**실시간 상담 현황 카드**:
| 요소 | 스펙 | 색상 |
|------|------|------|
| **카드** | grid grid-cols-4 gap-6, p-6, rounded-xl | bg-gradient-to-br from-white to-#F8FBFF |
| **아이콘** | 48px, 좌측 상단 | #0047AB |
| **수치** | text-3xl, font-bold | #0047AB |
| **레이블** | text-sm | #666666 |
| **border** | border-2 | border-#0047AB/20 |

**대기 콜 현황 테이블**:
| 요소 | 스펙 | 색상 |
|------|------|------|
| **테이블** | w-full, border-collapse | - |
| **헤더** | text-sm, font-bold, p-3 | bg-#F5F5F5, text-#333333 |
| **행** | p-3, border-b | border-#E0E0E0 |
| **우선순위 배지** | px-2 py-1, rounded, text-xs | 긴급: bg-#EA4335/10 text-#EA4335 |

**공지사항 리스트**:
| 요소 | 스펙 | 색상 |
|------|------|------|
| **아이템** | p-4, rounded-lg, flex items-center | bg-#F8FBFF, hover:bg-#E8F1FC |
| **태그** | px-2 py-1, rounded, text-xs | 긴급: bg-#EA4335 text-white |
| **제목** | text-sm, font-medium | text-#333333 |

#### 3.2.3 상태 및 인터랙션

| 인터랙션 | 동작 |
|---------|------|
| **대기 콜 클릭** | 해당 카테고리의 상담 시작 (실시간 상담 페이지 이동) |
| **공지사항 클릭** | 공지사항 상세 모달 표시 |
| **카드 hover** | shadow-lg, border-#0047AB/40 |
| **자동 새로고침** | 10초마다 실시간 데이터 갱신 |

#### 3.2.4 데이터 흐름

```
페이지 로드 → API 호출 (GET /api/dashboard/stats)
→ 상태 업데이트 → 렌더링
→ 10초 후 자동 재호출 (setInterval)
```

---

### 3.3 실시간 상담 페이지 (`/consultation`) ⭐ 핵심 페이지

#### 3.3.1 화면 구성 (3단 레이아웃)

```
┌─────────────────────────────────────────────────────────────┐
│ Header: CALL:ACT | 실시간 상담 | [종료] [저장]                │
├──────┬────────────────────────────────┬─────────────────────┤
│      │                                │                     │
│      │  STT 대화 영역                  │  고객 정보          │
│      │  ┌──────────────────────────┐  │  ┌───────────────┐  │
│      │  │ [고객] 카드를 잃어버렸어요 │  │  │ 김민지        │  │
│ Side │  │ [상담사] 확인하겠습니다    │  │  │ 010-2345-6789│  │
│ bar  │  │ [고객] 재발급은...        │  │  │ VIP 등급      │  │
│      │  └──────────────────────────┘  │  └───────────────┘  │
│      │                                │                     │
│      │  ───────────────────────────   │  최근 상담 이력     │
│      │                                │  ┌───────────────┐  │
│      │  현재 상황 관련 정보 (칸반보드)  │  │ 한도조회      │  │
│      │  Step 1 ●──○──○                │  │ 포인트 문의   │  │
│      │  ┌─────────┐ ┌─────────┐      │  └───────────────┘  │
│      │  │ 카드     │ │ 분실     │      │                     │
│      │  │ 즉시정지 │ │ 신고접수 │      │  AI 어시스턴트     │
│      │  │         │ │         │      │  ┌───────────────┐  │
│      │  │ [상세]  │ │ [상세]  │      │  │ "카드 분실    │  │
│      │  └─────────┘ └─────────┘      │  │  신고 시 본인 │  │
│      │                                │  │  확인 필수"   │  │
│      │  다음 단계 예상 정보             │  └───────────────┘  │
│      │  Step 2 ○──●──○                │                     │
│      │  ┌─────────┐ ┌─────────┐      │  상담 메모          │
│      │  │ 재발급   │ │ 부정     │      │  ┌───────────────┐  │
│      │  │ 신청     │ │ 사용확인 │      │  │ (자유 작성)   │  │
└──────┴────────────────────────────────┴─────────────────────┘
```

#### 3.3.2 영역별 상세 설계

##### 3.3.2.1 STT 대화 영역 (좌측 중앙)

**구조**:
```tsx
<div className="h-[400px] overflow-y-auto bg-white rounded-lg border-2 border-#E0E0E0 p-4">
  {/* 대화 시작 안내 */}
  {!isCallActive && (
    <div className="text-center text-#999999">
      통화를 시작하려면 [통화 시작] 버튼을 클릭하세요
    </div>
  )}
  
  {/* STT 대화 목록 */}
  {sttTexts.map((item, index) => (
    <div className={item.speaker === 'customer' ? 'justify-start' : 'justify-end'}>
      <span className="px-3 py-2 rounded-lg">
        {item.text}
      </span>
    </div>
  ))}
</div>
```

**UI 요소**:
| 요소 | 스펙 | 색상 |
|------|------|------|
| **컨테이너** | h-[400px], overflow-y-auto, p-4 | bg-white, border-#E0E0E0 |
| **고객 메시지** | float-left, px-3 py-2, rounded-lg | bg-#F0F0F0, text-#333333 |
| **상담사 메시지** | float-right, px-3 py-2, rounded-lg | bg-#0047AB, text-white |
| **키워드 강조** | font-bold, underline | text-#FBBC04 |
| **스크롤바** | thin, auto-hide | scrollbar-thumb-#CCCCCC |

**키워드 감지 표시**:
```tsx
// 키워드가 포함된 텍스트
<span className="font-bold text-#FBBC04 bg-#FFF9E6 px-1 rounded">
  카드분실
</span>
```

##### 3.3.2.2 현재 상황 칸반보드 (좌측 하단) ⭐ 핵심 차별점

**구조** (수평 슬라이딩 캐러셀):
```tsx
<div className="mb-5">
  <h2 className="text-sm font-bold text-#333333 mb-3 flex items-center gap-2">
    현재 상황 관련 정보
    {isAnalyzing && <span className="text-#0047AB">분석 중...</span>}
  </h2>
  
  {/* Step 인디케이터 */}
  <div className="flex items-center gap-2 mb-3">
    {steps.map((_, index) => (
      <button
        className={index < maxReachedStep ? 'bg-#0047AB w-8' : 'bg-#E0E0E0 w-4'}
      />
    ))}
    <span className="text-[10px] text-#666666">Step {currentStep} / {maxReachedStep}</span>
  </div>
  
  {/* 슬라이딩 컨테이너 */}
  <div className="relative overflow-hidden">
    <div 
      className="flex transition-transform duration-700"
      style={{ transform: `translateX(-${(currentStep - 1) * 100}%)` }}
    >
      {steps.map((step, stepIndex) => (
        <div className="w-full flex-shrink-0">
          {/* 카드 2개 */}
          <div className="flex gap-4">
            {step.currentSituationCards.map((card) => (
              <div className="w-1/2 bg-gradient-to-br from-white to-#F8FBFF border-2 border-#0047AB/20 rounded-lg p-5">
                {/* 카드 내용 */}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
</div>
```

**카드 UI 요소**:
| 요소 | 스펙 | 색상 |
|------|------|------|
| **카드** | w-1/2, p-5, rounded-lg | bg-gradient-to-br from-white to-#F8FBFF |
| **Step 배지** | px-1.5 py-0.5, text-[9px], rounded | bg-#0047AB, text-white |
| **제목** | text-base, font-bold | text-#0047AB |
| **키워드** | px-2 py-0.5, text-[11px], rounded | bg-#E8F1FC, text-#0047AB |
| **시스템 경로** | text-[11px], border-b | text-#0047AB, border-#0047AB/10 |
| **필수 확인** | text-[10px] | text-#666666 |
| **예외 사항** | text-[10px] | text-#EA4335 |
| **자세히 보기 버튼** | w-full, px-2.5 py-1.5, text-[11px] | bg-#0047AB, hover:bg-#003580 |

**Step 전환 애니메이션**:
```css
/* 좌→우 슬라이딩 */
@keyframes slideInFromRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 우→좌 슬라이딩 */
@keyframes slideInFromLeft {
  from {
    opacity: 0;
    transform: translateX(-100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

**카드 타입별 스타일**:

| 카드 타입 | 배지 색상 | 키워드 배경 | 버튼 색상 |
|----------|---------|-----------|---------|
| **상담 가이드** | bg-#0047AB | bg-#E8F1FC, text-#0047AB | bg-#0047AB |
| **카드 상품** | bg-#FBBC04 | bg-#FFF9E6, text-#FBBC04 | bg-#FBBC04 |
| **긴급 공지** | bg-#EA4335 | bg-#FDECEA, text-#EA4335 | bg-#EA4335 |

##### 3.3.2.3 다음 단계 예상 정보 (좌측 하단 2)

**구조**: 현재 상황 칸반보드와 동일하지만, Step이 하나 앞선 정보 표시

```tsx
<div className="mb-5" style={{ animation: 'fadeInUp 0.7s ease-out 1.1s both' }}>
  <h2 className="text-sm font-bold text-#333333 mb-3">
    다음 단계 예상 정보
  </h2>
  
  {/* 슬라이딩 컨테이너 (동일) */}
  <div className="flex gap-4">
    {nextStepCards.map((card) => (
      <div className="w-1/2">
        {/* 카드 (동일) */}
      </div>
    ))}
  </div>
</div>
```

##### 3.3.2.4 고객 정보 (우측 상단)

**구조**:
```tsx
<div className="bg-white rounded-lg border-2 border-#E0E0E0 p-4 mb-4">
  <h2 className="text-sm font-bold text-#333333 mb-3">고객 정보</h2>
  
  {!isCallActive ? (
    <div className="text-center text-#999999">
      통화 시작 후 자동으로 조회됩니다
    </div>
  ) : (
    <div className="space-y-2">
      <div className="flex justify-between">
        <span className="text-xs text-#666666">고객명</span>
        <span className="text-xs font-medium">{customer.name}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-xs text-#666666">전화번호</span>
        <span className="text-xs font-medium">{customer.phone}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-xs text-#666666">카드번호</span>
        <span className="text-xs font-medium">{customer.cardNumber}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-xs text-#666666">등급</span>
        <span className="px-2 py-0.5 rounded bg-#FBBC04 text-white text-xs">
          {customer.grade}
        </span>
      </div>
    </div>
  )}
</div>
```

**UI 요소**:
| 요소 | 스펙 | 색상 |
|------|------|------|
| **컨테이너** | p-4, rounded-lg | bg-white, border-#E0E0E0 |
| **레이블** | text-xs | text-#666666 |
| **값** | text-xs, font-medium | text-#333333 |
| **등급 배지** | px-2 py-0.5, rounded, text-xs | bg-#FBBC04, text-white |

##### 3.3.2.5 최근 상담 이력 (우측 중앙)

**구조**:
```tsx
<div className="bg-white rounded-lg border-2 border-#E0E0E0 p-4 mb-4">
  <h2 className="text-sm font-bold text-#333333 mb-3">최근 상담 이력</h2>
  
  {recentConsultations.length === 0 ? (
    <div className="text-center text-#999999 text-xs">
      최근 상담 이력이 없습니다
    </div>
  ) : (
    <div className="space-y-2">
      {recentConsultations.map((item) => (
        <div className="p-2 rounded bg-#F8FBFF hover:bg-#E8F1FC cursor-pointer">
          <div className="text-xs font-medium text-#333333">{item.content}</div>
          <div className="text-[10px] text-#999999">{item.date}</div>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-#34A853/10 text-#34A853">
            {item.status}
          </span>
        </div>
      ))}
    </div>
  )}
</div>
```

##### 3.3.2.6 AI 어시스턴트 (우측 중앙 2)

**구조**:
```tsx
<div className="bg-gradient-to-br from-#E8F1FC to-white rounded-lg border-2 border-#0047AB/20 p-4 mb-4">
  <h2 className="text-sm font-bold text-#0047AB mb-3 flex items-center gap-2">
    <Bot className="w-4 h-4" />
    AI 어시스턴트
  </h2>
  
  {aiSuggestions.length === 0 ? (
    <div className="text-center text-#666666 text-xs">
      키워드 감지 후 추천 스크립트가 표시됩니다
    </div>
  ) : (
    <div className="space-y-2">
      {aiSuggestions.map((suggestion, index) => (
        <div className="bg-white p-2.5 rounded border border-#0047AB/10">
          <div className="text-xs text-#666666 leading-relaxed">
            💡 {suggestion}
          </div>
          <button className="mt-1 text-[10px] text-#0047AB hover:underline flex items-center gap-1">
            <Copy className="w-3 h-3" />
            스크립트 복사
          </button>
        </div>
      ))}
    </div>
  )}
</div>
```

##### 3.3.2.7 상담 메모 (우측 하단)

**구조**:
```tsx
<div className="bg-white rounded-lg border-2 border-#E0E0E0 p-4">
  <h2 className="text-sm font-bold text-#333333 mb-3">상담 메모</h2>
  
  <textarea
    className="w-full h-32 p-2 border border-#E0E0E0 rounded text-xs resize-none focus:border-#0047AB focus:outline-none"
    placeholder="상담 내용을 자유롭게 메모하세요..."
    value={memo}
    onChange={(e) => setMemo(e.target.value)}
  />
  
  <button className="mt-2 w-full px-3 py-2 bg-#0047AB text-white rounded text-xs hover:bg-#003580">
    <Save className="w-3 h-3 inline mr-1" />
    메모 저장
  </button>
</div>
```

#### 3.3.3 상단 액션 버튼

| 버튼 | 색상 | 아이콘 | 동작 |
|------|------|--------|------|
| **통화 시작** | bg-#34A853, hover:bg-#2D9A4C | Phone | 통화 시작, STT 활성화, 시뮬레이션 시작 |
| **통화 종료** | bg-#EA4335, hover:bg-#D93025 | PhoneOff | 통화 종료, 상담 후처리 페이지 이동 |
| **임시 저장** | bg-#FBBC04, hover:bg-#F9AB00 | Save | 현재 상태 임시 저장 (로컬스토리지) |

#### 3.3.4 상태 및 인터랙션

| 상태 | 설명 | UI 변화 |
|------|------|--------|
| **통화 전** | 초기 상태 | STT 영역: 안내 메시지, 칸반보드: 숨김, 고객 정보: 안내 메시지 |
| **통화 중** | 상담 진행 중 | STT 영역: 실시간 대화, 칸반보드: 표시 (키워드 감지 후) |
| **키워드 분석 중** | RAG 검색 중 | 칸반보드: 로딩 스켈레톤 (2개), "분석 중..." 표시 |
| **키워드 감지 완료** | 칸반보드 표시 | 칸반보드: fadeInUp 애니메이션, 카드 2개 표시 |
| **Step 전환** | Step 2로 이동 | 칸반보드: 좌→우 슬라이딩, Step 인디케이터 업데이트 |
| **통화 종료** | 상담 종료 | 상담 후처리 페이지 이동 (transition) |

#### 3.3.5 데이터 흐름

```
통화 시작 
→ 고객 정보 조회 (GET /api/customers/{phone})
→ STT 시작 (WebSocket /ws/stt)
→ 키워드 감지 (실시간)
→ RAG 검색 (POST /api/rag/search) { keywords: [...] }
→ 칸반보드 렌더링 (ScenarioCard[])
→ Step 전환 (새 키워드 감지 시)
→ 통화 종료
→ 상담 내용 저장 (POST /api/consultations)
→ 상담 후처리 페이지 이동
```

---

### 3.4 상담 후처리 페이지 (`/aftercall`)

#### 3.4.1 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│ Header: CALL:ACT | 상담 후처리 | [저장] [취소]                │
├──────┬──────────────────────────────────────────────────────┤
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 상담 요약 (AI 자동 생성)                           │  │
│      │ │ ┌─────────────────────────────────────────────┐  │  │
│ Side │ │ │ 고객이 카드 분실 신고를 요청했습니다.         │  │  │
│ bar  │ │ │ 카드 즉시 정지 및 재발급 신청 완료했습니다.   │  │  │
│      │ │ │ 해외 출장 일정 고려하여 임시 카드 발급...     │  │  │
│      │ │ └─────────────────────────────────────────────┘  │  │
│      │ └─────────────────────────────────────────────────┘  │
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 상담 분류                                          │  │
│      │ │ [ ] 카드분실  [ ] 해외결제  [ ] 수수료문의         │  │
│      │ └─────────────────────────────────────────────────┘  │
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 처리 결과                                          │  │
│      │ │ ( ) 완료  ( ) 진행중  ( ) 보류                     │  │
│      │ └─────────────────────────────────────────────────┘  │
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 추가 메모                                          │  │
│      │ │ [ 자유 작성 ]                                      │  │
│      │ └─────────────────────────────────────────────────┘  │
└──────┴──────────────────────────────────────────────────────┘
```

#### 3.4.2 UI 요소

| 요소 | 스펙 | 색상 |
|------|------|------|
| **상담 요약 박스** | p-4, rounded-lg, border-2 | bg-#F8FBFF, border-#0047AB/20 |
| **요약 텍스트** | text-sm, leading-relaxed | text-#333333 |
| **카테고리 버튼** | px-4 py-2, rounded-lg, border-2 | 선택: bg-#0047AB text-white, 미선택: bg-white border-#E0E0E0 |
| **라디오 버튼** | w-4 h-4 | accent-#0047AB |
| **메모 입력** | w-full h-32, p-2, border | border-#E0E0E0, focus:border-#0047AB |
| **저장 버튼** | px-6 py-3, rounded-lg | bg-#0047AB, hover:bg-#003580 |

#### 3.4.3 상태 및 인터랙션

| 인터랙션 | 동작 |
|---------|------|
| **카테고리 선택** | 다중 선택 가능 (체크박스) |
| **처리 결과 선택** | 단일 선택 (라디오) |
| **저장 버튼 클릭** | API 호출 → 대시보드 이동 (toast 메시지 표시) |
| **취소 버튼 클릭** | 확인 다이얼로그 → 대시보드 이동 |

#### 3.4.4 데이터 흐름

```
페이지 로드 → AI 요약 생성 (POST /api/ai/summarize) { transcript: [...] }
→ 요약 표시
→ 사용자 입력 (카테고리, 처리 결과, 메모)
→ 저장 (POST /api/consultations) { summary, categories, status, memo }
→ 대시보드 이동
```

---

### 3.5 상담 이력 페이지 (`/history`)

#### 3.5.1 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│ Header: CALL:ACT | 상담 이력 | [검색] [필터]                  │
├──────┬──────────────────────────────────────────────────────┤
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 검색 및 필터                                       │  │
│      │ │ [날짜 선택] [카테고리] [상담사] [상태] [검색]      │  │
│ Side │ └─────────────────────────────────────────────────┘  │
│ bar  │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 상담 이력 테이블                                   │  │
│      │ │ ID | 고객명 | 카테고리 | 상담사 | 일시 | 상태     │  │
│      │ │ ─────────────────────────────────────────────── │  │
│      │ │ 001 | 김민지 | 카드분실 | 김현우 | 01-15 | 완료  │  │
│      │ │ 002 | 이철수 | 한도증액 | 박지영 | 01-15 | 진행중│  │
│      │ └─────────────────────────────────────────────────┘  │
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 페이지네이션                                       │  │
│      │ │ < 1 2 3 4 5 >                                     │  │
│      │ └─────────────────────────────────────────────────┘  │
└──────┴──────────────────────────────────────────────────────┘
```

#### 3.5.2 UI 요소

| 요소 | 스펙 | 색상 |
|------|------|------|
| **검색 입력** | w-64, h-10, px-3, rounded-lg | border-#E0E0E0, focus:border-#0047AB |
| **필터 셀렉트** | w-40, h-10, rounded-lg | border-#E0E0E0 |
| **테이블** | w-full, border-collapse | - |
| **헤더** | text-sm, font-bold, p-3 | bg-#F5F5F5 |
| **행** | p-3, border-b, hover:bg-#F8FBFF | border-#E0E0E0 |
| **상태 배지** | px-2 py-1, rounded, text-xs | 완료: bg-#34A853/10 text-#34A853, 진행중: bg-#FBBC04/10 text-#FBBC04 |
| **페이지네이션** | px-3 py-1, rounded | 활성: bg-#0047AB text-white, 비활성: bg-#F5F5F5 |

#### 3.5.3 상태 및 인터랙션

| 인터랙션 | 동작 |
|---------|------|
| **행 클릭** | 상담 상세 모달 표시 |
| **검색** | 실시간 검색 (debounce 500ms) |
| **필터 선택** | 즉시 반영 |
| **페이지 변경** | API 호출 (offset, limit) |

#### 3.5.4 데이터 흐름

```
페이지 로드 → API 호출 (GET /api/consultations?page=1&limit=20)
→ 테이블 렌더링
→ 검색/필터 변경 → API 재호출
→ 테이블 업데이트
```

---

### 3.6 공지사항 페이지 (`/notices`)

#### 3.6.1 화면 구성

```
┌─────────────────────────────────────────────────────────────┐
│ Header: CALL:ACT | 공지사항 | [검색]                         │
├──────┬──────────────────────────────────────────────────────┤
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 상단 고정 공지 (2개)                               │  │
│      │ │ 🔴 [긴급] KT 화재로 인한 통신망 장애 대응          │  │
│ Side │ │ 🎉 [이벤트] 하나카드x메가커피 프로모션 안내         │  │
│ bar  │ └─────────────────────────────────────────────────┘  │
│      │ ┌─────────────────────────────────────────────────┐  │
│      │ │ 일반 공지 리스트                                   │  │
│      │ │ [시스템] 신규 상담 시스템 업데이트 안내            │  │
│      │ │ [교육] 신규 입사자 온보딩 교육 일정                │  │
│      │ │ [정책] 카드 분실 신고 처리 프로세스 변경           │  │
│      │ └─────────────────────────────────────────────────┘  │
└──────┴──────────────────────────────────────────────────────┘
```

#### 3.6.2 UI 요소

| 요소 | 스펙 | 색상 |
|------|------|------|
| **고정 공지 카드** | p-4, rounded-lg, border-l-4 | border-#EA4335, bg-#FFF3F0 |
| **일반 공지 아이템** | p-4, rounded-lg, hover:bg-#F8FBFF | bg-white |
| **태그** | px-2 py-1, rounded, text-xs | 긴급: bg-#EA4335 text-white, 이벤트: bg-#FBBC04 text-white |
| **제목** | text-sm, font-medium | text-#333333 |
| **날짜/조회수** | text-xs | text-#999999 |

#### 3.6.3 상태 및 인터랙션

| 인터랙션 | 동작 |
|---------|------|
| **공지 클릭** | 공지사항 상세 모달 표시 (전문 보기) |
| **검색** | 제목/내용 검색 (실시간) |

#### 3.6.4 데이터 흐름

```
페이지 로드 → API 호출 (GET /api/notices?pinned=true&status=active)
→ 상단 고정 공지 표시
→ API 호출 (GET /api/notices?status=active&orderBy=created_at)
→ 일반 공지 표시
```

---

### 3.7 관리자 페이지

#### 3.7.1 관리자 대시보드 (`/admin/stats`)

**화면 구성**: 대시보드와 유사하지만, 전체 상담사 통계 표시

| 위젯 | 설명 |
|------|------|
| **전체 상담 현황** | 오늘/주간/월간 상담 건수, FCR, 평균 처리 시간 |
| **상담사별 성과** | 상담사 랭킹 (FCR, 처리 시간, 상담 건수) |
| **카테고리별 통계** | 카테고리별 상담 건수 및 트렌드 |
| **시간대별 분석** | 시간대별 상담 집중도 (히트맵) |

#### 3.7.2 직원 관리 (`/admin/employees`)

**화면 구성**: 직원 목록 테이블 + 추가/수정/삭제 기능

| 기능 | 설명 |
|------|------|
| **직원 목록** | 테이블 (이름, 사원번호, 직급, 팀, 상태) |
| **직원 추가** | 모달 (폼 입력) |
| **직원 수정** | 모달 (기존 정보 수정) |
| **직원 삭제** | 확인 다이얼로그 → 삭제 |

#### 3.7.3 공지사항 작성 (`/admin/notices/create`)

**화면 구성**: 폼 입력 (제목, 내용, 카테고리, 우선순위, 공지 기간)

| 필드 | 타입 | 설명 |
|------|------|------|
| **제목** | text | 공지사항 제목 |
| **내용** | textarea | 공지사항 본문 (마크다운 지원) |
| **카테고리** | select | 긴급, 시스템, 이벤트 등 |
| **우선순위** | select | 긴급, 중요, 일반 |
| **공지 기간** | date range | 시작일 ~ 종료일 |
| **상단 고정** | checkbox | 상단 고정 여부 |

#### 3.7.4 상담 관리 (`/admin/consultations`)

**화면 구성**: 모든 상담 이력 조회 + 필터 + 통계

| 기능 | 설명 |
|------|------|
| **전체 상담 이력** | 모든 상담사의 상담 이력 조회 |
| **고급 필터** | 날짜, 상담사, 카테고리, 상태, 고객명 등 |
| **엑셀 다운로드** | 선택한 기간의 상담 이력 CSV 다운로드 |

---

## 4. 공통 컴포넌트

### 4.1 Header

**위치**: 모든 페이지 상단 고정

**구조**:
```tsx
<header className="h-16 bg-white border-b border-#E0E0E0 flex items-center justify-between px-6 fixed top-0 left-0 right-0 z-50">
  {/* 왼쪽: 로고 + 페이지명 */}
  <div className="flex items-center gap-4">
    <div className="text-xl font-bold text-#0047AB">CALL:ACT</div>
    <div className="text-sm text-#666666">| {currentPage}</div>
  </div>
  
  {/* 오른쪽: 알림 + 프로필 */}
  <div className="flex items-center gap-4">
    <button className="relative">
      <Bell className="w-5 h-5 text-#666666" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 w-4 h-4 bg-#EA4335 text-white text-[10px] rounded-full flex items-center justify-center">
          {unreadCount}
        </span>
      )}
    </button>
    
    <div className="flex items-center gap-2 cursor-pointer hover:bg-#F5F5F5 px-3 py-2 rounded">
      <Avatar className="w-8 h-8" />
      <span className="text-sm font-medium">{userName}</span>
    </div>
  </div>
</header>
```

### 4.2 Sidebar

**위치**: 좌측 고정

**구조**:
```tsx
<aside className="w-60 bg-white border-r border-#E0E0E0 h-screen fixed left-0 top-16 overflow-y-auto">
  <nav className="p-4">
    {menuItems.map((item) => (
      <Link
        to={item.path}
        className={isActive ? 'bg-#E8F1FC text-#0047AB' : 'text-#666666 hover:bg-#F5F5F5'}
      >
        <item.icon className="w-5 h-5" />
        <span>{item.label}</span>
      </Link>
    ))}
  </nav>
</aside>
```

**메뉴 구조**:
| 메뉴 | 경로 | 아이콘 |
|------|------|--------|
| **대시보드** | /dashboard | LayoutDashboard |
| **실시간 상담** | /consultation | Phone |
| **상담 이력** | /history | Clock |
| **공지사항** | /notices | Bell |
| **내 정보** | /profile | User |
| **관리자** | /admin | Settings (관리자만) |

### 4.3 모달 (Modal)

**공통 모달 구조**:
```tsx
<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
  <div className="bg-white rounded-lg w-[600px] max-h-[80vh] overflow-y-auto shadow-2xl">
    {/* 헤더 */}
    <div className="flex items-center justify-between p-6 border-b border-#E0E0E0">
      <h2 className="text-lg font-bold text-#333333">{title}</h2>
      <button onClick={onClose}>
        <X className="w-5 h-5 text-#666666" />
      </button>
    </div>
    
    {/* 본문 */}
    <div className="p-6">
      {children}
    </div>
    
    {/* 푸터 (선택) */}
    <div className="flex justify-end gap-2 p-6 border-t border-#E0E0E0">
      <button className="px-4 py-2 bg-#F5F5F5 text-#666666 rounded hover:bg-#E0E0E0">
        취소
      </button>
      <button className="px-4 py-2 bg-#0047AB text-white rounded hover:bg-#003580">
        확인
      </button>
    </div>
  </div>
</div>
```

**사용 예시**:
- 공지사항 상세 모달
- 상담 상세 모달
- 직원 추가/수정 모달
- 카드 "자세히 보기" 모달 (fullText 표시)

### 4.4 카드 상세 모달 (fullText)

**구조**:
```tsx
<Modal title={card.title} onClose={onClose}>
  <div className="space-y-4">
    {/* 키워드 */}
    <div className="flex flex-wrap gap-2">
      {card.keywords.map((keyword) => (
        <span className="px-2 py-1 bg-#E8F1FC text-#0047AB rounded text-xs">
          {keyword}
        </span>
      ))}
    </div>
    
    {/* 시스템 경로 */}
    <div className="text-sm text-#0047AB font-medium">
      🖥️ {card.systemPath}
    </div>
    
    {/* 법규 */}
    <div className="text-xs text-#666666">
      📜 {card.regulation}
    </div>
    
    {/* 구분선 */}
    <div className="border-t border-#E0E0E0 my-4"></div>
    
    {/* 약관 전문 */}
    <div className="bg-#F8FBFF p-4 rounded-lg">
      <h3 className="text-sm font-bold text-#333333 mb-3">약관 전문</h3>
      <pre className="text-xs text-#666666 leading-relaxed whitespace-pre-wrap font-sans">
        {card.fullText}
      </pre>
    </div>
  </div>
</Modal>
```

### 4.5 Toast (알림)

**라이브러리**: `sonner` (이미 설치됨)

**사용 예시**:
```tsx
import { toast } from 'sonner';

// 성공
toast.success('상담이 저장되었습니다.');

// 오류
toast.error('저장에 실패했습니다.');

// 정보
toast.info('새로운 공지사항이 있습니다.');
```

**스타일**:
| 타입 | 색상 | 아이콘 |
|------|------|--------|
| **success** | bg-#34A853 | CheckCircle |
| **error** | bg-#EA4335 | XCircle |
| **info** | bg-#0047AB | Info |
| **warning** | bg-#FBBC04 | AlertTriangle |

---

## 5. 칸반보드 시스템 (핵심 차별점)

### 5.1 개념

**칸반보드**는 CALL:ACT의 핵심 차별점으로, **실시간 상담 중 STT로 감지된 키워드를 기반으로 RAG 검색을 수행하고, 검색된 문서를 Step별로 수평 슬라이딩 캐러셀 형태로 표시**하는 시스템입니다.

### 5.2 특징

1. **수평 슬라이딩 캐러셀**: Step1 → Step2 → Step3가 좌에서 우로 배치
2. **자동 전환**: 새로운 Step 키워드 감지 시 우→좌 슬라이딩 애니메이션으로 자동 전환
3. **드래그 전환**: 마우스 드래그로 이전 Step으로 이동 가능
4. **Step 인디케이터**: 현재 Step 및 전체 Step 진행 상황 표시
5. **타입별 스타일**: 카드 소스(상담 가이드, 카드 상품, 긴급 공지)에 따라 색상 구분

### 5.3 칸반보드 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│ 현재 상황 관련 정보                                       │
│ Step 1 ●──○──○              ← 드래그하여 Step 전환 →    │
│ ┌──────────────────┐ ┌──────────────────┐              │
│ │ Step 1           │ │ Step 1           │              │
│ │ 카드 즉시 정지   │ │ 분실 신고 접수   │              │
│ │                  │ │                  │              │
│ │ #카드분실        │ │ #긴급정지        │              │
│ │ #긴급정지        │ │ #본인확인        │              │
│ │                  │ │                  │              │
│ │ 🖥️ 고객관리 >... │ │ 🖥️ 시스템 >...  │              │
│ │                  │ │                  │              │
│ │ 필수 확인 사항:  │ │ 필수 확인 사항:  │              │
│ │ ✓ 본인 확인      │ │ ✓ 정지 사유     │              │
│ │ ✓ 분실 시점     │ │ ✓ 정지 시각     │              │
│ │                  │ │                  │              │
│ │ 예외 사항:       │ │ 예외 사항:       │              │
│ │ ⚠️ 본인 확인... │ │ ⚠️ 정기결제...  │              │
│ │                  │ │                  │              │
│ │ ⏱️ 처리시간 1-2분│ │ ⏱️ 처리시간 즉시│              │
│ │ ✅ 즉시 처리 필수│ │ ✅ SMS 발송 확인│              │
│ │                  │ │                  │              │
│ │ [자세히 보기]    │ │ [자세히 보기]    │              │
│ └──────────────────┘ └──────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 5.4 Step 전환 시나리오

#### 5.4.1 자동 전환 (키워드 감지)

```
1. 고객: "카드를 잃어버렸어요"
   → 키워드 감지: "카드분실", "긴급정지"
   → Step 1 표시 (2개 카드: "카드 즉시 정지", "분실 신고 접수")
   
2. 고객: "재발급은 어떻게 받나요?"
   → 키워드 감지: "재발급", "배송"
   → Step 2로 자동 전환 (우→좌 슬라이딩)
   → Step 2 표시 (2개 카드: "재발급 신청", "부정 사용 확인")
   
3. 고객: "해외 출장이 다음주라서 급해요"
   → 키워드 감지: "해외", "긴급"
   → Step 3으로 자동 전환
   → Step 3 표시 (2개 카드: "긴급 카드 발급", "공항 라운지 수령")
```

#### 5.4.2 수동 전환 (드래그)

```
상담사가 이전 Step 정보를 다시 확인하고 싶을 때:
1. 칸반보드 영역에서 마우스 드래그 (좌→우)
2. Step 3 → Step 2로 이동 (좌→우 슬라이딩)
3. 다시 Step 2 정보 확인 가능
```

#### 5.4.3 클릭 전환 (Step 인디케이터)

```
Step 인디케이터에서 이미 지나간 Step 클릭:
1. Step 인디케이터에서 Step 1 클릭
2. Step 3 → Step 1로 즉시 전환
3. Step 1 정보 확인
```

### 5.5 카드 종류별 스타일

#### 5.5.1 상담 가이드 카드 (service_guide)

```
┌──────────────────┐
│ Step 1           │ ← 파란색 배지
│ 카드 즉시 정지   │
│                  │
│ #카드분실        │ ← 파란 배경 키워드
│ #긴급정지        │
│                  │
│ 🖥️ 고객관리 >... │ ← 파란색 텍스트
│                  │
│ [자세히 보기]    │ ← 파란색 버튼
└──────────────────┘
```

| 요소 | 색상 |
|------|------|
| **배지** | bg-#0047AB, text-white |
| **키워드** | bg-#E8F1FC, text-#0047AB |
| **시스템 경로** | text-#0047AB |
| **버튼** | bg-#0047AB, hover:bg-#003580 |

#### 5.5.2 카드 상품 카드 (card_info)

```
┌──────────────────┐
│ 카드 상품        │ ← 노란색 배지
│ K-패스 체크카드  │
│                  │
│ #대중교통        │ ← 노란 배경 키워드
│ #할인            │
│                  │
│ 💳 카드상품 안내 │ ← 노란색 텍스트
│                  │
│ [카드 약관 보기] │ ← 노란색 버튼
└──────────────────┘
```

| 요소 | 색상 |
|------|------|
| **배지** | bg-#FBBC04, text-white |
| **키워드** | bg-#FFF9E6, text-#FBBC04 |
| **정보** | text-#FBBC04 |
| **버튼** | bg-#FBBC04, hover:bg-#F9AB00 |

#### 5.5.3 긴급 공지 카드 (notice - emergency)

```
┌──────────────────┐
│ 긴급 공지        │ ← 빨간색 배지
│ 쿠팡 정보유출... │
│                  │
│ #보이스피싱      │ ← 빨간 배경 키워드
│ #스미싱          │
│                  │
│ 📢 공지사항 전문 │ ← 빨간색 텍스트
│                  │
│ [전문 보기]      │ ← 빨간색 버튼
└──────────────────┘
```

| 요소 | 색상 |
|------|------|
| **배지** | bg-#EA4335, text-white |
| **키워드** | bg-#FDECEA, text-#EA4335 |
| **정보** | text-#EA4335 |
| **버튼** | bg-#EA4335, hover:bg-#D93025 |

### 5.6 애니메이션 상세

#### 5.6.1 Step 전환 애니메이션

**좌→우 슬라이딩 (Step 증가)**:
```css
@keyframes slideInFromRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

animation: slideInFromRight 0.7s ease-out both;
```

**우→좌 슬라이딩 (Step 감소)**:
```css
@keyframes slideInFromLeft {
  from {
    opacity: 0;
    transform: translateX(-100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

animation: slideInFromLeft 0.7s ease-out both;
```

#### 5.6.2 카드 등장 애니메이션

**순차 등장** (stagger):
```css
/* 첫 번째 카드 */
animation: slideInFromRight 0.7s ease-out 0s both;

/* 두 번째 카드 */
animation: slideInFromRight 0.7s ease-out 0.1s both;
```

#### 5.6.3 키워드 감지 후 칸반보드 등장

```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 현재 상황 칸반보드 */
animation: fadeInUp 0.7s ease-out 0.4s both;

/* 다음 단계 칸반보드 */
animation: fadeInUp 0.7s ease-out 1.1s both;
```

---

## 6. 데이터 흐름

### 6.1 전체 데이터 흐름

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │ ───→ │  FastAPI    │ ───→ │  Database   │
│  (React)    │ ←─── │  (Backend)  │ ←─── │  (Postgres) │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                     │
       │                    │                     │
       ├─ WebSocket ────────┤                     │
       │  (STT 실시간)      │                     │
       │                    │                     │
       ├─ REST API ─────────┤                     │
       │  (RAG 검색,        │                     │
       │   고객 정보 등)    │                     │
       │                    │                     │
       └─ JWT 인증 ─────────┤                     │
                            │                     │
                            └─ pgvector ──────────┤
                              (벡터 검색)
```

### 6.2 주요 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 요청 | 응답 |
|-----------|--------|------|------|------|
| `/api/auth/login` | POST | 로그인 | { employeeId, password } | { token, user } |
| `/api/dashboard/stats` | GET | 대시보드 통계 | - | { stats, waitingCalls, notices } |
| `/api/customers/{phone}` | GET | 고객 정보 조회 | - | { customer, recentConsultations } |
| `/api/rag/search` | POST | RAG 검색 | { query, keywords } | { cards: ScenarioCard[] } |
| `/api/consultations` | POST | 상담 저장 | { customerId, summary, categories, status, memo } | { id } |
| `/api/consultations` | GET | 상담 이력 조회 | ?page=1&limit=20 | { consultations, total } |
| `/api/notices` | GET | 공지사항 조회 | ?status=active | { notices } |
| `/ws/stt` | WebSocket | 실시간 STT | { audio } | { text, isKeyword, speaker } |

### 6.3 ScenarioCard 데이터 구조 (통합)

**백엔드 API 응답 구조**:
```typescript
interface ScenarioCard {
  // 기본 필드 (모든 카드 공통)
  id: string;
  title: string;
  keywords: string[];
  content: string;
  systemPath: string;
  requiredChecks: string[];
  exceptions: string[];
  time: string;
  note: string;
  regulation: string;
  fullText: string;
  
  // 메타데이터 (타입 구분용)
  sourceDB: 'card_info' | 'notice' | 'service_guide';
  documentType: 'card_product' | 'notice' | 'faq' | 'guide' | 'emergency';
  priority?: 'urgent' | 'high' | 'normal';
  
  // 선택적 추가 데이터 (타입별 특화 정보)
  additionalData?: {
    // 카드 상품 전용
    cardType?: string;
    annualFee?: { domestic: number | null; global: number | null };
    mainBenefits?: string[];
    
    // 공지사항 전용
    startDate?: string;
    endDate?: string;
    isPinned?: boolean;
    category?: string;
  };
}
```

**프론트엔드에서 타입별 렌더링**:
```tsx
const renderCard = (card: ScenarioCard) => {
  // 타입별 스타일 정의
  const getCardStyle = () => {
    switch (card.sourceDB) {
      case 'card_info':
        return {
          badgeColor: 'bg-[#FBBC04] text-white',
          badgeText: '카드 상품',
          keywordBg: 'bg-[#FFF9E6]',
          keywordColor: 'text-[#FBBC04]',
          buttonBg: 'bg-[#FBBC04] hover:bg-[#F9AB00]'
        };
      case 'notice':
        return {
          badgeColor: 'bg-[#EA4335] text-white',
          badgeText: card.priority === 'urgent' ? '긴급 공지' : '공지사항',
          keywordBg: 'bg-[#FDECEA]',
          keywordColor: 'text-[#EA4335]',
          buttonBg: 'bg-[#EA4335] hover:bg-[#D93025]'
        };
      default: // service_guide
        return {
          badgeColor: 'bg-[#0047AB] text-white',
          badgeText: '상담 가이드',
          keywordBg: 'bg-[#E8F1FC]',
          keywordColor: 'text-[#0047AB]',
          buttonBg: 'bg-[#0047AB] hover:bg-[#003580]'
        };
    }
  };
  
  const style = getCardStyle();
  
  return (
    <div className="...">
      {/* 배지, 키워드, 버튼에 style 적용 */}
    </div>
  );
};
```

---

## 7. 인터랙션 및 애니메이션

### 7.1 페이지 전환 애니메이션

**라이브러리**: `framer-motion` (설치 필요) 또는 CSS transition

```tsx
// 페이지 전환 (fade)
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.3 }}
>
  {children}
</motion.div>
```

### 7.2 호버 효과

| 요소 | 효과 |
|------|------|
| **버튼** | hover:bg-darker, hover:shadow-lg |
| **카드** | hover:shadow-xl, hover:border-darker |
| **테이블 행** | hover:bg-#F8FBFF |
| **링크** | hover:underline |

### 7.3 로딩 상태

**스켈레톤 로딩** (칸반보드):
```tsx
<div className="grid grid-cols-2 gap-3">
  {[1, 2].map((i) => (
    <div key={i} className="bg-gradient-to-br from-white to-#F8FBFF border-2 border-#0047AB/20 rounded-lg p-4 animate-pulse h-[180px]">
      <div className="h-5 bg-#E8F1FC rounded w-3/4 mb-3"></div>
      <div className="flex gap-1.5 mb-3">
        <div className="h-5 bg-#E8F1FC rounded w-16"></div>
        <div className="h-5 bg-#E8F1FC rounded w-20"></div>
      </div>
      <div className="space-y-2">
        <div className="h-3 bg-#F0F0F0 rounded w-full"></div>
        <div className="h-3 bg-#F0F0F0 rounded w-5/6"></div>
        <div className="h-3 bg-#F0F0F0 rounded w-4/6"></div>
      </div>
    </div>
  ))}
</div>
```

**스피너** (버튼 로딩):
```tsx
<button disabled className="...">
  <Loader2 className="w-4 h-4 animate-spin mr-2" />
  처리 중...
</button>
```

### 7.4 마이크로 인터랙션

| 인터랙션 | 효과 |
|---------|------|
| **버튼 클릭** | scale-95 (0.1s) |
| **카드 클릭** | scale-[0.98] (0.1s) |
| **입력 focus** | border 색상 변경, scale-[1.01] |
| **알림 표시** | slideInRight (toast) |

---

## 8. 반응형 디자인

### 8.1 브레이크포인트

| 디바이스 | 브레이크포인트 | Sidebar | Main Content |
|---------|--------------|---------|--------------|
| **Mobile** | < 768px | 숨김 (햄버거 메뉴) | 전체 너비 |
| **Tablet** | 768px ~ 1024px | 축소 (80px) | 축소 너비 |
| **Desktop** | > 1024px | 기본 (240px) | 기본 너비 |
| **4K** | > 1920px | 기본 (240px) | max-w-[1920px] |

### 8.2 모바일 최적화

**실시간 상담 페이지 (모바일)**:
```
┌─────────────────────┐
│ Header              │
├─────────────────────┤
│ 탭 네비게이션       │
│ [STT] [카드] [정보] │
├─────────────────────┤
│                     │
│ STT 대화 영역       │
│ (선택된 탭만 표시)  │
│                     │
├─────────────────────┤
│ 통화 시작 버튼      │
└─────────────────────┘
```

**칸반보드 (모바일)**:
- 카드를 1열로 세로 배치
- Step은 그대로 유지 (좌우 스와이프로 전환)

---

## 9. 접근성 (Accessibility)

### 9.1 키보드 네비게이션

| 요소 | 키보드 동작 |
|------|-----------|
| **버튼/링크** | Tab으로 이동, Enter로 클릭 |
| **모달** | Esc로 닫기 |
| **셀렉트** | 화살표로 옵션 선택 |
| **테이블** | 화살표로 행 이동 |

### 9.2 ARIA 속성

```tsx
// 모달
<div role="dialog" aria-labelledby="modal-title" aria-modal="true">
  <h2 id="modal-title">{title}</h2>
  {children}
</div>

// 버튼
<button aria-label="공지사항 상세 보기">
  <FileText />
</button>

// 로딩
<div aria-live="polite" aria-busy="true">
  로딩 중...
</div>
```

### 9.3 색상 대비

모든 텍스트는 WCAG 2.1 AA 기준 이상의 대비율 준수:
- **일반 텍스트**: 4.5:1 이상
- **큰 텍스트 (18px+)**: 3:1 이상

---

## 10. 부록

### 10.1 색상 팔레트

| 색상 이름 | HEX | 사용처 |
|----------|-----|--------|
| **Primary Blue** | #0047AB | 주요 버튼, 링크, 상담 가이드 |
| **Primary Blue Dark** | #003580 | Hover 상태 |
| **Secondary Yellow** | #FBBC04 | 강조, 카드 상품 |
| **Secondary Yellow Dark** | #F9AB00 | Hover 상태 |
| **Success Green** | #34A853 | 완료 상태, 성공 메시지 |
| **Success Green Dark** | #2D9A4C | Hover 상태 |
| **Danger Red** | #EA4335 | 긴급, 오류, 공지사항 |
| **Danger Red Dark** | #D93025 | Hover 상태 |
| **Text Primary** | #333333 | 주요 텍스트 |
| **Text Secondary** | #666666 | 보조 텍스트 |
| **Text Tertiary** | #999999 | 힌트, 비활성 텍스트 |
| **Background Light** | #F8FBFF | 카드 배경, 섹션 배경 |
| **Border Light** | #E0E0E0 | 일반 경계선 |
| **Border Blue** | #0047AB/20 | 카드 경계선 (20% 투명도) |

### 10.2 타이포그래피

| 요소 | 스타일 |
|------|--------|
| **Heading 1** | text-2xl (24px), font-bold |
| **Heading 2** | text-xl (20px), font-bold |
| **Heading 3** | text-lg (18px), font-bold |
| **Body** | text-base (16px), font-normal |
| **Small** | text-sm (14px), font-normal |
| **Extra Small** | text-xs (12px), font-normal |
| **Tiny** | text-[10px], font-normal |

### 10.3 간격 (Spacing)

| 간격 이름 | 값 | 사용처 |
|----------|---|--------|
| **xs** | 4px | 작은 요소 간격 |
| **sm** | 8px | 중간 요소 간격 |
| **md** | 16px | 일반 요소 간격 |
| **lg** | 24px | 섹션 간격 |
| **xl** | 32px | 큰 섹션 간격 |

### 10.4 그림자 (Shadow)

| 그림자 이름 | 값 | 사용처 |
|-----------|---|--------|
| **sm** | shadow-sm | 작은 카드 |
| **md** | shadow-md | 일반 카드 |
| **lg** | shadow-lg | 강조 카드 |
| **xl** | shadow-xl | 모달, hover 상태 |
| **2xl** | shadow-2xl | 최상위 모달 |

### 10.5 Border Radius

| 요소 | border-radius |
|------|--------------|
| **버튼** | rounded-lg (8px) |
| **카드** | rounded-lg (8px) |
| **입력 필드** | rounded-lg (8px) |
| **모달** | rounded-lg (8px) |
| **배지** | rounded (4px) |
| **아바타** | rounded-full |

---

## 11. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-17 | 초안 작성 | CALL:ACT 개발팀 |

---

## 12. 참고 문서

- `/docs/Phase6_데이터_구조_분석_및_개선방안.md`: 데이터 구조 분석 및 통합 방안
- `/docs/CALL_ACT_3개_데이터베이스_구조.md`: DB 구조 상세
- `/docs/14_칸반보드_시스템.md`: 칸반보드 설계
- `/docs/16_API_명세서.md`: API 명세
- `/src/data/scenarios.ts`: ScenarioCard 인터페이스

---

**문서 끝**
