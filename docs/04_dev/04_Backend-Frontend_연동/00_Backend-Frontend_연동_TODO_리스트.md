# Backend-Frontend 연동 TODO 리스트

**작성일**: 2026-01-13  
**작성자**: CALL:ACT Team  
**버전**: v1.0  
**관련 문서**: 
- [DB 초기화 및 재적재 가이드](../03_DB_적재_배포/14_DB_초기화_및_재적재_가이드.md)
- [Phase6 데이터 구조 분석 및 개선방안](../../../frontend_dev/docs/Phase6_데이터_구조_분석_및_개선방안.md)

---

## 개요

이 문서는 Backend와 Frontend 간 데이터 연동 및 동기화를 위한 TODO 리스트를 제공합니다. 현재 하드코딩된 Mock 데이터를 실제 DB 데이터로 전환하는 작업을 단계별로 정리했습니다.

---

## 현재 상태

### 1. Backend (DB)
- ✅ `employees` 테이블: 70명 (EMP-001 ~ EMP-070)
- ✅ `consultations` 테이블: 하나카드 상담 데이터 (6,533건)
- ✅ `consultation_documents` 테이블: 벡터 임베딩 데이터
- ✅ `service_guide_documents` 테이블: 테디카드 서비스 가이드
- ✅ `card_products` 테이블: 테디카드 카드 상품 정보
- ✅ `notices` 테이블: 테디카드 공지사항
- ✅ `keyword_dictionary` 테이블: 키워드 사전
- ✅ 성과 지표 자동 업데이트: `consultations`, `fcr`, `avgTime`, `rank`

### 2. Frontend (Mock Data)
- ⚠️ `mockData.ts`의 `employeesData`: 50명 (EMP-002 ~ EMP-050) - 하드코딩
- ⚠️ `mockData.ts`의 `consultationsData`: 27건 - 하드코딩
- ⚠️ `DashboardPage.tsx`의 통계: 하드코딩된 값
- ⚠️ `07_MockData_구조.md`의 TOP 10 상담사: 하드코딩된 값

### 3. 데이터 구조 일치성
- ✅ `consultationsData`의 `agent` → `agent_id` 변경 완료
- ✅ `getAgentName()` 헬퍼 함수 생성 완료
- ⚠️ 실제 DB 연동 미구현 (현재 Mock 데이터 사용)

---

## TODO 리스트

### Phase 1: API 엔드포인트 개발 (Backend)

#### 1.1 Employees API
- [ ] **GET `/api/employees`**: 전체 상담사 목록 조회
  - 응답: `{ employees: Employee[] }`
  - 필터링 옵션: `team`, `status`, `position`
  - 정렬 옵션: `rank`, `consultations`, `fcr`, `avgTime`
  
- [ ] **GET `/api/employees/:id`**: 특정 상담사 상세 정보 조회
  - 응답: `{ employee: Employee }`
  
- [ ] **GET `/api/employees/stats`**: 상담사 통계 조회
  - 응답: `{ total: number, byTeam: {...}, byPosition: {...} }`

#### 1.2 Consultations API
- [ ] **GET `/api/consultations`**: 상담 내역 목록 조회
  - 응답: `{ consultations: Consultation[], total: number }`
  - 필터링 옵션: `agent_id`, `category`, `status`, `dateFrom`, `dateTo`
  - 정렬 옵션: `datetime`, `duration`, `fcr`
  - 페이지네이션: `page`, `limit`
  
- [ ] **GET `/api/consultations/:id`**: 특정 상담 상세 정보 조회
  - 응답: `{ consultation: Consultation, documents: ConsultationDocument[] }`
  
- [ ] **GET `/api/consultations/stats`**: 상담 통계 조회
  - 응답: `{ todayCalls: number, completed: number, pending: number, incomplete: number, fcrRate: number }`

#### 1.3 Dashboard API
- [ ] **GET `/api/dashboard/stats`**: 대시보드 통계 조회
  - 응답: `{ todayCalls: number, avgConsultationTime: string, fcrRate: number, ongoingConsultations: number, teamStats: [...], topEmployees: [...] }`

---

### Phase 2: Frontend API 연동

#### 2.1 API 클라이언트 설정
- [ ] **`src/utils/api.ts`** 생성
  - Axios 또는 Fetch 기반 API 클라이언트
  - Base URL 설정 (환경 변수)
  - 에러 핸들링
  - 인증 토큰 관리 (필요 시)

#### 2.2 Employees 데이터 연동
- [ ] **`src/hooks/useEmployees.ts`** 생성
  - `useEmployees()`: 전체 상담사 목록 조회
  - `useEmployee(id)`: 특정 상담사 조회
  - `useEmployeeStats()`: 상담사 통계 조회
  - 캐싱 및 리프레시 로직

- [ ] **`EmployeesPage.tsx`** 수정
  - Mock 데이터 제거
  - `useEmployees()` 훅 사용
  - 로딩 상태 처리
  - 에러 처리

- [ ] **`DashboardPage.tsx`** 수정
  - `topEmployees` Mock 데이터 제거
  - API에서 우수 상담사 데이터 조회

#### 2.3 Consultations 데이터 연동
- [ ] **`src/hooks/useConsultations.ts`** 생성
  - `useConsultations(filters)`: 상담 내역 목록 조회
  - `useConsultation(id)`: 특정 상담 조회
  - `useConsultationStats()`: 상담 통계 조회
  - 필터링 및 페이지네이션 로직

- [ ] **`ConsultationHistoryPage.tsx`** 수정
  - Mock 데이터 제거
  - `useConsultations()` 훅 사용
  - 필터링 및 검색 기능 유지

