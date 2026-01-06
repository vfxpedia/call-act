# CALL:ACT Figma Make Prompts

**Project**: CALL:ACT (Card Company Customer Service Support System)
**Created**: 2026-01-05
**Version**: 1.0
**Purpose**: Comprehensive Figma Make AI design prompts for enterprise-grade UI/UX

---

## 📋 Document Overview

This document provides detailed natural language prompts for Figma Make AI to generate professional UI/UX designs for CALL:ACT, an AI-powered customer service support system for card company call centers.

**Language Strategy**:
- Prompts: English (for Figma Make AI)
- UI Text: Korean (for actual display)

**Development Integration**:
- Figma Design → Figma Dev Mode → Code Export
- Initial: Mock Data → Later: FastAPI Backend + PostgreSQL
- Component Structure: React-based (PascalCase naming)
- Data Structure: JSON format aligned with API/DB schema

---

## 🎨 1. Project Overview

### 1.1 Project Identity

**Project Name**: CALL:ACT
**Meaning**: Call + Correct (accurate information) + Act (efficient action/completion)

**Tagline (Korean)**: "상담사에게 올바른 정보를 즉시 제공, 전화 한 통으로 완벽한 마무리를 제공하는 ONESTOP 서비스"

**Tagline (English)**: "ONESTOP: Correct answers at your fingertips, Every call, perfectly handled."

**Core Values**:
- ONESTOP: All information in one place
- Correct: Accurate information
- Immediate: Instant access
- Complete: Perfect closure

### 1.2 Target Users

- Primary: Card company customer service representatives
- Secondary: Call center supervisors and administrators
- Tertiary: New employee trainees

### 1.3 Core Differentiators

1. **Agent-Assist AI** (not customer-replacing AI) - ONESTOP service
2. **Real-time STT + RAG document search** - Kanban board information display
3. **Real consultation case-based simulation** - AI personas + TTS
4. Call emotion analysis + post-call visualization (supporting feature)

### 1.4 Key Features

- **Real-time Consultation (CSU)**: STT keyword extraction, AI kanban board with document search, consultation guide
- **Post-Call Workflow (ACW)**: Emotion analysis, quality feedback, AI-generated summary, similar case reference
- **Education Simulation (EDU)**: AI persona generation, scenario practice, evaluation system
- **Dashboard (DASH)**: Consultation statistics, announcement management, weekly issues
- **Admin Management (ADM)**: Employee management, consultation oversight, excellence case registration
- **Profile & Gamification (PROF)**: Badge system, rankings, monthly statistics

---

## 🎨 2. Design System

### 2.1 Color Palette

**Primary Colors**:
- **Primary Blue**: `#0047AB` - Trust, professionalism (main brand color)
- **Secondary Blue**: `#4A90E2` - Vitality, innovation (accent)

**Functional Colors**:
- **Accent Orange**: `#FF6B35` - Urgency, emphasis
- **Success Green**: `#34A853` - Completed, positive
- **Warning Yellow**: `#FBBC04` - Caution, pending
- **Danger Red**: `#EA4335` - Error, negative

**Neutral Colors**:
- **Background**: `#F5F5F5` - Light gray (main background)
- **Card Background**: `#FFFFFF` - White (card/panel background)
- **Text Primary**: `#333333` - Dark gray (main text)
- **Text Secondary**: `#666666` - Medium gray (secondary text)
- **Text Disabled**: `#999999` - Light gray (disabled text)
- **Border**: `#E0E0E0` - Light gray (borders, dividers)
- **Audio Player BG**: `#F8F8F8` - Very light gray (inline player)

### 2.2 Typography

**Font Family**: Pretendard (Korean), Inter (fallback for English)

**Type Scale**:
- **Display**: Pretendard Bold, 32px, line-height 1.2 (page titles)
- **H1**: Pretendard Bold, 24px, line-height 1.3 (section headers)
- **H2**: Pretendard Semibold, 20px, line-height 1.4 (sub-headers)
- **H3**: Pretendard Semibold, 16px, line-height 1.5 (card titles)
- **Body**: Pretendard Regular, 14px, line-height 1.6 (main content)
- **Caption**: Pretendard Regular, 12px, line-height 1.5 (labels, metadata)
- **Small**: Pretendard Regular, 10px, line-height 1.4 (timestamps, badges)

### 2.3 Spacing System

**8px Base Grid**:
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px
- **2xl**: 48px
- **3xl**: 64px

### 2.4 Component Standards

**Buttons**:
- **Primary**: Background `#0047AB`, Text White, Height 40px, Padding 16px 24px, Border-radius 6px
- **Secondary**: Background White, Text `#0047AB`, Border `1px solid #0047AB`, Height 40px
- **Danger**: Background `#EA4335`, Text White
- **Disabled**: Background `#E0E0E0`, Text `#999999`

**Input Fields**:
- Height: 40px
- Padding: 12px 16px
- Border: `1px solid #E0E0E0`
- Border-radius: 6px
- Focus: Border `#0047AB`, Box-shadow `0 0 0 3px rgba(0, 71, 171, 0.1)`

**Cards**:
- Background: White
- Border-radius: 8px
- Box-shadow: `0 1px 3px rgba(0, 0, 0, 0.1)`
- Padding: 20px

**Badges/Tags**:
- Height: 24px
- Padding: 4px 12px
- Border-radius: 12px (pill shape)
- Font-size: 12px
- Font-weight: 500

**Modals**:
- Background: White
- Border-radius: 12px
- Max-width: 800px (large), 600px (medium), 400px (small)
- Box-shadow: `0 10px 40px rgba(0, 0, 0, 0.2)`
- Overlay: Background `rgba(0, 0, 0, 0.5)`

### 2.5 Icon System

- **Style**: Outlined, 2px stroke weight
- **Sizes**: 16px (small), 20px (medium), 24px (large), 32px (extra-large)
- **Color**: Inherit from parent text color

### 2.6 Data Structure Guidelines

**Component Naming** (PascalCase):
- `CallHistoryCard`, `CustomerInfoPanel`, `KanbanBoard`, `AudioPlayer`, `EmotionChart`

**Data Fields** (camelCase):
- `consultationId`, `customerId`, `timestamp`, `status`, `category`, `duration`

**Mock Data Format** (JSON):
```json
{
  "consultationId": "CS-20250105-1432",
  "customerId": "CUST-001",
  "customerName": "홍길동",
  "category": "카드분실",
  "status": "완료",
  "timestamp": "2025-01-05T14:32:00Z",
  "duration": "05:12"
}
```

---

## 📄 3. Page-by-Page Figma Make Prompts

### 3.1 Login Page (MBM-AUTH-001)

#### Page Purpose
Authentication screen for card company customer service representatives to access the CALL:ACT system using their employee ID and password.

#### User Scenario
1. Employee opens CALL:ACT application
2. Enters employee ID (사번) and password
3. System validates credentials
4. On success: Navigate to dashboard
5. On failure: Display error message

#### Layout Structure