- [ ] **`AdminConsultationManagePage.tsx`** 수정
  - Mock 데이터 제거
  - `useConsultations()` 훅 사용
  - 필터링 기능 유지

- [ ] **`DashboardPage.tsx`** 수정
  - `consultationHistory` Mock 데이터 제거
  - API에서 최근 상담 내역 조회

#### 2.4 Dashboard 통계 연동
- [ ] **`src/hooks/useDashboard.ts`** 생성
  - `useDashboardStats()`: 대시보드 통계 조회
  - 실시간 업데이트 (필요 시)

- [ ] **`DashboardPage.tsx`** 수정
  - 하드코딩된 통계 제거:
    - `stats.todayCalls`
    - `stats.completed`
    - `stats.pending`
    - `stats.incomplete`
    - `teamStats`
    - `weeklyGoal`
  - API에서 통계 데이터 조회
  - 로딩 상태 처리

---

### Phase 3: 데이터 구조 변환 (Backend)

#### 3.1 ScenarioCard 변환 로직
- [ ] **카드 상품 데이터 → ScenarioCard 변환**
  - `card_products` 테이블 데이터를 `ScenarioCard` 형식으로 변환
  - `systemPath`, `requiredChecks`, `exceptions`, `regulation` 필드 매핑
  - Phase6 문서의 "하이브리드 방식 (옵션 3)" 참고

- [ ] **공지사항 데이터 → ScenarioCard 변환**
  - `notices` 테이블 데이터를 `ScenarioCard` 형식으로 변환
  - `structured` 필드 활용

- [ ] **서비스 가이드 데이터 → ScenarioCard 변환**
  - `service_guide_documents` 테이블 데이터를 `ScenarioCard` 형식으로 변환
  - `fullTerms` 필드 활용

#### 3.2 API 응답 형식 통일
- [ ] **GET `/api/documents/search`**: RAG 검색 API
  - 응답: `{ documents: ScenarioCard[] }`
  - `sourceDB`, `documentType` 필드 포함
  - 프론트엔드에서 타입별 UI 최적화

---

### Phase 4: 문서 업데이트

#### 4.1 MockData 구조 문서
- [ ] **`frontend_dev/docs/07_MockData_구조.md`** 업데이트
  - Mock 데이터 사용 중단 안내
  - API 연동 가이드 추가
  - 데이터 구조 변경 이력 기록

#### 4.2 API 문서
- [ ] **`docs/04_dev/04_Backend-Frontend_연동/01_API_명세서.md`** 생성
  - 모든 API 엔드포인트 명세
  - 요청/응답 형식
  - 에러 코드 정의

#### 4.3 연동 가이드
- [ ] **`docs/04_dev/04_Backend-Frontend_연동/02_연동_가이드.md`** 생성
  - API 연동 단계별 가이드
  - 환경 설정
  - 테스트 방법

---

### Phase 5: 테스트 및 검증

#### 5.1 Backend API 테스트
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] 성능 테스트 (대량 데이터)

#### 5.2 Frontend 연동 테스트
- [ ] API 호출 테스트
- [ ] 데이터 표시 테스트
- [ ] 필터링 및 검색 테스트
- [ ] 에러 처리 테스트

#### 5.3 통합 테스트
- [ ] End-to-End 테스트
- [ ] 데이터 일치성 검증
- [ ] 성능 검증

---

## 우선순위

### 높음 (즉시 진행)
1. ✅ Employees API 개발
2. ✅ Consultations API 개발
3. ✅ Dashboard 통계 API 개발
4. ✅ Frontend API 클라이언트 설정
5. ✅ Employees 데이터 연동

### 중간 (단계별 진행)
6. Consultations 데이터 연동
7. Dashboard 통계 연동
8. ScenarioCard 변환 로직

### 낮음 (나중에 진행)
9. 문서 업데이트
10. 테스트 작성

---

## 주의사항

### 1. 데이터 일치성
- Backend의 `employees` 테이블은 70명 (EMP-001 ~ EMP-070)
- Frontend의 `mockData.ts`는 50명 (EMP-002 ~ EMP-050) - 개발용
- API 연동 시 실제 DB 데이터(70명) 사용

### 2. 성과 지표 동적 업데이트
- `employees` 테이블의 `consultations`, `fcr`, `avgTime`, `rank`는 DB에서 자동 계산
- `update_employee_performance()` 함수가 하나카드 데이터 적재 후 실행됨
- Frontend에서 조회 시 최신 데이터 반영

### 3. agent_id 사용
- `consultations` 테이블은 `agent_id` (VARCHAR(50)) 사용
- Frontend에서 상담사 이름 표시 시 `getAgentName(agent_id, employees)` 사용
- Mock 데이터도 `agent_id` 형식으로 변경 완료

### 4. Phase6 문서 참고
- 카드 상품, 공지사항, 서비스 가이드 데이터는 ScenarioCard 형식으로 변환 필요
- 하이브리드 방식 (옵션 3) 권장
- 자세한 내용은 `frontend_dev/docs/Phase6_데이터_구조_분석_및_개선방안.md` 참고

---

## 관련 문서

- [DB 초기화 및 재적재 가이드](../03_DB_적재_배포/14_DB_초기화_및_재적재_가이드.md)
- [Phase6 데이터 구조 분석 및 개선방안](../../../frontend_dev/docs/Phase6_데이터_구조_분석_및_개선방안.md)
- [MockData 구조 문서](../../../frontend_dev/docs/07_MockData_구조.md)

---

**문서 버전**: v1.0  
**최종 업데이트**: 2026-01-13