**Container**:
- Centered login form: 400px width × 500px height
- Background: Full-screen gradient from `#0047AB` (top) to `#4A90E2` (bottom)

**Content Hierarchy**:
1. Logo area (top)
2. Login form (center)
3. Error message area (conditional, below form)

#### Figma Make Prompt

```
Create a modern, professional login page for an enterprise card company customer service system called CALL:ACT.

LAYOUT:
- Full-screen background with a vertical gradient from deep blue (#0047AB) at top to bright blue (#4A90E2) at bottom
- Centered white card: 400px width × 500px height, border-radius 12px, box-shadow 0 10px 40px rgba(0,0,0,0.2)
- Card padding: 48px 40px

CONTENT (top to bottom):
1. Logo area:
   - Text "CALL:ACT" centered, font size 32px, bold, color #0047AB
   - Subtitle "상담사 지원 시스템" centered below logo, font size 14px, color #666666, margin-top 8px

2. Spacing: 40px vertical gap

3. Login form:
   - Label "사번" (Employee ID), font size 14px, color #333333, margin-bottom 8px
   - Input field: height 48px, full width, border 1px solid #E0E0E0, border-radius 6px, padding 12px 16px, placeholder "사번을 입력하세요"

   - Spacing: 20px vertical gap

   - Label "비밀번호" (Password), font size 14px, color #333333, margin-bottom 8px
   - Password input field: height 48px, full width, border 1px solid #E0E0E0, border-radius 6px, padding 12px 16px, placeholder "비밀번호를 입력하세요"

   - Spacing: 32px vertical gap

   - Submit button "로그인": full width, height 48px, background #0047AB, text white, font size 16px, bold, border-radius 6px

4. Error message area (conditional, initially hidden):
   - Below login button, margin-top 16px
   - Background #FEE, border 1px solid #EA4335, border-radius 6px, padding 12px 16px
   - Icon: warning icon in red (#EA4335), 16px size
   - Text: "입력된 정보가 올바르지 않습니다." or "관리자에게 권한을 요청하세요.", color #EA4335, font size 14px

INTERACTIONS:
- Input focus: border changes to #0047AB, box-shadow 0 0 0 3px rgba(0, 71, 171, 0.1)
- Button hover: background darkens to #003580
- Button active: slight scale down (0.98)

STYLE:
- Clean, minimal, professional
- High contrast for accessibility
- Adequate spacing for touch targets
```

**Component Data Structure**:
```json
{
  "LoginForm": {
    "employeeId": "",
    "password": "",
    "errorMessage": null,
    "errorType": "invalid_credentials" | "no_permission" | null
  }
}
```

---

### 3.2 Main Dashboard (DASH)

#### Page Purpose
Central hub for customer service representatives to view consultation statistics, recent activity, announcements, and navigate to key functions (start consultation, training simulation).

#### User Scenario
1. User logs in and lands on dashboard
2. Views today's consultation statistics
3. Checks recent consultation history
4. Reads latest announcements and weekly issues
5. Clicks "상담 시작" to begin work

#### Layout Structure

**Global Layout**:
- Header: Fixed, 60px height, full width
- Sidebar: Fixed, 250px width, full height
- Main Content: 3-column grid, remaining space

**Header** (60px height):
- Left: CALL:ACT logo (120px width)
- Right: User profile icon (32px), notification icon (24px with badge)

**Sidebar** (250px width):
- Menu items (each 48px height):
  1. 대시보드 (Home icon, active state: background #E8F1FC)
  2. 상담 시작 (Primary button style, emphasized)
  3. 교육 시뮬레이션
  4. 상담 내역
  5. 시뮬레이션 내역
  6. 사원 목록
  7. 프로필
  8. [관리자 전용] 총괄 현황
  9. [관리자 전용] 사원 관리
  10. [관리자 전용] 공지사항 관리

**Main Content Grid**:
- Left column: 30% width
- Center column: 40% width
- Right column: 30% width
- Gap between columns: 24px

#### Figma Make Prompt

```
Create an enterprise-grade dashboard for a card company customer service system called CALL:ACT. The dashboard should have a clean, data-driven, professional appearance suitable for call center agents.

HEADER (60px height, full width, background white, border-bottom 1px solid #E0E0E0):
- Left side: Logo "CALL:ACT" in bold, color #0047AB, font size 20px, margin-left 24px
- Right side (margin-right 24px):
  - Notification icon (bell icon, 20px, color #666666) with small red badge showing "3"
  - User profile avatar (32px circle, background #0047AB, white initials "홍길" inside)
  - Horizontal spacing between icons: 16px

SIDEBAR (250px width, full height, background white, border-right 1px solid #E0E0E0):
- Padding: 16px
- Menu items (vertical list, each 48px height, border-radius 6px):
  1. "대시보드" - Home icon (20px), active state: background #E8F1FC, text #0047AB, bold
  2. "상담 시작" - Phone icon (20px), background #0047AB, text white, bold (emphasized button)
  3. "교육 시뮬레이션" - Book icon (20px)
  4. "상담 내역" - List icon (20px)
  5. "시뮬레이션 내역" - History icon (20px)
  6. "사원 목록" - Users icon (20px)
  7. "프로필" - User icon (20px)
  8. Divider line (margin 16px vertical)
  9. "[관리자]" section header in gray, font size 12px
  10. "총괄 현황" - Chart icon (20px)
  11. "사원 관리" - Settings icon (20px)
  12. "공지사항 관리" - Megaphone icon (20px)

- Menu item styling (non-active):
  - Padding: 12px 16px
  - Icon and text horizontal spacing: 12px
  - Text color: #333333, font size 14px
  - Hover: background #F5F5F5

MAIN CONTENT AREA (3-column grid, padding 24px, background #F5F5F5):

LEFT COLUMN (30% width):
Card 1: 상담 현황 (Consultation Stats)
- Title "상담 현황", font size 18px, bold, color #333333
- Large number "127" (total count), font size 48px, bold, color #0047AB, centered
- Below: 3 sub-stats in a horizontal row:
  - "완료 95" (green icon, #34A853)
  - "대기 12" (yellow icon, #FBBC04)
  - "미완료 20" (red icon, #EA4335)
- Each sub-stat: font size 14px, vertical layout (icon above text)
- Card background white, border-radius 8px, padding 20px, box-shadow 0 1px 3px rgba(0,0,0,0.1)

Spacing: 20px

Card 2: 공지사항 (Announcements)
- Title "공지사항", font size 18px, bold, color #333333, with "더보기" link (font size 12px, color #0047AB) on the right
- List of 5 items, each:
  - Tag badge (e.g., "[이벤트]", "[시스템]"), background #E8F1FC, color #0047AB, font size 12px, padding 4px 8px, border-radius 4px
  - Title text (e.g., "하나카드x메가커피 프로모션 안내"), font size 14px, color #333333, truncate to 1 line
  - Date "2025-01-05", font size 12px, color #999999
  - Vertical spacing: 12px between items
  - Hover: background #F5F5F5
- Card background white, border-radius 8px, padding 20px

CENTER COLUMN (40% width):
Card 3: 상담 내역 (Consultation History)
- Title "상담 내역", font size 18px, bold, color #333333, with "전체보기" link on the right
- Table/list of 10 recent consultations:
  - Each row: 48px height, padding 12px, border-bottom 1px solid #F0F0F0
  - Status badge (left): "완료" (green), "진행중" (blue), "미완료" (gray), 60px width, centered text
  - Category tag: "[카드분실]", background light blue, font size 12px
  - Title: "카드 분실 신고 및 재발급 요청", font size 14px, color #333333, truncate to 1 line
  - Customer name: "홍길동", font size 12px, color #666666
  - Timestamp: "14:32", font size 12px, color #999999
  - Row hover: background #F8F8F8
- Card background white, border-radius 8px, padding 20px

RIGHT COLUMN (30% width):
Card 4: 금주의 이슈 (Weekly Issues)
- Title "금주의 이슈", font size 18px, bold, color #333333
- List of 5 issues, each:
  - Icon (warning triangle, 16px, color #FF6B35) on the left
  - Summary text (e.g., "해외 결제 차단 문의 급증 (42건)"), font size 14px, color #333333, multi-line allowed
  - Timestamp "3시간 전", font size 12px, color #999999
  - Vertical spacing: 16px between items
- Card background white, border-radius 8px, padding 20px

Spacing: 20px

Card 5: 우수사원 사례집 (Excellence Cases)
- Title "우수사원 사례집", font size 18px, bold, color #333333
- 3 cards in vertical stack:
  - Each card: background #FFF9E6, border-left 4px solid #FBBC04, padding 16px, border-radius 6px
  - Star icon (16px, gold color) + Employee name "김민수", font size 14px, bold
  - Case title: "진상 고객 대응 우수 사례", font size 13px, color #666666
  - Vertical spacing: 12px between cards

OVERALL STYLE:
- Professional, clean, data-driven
- Adequate whitespace for readability
- Color coding for quick visual scanning
- Card-based layout for modularity
```

**Component Data Structure**:
```json
{
  "DashboardStats": {
    "totalConsultations": 127,
    "completed": 95,
    "pending": 12,
    "incomplete": 20
  },
  "Announcements": [
    {
      "announcementId": "ANN-001",
      "tag": "이벤트",
      "title": "하나카드x메가커피 프로모션 안내",
      "date": "2025-01-05"
    }
  ],
  "ConsultationHistory": [
    {
      "consultationId": "CS-20250105-1432",
      "status": "완료" | "진행중" | "미완료",
      "category": "카드분실",
      "title": "카드 분실 신고 및 재발급 요청",
      "customerName": "홍길동",
      "timestamp": "2025-01-05T14:32:00Z"
    }
  ],
  "WeeklyIssues": [
    {
      "issueId": "ISS-001",
      "summary": "해외 결제 차단 문의 급증",
      "count": 42,
      "timestamp": "3시간 전"
    }
  ],
  "ExcellenceCases": [
    {
      "caseId": "EXC-001",
      "employeeName": "김민수",
      "title": "진상 고객 대응 우수 사례"
    }
  ]
}
```

---

### 3.3 Real-time Consultation Screen (CSU) 🎯

#### Page Purpose
Core service screen where customer service representatives receive real-time AI assistance during live calls. Displays STT-extracted keywords, AI-powered document search results in kanban board format, customer history, and direct KMS search.

#### User Scenario
1. Agent accepts incoming call
2. STT extracts keywords in real-time ("카드분실", "해외결제")
3. AI displays relevant documents in kanban board (current situation + next steps)
4. Agent refers to consultation guide for recommended phrases
5. Agent takes notes in memo pad
6. Agent can manually search KMS if AI misses information
7. Call ends, proceeds to post-call workflow

#### Layout Structure

**3-Column Layout**:
- Column 1 (Left, ~10%): Customer info + call controls
- Column 2 (Center, Main ~65%): AI kanban board area (CORE SERVICE)
- Column 3 (Right, ~25%): Memo + KMS search

#### Figma Make Prompt

```
Create a highly functional, real-time consultation screen for a card company call center system. This is the CORE SERVICE screen where AI assists agents during live calls. The design must be clean, efficient, and optimized for rapid information scanning.

LAYOUT: 3-column structure, full screen

--- COLUMN 1 (LEFT, ~10% width, background #FAFAFA, border-right 1px solid #E0E0E0) ---

CALL CONTROLS (top, fixed section):
- Timer display: "05:32" large font size 32px, bold, color #333333, centered
- Accept button: Large circular button (64px diameter), background #34A853 (green), phone icon in white, centered
- End call button: Large circular button (64px diameter), background #EA4335 (red), phone-x icon in white, centered, margin-top 16px

Spacing: 32px

CUSTOMER INFO CARD (compact, background white, border-radius 8px, padding 16px):
- Title "고객 정보", font size 14px, bold, color #333333
- Customer details (vertical list, font size 13px, color #666666, line-height 1.8):
  - ID: CUST-001
  - 이름: 홍길동
  - 전화: 010-1234-5678
  - 생년월일: 1985-03-15
  - 주소: 서울시 강남구... (truncate)

Spacing: 20px

RECENT CONSULTATION HISTORY (compact list):
- Title "최근 상담", font size 14px, bold, color #333333, margin-bottom 12px
- 2 items, each (padding 8px, background white, border-radius 6px, border-left 3px solid):
  - Border color: green (#34A853) for "완료", blue (#4A90E2) for "진행중"
  - Title: "카드 재발급 문의" (1 line, truncate), font size 12px, color #333333
  - Timestamp: "2025-01-03 10:30", font size 11px, color #999999
  - Category tag: "[카드분실]", font size 10px, background #E8F1FC, color #0047AB, padding 2px 6px, border-radius 3px
  - Click: opens detail modal

--- COLUMN 2 (CENTER, MAIN ~65% width, background white, padding 24px) ---

STT KEYWORD BADGES (top, fixed section):
- Section title "인입 키워드", font size 14px, color #666666, margin-bottom 12px
- Horizontal row of badges:
  - Each badge: background #0047AB, color white, padding 8px 16px, border-radius 16px, font size 14px, bold
  - Examples: "카드분실", "해외결제", "수수료문의"
  - Spacing between badges: 8px

Spacing: 24px

CURRENT SITUATION KANBAN BOARD:
- Section title "현재 상황 관련 정보", font size 18px, bold, color #333333, margin-bottom 16px
- 2-column grid (max 2 cards side by side):
  - Each kanban card:
    - Background white
    - Border 1px solid #E0E0E0
    - Border-radius 8px
    - Padding 20px
    - Box-shadow 0 2px 4px rgba(0,0,0,0.05)
    - Min-height 200px

    Card content:
    - Document title: "카드 분실 신고 처리 절차", font size 16px, bold, color #0047AB, margin-bottom 12px
    - Keyword tags: horizontal badges (e.g., "#분실신고", "#즉시정지"), background #E8F1FC, color #0047AB, font size 11px, padding 4px 8px, border-radius 4px, margin-right 6px
    - Main content: 3-4 lines of text, font size 14px, color #333333, line-height 1.6
      - Highlighted keywords within text: background yellow (#FFF9C4), font-weight bold
    - "자세히 보기" button: bottom-right, text button, color #0047AB, font size 13px, underline on hover

- Grid gap: 16px

Spacing: 32px

NEXT STEPS KANBAN BOARD:
- Section title "다음 단계 예상 정보", font size 18px, bold, color #333333, margin-bottom 16px
- Same structure as Current Situation Kanban (2-column grid, 2 cards max)
- Content focuses on predicted next process based on similar past cases
- Example card title: "재발급 카드 배송 안내"

Spacing: 32px

CONSULTATION GUIDE (bottom of kanban area, small card):
- Background #F0F7FF (light blue), border-left 4px solid #0047AB, padding 16px, border-radius 6px
- Icon: lightbulb icon (16px, color #0047AB) on the left
- Title "권장 안내 멘트", font size 14px, bold, color #0047AB, margin-bottom 8px
- AI-generated phrase (2-3 lines): "고객님, 카드 분실 신고 접수되었습니다. 즉시 카드 사용이 정지되며, 3-5일 내 재발급 카드가 등록된 주소로 배송됩니다.", font size 14px, color #333333, line-height 1.6
- Copy button (top-right): small icon button (24px), copy icon, color #0047AB

--- COLUMN 3 (RIGHT, ~25% width, background #FAFAFA, padding 20px) ---

MEMO PAD (top section):
- Title "상담 메모", font size 16px, bold, color #333333, margin-bottom 12px
- Textarea: height 200px, background white, border 1px solid #E0E0E0, border-radius 6px, padding 12px, font size 14px, color #333333, placeholder "상담 중 메모를 입력하세요..."
- Save button: width 100%, height 36px, background #0047AB, color white, font size 14px, border-radius 6px, margin-top 12px

Spacing: 32px

KMS DIRECT SEARCH (bottom section):
- Title "직접 검색", font size 16px, bold, color #333333, margin-bottom 12px
- Helper text: "AI가 놓친 정보를 직접 검색하세요", font size 12px, color #999999, margin-bottom 12px
- Search input: height 40px, background white, border 1px solid #E0E0E0, border-radius 6px, padding 12px, placeholder "검색어 입력", icon (search icon, 16px, color #999999) inside right
- Search button: width 100%, height 36px, background #4A90E2, color white, font size 14px, border-radius 6px, margin-top 8px
- Search results (if any): simple list below search button
  - Each result: padding 8px, background white, border-radius 4px, font size 13px, color #333333, truncate to 1 line, margin-top 8px
  - Hover: background #E8F1FC, clickable to open modal

OVERALL STYLE:
- Optimized for rapid information scanning
- Clear visual hierarchy
- Kanban cards prominently displayed in center
- Adequate whitespace despite high information density
- Professional, clean, enterprise-grade
```

**Component Data Structure**:
```json
{
  "CallSession": {
    "sessionId": "SESSION-20250105-1432",
    "duration": 332,
    "status": "active"
  },
  "CustomerInfo": {
    "customerId": "CUST-001",
    "name": "홍길동",
    "phone": "010-1234-5678",
    "birthdate": "1985-03-15",
    "address": "서울시 강남구..."
  },
  "RecentHistory": [
    {
      "consultationId": "CS-20250103-1030",
      "title": "카드 재발급 문의",
      "timestamp": "2025-01-03T10:30:00Z",
      "status": "완료",
      "category": "카드분실"
    }
  ],
  "STTKeywords": ["카드분실", "해외결제", "수수료문의"],
  "CurrentSituationKanban": [
    {
      "documentId": "DOC-001",
      "title": "카드 분실 신고 처리 절차",
      "tags": ["#분실신고", "#즉시정지"],
      "content": "고객의 카드 분실 신고 시 즉시 카드 사용을 정지하고...",
      "highlights": ["즉시 정지", "재발급"]
    }
  ],
  "NextStepsKanban": [
    {
      "documentId": "DOC-002",
      "title": "재발급 카드 배송 안내",
      "tags": ["#재발급", "#배송"],
      "content": "재발급 카드는 등록된 주소로 3-5일 내 배송됩니다..."
    }
  ],
  "ConsultationGuide": {
    "phrase": "고객님, 카드 분실 신고 접수되었습니다. 즉시 카드 사용이 정지되며, 3-5일 내 재발급 카드가 등록된 주소로 배송됩니다."
  },
  "Memo": "",
  "KMSSearchResults": [
    {
      "documentId": "DOC-003",
      "title": "해외 결제 차단 해제 방법"
    }
  ]
}
```

---

### 3.4 Post-Call Workflow Screen (ACW)

#### Page Purpose
Post-call processing screen where agents review call transcript, emotion analysis, quality feedback, and complete AI-generated consultation summary.

#### User Scenario
1. Call ends, agent proceeds to ACW screen
2. Reviews call transcript and checks emotion analysis (collapsible)
3. Reviews current case summary and similar past case
4. Edits AI-generated post-call document
5. Completes follow-up tasks and department handoff
6. Saves and finalizes consultation record

#### Figma Make Prompt

```
Create a comprehensive post-call workflow screen. This screen helps agents efficiently complete post-call documentation with AI assistance.

LAYOUT: 2-column structure

COLUMN 1 (LEFT, ~30% width):
- Call transcript in chat-style format, height ~300px, scrollable
- Agent messages: right-aligned, background #0047AB, white text, border-radius 12px 12px 4px 12px
- Customer messages: left-aligned, background #E0E0E0, dark text, border-radius 12px 12px 12px 4px
- Timestamps below each message, font size 11px

- Feedback section (collapsible accordion below transcript):
  - Header "상담 피드백" with chevron icon
  - Emotion Analysis: 3 emojis (😠 초반, 😐 중반, 😊 후반), size 32px
  - Quality badge: "품질 평가: 상", background green
  - Pentagon radar chart (180px × 180px): 5 axes (후처리 시간, 감사 표현, 감정 전환, 매뉴얼 준수), filled area semi-transparent blue

COLUMN 2 (RIGHT, ~70% width):
- Similar case reference cards (top, 2 cards side-by-side, ~48% width each):
  - Card 1: "현재 상담 케이스", border 2px solid #0047AB, category tag, summary 2-3 lines
  - Card 2: "유사 사례 참고", background #F8F8F8, past case summary, "자세히 보기" button

- AI-generated post-call document (main form section):
  - Title "상담 후처리 문서", font size 20px
  - Form fields:
    1. 제목 (text input, height 40px)
    2. 상담 ID (read-only, background #F5F5F5)
    3. 상담 상태 & 분류 (horizontal row, 2 dropdowns)
    4. 고객 정보 (read-only box, background #F5F5F5, 3 lines)
    5. 통화 일시 (read-only)
    6. AI 상담 요약본 (large textarea, height 200px, pre-filled with AI content)
    7. 후속 일정:
       - 추후 할 일 (textarea 80px)
       - 이관 부서 (dropdown)
       - 이관 부서 전달 사항 (textarea 80px)
    8. 상담 메모 (textarea 100px, auto-populated from CSU)

  - All inputs: border 1px solid #E0E0E0, border-radius 6px, padding 12-16px
  - Spacing between sections: 20px

- Save button (sticky bottom-right):
  - Width 200px, height 48px, background #0047AB, white text, font size 16px
  - Text: "후처리 완료 및 저장"
  - Box-shadow 0 4px 12px rgba(0,71,171,0.3)

STYLE: Organized, form-based, clean, professional
```

---

### 3.5 Education Simulation Screens (EDU)

#### Page Purpose
Training system for employees to practice consultation scenarios using AI-generated personas.

#### Figma Make Prompt

```
Create an education simulation system with 4 sub-screens: scenario selection, simulation in-progress (identical to CSU), post-simulation (identical to ACW with evaluation), and history list.

SCREEN 1: SCENARIO SELECTION
- Background #F5F5F5, centered content
- Title "교육 시뮬레이션", font size 28px, color #0047AB, centered
- Subtitle "실제 상담 사례로 연습하고 AI 피드백을 받으세요", font size 16px, color #666666

- Category grid (2×3 or 3×2):
  - Each card: width ~30%, background white, border-radius 12px, padding 32px
  - Icon 64px (card, globe, dollar, star, warning icons based on category)
  - Category title: font size 18px, bold, below icon
  - Description 2 lines, font size 14px, color #666666
  - Badge "12건 학습 가능", background #E8F1FC, color #0047AB
  - Hover: scale 1.02, enhanced shadow

- Recent simulations (bottom):
  - Horizontal scrollable list, 5 items
  - Each: width 240px, "[시뮬레이션]" tag (background #FBBC04), title, date, score

SCREEN 2: SIMULATION IN-PROGRESS
- Identical to CSU screen (section 3.3)
- Add: "[시뮬레이션]" badge (top-left, background #FBBC04, white text)
- Add: AI Persona Info panel (top-right, 250px width):
  - Border 2px solid #FBBC04, background white
  - Details: 나이대, 성향, 문의 유형, 시나리오

SCREEN 3: SIMULATION POST-PROCESSING
- Identical to ACW screen (section 3.4)
- Add: "[시뮬레이션]" badge (top-left)
- Add: Evaluation score panel (top of Column 2, before similar case cards):
  - Background gradient #E8F1FC to white
  - Large score "85점", font size 48px, color #0047AB, centered
  - 4.5/5 gold stars
  - Evaluation text, font size 14px, centered
- Save button text: "시뮬레이션 완료 및 저장"

SCREEN 4: SIMULATION HISTORY
- Title "시뮬레이션 내역", font size 24px
- Filter bar: category dropdown, date picker, search button
- Table format:
  - Columns: [시뮬레이션] tag, category, title, score, date, actions
  - Each row 60px, hover background #F8F8F8
- Pagination at bottom
- Max 30 items stored

STYLE: Encouraging, educational, gamified with scores/ratings
```

---

### 3.6 Admin - Overall Statistics (ADM-STAT)

#### Page Purpose
Admin dashboard showing center-wide, category-specific, and individual agent consultation statistics for performance monitoring and management.

#### Figma Make Prompt

```
Create an admin statistics dashboard with 3-tier structure: center overview, category breakdown, and individual agent performance.

LAYOUT: 3-section vertical stack, full width

SECTION 1: CENTER OVERVIEW (top)
- Section title "센터 현황", font size 24px, bold, color #333333, margin-bottom 20px
- 4 statistic cards in horizontal row:
  - Each card: width 23%, background white, border-radius 8px, padding 24px, box-shadow 0 1px 3px rgba(0,0,0,0.1)
  - Card 1: "상담 대기 건수"
    - Icon: clock icon, 32px, color #FBBC04
    - Large number "12", font size 48px, bold, color #FBBC04
    - Label below, font size 14px, color #666666
  - Card 2: "하루 평균 상담 완료 건수"
    - Icon: check icon, 32px, color #34A853
    - Large number "95", font size 48px, bold, color #34A853
  - Card 3: "평균 통화 시간"
    - Icon: phone icon, 32px, color #0047AB
    - Large number "4:32", font size 48px, bold, color #0047AB
    - Subtext "분:초", font size 12px, color #999999
  - Card 4: "평균 후처리 시간"
    - Icon: edit icon, 32px, color #4A90E2
    - Large number "2:15", font size 48px, bold, color #4A90E2
  - Gap between cards: 2%

SECTION 2: CATEGORY BREAKDOWN (middle)
- Section title "카테고리별 현황", font size 24px, bold, color #333333, margin-top 48px, margin-bottom 20px
- Category tabs (horizontal):
  - Tab pills: background #E0E0E0 (inactive), #0047AB (active), color #666666 (inactive), white (active)
  - Tabs: "전체", "카드분실", "해외결제", "수수료문의", "기타"
  - Height 40px, padding 12px 24px, border-radius 20px, font size 14px
- Selected category statistics (same 4-card layout as Section 1, but category-specific)

SECTION 3: INDIVIDUAL AGENT PERFORMANCE (bottom)
- Section title "카테고리별 상담사 개인 현황", font size 24px, bold, color #333333, margin-top 48px, margin-bottom 20px
- Table format:
  - Header row: background #F5F5F5, height 48px, font size 14px, bold, color #666666
  - Columns: "이름", "완료 건수", "평균 통화 시간", "평균 후처리 시간", "상세보기"
  - Data rows: each 56px height, border-bottom 1px solid #E0E0E0
  - Agent name: font size 14px, bold, color #333333
  - Numbers: font size 14px, color #666666, right-aligned
  - "상세보기" button: small text button, color #0047AB, underline on hover
  - Hover: background #F8F8F8

STYLE: Data-driven, clean, professional, suitable for management oversight
```

---

### 3.7 Admin - Employee Management (ADM-EMP)

#### Page Purpose
Admin interface for managing employee accounts including registration, activation/deactivation, role assignment, and password reset.

#### Figma Make Prompt

```
Create an employee management interface for admins to manage call center staff accounts.

LAYOUT: Header with actions + table

HEADER (horizontal row, margin-bottom 24px):
- Left side:
  - Title "사원 관리", font size 24px, bold, color #333333
- Right side:
  - "사원 등록" button: background #0047AB, color white, height 40px, padding 12px 24px, border-radius 6px
  - "활성화" button (batch action): background #34A853, color white, margin-left 12px
  - "비활성화" button (batch action): background #EA4335, color white, margin-left 12px

EMPLOYEE TABLE:
- Table header: background #F5F5F5, height 48px, font size 14px, bold, color #666666
- Columns:
  - Checkbox (40px width, for batch selection)
  - 사번 (120px)
  - 이름 (100px)
  - 소속 (120px)
  - 직급 (80px)
  - 연락처 (140px)
  - 이메일 (200px, truncate if needed)
  - 상태 (80px: toggle switch - active/inactive)
  - 상세 (60px: icon button)

- Data rows: each 60px height, border-bottom 1px solid #E0E0E0
- Checkbox: standard checkbox, 20px size
- Toggle switch:
  - Active: background #34A853, circle on right
  - Inactive: background #E0E0E0, circle on left
  - Switch size: 44px × 24px
- "상세" button: eye icon, 20px, color #0047AB, clickable
- Hover: background #F8F8F8

PAGINATION (bottom):
- Standard pagination: "이전", 1, 2, 3, ..., 10, "다음"
- Current page highlighted: background #0047AB, color white

EMPLOYEE REGISTRATION MODAL (triggered by "사원 등록" button):
- Modal size: 600px width, auto height
- Background white, border-radius 12px, box-shadow 0 10px 40px rgba(0,0,0,0.2)
- Padding: 32px
- Title "사원 등록", font size 24px, bold, color #333333, margin-bottom 24px

- Form fields (2-column grid for some):
  - 사번 (text input, required, full width)
  - 이름 (text input, required, left column)
  - 소속 (text input, required, right column)
  - 직급 (dropdown, left column)
  - 연락처 (text input, right column)
  - 입사일 (date picker, left column)
  - 이메일 (text input, full width)

- Info note: "신규 사원 초기 비밀번호: 0000", font size 13px, color #666666, background #F5F5F5, padding 12px, border-radius 6px, margin-top 16px

- Modal actions (bottom):
  - "취소" button: background white, border 1px solid #E0E0E0, color #666666
  - "등록" button: background #0047AB, color white
  - Horizontal spacing: 12px, right-aligned

EMPLOYEE DETAIL MODAL (triggered by eye icon):
- Similar layout to registration modal
- All fields editable
- Additional fields:
  - 퇴사일 (date picker, optional)
  - 프로그램 권한 생성일 (read-only, background #F5F5F5)
  - 프로그램 권한 해지일 (date picker, optional)
  - 관리자 권한 (toggle: "관리자" / "사원")
- "비밀번호 초기화" button: background #EA4335, color white, full width, margin-top 16px
  - Confirmation text: "0000으로 초기화됩니다", font size 12px, color #999999

STYLE: Clean, table-based, functional admin interface
```

---

### 3.8 Admin - Call Management (ADM-CALL) 🆕

#### Page Purpose
Admin interface for managing all consultation records including filtering, inline audio playback, and excellence case registration for training purposes.

#### Figma Make Prompt

```
Create a call management interface with advanced filtering, inline audio playback, and excellence case registration. This is a NEW admin page for comprehensive consultation oversight.

LAYOUT: Filter bar + consultation table with inline audio player

FILTER BAR (top, background white, padding 20px, border-radius 8px, box-shadow 0 1px 3px rgba(0,0,0,0.1)):
- Horizontal row of filters:
  - 날짜 범위 (date range picker, width 280px)
  - 상담사 (dropdown, width 160px, options: "전체", individual agents)
  - 카테고리 (dropdown, width 140px, options: "전체", "카드분실", "해외결제", etc.)
  - 상담 상태 (button group toggle: "전체", "완료", "진행중", "미완료")
  - 검색 button: background #0047AB, color white, width 100px, height 40px
- Spacing between filters: 12px

BATCH ACTIONS BAR (below filter bar, margin-top 16px):
- Left: Selected count "3개 선택됨", font size 14px, color #666666
- Right: "우수 사례 일괄 등록" button, background #FBBC04, color white, padding 10px 20px

CONSULTATION TABLE:
- Header row: background #F5F5F5, height 48px, font size 14px, bold, color #666666
- Columns:
  - Checkbox (40px)
  - 상담 ID (140px)
  - 상담사 (100px)
  - 고객명 (100px)
  - 카테고리 (120px: tag badge)
  - 상담 상태 (100px: colored badge)
  - 일시 (160px)
  - 통화시간 (80px)
  - 재생 (60px: play icon button)
  - 상세 (60px: view icon button)
  - 우수사례 (60px: star icon button)

- Data rows: each 60px height (when collapsed), 100px height (when player expanded)
- Row hover: background #F8F8F8

INLINE AUDIO PLAYER (expands when play button clicked):
- Initial state: Row height 60px, player hidden
- Clicked state: Row height expands to 100px with smooth animation (300ms ease-out)
- Player UI (appears below row content, margin-top 8px):
  - Background #F8F8F8 (neutral gray, no emphasis)
  - Border-radius 6px
  - Padding 12px
  - Height 40px

  Player controls (horizontal layout):
  - Play/Pause button (left): circular button 24px, icon 16px, color #0047AB
  - Progress bar (center, flexible width):
    - Background #E0E0E0
    - Height 2px
    - Played portion: background #0047AB
    - Draggable handle: 8px circle, color #0047AB
  - Time display (right of progress): "03:45 / 05:12", font size 12px, color #666666
  - Download icon (right): 16px, color #666666, clickable
  - Speed control (right-most): dropdown "1x", "1.5x", "2x", font size 12px, color #666666

- Behavior:
  - Click play on another row: previous player auto-collapses
  - Only ONE player open at a time
  - Smooth collapse animation when switching

EXCELLENCE CASE REGISTRATION MODAL:
- Modal size: 700px width, auto height (scrollable if needed)
- Title "📋 우수 사례로 등록", font size 24px, bold, color #333333

- Auto-filled info (read-only, background #F5F5F5):
  - 상담 ID: CS-20250105-1432
  - 상담사: 홍길동 (EMP-001) | 상담1팀
  - 일시: 2025-01-05 14:32

- Input fields:
  1. 우수 사례 분류 (checkboxes, multi-select):
     - ☑ 진상 고객 대응 우수
     - ☑ 복잡한 다단계 처리
     - ☑ 높은 FCR (1회 완결)
     - ☑ 감정 전환 우수 (부정→긍정)
     - ☑ 매뉴얼 준수 모범
     - ☑ 크로스셀/업셀 성공
     - Grid: 2 columns, checkbox size 20px, label font size 14px

  2. 난이도 (radio buttons, 3 options):
     - ⭐ 일반 / ⭐⭐ 어려움 / ⭐⭐⭐ 매우 어려움
     - Horizontal layout, star icons in gold (#FBBC04)

  3. 교육 가치 점수 (star rating, 1-5):
     - "신입 교육에 얼마나 유용한가?", subtitle font size 13px, color #666666
     - 5 clickable stars, 24px each, gold when selected

  4. 사례 요약 (textarea):
     - Height 100px, border 1px solid #E0E0E0, border-radius 6px
     - Placeholder: "예: 고객이 해외 결제 차단 해제 요청 후 추가로 한도 증액까지 1회 통화로 처리..."
     - Character counter: "45 / 200", font size 12px, color #999999, right-aligned

  5. 학습 포인트 (tag input):
     - Tag pills: #다단계처리, #감정관리, #크로스셀
     - Background #E8F1FC, color #0047AB, removable (X icon)
     - "+ 태그 추가" input, max 5 tags
     - Font size 13px

  6. 추천 대상 (checkboxes):
     - ☑ 신입 필수 시뮬레이션
     - ☑ 중급자 역량 강화
     - ☑ 전체 공유

- Auto-analysis metrics (display only, background #F0F7FF, padding 16px, border-radius 6px):
  - FCR: ✅ 1회 완결 (green check icon)
  - 감정: 😠 → 😐 → 😊 (+85% 긍정 전환)
  - Font size 14px, color #333333

- Modal actions:
  - "취소" button: background white, border 1px solid #E0E0E0
  - "우수 사례로 등록" button: background #0047AB, color white, padding 12px 24px

STYLE: Professional admin interface, inline player is minimalist and unobtrusive, excellence case form is comprehensive and well-organized
```

---

### 3.9 Profile Page with Gamification (PROF) 🎮

#### Page Purpose
Employee profile page showcasing personal information, achievement badges, monthly performance statistics, center rankings, and personal information editing capabilities.

#### Figma Make Prompt

```
Create an engaging profile page with gamification elements (badges, rankings, statistics) to motivate call center agents.

LAYOUT: 3-section vertical stack

SECTION 1: PROFILE CARD WITH BADGES (top)
- Background white, border-radius 12px, padding 32px, box-shadow 0 2px 8px rgba(0,0,0,0.08)

- Horizontal layout:
  - Left side: Profile photo
    - Circular avatar 100px diameter
    - Border 4px solid #0047AB
    - Placeholder: Initials "홍길" on blue background

  - Right side (info + badges):
    - Name "홍길동", font size 24px, bold, color #333333
    - Employee info (vertical stack, font size 14px, color #666666, line-height 1.8):
      - 사번: EMP-001
      - 소속: 상담1팀
      - 직급: 대리
      - **권한 부여일: 2024-01-15** (NOT 입사일)

    - Spacing: 20px

    - Achievement badges section:
      - Subtitle "획득 배지", font size 16px, bold, color #333333, margin-bottom 12px
      - Horizontal row of 5-7 badges:
        - Each badge: width 80px, padding 12px, background white, border 2px solid based on type, border-radius 8px, text-align center
        - Badge 1: 🏆 "FCR 마스터" (border gold #FBBC04, color #FBBC04)
        - Badge 2: ⚡ "스피드 레이서" (border blue #0047AB, color #0047AB)
        - Badge 3: 💬 "감정 케어" (border green #34A853, color #34A853)
        - Badge 4: ⭐ "완벽주의자" (border purple #9C27B0, color #9C27B0)
        - Badge 5: 🎓 "시뮬 마니아" (border orange #FF6B35, color #FF6B35)
        - Icon 32px, label below font size 11px, bold
        - Hover: transform scale(1.05)

SECTION 2: MONTHLY STATISTICS CARD (middle, margin-top 24px)
- Title "📊 1월 성과", font size 20px, bold, color #333333, margin-bottom 20px
- Background gradient from #E8F1FC to white, border-radius 12px, padding 32px

- Statistics list (vertical):
  - Each item: horizontal layout, padding 12px 0, border-bottom 1px solid #E0E0E0 (except last)

  - Item 1: "상담 완료: 127건 (팀 평균 대비 +15%)"
    - Left: metric name + value, font size 16px, color #333333
    - Right: comparison badge "+15%", background #34A853, color white, padding 4px 12px, border-radius 12px, font size 13px

  - Item 2: "FCR: 94% (목표: 90%) ✅"
    - Same layout
    - Checkmark indicates goal achieved, color #34A853

  - Item 3: "평균 통화: 4분 32초 (팀 평균: 5분 10초)"
    - Comparison: "-38초 빠름", green badge

  - Item 4: "후처리 시간: 2분 15초 (목표: 3분) ✅"
    - Achievement checkmark

  - Item 5: "감정 전환율: 82% (목표: 75%) ✅"
    - Achievement checkmark

- Center ranking (prominent display at bottom):
  - Large text "센터 랭킹: 3위 / 45명", font size 24px, bold, color #0047AB, centered
  - Trophy icon 32px next to ranking
  - Background #FFF9E6, padding 20px, border-radius 8px, margin-top 20px

SECTION 3: PERSONAL INFORMATION EDIT (bottom, margin-top 24px)
- Title "개인정보 수정", font size 20px, bold, color #333333, margin-bottom 20px
- Background white, border-radius 12px, padding 32px

- Form fields (2-column grid):
  - Left column:
    - 연락처 (text input, height 40px, full width)
    - 이메일 (text input, height 40px, full width)

  - Right column:
    - 비밀번호 변경 button: background #0047AB, color white, height 40px, full width, text "비밀번호 변경"

- Save button:
  - Full width (spanning both columns), height 48px, background #0047AB, color white, font size 16px, bold
  - Text: "저장", margin-top 24px

OVERALL STYLE:
- Engaging, motivational tone
- Gamification elements prominent but professional
- Clear visual hierarchy
- Badges use color-coding for different achievement types
- Statistics comparison shows progress and motivation
```

---

## 📱 4. Common Modals & Components

### 4.1 Consultation Detail Modal

#### Purpose
View full consultation details including transcript, post-call document, and audio playback when clicking consultation ID from any list.

#### Figma Make Prompt

```
Create a comprehensive consultation detail view modal.

MODAL:
- Size: 1000px width × 800px height
- Background white, border-radius 12px, box-shadow 0 10px 40px rgba(0,0,0,0.2)
- Close button: top-right corner, X icon 24px, color #999999

HEADER (top, padding 24px, border-bottom 1px solid #E0E0E0):
- Consultation ID: "CS-20250105-1432", font size 20px, bold, color #0047AB
- Metadata row:
  - Agent: "홍길동", font size 14px, color #666666
  - Customer: "고객명: 김민수", font size 14px, color #666666
  - Date: "2025-01-05 14:32", font size 14px, color #999999
  - Horizontal spacing: 24px between items

CONTENT (2-column layout, padding 24px):

LEFT COLUMN (40%):
- Call transcript:
  - Title "상담 전문", font size 16px, bold, margin-bottom 12px
  - Chat-style format (same as ACW), height 500px, scrollable
  - Agent/customer messages with timestamps

- Audio player (bottom of left column):
  - Full-width audio player, height 60px
  - Play/pause, progress bar, time display, download button
  - Background #F8F8F8, border-radius 6px, padding 12px
  - Sync with transcript: playing section highlights corresponding messages

RIGHT COLUMN (60%):
- Post-call document (scrollable):
  - All form fields from ACW, but in READ-ONLY mode
  - Background #F5F5F5 for read-only fields
  - Category tags, status badges displayed
  - AI summary, follow-up tasks, memo all visible

FOOTER (bottom, padding 20px, border-top 1px solid #E0E0E0):
- Download buttons:
  - "PDF 다운로드" button: background white, border 1px solid #E0E0E0, color #666666
  - "오디오 다운로드" button: background white, border 1px solid #E0E0E0, color #666666
  - Horizontal spacing: 12px, right-aligned

INTERACTION:
- Clicking message in transcript jumps to that timestamp in audio
- Playing audio highlights corresponding transcript section
```

---

### 4.2 Document Detail Modal

#### Purpose
View full document content from kanban boards or KMS search results.

#### Figma Make Prompt

```
Create a document viewer modal for policy documents and knowledge base articles.

MODAL:
- Size: 800px width × 700px height
- Background white, border-radius 12px
- Close button: top-right, X icon

HEADER (padding 24px, border-bottom 1px solid #E0E0E0):
- Document title: "카드 분실 신고 처리 절차", font size 22px, bold, color #0047AB
- Category tags: horizontal row
  - Each tag: background #E8F1FC, color #0047AB, font size 12px, padding 4px 10px, border-radius 4px
  - Examples: "#분실신고", "#즉시정지", "#재발급"

CONTENT (padding 24px, scrollable):
- Markdown-style formatting:
  - Headings (H1-H3): bold, sizes 20px/18px/16px
  - Paragraphs: font size 14px, line-height 1.8, color #333333
  - Lists (bullet/numbered): proper indentation, 14px
  - Tables: bordered, header background #F5F5F5
  - Code blocks: background #F5F5F5, monospace font, padding 16px
  - Highlighted keywords: background yellow (#FFF9C4), bold

- Example content structure:
  ```
  ## 1. 즉시 처리 사항
  - 카드 사용 즉시 정지
  - 고객 확인 (생년월일, 주소)

  ## 2. 재발급 절차
  1. 재발급 신청 접수
  2. 등록 주소 확인
  3. 배송 예정일 안내 (3-5일)
  ```

FOOTER (padding 20px, border-top 1px solid #E0E0E0):
- "복사" button: background white, border, copies content to clipboard
- "인쇄" button: background white, border, opens print dialog
- Horizontal spacing: 12px, right-aligned

STYLE: Clean, readable, document-focused
```

---

### 4.3 Announcement/Issue Detail Modal

#### Purpose
View full announcement or weekly issue content from dashboard.

#### Figma Make Prompt

```
Create announcement/issue detail viewer.

MODAL:
- Size: 700px width × auto height (max 600px)
- Background white, border-radius 12px
- Close button: top-right

HEADER (padding 24px, border-bottom 1px solid #E0E0E0):
- Tag badge: "[이벤트]" or "[시스템]" or "[긴급]", background based on type
  - 이벤트: #E8F1FC
  - 시스템: #FFF9E6
  - 긴급: #FFEBEE
- Title: "하나카드x메가커피 프로모션 안내", font size 20px, bold, color #333333, margin-top 8px
- Metadata:
  - Author: "운영팀", font size 13px, color #666666
  - Date: "2025-01-05 09:30", font size 13px, color #999999
  - Source (for external news): "출처: 외부 뉴스", font size 12px, color #999999, italic

CONTENT (padding 24px, scrollable):
- Markdown content:
  - Text paragraphs: font size 14px, line-height 1.8
  - Images: centered, max-width 100%, border-radius 8px
  - Links: color #0047AB, underline on hover

- For "금주의 이슈" (weekly issues):
  - AI summary style (like Coupang reviews):
    - Keyword badges: "해외 결제 차단", "42건 발생"
    - Summary text: "최근 7일간 해외 결제 차단 문의가 급증하였습니다. 주요 원인은..."
    - Bullet points with key insights

FOOTER (padding 20px, border-top 1px solid #E0E0E0):
- "닫기" button: background #0047AB, color white, padding 10px 24px, centered

STYLE: Clean, news-article style, appropriate for informational content
```

---

### 4.4 Excellence Case Detail Modal (from ADM-CALL)

#### Purpose
Comprehensive modal for registering consultation cases as excellence examples for training.

#### Figma Make Prompt

```
Create excellence case registration form (covered in detail in section 3.8 Admin - Call Management).

REFERENCE: See ADM-CALL Excellence Case Registration Modal in section 3.8 for complete specifications including:
- 6 classification checkboxes (multi-select)
- 3-tier difficulty rating
- 1-5 star education value score
- 100-200 character case summary textarea
- Tag input for learning points (max 5 tags)
- Target audience checkboxes
- Auto-analysis metrics display (FCR, emotion shift)

MODAL SIZE: 700px width × auto height (scrollable)

STYLE: Comprehensive, form-heavy, organized into clear sections
```

---

## 5. Document Summary & Usage Guide

### 5.1 Pages Overview

This document includes comprehensive Figma Make prompts for **9 main pages + 4 common modals**:

**Priority 1 (Core Service)**:
1. Login Page
2. Main Dashboard
3. Real-time Consultation (CSU) - 3-column layout
4. Post-Call Workflow (ACW) - 2-column layout

**Priority 2 (High Importance)**:
5. Education Simulation (4 sub-screens)
6. Admin - Overall Statistics
7. Admin - Employee Management
8. Admin - Call Management (with inline audio player)

**Priority 3 (Supporting Features)**:
9. Profile Page (with gamification)

**Common Modals**:
- Consultation Detail Modal
- Document Detail Modal
- Announcement/Issue Detail Modal
- Excellence Case Registration Modal

### 5.2 How to Use These Prompts

1. **Copy the prompt** for the desired page from the code blocks above
2. **Paste into Figma Make** (AI design generation feature)
3. **Review generated design** and iterate as needed
4. **Export to Figma Dev Mode** to extract React code
5. **Integrate with mock data** initially, then connect to FastAPI backend + PostgreSQL

### 5.3 Design System Consistency

All prompts follow the established design system:
- **Colors**: Primary Blue (#0047AB), Success Green (#34A853), etc.
- **Typography**: Pretendard font family, consistent size scale
- **Spacing**: 8px base grid
- **Components**: Standardized buttons, inputs, cards, modals

### 5.4 Data Structure Integration

Each prompt includes:
- **Component naming** (PascalCase): `CallHistoryCard`, `KanbanBoard`
- **Data field naming** (camelCase): `consultationId`, `customerId`
- **Mock data examples** in JSON format aligned with future API/DB schema

### 5.5 Next Steps

After Figma design completion:
1. Review all designs for consistency
2. Gather user feedback from call center representatives
3. Iterate based on feedback
4. Export code from Figma Dev Mode
5. Implement React components with mock data
6. Connect to FastAPI backend
7. Integrate with PostgreSQL database
8. Deploy and test with real users

---

**Document End**

**Total Pages**: 9 main pages + 4 modals = 13 comprehensive UI/UX specifications

**Created**: 2026-01-05
**Version**: 1.0
**Project**: CALL:ACT (Card Company Customer Service Support System)
